"""
MarketAI Suite — Lead Scoring Routes
======================================
POST /api/leads/score       — Score a single manual lead
POST /api/leads/upload      — Upload and score a CSV of leads
GET  /api/leads             — List all lead scoring sessions
GET  /api/leads/<id>        — Get a specific lead analysis
DELETE /api/leads/<id>
"""

from __future__ import annotations

from flask import Blueprint, request, jsonify, Response

from services.lead_scoring_service import lead_scoring_service
from services.groq_service import GroqServiceError
from services.report_service import report_service
from models.schemas import HistoryRepository
from utils.validators import validate_manual_lead, validate_csv_upload, validate_lead_csv_columns, sanitise_string
from utils.helpers import build_success_response, build_error_response
from utils.logger import get_logger

log = get_logger("lead_routes")
bp = Blueprint("leads", __name__, url_prefix="/api/leads")


@bp.route("/score", methods=["POST"])
def score_lead():
    """Score a single manually entered lead."""
    data = request.get_json(silent=True) or {}
    sanitised = {k: sanitise_string(str(v)) if isinstance(v, str) else v for k, v in data.items()}

    ok, err = validate_manual_lead(sanitised)
    if not ok:
        return jsonify(build_error_response("VALIDATION_ERROR", err)), 400

    try:
        result = lead_scoring_service.score_manual_lead(sanitised)
        return jsonify(build_success_response(result, "Lead scored successfully")), 201
    except GroqServiceError as exc:
        return jsonify(build_error_response(exc.code, exc.message)), 503
    except Exception as exc:
        log.error("Unexpected error scoring lead: %s", exc, exc_info=True)
        return jsonify(build_error_response("INTERNAL_ERROR", "Failed to score lead.")), 500


@bp.route("/upload", methods=["POST"])
def upload_leads():
    """Process a CSV upload of multiple leads."""
    if "file" not in request.files:
        return jsonify(build_error_response("VALIDATION_ERROR", "No file provided. Use form-data with key 'file'.")), 400

    file = request.files["file"]
    ok, err = validate_csv_upload(file)
    if not ok:
        return jsonify(build_error_response("VALIDATION_ERROR", err)), 400

    try:
        file_bytes = file.read()
        if len(file_bytes) == 0:
            return jsonify(build_error_response("VALIDATION_ERROR", "Uploaded file is empty.")), 400

        # Quick column validation before heavy processing
        import io, pandas as pd
        try:
            preview_df = pd.read_csv(io.BytesIO(file_bytes), nrows=0)
            cols_ok, col_err = validate_lead_csv_columns(list(preview_df.columns))
            if not cols_ok:
                return jsonify(build_error_response("VALIDATION_ERROR", col_err)), 400
        except Exception as parse_err:
            return jsonify(build_error_response("VALIDATION_ERROR", f"Cannot read CSV: {parse_err}")), 400

        result = lead_scoring_service.process_csv(file_bytes, file.filename or "leads.csv")
        return jsonify(build_success_response(result, "Leads processed successfully")), 201

    except ValueError as exc:
        return jsonify(build_error_response("VALIDATION_ERROR", str(exc))), 400
    except GroqServiceError as exc:
        return jsonify(build_error_response(exc.code, exc.message)), 503
    except Exception as exc:
        log.error("Unexpected error uploading leads: %s", exc, exc_info=True)
        return jsonify(build_error_response("INTERNAL_ERROR", "Failed to process leads CSV.")), 500


@bp.route("", methods=["GET"])
def list_leads():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    result = HistoryRepository.list_all(generation_type="lead_scoring", page=page, per_page=per_page)
    return jsonify(build_success_response(result)), 200


@bp.route("/<record_id>", methods=["GET"])
def get_lead_analysis(record_id: str):
    """Load a previously scored lead analysis — NO new Groq call."""
    record = HistoryRepository.get_by_id(record_id)
    if not record or record.get("generation_type") != "lead_scoring":
        return jsonify(build_error_response("NOT_FOUND", "Lead analysis not found.")), 404
    return jsonify(build_success_response({
        "history_id": record["id"],
        "summary": record.get("metadata", {}),
        "ai_output": record.get("ai_output", {}),
        "user_inputs": record.get("user_inputs", {}),
        "created_at": record.get("created_at"),
        "loaded_from_history": True,
    })), 200


@bp.route("/<record_id>/export", methods=["GET"])
def export_lead_csv(record_id: str):
    """Export lead analysis as CSV."""
    record = HistoryRepository.get_by_id(record_id)
    if not record or record.get("generation_type") != "lead_scoring":
        return jsonify(build_error_response("NOT_FOUND", "Lead analysis not found.")), 404

    ai_output = record.get("ai_output", {})
    scored_leads = ai_output.get("scored_leads", [])
    if not scored_leads:
        # Single lead
        single = ai_output
        if isinstance(single, dict):
            scored_leads = [single]

    csv_content = report_service.generate_leads_csv(scored_leads)
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=leads_analysis_{record_id[:8]}.csv"},
    )


@bp.route("/<record_id>", methods=["DELETE"])
def delete_lead_analysis(record_id: str):
    deleted = HistoryRepository.delete(record_id)
    if not deleted:
        return jsonify(build_error_response("NOT_FOUND", "Record not found.")), 404
    return jsonify(build_success_response(None, "Deleted")), 200
