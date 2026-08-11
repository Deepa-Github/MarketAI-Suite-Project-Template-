"""
MarketAI Suite — Campaign Routes
==================================
POST /api/campaigns/generate
GET  /api/campaigns
GET  /api/campaigns/<id>
DELETE /api/campaigns/<id>
"""

from __future__ import annotations

from flask import Blueprint, request, jsonify

from services.campaign_service import campaign_service
from services.groq_service import GroqServiceError
from models.schemas import HistoryRepository
from utils.validators import validate_campaign_input, sanitise_string
from utils.helpers import build_success_response, build_error_response
from utils.logger import get_logger

log = get_logger("campaign_routes")
bp = Blueprint("campaigns", __name__, url_prefix="/api/campaigns")


@bp.route("/generate", methods=["POST"])
def generate_campaign():
    """Generate a new AI marketing campaign."""
    data = request.get_json(silent=True) or {}

    # Sanitise inputs
    sanitised = {k: sanitise_string(str(v)) if isinstance(v, str) else v for k, v in data.items()}

    ok, err = validate_campaign_input(sanitised)
    if not ok:
        return jsonify(build_error_response("VALIDATION_ERROR", err)), 400

    try:
        result = campaign_service.generate(sanitised)
        return jsonify(build_success_response(result, "Campaign generated successfully")), 201
    except GroqServiceError as exc:
        log.error("Groq error generating campaign: %s", exc.message)
        return jsonify(build_error_response(exc.code, exc.message)), 503
    except Exception as exc:
        log.error("Unexpected error: %s", exc, exc_info=True)
        return jsonify(build_error_response("INTERNAL_ERROR", "Failed to generate campaign.")), 500


@bp.route("", methods=["GET"])
def list_campaigns():
    """List all saved campaigns (from history)."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    result = HistoryRepository.list_all(generation_type="campaign", page=page, per_page=per_page)
    return jsonify(build_success_response(result)), 200


@bp.route("/<record_id>", methods=["GET"])
def get_campaign(record_id: str):
    """
    Retrieve a previously generated campaign from history.
    NO Groq API call is made — data is loaded from database.
    """
    record = HistoryRepository.get_by_id(record_id)
    if not record or record.get("generation_type") != "campaign":
        return jsonify(build_error_response("NOT_FOUND", "Campaign not found.")), 404

    return jsonify(build_success_response({
        "history_id": record["id"],
        "campaign": record.get("ai_output", {}),
        "user_inputs": record.get("user_inputs", {}),
        "created_at": record.get("created_at"),
        "loaded_from_history": True,  # ← clearly flagged
    }, "Campaign loaded from history")), 200


@bp.route("/<record_id>", methods=["DELETE"])
def delete_campaign(record_id: str):
    """Delete a campaign from history."""
    deleted = HistoryRepository.delete(record_id)
    if not deleted:
        return jsonify(build_error_response("NOT_FOUND", "Campaign not found.")), 404
    return jsonify(build_success_response(None, "Campaign deleted")), 200
