from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str
    musicxml_storage_dir: Path
    recording_storage_dir: Path = Path("./data/recordings")
    max_recording_bytes: int = 100 * 1024 * 1024

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            database_url=os.getenv("CELLO_DATABASE_URL", "sqlite:///./data/cello-practice.db"),
            musicxml_storage_dir=Path(os.getenv("CELLO_MUSICXML_STORAGE_DIR", "./data/musicxml")),
            recording_storage_dir=Path(os.getenv("CELLO_RECORDING_STORAGE_DIR", "./data/recordings")),
            max_recording_bytes=int(os.getenv("CELLO_MAX_RECORDING_BYTES", str(100 * 1024 * 1024))),
        )
