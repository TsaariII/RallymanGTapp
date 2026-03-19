from __future__ import annotations

import sqlite3
from pathlib import Path

# Tracks live as SQL scripts under ./tracks at the repo root.
# We generate ./tracks.db on first launch (or rebuild it if it's missing/corrupt).

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "tracks.db"
TRACKS_SQL_DIR = PROJECT_ROOT / "tracks"

REQUIRED_TABLES = {"tracks", "tiles", "squares"}


def _has_required_tables(conn: sqlite3.Connection) -> bool:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    existing = {r[0] for r in rows}
    return REQUIRED_TABLES.issubset(existing)


def init_tracks_db(db_path: Path = DB_PATH, sql_dir: Path = TRACKS_SQL_DIR) -> None:
    """Ensure the tracks SQLite database exists and is usable.

    Strategy:
      - If db exists and has required tables -> do nothing.
      - Otherwise, build a fresh db from *.sql scripts under ./tracks.

    This keeps the app runnable out-of-the-box without shipping a binary .db.
    """

    sql_dir = sql_dir.resolve()
    db_path = db_path.resolve()

    if not sql_dir.exists():
        raise FileNotFoundError(f"Tracks SQL directory not found: {sql_dir}")

    # Fast path: existing db looks usable.
    if db_path.exists():
        try:
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("PRAGMA foreign_keys = ON;")
                if _has_required_tables(conn):
                    return
        except sqlite3.Error:
            # Corrupt/unreadable, we'll rebuild below.
            pass

    scripts = sorted(sql_dir.glob("*.sql"))
    if not scripts:
        raise FileNotFoundError(f"No .sql files found under: {sql_dir}")

    tmp_path = db_path.with_suffix(db_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    try:
        with sqlite3.connect(str(tmp_path)) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            for script in scripts:
                sql = script.read_text(encoding="utf-8")
                conn.executescript(sql)
            conn.commit()
    except sqlite3.Error as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise RuntimeError(f"Failed to initialize database from {sql_dir}: {e}")

    tmp_path.replace(db_path)