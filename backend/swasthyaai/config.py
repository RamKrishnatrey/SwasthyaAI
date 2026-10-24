import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path

    @property
    def database_path(self) -> Path:
        return self.data_dir / "swasthya.sqlite3"


def get_settings() -> Settings:
    return Settings(data_dir=Path(os.getenv("SWASTHYAAI_DATA_DIR", ".local")).expanduser())
