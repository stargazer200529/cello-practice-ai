from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str
    musicxml_storage_dir: Path

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            database_url=os.getenv("CELLO_DATABASE_URL", "sqlite:///./data/cello-practice.db"),
            musicxml_storage_dir=Path(os.getenv("CELLO_MUSICXML_STORAGE_DIR", "./data/musicxml")),
        )
