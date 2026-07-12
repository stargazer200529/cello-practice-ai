import os
from pathlib import Path
from uuid import uuid4


MIME_SUFFIXES = {
    "audio/mp4": ".m4a",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/webm": ".webm",
    "audio/x-wav": ".wav",
}


class RecordingStorage:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def write(
        self,
        user_id: str,
        practice_session_id: str,
        recording_id: str,
        mime_type: str,
        content: bytes,
    ) -> str:
        destination_dir = self.root / user_id / practice_session_id
        destination_dir.mkdir(parents=True, exist_ok=True)
        suffix = MIME_SUFFIXES.get(mime_type.partition(";")[0].strip().lower(), ".audio")
        destination = destination_dir / f"{recording_id}{suffix}"
        temporary = destination_dir / f".{recording_id}-{uuid4().hex}.tmp"
        try:
            temporary.write_bytes(content)
            os.replace(temporary, destination)
            return str(destination.resolve())
        finally:
            temporary.unlink(missing_ok=True)

    def path(self, storage_key: str) -> Path:
        path = Path(storage_key).resolve()
        if path != self.root and self.root not in path.parents:
            raise FileNotFoundError("Recording is outside the configured storage directory.")
        return path

    def delete(self, storage_key: str) -> None:
        self.path(storage_key).unlink(missing_ok=True)
