import os
from pathlib import Path
from uuid import uuid4


class PieceStorage:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, piece_id: str, suffix: str, content: bytes) -> str:
        destination = self.root / f"{piece_id}{suffix.lower()}"
        temporary = self.root / f".{piece_id}-{uuid4().hex}.tmp"
        try:
            temporary.write_bytes(content)
            os.replace(temporary, destination)
            return str(destination.resolve())
        finally:
            temporary.unlink(missing_ok=True)

    def read(self, path: str) -> bytes:
        return Path(path).read_bytes()

    def delete(self, path: str) -> None:
        Path(path).unlink(missing_ok=True)
