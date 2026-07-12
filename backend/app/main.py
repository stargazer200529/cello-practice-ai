from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import Database, PieceEntity, PracticeSessionEntity, PracticeSegmentEntity, RecordingEntity, utc_now
from app.musicxml import (
    MAX_MUSICXML_BYTES,
    MusicXMLValidationError,
    musicxml_document,
    musicxml_text,
    parse_musicxml,
    validate_filename,
)
from app.piece_repository import PieceRepository
from app.piece_storage import PieceStorage
from app.practice_session_repository import PracticeSessionRepository
from app.practice_session_schemas import (
    PracticeSegmentResponse,
    PracticeSessionComplete,
    PracticeSessionCreate,
    PracticeSessionResponse,
)
from app.recording_repository import RecordingRepository
from app.recording_schemas import RecordingCreate, RecordingRemove, RecordingResponse
from app.recording_storage import RecordingStorage

MAX_UPLOAD_BYTES = MAX_MUSICXML_BYTES
LOCAL_USER_ID = "00000000-0000-0000-0000-000000000001"


def piece_response(piece: PieceEntity) -> dict[str, object]:
    def timestamp(value: datetime) -> str:
        return (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).isoformat()
    return {"id": piece.id, "title": piece.title, "composer": piece.composer,
        "original_filename": piece.original_filename, "part_names": piece.part_names,
        "measure_count": piece.measure_count, "time_signatures": piece.time_signatures,
        "key_signatures": piece.key_signatures, "created_at": timestamp(piece.created_at),
        "updated_at": timestamp(piece.updated_at)}


def practice_session_response(practice_session: PracticeSessionEntity) -> PracticeSessionResponse:
    def timestamp(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    def segment_response(segment: PracticeSegmentEntity) -> PracticeSegmentResponse:
        return PracticeSegmentResponse(
            id=segment.id,
            passage_id=segment.passage_definition_id,
            focus_codes=segment.focus_codes,
            sequence_number=segment.sequence_number,
            started_at=timestamp(segment.started_at),
            ended_at=timestamp(segment.ended_at),
            target_tempo_bpm=float(segment.target_tempo_bpm) if segment.target_tempo_bpm is not None else None,
            notes=segment.notes,
        )

    segments = [segment_response(segment) for segment in practice_session.segments]
    current_segment = next((segment for segment in reversed(segments) if segment.ended_at is None), None)
    return PracticeSessionResponse(
        id=practice_session.id,
        piece_id=practice_session.piece_id,
        status=practice_session.status,
        practice_source=practice_session.practice_source,
        instrument_profile_id=practice_session.instrument_profile_id,
        started_at=timestamp(practice_session.started_at),
        ended_at=timestamp(practice_session.ended_at),
        elapsed_seconds=practice_session.elapsed_seconds,
        target_duration_seconds=practice_session.target_duration_seconds,
        session_notes=practice_session.session_notes,
        current_segment=current_segment,
        segments=segments,
    )


def recording_response(recording: RecordingEntity) -> RecordingResponse:
    def timestamp(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    return RecordingResponse(
        id=recording.id,
        practice_session_id=recording.practice_session_id,
        practice_segment_id=recording.practice_segment_id,
        passage_id=recording.passage_definition_id,
        recording_number=recording.recording_number,
        label=f"Recording {recording.recording_number}",
        status=recording.status,
        started_at=timestamp(recording.started_at),
        ended_at=timestamp(recording.ended_at),
        duration_ms=recording.duration_ms,
        original_mime_type=recording.original_mime_type,
        size_bytes=recording.size_bytes,
        sha256_checksum=recording.sha256_checksum,
        sample_rate_hz=recording.sample_rate_hz,
        channel_count=recording.channel_count,
        microphone_label=recording.microphone_label,
        removal_reason=recording.removal_reason,
        removed_at=timestamp(recording.removed_at),
        created_at=timestamp(recording.created_at),
        updated_at=timestamp(recording.updated_at),
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    if settings.database_url.startswith("sqlite:///"):
        Path(settings.database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    database = Database(settings.database_url)
    database.initialize()
    storage = PieceStorage(settings.musicxml_storage_dir)
    recording_storage = RecordingStorage(settings.recording_storage_dir)
    app = FastAPI(title="Cello Practice AI API", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["*"])

    def get_session():
        yield from database.session()

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    async def read_and_parse(file: UploadFile):
        validate_filename(file.filename)
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise MusicXMLValidationError("The MusicXML file must be 5 MB or smaller.")
        if not content:
            raise MusicXMLValidationError("The uploaded MusicXML file is empty.")
        document = musicxml_document(file.filename or "", content)
        text = musicxml_text(document)
        return document, text, parse_musicxml(document)

    @app.post("/scores/metadata", tags=["scores"])
    async def score_metadata(file: UploadFile = File(...)) -> dict[str, object]:
        try:
            _, text, metadata = await read_and_parse(file)
            return {**asdict(metadata), "musicxml": text}
        except MusicXMLValidationError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        finally:
            await file.close()

    @app.post("/pieces", status_code=201, tags=["pieces"])
    async def create_piece(file: UploadFile = File(...), session: Session = Depends(get_session)):
        stored_path: str | None = None
        try:
            document, _, metadata = await read_and_parse(file)
            piece_id = str(uuid4())
            stored_path = storage.write(piece_id, ".musicxml", document)
            now = utc_now()
            piece = PieceEntity(id=piece_id, title=metadata.title, composer=metadata.composer,
                original_filename=file.filename or "score.musicxml", musicxml_path=stored_path,
                part_names=metadata.part_names, measure_count=metadata.measure_count,
                time_signatures=metadata.time_signatures, key_signatures=metadata.key_signatures,
                created_at=now, updated_at=now, archived=False)
            try:
                return piece_response(PieceRepository(session).add(piece))
            except Exception:
                session.rollback()
                storage.delete(stored_path)
                raise
        except MusicXMLValidationError as error:
            if stored_path:
                storage.delete(stored_path)
            raise HTTPException(status_code=422, detail=str(error)) from error
        finally:
            await file.close()

    @app.get("/pieces", tags=["pieces"])
    def list_pieces(session: Session = Depends(get_session)):
        return [piece_response(piece) for piece in PieceRepository(session).list_active()]

    def require_piece(piece_id: str, session: Session) -> PieceEntity:
        piece = PieceRepository(session).get_active(piece_id)
        if not piece:
            raise HTTPException(status_code=404, detail="Piece not found.")
        return piece

    @app.get("/pieces/{piece_id}", tags=["pieces"])
    def get_piece(piece_id: str, session: Session = Depends(get_session)):
        return piece_response(require_piece(piece_id, session))

    @app.get("/pieces/{piece_id}/musicxml", response_class=PlainTextResponse, tags=["pieces"])
    def get_piece_musicxml(piece_id: str, session: Session = Depends(get_session)):
        piece = require_piece(piece_id, session)
        try:
            return storage.read(piece.musicxml_path).decode("utf-8")
        except (FileNotFoundError, UnicodeDecodeError) as error:
            raise HTTPException(status_code=500, detail="Stored MusicXML is unavailable.") from error

    @app.delete("/pieces/{piece_id}", status_code=204, tags=["pieces"])
    def delete_piece(piece_id: str, session: Session = Depends(get_session)):
        piece = require_piece(piece_id, session)
        path = piece.musicxml_path
        PieceRepository(session).delete(piece)
        storage.delete(path)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.post(
        "/api/v1/practice-sessions",
        status_code=201,
        tags=["practice sessions"],
        response_model=PracticeSessionResponse,
    )
    def create_practice_session(
        payload: PracticeSessionCreate, session: Session = Depends(get_session)
    ) -> PracticeSessionResponse:
        require_piece(payload.piece_id, session)
        now = utc_now()
        practice_session = PracticeSessionEntity(
            id=str(uuid4()),
            user_id=LOCAL_USER_ID,
            piece_id=payload.piece_id,
            instrument_profile_id=payload.instrument_profile_id,
            status="active",
            practice_source=payload.practice_source,
            started_at=now,
            ended_at=None,
            elapsed_seconds=0,
            target_duration_seconds=payload.target_duration_seconds,
            session_notes=payload.session_notes,
            created_at=now,
            updated_at=now,
        )
        initial_segment = PracticeSegmentEntity(
            id=str(uuid4()),
            practice_session_id=practice_session.id,
            passage_definition_id=payload.initial_passage_id,
            focus_codes=payload.focus_codes,
            sequence_number=0,
            started_at=now,
            ended_at=None,
            target_tempo_bpm=payload.target_tempo_bpm,
            notes=None,
            created_at=now,
            updated_at=now,
        )
        try:
            created = PracticeSessionRepository(session).add(practice_session, initial_segment)
        except Exception:
            session.rollback()
            raise
        return practice_session_response(created)

    def require_practice_session(session_id: str, session: Session) -> PracticeSessionEntity:
        practice_session = PracticeSessionRepository(session).get(session_id)
        if practice_session is None or practice_session.user_id != LOCAL_USER_ID:
            raise HTTPException(status_code=404, detail="Practice session not found.")
        return practice_session

    def require_recording(recording_id: str, session: Session) -> RecordingEntity:
        recording = RecordingRepository(session).get(recording_id)
        if recording is None:
            raise HTTPException(status_code=404, detail="Recording not found.")
        require_practice_session(recording.practice_session_id, session)
        return recording

    @app.get(
        "/api/v1/practice-sessions/{session_id}",
        tags=["practice sessions"],
        response_model=PracticeSessionResponse,
    )
    def get_practice_session(
        session_id: str, session: Session = Depends(get_session)
    ) -> PracticeSessionResponse:
        return practice_session_response(require_practice_session(session_id, session))

    @app.post(
        "/api/v1/practice-sessions/{session_id}/complete",
        tags=["practice sessions"],
        response_model=PracticeSessionResponse,
    )
    def complete_practice_session(
        session_id: str,
        payload: PracticeSessionComplete | None = None,
        session: Session = Depends(get_session),
    ) -> PracticeSessionResponse:
        practice_session = require_practice_session(session_id, session)
        if practice_session.status == "completed":
            return practice_session_response(practice_session)
        if practice_session.status != "active":
            raise HTTPException(status_code=409, detail="Practice session is not active.")
        ended_at = payload.ended_at if payload and payload.ended_at else utc_now()
        if ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        started_at = practice_session.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        if ended_at < started_at:
            raise HTTPException(status_code=422, detail="Session end time cannot precede its start time.")
        elapsed_seconds = int((ended_at - started_at).total_seconds())
        PracticeSessionRepository(session).complete(practice_session, ended_at, elapsed_seconds)
        return practice_session_response(require_practice_session(session_id, session))

    @app.post(
        "/api/v1/practice-sessions/{session_id}/recordings",
        status_code=201,
        tags=["recordings"],
        response_model=RecordingResponse,
    )
    def create_recording(
        session_id: str,
        payload: RecordingCreate,
        session: Session = Depends(get_session),
    ) -> RecordingResponse:
        practice_session = require_practice_session(session_id, session)
        if practice_session.status != "active":
            raise HTTPException(status_code=409, detail="Practice session is not active.")
        repository = RecordingRepository(session)
        segment = repository.get_segment(payload.practice_segment_id)
        if (
            segment is None
            or segment.practice_session_id != practice_session.id
            or segment.ended_at is not None
        ):
            raise HTTPException(status_code=404, detail="Active practice segment not found.")
        started_at = payload.started_at or utc_now()
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        recording = RecordingEntity(
            id=str(uuid4()),
            practice_session_id=practice_session.id,
            practice_segment_id=segment.id,
            passage_definition_id=payload.passage_id or segment.passage_definition_id,
            recording_number=repository.next_number(practice_session.id),
            status="capturing",
            started_at=started_at,
            ended_at=None,
            duration_ms=None,
            storage_key=None,
            original_mime_type=None,
            size_bytes=None,
            sha256_checksum=None,
            sample_rate_hz=None,
            channel_count=None,
            microphone_label=payload.microphone_label,
            removal_reason=None,
            removed_at=None,
            created_at=started_at,
            updated_at=started_at,
        )
        try:
            return recording_response(repository.add(recording))
        except Exception:
            session.rollback()
            raise

    @app.post(
        "/api/v1/recordings/{recording_id}/audio",
        tags=["recordings"],
        response_model=RecordingResponse,
    )
    async def upload_recording_audio(
        recording_id: str,
        file: UploadFile = File(...),
        ended_at: datetime = Form(...),
        duration_ms: int = Form(..., ge=0),
        original_mime_type: str | None = Form(default=None),
        sample_rate_hz: int | None = Form(default=None, gt=0),
        channel_count: int | None = Form(default=None, gt=0),
        session: Session = Depends(get_session),
    ) -> RecordingResponse:
        recording = require_recording(recording_id, session)
        practice_session = require_practice_session(recording.practice_session_id, session)
        if practice_session.status != "active":
            raise HTTPException(status_code=409, detail="Practice session is not active.")
        if recording.status != "capturing":
            raise HTTPException(status_code=409, detail="Recording audio has already been finalized.")
        stored_path: str | None = None
        try:
            mime_type = (original_mime_type or file.content_type or "").strip()
            if not mime_type.lower().startswith("audio/"):
                raise HTTPException(status_code=415, detail="An audio MIME type is required.")
            content = await file.read(settings.max_recording_bytes + 1)
            if len(content) > settings.max_recording_bytes:
                raise HTTPException(status_code=413, detail="The recording exceeds the configured size limit.")
            if not content:
                raise HTTPException(status_code=422, detail="The uploaded recording is empty.")
            normalized_end = ended_at if ended_at.tzinfo else ended_at.replace(tzinfo=timezone.utc)
            normalized_start = (
                recording.started_at
                if recording.started_at.tzinfo
                else recording.started_at.replace(tzinfo=timezone.utc)
            )
            if normalized_end < normalized_start:
                raise HTTPException(status_code=422, detail="Recording end time cannot precede its start time.")
            stored_path = recording_storage.write(
                practice_session.user_id,
                recording.practice_session_id,
                recording.id,
                mime_type,
                content,
            )
            try:
                saved = RecordingRepository(session).save_audio(
                    recording,
                    ended_at=normalized_end,
                    duration_ms=duration_ms,
                    storage_key=stored_path,
                    mime_type=mime_type,
                    size_bytes=len(content),
                    checksum=sha256(content).hexdigest(),
                    sample_rate_hz=sample_rate_hz,
                    channel_count=channel_count,
                )
            except Exception:
                session.rollback()
                recording_storage.delete(stored_path)
                raise
            return recording_response(saved)
        finally:
            await file.close()

    @app.get(
        "/api/v1/recordings/{recording_id}",
        tags=["recordings"],
        response_model=RecordingResponse,
    )
    def get_recording(recording_id: str, session: Session = Depends(get_session)) -> RecordingResponse:
        return recording_response(require_recording(recording_id, session))

    @app.get("/api/v1/recordings/{recording_id}/audio", tags=["recordings"])
    def get_recording_audio(recording_id: str, session: Session = Depends(get_session)) -> FileResponse:
        recording = require_recording(recording_id, session)
        if recording.status == "removed" or not recording.storage_key or not recording.original_mime_type:
            raise HTTPException(status_code=404, detail="Recording audio not found.")
        try:
            path = recording_storage.path(recording.storage_key)
            if not path.is_file():
                raise FileNotFoundError
        except FileNotFoundError as error:
            raise HTTPException(status_code=404, detail="Recording audio not found.") from error
        return FileResponse(
            path,
            media_type=recording.original_mime_type,
            filename=f"Recording {recording.recording_number}{path.suffix}",
            content_disposition_type="inline",
        )

    @app.get(
        "/api/v1/practice-sessions/{session_id}/recordings",
        tags=["recordings"],
        response_model=list[RecordingResponse],
    )
    def list_recordings(
        session_id: str, session: Session = Depends(get_session)
    ) -> list[RecordingResponse]:
        require_practice_session(session_id, session)
        return [
            recording_response(recording)
            for recording in RecordingRepository(session).list_for_session(session_id)
        ]

    @app.post(
        "/api/v1/recordings/{recording_id}/remove",
        tags=["recordings"],
        response_model=RecordingResponse,
    )
    def remove_recording(
        recording_id: str,
        payload: RecordingRemove | None = None,
        session: Session = Depends(get_session),
    ) -> RecordingResponse:
        recording = require_recording(recording_id, session)
        if recording.status == "removed":
            return recording_response(recording)
        if recording.storage_key:
            recording_storage.delete(recording.storage_key)
        removed = RecordingRepository(session).remove(
            recording,
            payload.reason if payload else None,
            utc_now(),
        )
        return recording_response(removed)

    return app


app = create_app()
