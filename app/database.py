import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).parent / "todos.db")


def init_db(path: str = DB_PATH) -> None:
    """Create the todos table if it does not already exist."""
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_db(path: str = DB_PATH) -> sqlite3.Connection:
    """Open and return a SQLite connection with row_factory set."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn
