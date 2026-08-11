"""
MarketAI Suite — Strategy Routes
POST /api/strategies/generate
GET  /api/strategies
GET  /api/strategies/<id>
DELETE /api/strategies/<id>

POST /api/recommendations/generate
GET  /api/recommendations
GET  /api/recommendations/<id>
"""

from flask import Blueprint, request, jsonify
from services.strategy_service import strategy_service
from services.recommendation_service import recommendation_service
from services.groq_service import GroqServiceError
from models.schemas import HistoryRepository
from utils.validators import validate_strategy_input, sanitise_string
from utils.helpers import build_success_response, build_error_response
from utils.logger import get_logger

log = get_logger("strategy_routes")

strategy_bp = Blueprint("strategies", __name__, url_prefix="/api/strategies")
recommendation_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")


# ── Strategy endpoints ─────────────────────────────────────────

@strategy_bp.route("/generate", methods=["POST"])
def generate_strategy():
    data = request.get_json(silent=True) or {}
    sanitised = {k: sanitise_string(str(v)) if isinstance(v, str) else v for k, v in data.items()}
    ok, err = validate_strategy_input(sanitised)
    if not ok:
        return jsonify(build_error_response("VALIDATION_ERROR", err)), 400
    try:
        result = strategy_service.generate(sanitised)
        return jsonify(build_success_response(result, "Strategy generated successfully")), 201
    except GroqServiceError as exc:
        return jsonify(build_error_response(exc.code, exc.message)), 503
    except Exception as exc:
        log.error("Error: %s", exc, exc_info=True)
        return jsonify(build_error_response("INTERNAL_ERROR", "Failed to generate strategy.")), 500


@strategy_bp.route("", methods=["GET"])
def list_strategies():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    result = HistoryRepository.list_all(generation_type="strategy", page=page, per_page=per_page)
    return jsonify(build_success_response(result)), 200


@strategy_bp.route("/<record_id>", methods=["GET"])
def get_strategy(record_id: str):
    record = HistoryRepository.get_by_id(record_id)
    if not record or record.get("generation_type") != "strategy":
        return jsonify(build_error_response("NOT_FOUND", "Strategy not found.")), 404
    return jsonify(build_success_response({
        "history_id": record["id"],
        "strategy": record.get("ai_output", {}),
        "user_inputs": record.get("user_inputs", {}),
        "created_at": record.get("created_at"),
        "loaded_from_history": True,
    })), 200


@strategy_bp.route("/<record_id>", methods=["DELETE"])
def delete_strategy(record_id: str):
    deleted = HistoryRepository.delete(record_id)
    if not deleted:
        return jsonify(build_error_response("NOT_FOUND", "Not found.")), 404
    return jsonify(build_success_response(None, "Deleted")), 200


# ── Recommendation endpoints ───────────────────────────────────

@recommendation_bp.route("/generate", methods=["POST"])
def generate_recommendations():
    data = request.get_json(silent=True) or {}
    sanitised = {k: sanitise_string(str(v)) if isinstance(v, str) else v for k, v in data.items()}
    try:
        result = recommendation_service.generate(sanitised)
        return jsonify(build_success_response(result, "Recommendations generated successfully")), 201
    except GroqServiceError as exc:
        return jsonify(build_error_response(exc.code, exc.message)), 503
    except Exception as exc:
        log.error("Error: %s", exc, exc_info=True)
        return jsonify(build_error_response("INTERNAL_ERROR", "Failed to generate recommendations.")), 500


@recommendation_bp.route("", methods=["GET"])
def list_recommendations():
    result = HistoryRepository.list_all(generation_type="recommendation")
    return jsonify(build_success_response(result)), 200


@recommendation_bp.route("/<record_id>", methods=["GET"])
def get_recommendation(record_id: str):
    record = HistoryRepository.get_by_id(record_id)
    if not record or record.get("generation_type") != "recommendation":
        return jsonify(build_error_response("NOT_FOUND", "Recommendations not found.")), 404
    return jsonify(build_success_response({
        "history_id": record["id"],
        "recommendations": record.get("ai_output", {}),
        "user_inputs": record.get("user_inputs", {}),
        "created_at": record.get("created_at"),
        "loaded_from_history": True,
    })), 200
