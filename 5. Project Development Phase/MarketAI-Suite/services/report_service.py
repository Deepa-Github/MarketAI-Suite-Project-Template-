"""
MarketAI Suite — Report Service
=================================
CSV and optional export generation.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime


class ReportService:

    def generate_leads_csv(self, scored_leads: list[dict]) -> str:
        """Return a CSV string of scored leads."""
        if not scored_leads:
            return ""

        # Define ordered columns for the export
        priority_columns = [
            "name", "email", "company", "industry", "job_title",
            "lead_score", "priority", "ai_conversion_estimate", "lead_quality",
            "score_reasoning", "recommended_action", "recommended_channel",
            "follow_up_timing", "positive_signals", "negative_signals",
        ]

        # Union with any extra columns from the leads
        all_keys = list(scored_leads[0].keys()) if scored_leads else []
        extra_cols = [k for k in all_keys if k not in priority_columns]
        fieldnames = priority_columns + extra_cols

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()

        for lead in scored_leads:
            row = dict(lead)
            # Convert lists to readable strings
            for key in ("positive_signals", "negative_signals", "data_gaps"):
                val = row.get(key)
                if isinstance(val, list):
                    row[key] = "; ".join(str(v) for v in val)
            writer.writerow(row)

        return output.getvalue()

    def generate_history_summary_csv(self, history_items: list[dict]) -> str:
        """Return a CSV of history records."""
        if not history_items:
            return ""

        fieldnames = ["id", "generation_type", "title", "status", "created_at"]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(history_items)
        return output.getvalue()


report_service = ReportService()
