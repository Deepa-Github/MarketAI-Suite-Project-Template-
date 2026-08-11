"""
MarketAI Suite — SQLite Database Layer
=======================================
Handles database initialisation, connection management and schema creation.
All SQL uses parameterised queries to prevent injection.
"""

from __future__ import annotations

import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from config import config
from utils.logger import get_logger

log = get_logger("database")

# ──────────────────────────────────────────────────────────────
# DDL — table creation statements
# ──────────────────────────────────────────────────────────────

_DDL_STATEMENTS = [
    # ── Sessions / History ────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS history (
        id              TEXT PRIMARY KEY,
        generation_type TEXT NOT NULL,
        title           TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'completed',
        user_inputs     TEXT,          -- JSON
        ai_output       TEXT,          -- JSON or free text
        metadata        TEXT,          -- JSON
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_history_type     ON history (generation_type)",
    "CREATE INDEX IF NOT EXISTS idx_history_created  ON history (created_at)",

    # ── Campaigns ─────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS campaigns (
        id              TEXT PRIMARY KEY,
        history_id      TEXT NOT NULL,
        campaign_name   TEXT,
        product_name    TEXT,
        target_audience TEXT,
        objective       TEXT,
        channels        TEXT,          -- JSON array
        ai_output       TEXT,          -- JSON
        created_at      TEXT NOT NULL,
        FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_campaigns_history ON campaigns (history_id)",

    # ── Sales Pitches ─────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS sales_pitches (
        id              TEXT PRIMARY KEY,
        history_id      TEXT NOT NULL,
        product_name    TEXT,
        customer_name   TEXT,
        customer_industry TEXT,
        ai_output       TEXT,          -- JSON
        created_at      TEXT NOT NULL,
        FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_pitches_history ON sales_pitches (history_id)",

    # ── Lead Uploads ──────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS lead_uploads (
        id              TEXT PRIMARY KEY,
        history_id      TEXT NOT NULL,
        filename        TEXT,
        total_leads     INTEGER DEFAULT 0,
        high_priority   INTEGER DEFAULT 0,
        medium_priority INTEGER DEFAULT 0,
        low_priority    INTEGER DEFAULT 0,
        avg_score       REAL DEFAULT 0,
        ai_output       TEXT,          -- JSON array of scored leads
        created_at      TEXT NOT NULL,
        FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_leads_history ON lead_uploads (history_id)",

    # ── Segments ──────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS segments (
        id              TEXT PRIMARY KEY,
        history_id      TEXT NOT NULL,
        business_name   TEXT,
        target_market   TEXT,
        ai_output       TEXT,          -- JSON
        created_at      TEXT NOT NULL,
        FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_segments_history ON segments (history_id)",

    # ── Strategies ────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS strategies (
        id              TEXT PRIMARY KEY,
        history_id      TEXT NOT NULL,
        business_name   TEXT,
        industry        TEXT,
        objective       TEXT,
        ai_output       TEXT,          -- JSON
        created_at      TEXT NOT NULL,
        FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_strategies_history ON strategies (history_id)",

    # ── Recommendations ───────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS recommendations (
        id              TEXT PRIMARY KEY,
        history_id      TEXT NOT NULL,
        context_summary TEXT,
        ai_output       TEXT,          -- JSON
        created_at      TEXT NOT NULL,
        FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_recommendations_history ON recommendations (history_id)",
]


# ──────────────────────────────────────────────────────────────
# Connection management
# ──────────────────────────────────────────────────────────────

def _get_db_path() -> Path:
    return config.get_database_path()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context-manager that yields an open SQLite connection.
    Commits on success, rolls back on error, always closes.
    """
    db_path = _get_db_path()
    conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row  # rows accessible by column name
    conn.execute("PRAGMA journal_mode=WAL")   # better concurrent read performance
    conn.execute("PRAGMA foreign_keys=ON")    # enforce FK constraints
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────
# Initialisation
# ──────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create all tables and indexes if they do not already exist.
    Safe to call on every application start.
    """
    log.info("Initialising database at: %s", _get_db_path())
    with get_db() as conn:
        for stmt in _DDL_STATEMENTS:
            conn.execute(stmt)
    log.info("Database initialised successfully.")


def check_db_health() -> dict:
    """Return basic database health info."""
    try:
        with get_db() as conn:
            version = conn.execute("SELECT sqlite_version()").fetchone()[0]
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            return {
                "status": "healthy",
                "sqlite_version": version,
                "tables": [t[0] for t in tables],
            }
    except Exception as exc:
        log.error("Database health check failed: %s", exc)
        return {"status": "unhealthy", "error": str(exc)}


# ──────────────────────────────────────────────────────────────
# Generic CRUD helpers
# ──────────────────────────────────────────────────────────────

def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict."""
    return dict(row)


def rows_to_list(rows: list[sqlite3.Row]) -> list[dict]:
    return [row_to_dict(r) for r in rows]


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def json_loads_safe(text: str | None, fallback: Any = None) -> Any:
    if not text:
        return fallback
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return fallback
