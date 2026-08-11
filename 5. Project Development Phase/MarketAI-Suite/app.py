"""
MarketAI Suite — Flask Application Entry Point
===============================================
Initialises the Flask app, database, logging, blueprints, and error handlers.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, send_from_directory

# ── Logging (initialise FIRST — before any module imports that use logging) ──
from utils.logger import setup_logger
from config import config, Config

_logger = setup_logger(
    name="marketai",
    log_level=config.LOG_LEVEL,
    log_file=config.LOG_FILE,
)

# ── Now import application modules ─────────────────────────────
from models.database import init_db, check_db_health
from utils.error_handlers import register_error_handlers

# Routes
from routes.campaign_routes import bp as campaign_bp
from routes.sales_routes import bp as sales_bp
from routes.lead_routes import bp as lead_bp
from routes.segmentation_routes import bp as segmentation_bp
from routes.strategy_routes import strategy_bp, recommendation_bp
from routes.history_routes import bp as history_bp
from routes.dashboard_routes import bp as dashboard_bp
from services.groq_service import groq_service

log = _logger


def create_app(test_config: dict | None = None) -> Flask:
    """
    Application factory.

    Parameters
    ----------
    test_config : Optional dict of config overrides (used in tests).

    Returns
    -------
    Flask application instance
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ── Apply configuration ────────────────────────────────────
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    app.config["DEBUG"] = config.DEBUG
    app.config["TESTING"] = False

    if test_config:
        app.config.update(test_config)

    # ── Initialise database ────────────────────────────────────
    if not app.config.get("TESTING") or app.config.get("INIT_DB_FOR_TESTING"):
        try:
            init_db()
        except Exception as exc:
            log.error("Database initialisation failed: %s", exc)

    # ── Register error handlers ────────────────────────────────
    register_error_handlers(app)

    # ── Register API blueprints ────────────────────────────────
    for blueprint in [
        campaign_bp,
        sales_bp,
        lead_bp,
        segmentation_bp,
        strategy_bp,
        recommendation_bp,
        history_bp,
        dashboard_bp,
    ]:
        app.register_blueprint(blueprint)

    # ── Health endpoint ────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        db_status = check_db_health()
        groq_status = groq_service.get_status()
        return jsonify({
            "success": True,
            "status": "healthy",
            "service": "MarketAI Suite",
            "version": "1.0.0",
            "database": db_status,
            "ai_service": {
                "configured": groq_status["configured"],
                "model": groq_status["model"],
                # NOTE: API key is NEVER included in this response
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }), 200

    # ── Frontend page routes ───────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/campaign")
    def campaign():
        return render_template("campaign.html")

    @app.route("/sales-pitch")
    def sales_pitch():
        return render_template("sales_pitch.html")

    @app.route("/lead-scoring")
    def lead_scoring():
        return render_template("lead_scoring.html")

    @app.route("/segmentation")
    def segmentation():
        return render_template("segmentation.html")

    @app.route("/strategy")
    def strategy():
        return render_template("strategy.html")

    @app.route("/history")
    def history():
        return render_template("history.html")

    @app.route("/reports")
    def reports():
        return render_template("reports.html")

    @app.route("/settings")
    def settings():
        return render_template("settings.html")

    # ── Config validation warning ──────────────────────────────
    errors = Config.validate()
    if errors:
        for err in errors:
            log.warning("Configuration issue: %s", err)

    log.info(
        "MarketAI Suite started | env=%s debug=%s model=%s",
        config.FLASK_ENV,
        config.DEBUG,
        config.GROQ_MODEL,
    )

    return app


# ── Entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    application = create_app()
    application.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=config.DEBUG,
    )
