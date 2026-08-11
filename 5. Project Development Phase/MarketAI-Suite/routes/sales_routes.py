"""
MarketAI Suite — Sales Pitch Routes
=====================================
POST /api/sales-pitches/generate
GET  /api/sales-pitches
GET  /api/sales-pitches/<id>
DELETE /api/sales-pitches/<id>
"""

from __future__ import annotations

from flask import Blueprint, request, jsonify

from services.sales_pitch_service import sales_pitch_service
from services.groq_service import GroqServiceError
from models.schemas import HistoryRepository
from utils.validators import validate_sales_pitch_input, sanitise_string
from utils.helpers import build_success_response, build_error_response
from utils.logger import get_logger

log = get_logger("sales_routes")
bp = Blueprint("sales_pitches", __name__, url_prefix="/api/sales-pitches")


@bp.route("/generate", methods=["POST"])
def generate_pitch():
    data = request.get_json(silent=True) or {}
    sanitised = {k: sanitise_string(str(v)) if isinstance(v, str) else v for k, v in data.items()}

    ok, err = validate_sales_pitch_input(sanitised)
    if not ok:
        return jsonify(build_error_response("VALIDATION_ERROR", err)), 400

    try:
        result = sales_pitch_service.generate(sanitised)
        return jsonify(build_success_response(result, "Sales pitch generated successfully")), 201
    except GroqServiceError as exc:
        return jsonify(build_error_response(exc.code, exc.message)), 503
    except Exception as exc:
        log.error("Unexpected error: %s", exc, exc_info=True)
        return jsonify(build_error_response("INTERNAL_ERROR", "Failed to generate sales pitch.")), 500


@bp.route("", methods=["GET"])
def list_pitches():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    result = HistoryRepository.list_all(generation_type="sales_pitch", page=page, per_page=per_page)
    return jsonify(build_success_response(result)), 200


@bp.route("/<record_id>", methods=["GET"])
def get_pitch(record_id: str):
    """Load previously generated pitch — NO new Groq call."""
    record = HistoryRepository.get_by_id(record_id)
    if not record or record.get("generation_type") != "sales_pitch":
        return jsonify(build_error_response("NOT_FOUND", "Sales pitch not found.")), 404
    return jsonify(build_success_response({
        "history_id": record["id"],
        "pitch": record.get("ai_output", {}),
        "user_inputs": record.get("user_inputs", {}),
        "created_at": record.get("created_at"),
        "loaded_from_history": True,
    }, "Sales pitch loaded from history")), 200


@bp.route("/<record_id>", methods=["DELETE"])
def delete_pitch(record_id: str):
    deleted = HistoryRepository.delete(record_id)
    if not deleted:
        return jsonify(build_error_response("NOT_FOUND", "Sales pitch not found.")), 404
    return jsonify(build_success_response(None, "Sales pitch deleted")), 200
