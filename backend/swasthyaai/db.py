import sqlite3
from pathlib import Path


def init_db(path: str | Path) -> None:
    database = Path(path)
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database):
        pass
