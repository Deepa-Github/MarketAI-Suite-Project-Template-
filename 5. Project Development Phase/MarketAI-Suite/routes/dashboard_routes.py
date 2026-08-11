"""
MarketAI Suite — Dashboard Routes
GET /api/dashboard/summary
"""

from flask import Blueprint, jsonify
from models.schemas import HistoryRepository, LeadUploadRepository, SegmentRepository
from utils.helpers import build_success_response
from utils.logger import get_logger

log = get_logger("dashboard_routes")
bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.route("/summary", methods=["GET"])
def dashboard_summary():
    """Aggregate summary for the dashboard — reads from DB, no AI calls."""
    try:
        campaigns_count = HistoryRepository.count_by_type("campaign")
        pitches_count = HistoryRepository.count_by_type("sales_pitch")
        segmentation_count = HistoryRepository.count_by_type("segmentation")
        strategy_count = HistoryRepository.count_by_type("strategy")
        recommendation_count = HistoryRepository.count_by_type("recommendation")

        lead_stats = LeadUploadRepository.get_aggregate_stats()
        segment_count = SegmentRepository.count()
        recent_activity = HistoryRepository.recent(limit=8)

        summary = {
            "metrics": {
                "total_campaigns": campaigns_count,
                "total_sales_pitches": pitches_count,
                "total_segmentations": segmentation_count,
                "total_strategies": strategy_count,
                "total_recommendations": recommendation_count,
                "total_leads": lead_stats.get("total_leads", 0),
                "high_priority_leads": lead_stats.get("high_priority", 0),
                "medium_priority_leads": lead_stats.get("medium_priority", 0),
                "low_priority_leads": lead_stats.get("low_priority", 0),
                "avg_lead_score": round(lead_stats.get("avg_score", 0), 1),
                "total_segments": segment_count,
            },
            "recent_activity": recent_activity,
        }

        return jsonify(build_success_response(summary)), 200

    except Exception as exc:
        log.error("Dashboard summary error: %s", exc, exc_info=True)
        return jsonify(build_success_response({
            "metrics": {},
            "recent_activity": [],
        }, "Partial dashboard data")), 200
