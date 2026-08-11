"""
MarketAI Suite — Centralised Error Handlers
============================================
Register HTTP and application error handlers on the Flask app.
"""

from __future__ import annotations

from flask import Flask, jsonify
from utils.logger import get_logger

log = get_logger("error_handlers")


def register_error_handlers(app: Flask) -> None:
    """Attach all error handlers to the Flask application."""

    @app.errorhandler(400)
    def bad_request(exc):
        log.warning("400 Bad Request: %s", exc)
        return jsonify({"success": False, "error": {"code": "BAD_REQUEST", "message": str(exc)}}), 400

    @app.errorhandler(401)
    def unauthorized(exc):
        log.warning("401 Unauthorized: %s", exc)
        return jsonify({"success": False, "error": {"code": "UNAUTHORIZED", "message": "Authentication required."}}), 401

    @app.errorhandler(403)
    def forbidden(exc):
        log.warning("403 Forbidden: %s", exc)
        return jsonify({"success": False, "error": {"code": "FORBIDDEN", "message": "Access denied."}}), 403

    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "Resource not found."}}), 404

    @app.errorhandler(413)
    def file_too_large(exc):
        log.warning("413 Payload Too Large")
        return jsonify({"success": False, "error": {"code": "FILE_TOO_LARGE", "message": "Uploaded file exceeds the maximum allowed size."}}), 413

    @app.errorhandler(429)
    def rate_limited(exc):
        log.warning("429 Rate Limited: %s", exc)
        return jsonify({"success": False, "error": {"code": "RATE_LIMITED", "message": "Too many requests. Please wait before retrying."}}), 429

    @app.errorhandler(500)
    def internal_server_error(exc):
        log.error("500 Internal Server Error: %s", exc, exc_info=True)
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred. Please try again later."}}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(exc):
        log.error("Unhandled exception: %s", exc, exc_info=True)
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}}), 500
