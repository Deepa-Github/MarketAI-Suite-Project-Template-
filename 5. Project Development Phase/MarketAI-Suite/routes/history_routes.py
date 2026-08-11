"""
MarketAI Suite — History Routes
GET  /api/history
GET  /api/history/<id>
DELETE /api/history/<id>
"""

from flask import Blueprint, request, jsonify
from models.schemas import HistoryRepository
from utils.helpers import build_success_response, build_error_response
from utils.logger import get_logger

log = get_logger("history_routes")
bp = Blueprint("history", __name__, url_prefix="/api/history")


@bp.route("", methods=["GET"])
def list_history():
    """List history with optional filtering and search."""
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)
    generation_type = request.args.get("type")  # campaign, sales_pitch, lead_scoring, etc.
    search = request.args.get("search")

    result = HistoryRepository.list_all(
        generation_type=generation_type,
        search=search,
        page=page,
        per_page=per_page,
    )
    return jsonify(build_success_response(result)), 200


@bp.route("/<record_id>", methods=["GET"])
def get_history_item(record_id: str):
    """
    Load a history record by ID.
    IMPORTANT: This endpoint NEVER calls Groq.
    It retrieves the stored AI output from SQLite.
    """
    record = HistoryRepository.get_by_id(record_id)
    if not record:
        return jsonify(build_error_response("NOT_FOUND", "History record not found.")), 404

    return jsonify(build_success_response({
        **record,
        "loaded_from_history": True,
    }, "Loaded from history (no AI call made)")), 200


@bp.route("/<record_id>", methods=["DELETE"])
def delete_history_item(record_id: str):
    """Delete a history record."""
    deleted = HistoryRepository.delete(record_id)
    if not deleted:
        return jsonify(build_error_response("NOT_FOUND", "History record not found.")), 404
    return jsonify(build_success_response(None, "History record deleted")), 200


@bp.route("/recent", methods=["GET"])
def recent_history():
    """Return the most recent history items for dashboard display."""
    limit = min(int(request.args.get("limit", 10)), 50)
    items = HistoryRepository.recent(limit=limit)
    return jsonify(build_success_response(items)), 200
