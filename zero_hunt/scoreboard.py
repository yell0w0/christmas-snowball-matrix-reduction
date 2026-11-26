"""Global high-score table for Zero Hunt.

Backed by SQLite so it works with zero setup. Set ZERO_HUNT_DB to a path on
persistent, shared storage when hosting (e.g. a mounted volume); every app
instance must see the same file. To use a warehouse instead, re-implement
`submit` and `top` with the same signatures.
"""

from __future__ import annotations

import os
import re
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB = Path(__file__).parent / "data" / "scores.sqlite3"
MAX_NAME = 16
MAX_SCORE = 60_000  # comfortably above the best possible run
N_BAUBLES = 30

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scores (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id     TEXT UNIQUE NOT NULL,
    name       TEXT NOT NULL,
    score      INTEGER NOT NULL,
    caught     INTEGER NOT NULL,
    perfect    INTEGER NOT NULL,
    falls      INTEGER NOT NULL,
    seconds    REAL NOT NULL,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS scores_by_score ON scores (score DESC, created_at ASC);
"""


def db_path() -> Path:
    return Path(os.environ.get("ZERO_HUNT_DB", DEFAULT_DB))


@contextmanager
def _connect():
    """Open, yield, commit and always close (Streamlit servers are long-lived)."""
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        conn.executescript(_SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def clean_name(raw: object) -> str:
    """Printable, single-spaced, upper-case, at most MAX_NAME characters."""
    s = re.sub(r"\s+", " ", str(raw or ""))
    s = re.sub(r"[^\w .\-'&!]", "", s, flags=re.UNICODE)
    s = re.sub(r" +", " ", s).strip().upper()[:MAX_NAME].strip()
    return s or "ANON"


def _clamp_int(v: object, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return lo


def submit(entry: dict) -> int | None:
    """Store a finished run; returns its global rank (1 = best). Idempotent per run_id."""
    run_id = str(entry.get("run_id") or "")[:64]
    if not re.fullmatch(r"[A-Za-z0-9_\-]{6,64}", run_id):
        return None
    row = (
        run_id,
        clean_name(entry.get("name")),
        _clamp_int(entry.get("score"), 0, MAX_SCORE),
        _clamp_int(entry.get("caught"), 0, N_BAUBLES),
        _clamp_int(entry.get("perfect"), 0, N_BAUBLES),
        _clamp_int(entry.get("falls"), 0, 999),
        float(min(max(float(entry.get("seconds") or 0), 0), 3600)),
        time.time(),
    )
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO scores (run_id, name, score, caught, perfect, falls, seconds, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            row,
        )
    return rank_of(run_id)


def rank_of(run_id: str) -> int | None:
    with _connect() as conn:
        r = conn.execute("SELECT score, created_at FROM scores WHERE run_id = ?", (run_id,)).fetchone()
        if r is None:
            return None
        better = conn.execute(
            "SELECT COUNT(*) FROM scores WHERE score > ? OR (score = ? AND created_at < ?)",
            (r["score"], r["score"], r["created_at"]),
        ).fetchone()[0]
    return better + 1


def top(n: int = 10) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT run_id, name, score, caught, perfect, falls, seconds FROM scores"
            " ORDER BY score DESC, created_at ASC LIMIT ?",
            (n,),
        ).fetchall()
    return [dict(r) for r in rows]


def count() -> int:
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
