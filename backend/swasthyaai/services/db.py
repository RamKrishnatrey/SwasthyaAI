import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator

from backend.swasthyaai.config import get_settings
from backend.swasthyaai.db import init_db


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = get_settings().database_path
    init_db(path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()
