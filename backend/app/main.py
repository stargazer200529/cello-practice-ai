from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import Database, PieceEntity, utc_now
from app.database import PracticeSessionEntity, PracticeSegmentEntity
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


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    if settings.database_url.startswith("sqlite:///"):
        Path(settings.database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    database = Database(settings.database_url)
    database.initialize()
    storage = PieceStorage(settings.musicxml_storage_dir)
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

    return app


app = create_app()
