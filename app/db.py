import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = os.environ.get("KANBAN_DB_PATH", "kanban.db")
_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def _get_connection(db_path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def get_db(db_path: str | None = None):
    conn = _get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows: list) -> list[dict]:
    return [dict(r) for r in rows]


def utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_migrations(db_path: str | None = None):
    with get_db(db_path) as conn:
        # Ensure migrations tracking table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT    NOT NULL UNIQUE,
                applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
            )
        """)
        for sql_file in sorted(_MIGRATIONS_DIR.glob("*.sql")):
            name = sql_file.name
            already = conn.execute(
                "SELECT 1 FROM _migrations WHERE name = ?", (name,)
            ).fetchone()
            if already:
                continue
            conn.executescript(sql_file.read_text())
            # Re-open connection state after executescript
            conn.execute("INSERT OR IGNORE INTO _migrations (name) VALUES (?)", (name,))
