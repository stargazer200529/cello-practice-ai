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
from app.musicxml import MusicXMLValidationError, parse_musicxml, validate_filename
from app.piece_repository import PieceRepository
from app.piece_storage import PieceStorage

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def piece_response(piece: PieceEntity) -> dict[str, object]:
    def timestamp(value: datetime) -> str:
        return (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).isoformat()

    return {
        "id": piece.id, "title": piece.title, "composer": piece.composer,
        "original_filename": piece.original_filename, "part_names": piece.part_names,
        "measure_count": piece.measure_count, "time_signatures": piece.time_signatures,
        "key_signatures": piece.key_signatures, "created_at": timestamp(piece.created_at),
        "updated_at": timestamp(piece.updated_at),
    }


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
        if len(content) > MAX_UPLOAD_BYTES: raise MusicXMLValidationError("The MusicXML file must be 5 MB or smaller.")
        if not content: raise MusicXMLValidationError("The uploaded MusicXML file is empty.")
        return content, parse_musicxml(content)

    @app.post("/scores/metadata", tags=["scores"])
    async def score_metadata(file: UploadFile = File(...)) -> dict[str, object]:
        try:
            _, metadata = await read_and_parse(file)
            return asdict(metadata)
        except MusicXMLValidationError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        finally: await file.close()

    @app.post("/pieces", status_code=201, tags=["pieces"])
    async def create_piece(file: UploadFile = File(...), session: Session = Depends(get_session)):
        stored_path: str | None = None
        try:
            content, metadata = await read_and_parse(file)
            piece_id = str(uuid4())
            stored_path = storage.write(piece_id, Path(file.filename or "score.musicxml").suffix, content)
            now = utc_now()
            piece = PieceEntity(id=piece_id, title=metadata.title, composer=metadata.composer,
                original_filename=file.filename or "score.musicxml", musicxml_path=stored_path,
                part_names=metadata.part_names, measure_count=metadata.measure_count,
                time_signatures=metadata.time_signatures, key_signatures=metadata.key_signatures,
                created_at=now, updated_at=now, archived=False)
            try: return piece_response(PieceRepository(session).add(piece))
            except Exception:
                session.rollback(); storage.delete(stored_path); raise
        except MusicXMLValidationError as error:
            if stored_path: storage.delete(stored_path)
            raise HTTPException(status_code=422, detail=str(error)) from error
        finally: await file.close()

    @app.get("/pieces", tags=["pieces"])
    def list_pieces(session: Session = Depends(get_session)):
        return [piece_response(piece) for piece in PieceRepository(session).list_active()]

    def require_piece(piece_id: str, session: Session) -> PieceEntity:
        piece = PieceRepository(session).get_active(piece_id)
        if not piece: raise HTTPException(status_code=404, detail="Piece not found.")
        return piece

    @app.get("/pieces/{piece_id}", tags=["pieces"])
    def get_piece(piece_id: str, session: Session = Depends(get_session)):
        return piece_response(require_piece(piece_id, session))

    @app.get("/pieces/{piece_id}/musicxml", response_class=PlainTextResponse, tags=["pieces"])
    def get_piece_musicxml(piece_id: str, session: Session = Depends(get_session)):
        piece = require_piece(piece_id, session)
        try: return storage.read(piece.musicxml_path).decode("utf-8")
        except (FileNotFoundError, UnicodeDecodeError) as error:
            raise HTTPException(status_code=500, detail="Stored MusicXML is unavailable.") from error

    @app.delete("/pieces/{piece_id}", status_code=204, tags=["pieces"])
    def delete_piece(piece_id: str, session: Session = Depends(get_session)):
        piece = require_piece(piece_id, session)
        path = piece.musicxml_path
        PieceRepository(session).delete(piece)
        storage.delete(path)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
