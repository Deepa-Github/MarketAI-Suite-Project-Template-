"""
MarketAI Suite — Data Access / Repository Layer
================================================
All database read/write operations are centralised here.
Routes and services should call these functions — never write raw SQL in routes.
"""

from __future__ import annotations

import json
from typing import Any

from models.database import get_db, rows_to_list, row_to_dict, json_dumps, json_loads_safe
from utils.helpers import generate_id, utcnow_iso
from utils.logger import get_logger

log = get_logger("schemas")


# ══════════════════════════════════════════════════════════════
# HISTORY REPOSITORY
# ══════════════════════════════════════════════════════════════

class HistoryRepository:
    """CRUD operations for the history table."""

    @staticmethod
    def create(
        generation_type: str,
        title: str,
        user_inputs: dict,
        ai_output: Any,
        metadata: dict | None = None,
        status: str = "completed",
    ) -> dict:
        """Insert a new history record and return it."""
        record_id = generate_id()
        now = utcnow_iso()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO history
                   (id, generation_type, title, status, user_inputs, ai_output, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id,
                    generation_type,
                    title,
                    status,
                    json_dumps(user_inputs),
                    json_dumps(ai_output) if not isinstance(ai_output, str) else ai_output,
                    json_dumps(metadata or {}),
                    now,
                    now,
                ),
            )
        log.info("History record created: id=%s type=%s", record_id, generation_type)
        return HistoryRepository.get_by_id(record_id)

    @staticmethod
    def get_by_id(record_id: str) -> dict | None:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM history WHERE id = ?", (record_id,)).fetchone()
        if not row:
            return None
        return _deserialise_history(row_to_dict(row))

    @staticmethod
    def list_all(
        generation_type: str | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Return paginated history records, optionally filtered."""
        conditions: list[str] = []
        params: list[Any] = []

        if generation_type:
            conditions.append("generation_type = ?")
            params.append(generation_type)

        if search:
            conditions.append("(title LIKE ? OR user_inputs LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with get_db() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM history {where_clause}", params
            ).fetchone()[0]
            offset = (page - 1) * per_page
            rows = conn.execute(
                f"SELECT * FROM history {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                params + [per_page, offset],
            ).fetchall()

        items = [_deserialise_history(row_to_dict(r)) for r in rows]
        return {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": max(1, -(-total // per_page)),
            },
        }

    @staticmethod
    def delete(record_id: str) -> bool:
        with get_db() as conn:
            cursor = conn.execute("DELETE FROM history WHERE id = ?", (record_id,))
        return cursor.rowcount > 0

    @staticmethod
    def count_by_type(generation_type: str) -> int:
        with get_db() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM history WHERE generation_type = ?", (generation_type,)
            ).fetchone()[0]

    @staticmethod
    def recent(limit: int = 10) -> list[dict]:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [_deserialise_history(row_to_dict(r)) for r in rows]


def _deserialise_history(row: dict) -> dict:
    row["user_inputs"] = json_loads_safe(row.get("user_inputs"), {})
    row["ai_output"] = json_loads_safe(row.get("ai_output"), row.get("ai_output"))
    row["metadata"] = json_loads_safe(row.get("metadata"), {})
    return row


# ══════════════════════════════════════════════════════════════
# CAMPAIGN REPOSITORY
# ══════════════════════════════════════════════════════════════

class CampaignRepository:

    @staticmethod
    def create(history_id: str, inputs: dict, ai_output: dict) -> dict:
        record_id = generate_id()
        now = utcnow_iso()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO campaigns
                   (id, history_id, campaign_name, product_name, target_audience, objective, channels, ai_output, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id,
                    history_id,
                    ai_output.get("campaign_name", ""),
                    inputs.get("product_name", ""),
                    inputs.get("target_audience", ""),
                    inputs.get("campaign_objective", ""),
                    json_dumps(inputs.get("channels", [])),
                    json_dumps(ai_output),
                    now,
                ),
            )
        return {"id": record_id, "history_id": history_id}

    @staticmethod
    def list_all() -> list[dict]:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM campaigns ORDER BY created_at DESC").fetchall()
        return rows_to_list(rows)


# ══════════════════════════════════════════════════════════════
# SALES PITCH REPOSITORY
# ══════════════════════════════════════════════════════════════

class SalesPitchRepository:

    @staticmethod
    def create(history_id: str, inputs: dict, ai_output: dict) -> dict:
        record_id = generate_id()
        now = utcnow_iso()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO sales_pitches
                   (id, history_id, product_name, customer_name, customer_industry, ai_output, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id,
                    history_id,
                    inputs.get("product_name", ""),
                    inputs.get("customer_name", ""),
                    inputs.get("customer_industry", ""),
                    json_dumps(ai_output),
                    now,
                ),
            )
        return {"id": record_id, "history_id": history_id}


# ══════════════════════════════════════════════════════════════
# LEAD UPLOAD REPOSITORY
# ══════════════════════════════════════════════════════════════

class LeadUploadRepository:

    @staticmethod
    def create(history_id: str, filename: str, summary: dict, scored_leads: list) -> dict:
        record_id = generate_id()
        now = utcnow_iso()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO lead_uploads
                   (id, history_id, filename, total_leads, high_priority, medium_priority,
                    low_priority, avg_score, ai_output, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id,
                    history_id,
                    filename,
                    summary.get("total_leads", 0),
                    summary.get("high_priority", 0),
                    summary.get("medium_priority", 0),
                    summary.get("low_priority", 0),
                    summary.get("avg_score", 0.0),
                    json_dumps(scored_leads),
                    now,
                ),
            )
        return {"id": record_id, "history_id": history_id}

    @staticmethod
    def get_aggregate_stats() -> dict:
        with get_db() as conn:
            row = conn.execute(
                """SELECT
                       COALESCE(SUM(total_leads), 0)     AS total_leads,
                       COALESCE(SUM(high_priority), 0)   AS high_priority,
                       COALESCE(SUM(medium_priority), 0) AS medium_priority,
                       COALESCE(SUM(low_priority), 0)    AS low_priority,
                       COALESCE(AVG(avg_score), 0)       AS avg_score
                   FROM lead_uploads"""
            ).fetchone()
        return dict(row) if row else {}


# ══════════════════════════════════════════════════════════════
# SEGMENT REPOSITORY
# ══════════════════════════════════════════════════════════════

class SegmentRepository:

    @staticmethod
    def create(history_id: str, inputs: dict, ai_output: dict) -> dict:
        record_id = generate_id()
        now = utcnow_iso()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO segments
                   (id, history_id, business_name, target_market, ai_output, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    record_id, history_id,
                    inputs.get("business_name", ""),
                    inputs.get("target_market", ""),
                    json_dumps(ai_output), now,
                ),
            )
        return {"id": record_id}

    @staticmethod
    def count() -> int:
        with get_db() as conn:
            return conn.execute("SELECT COUNT(*) FROM segments").fetchone()[0]


# ══════════════════════════════════════════════════════════════
# STRATEGY REPOSITORY
# ══════════════════════════════════════════════════════════════

class StrategyRepository:

    @staticmethod
    def create(history_id: str, inputs: dict, ai_output: dict) -> dict:
        record_id = generate_id()
        now = utcnow_iso()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO strategies
                   (id, history_id, business_name, industry, objective, ai_output, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id, history_id,
                    inputs.get("business_name", ""),
                    inputs.get("industry", ""),
                    inputs.get("marketing_objective", ""),
                    json_dumps(ai_output), now,
                ),
            )
        return {"id": record_id}


# ══════════════════════════════════════════════════════════════
# RECOMMENDATION REPOSITORY
# ══════════════════════════════════════════════════════════════

class RecommendationRepository:

    @staticmethod
    def create(history_id: str, context_summary: str, ai_output: dict) -> dict:
        record_id = generate_id()
        now = utcnow_iso()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO recommendations
                   (id, history_id, context_summary, ai_output, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (record_id, history_id, context_summary, json_dumps(ai_output), now),
            )
        return {"id": record_id}
