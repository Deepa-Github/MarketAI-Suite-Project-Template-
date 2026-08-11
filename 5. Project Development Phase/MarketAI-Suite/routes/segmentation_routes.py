"""
MarketAI Suite — Segmentation Routes
POST /api/segments/generate
GET  /api/segments
GET  /api/segments/<id>
DELETE /api/segments/<id>
"""

from flask import Blueprint, request, jsonify
from services.segmentation_service import segmentation_service
from services.groq_service import GroqServiceError
from models.schemas import HistoryRepository
from utils.validators import validate_segmentation_input, sanitise_string
from utils.helpers import build_success_response, build_error_response
from utils.logger import get_logger

log = get_logger("segmentation_routes")
bp = Blueprint("segments", __name__, url_prefix="/api/segments")


@bp.route("/generate", methods=["POST"])
def generate_segmentation():
    data = request.get_json(silent=True) or {}
    sanitised = {k: sanitise_string(str(v)) if isinstance(v, str) else v for k, v in data.items()}
    ok, err = validate_segmentation_input(sanitised)
    if not ok:
        return jsonify(build_error_response("VALIDATION_ERROR", err)), 400
    try:
        result = segmentation_service.generate(sanitised)
        return jsonify(build_success_response(result, "Segmentation generated successfully")), 201
    except GroqServiceError as exc:
        return jsonify(build_error_response(exc.code, exc.message)), 503
    except Exception as exc:
        log.error("Error: %s", exc, exc_info=True)
        return jsonify(build_error_response("INTERNAL_ERROR", "Failed to generate segmentation.")), 500


@bp.route("", methods=["GET"])
def list_segments():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    result = HistoryRepository.list_all(generation_type="segmentation", page=page, per_page=per_page)
    return jsonify(build_success_response(result)), 200


@bp.route("/<record_id>", methods=["GET"])
def get_segment(record_id: str):
    record = HistoryRepository.get_by_id(record_id)
    if not record or record.get("generation_type") != "segmentation":
        return jsonify(build_error_response("NOT_FOUND", "Segmentation not found.")), 404
    return jsonify(build_success_response({
        "history_id": record["id"],
        "segmentation": record.get("ai_output", {}),
        "user_inputs": record.get("user_inputs", {}),
        "created_at": record.get("created_at"),
        "loaded_from_history": True,
    })), 200


@bp.route("/<record_id>", methods=["DELETE"])
def delete_segment(record_id: str):
    deleted = HistoryRepository.delete(record_id)
    if not deleted:
        return jsonify(build_error_response("NOT_FOUND", "Not found.")), 404
    return jsonify(build_success_response(None, "Deleted")), 200
