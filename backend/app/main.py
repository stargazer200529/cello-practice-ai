from dataclasses import asdict

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.musicxml import (
    MusicXMLValidationError,
    parse_musicxml,
    validate_filename,
)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024

app = FastAPI(title="Cello Practice AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Report whether the local API process is ready to receive requests."""
    return {"status": "ok"}


@app.post("/scores/metadata", tags=["scores"])
async def score_metadata(file: UploadFile = File(...)) -> dict[str, object]:
    """Parse basic metadata without retaining the uploaded MusicXML file."""
    try:
        validate_filename(file.filename)
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise MusicXMLValidationError("The MusicXML file must be 5 MB or smaller.")
        if not content:
            raise MusicXMLValidationError("The uploaded MusicXML file is empty.")
        return asdict(parse_musicxml(content))
    except MusicXMLValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    finally:
        await file.close()
