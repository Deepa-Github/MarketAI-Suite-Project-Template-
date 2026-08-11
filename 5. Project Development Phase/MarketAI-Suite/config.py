"""
MarketAI Suite — Central Application Configuration
===================================================
Reads all configuration from environment variables via python-dotenv.
Never hardcode secrets here. Use .env for local development.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────
# Load .env file from the project root
# ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration class — all settings sourced from environment."""

    # ── Flask ──────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    FLASK_ENV: str = os.environ.get("FLASK_ENV", "development")
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    HOST: str = os.environ.get("FLASK_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("FLASK_PORT", "5000"))

    # ── File Uploads ───────────────────────────────────────────
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))
    ALLOWED_UPLOAD_EXTENSIONS: set = {"csv"}

    # ── Database ───────────────────────────────────────────────
    DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "database/marketai.db")

    @classmethod
    def get_database_path(cls) -> Path:
        """Return absolute path to the SQLite database file."""
        path = Path(cls.DATABASE_PATH)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    # ── Groq AI ────────────────────────────────────────────────
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_MAX_TOKENS: int = int(os.environ.get("GROQ_MAX_TOKENS", "4096"))
    GROQ_TEMPERATURE: float = float(os.environ.get("GROQ_TEMPERATURE", "0.7"))
    GROQ_TIMEOUT: int = int(os.environ.get("GROQ_TIMEOUT", "120"))

    # ── Logging ────────────────────────────────────────────────
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.environ.get("LOG_FILE", "logs/marketai.log")

    # ── Rate Limiting ──────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate critical configuration.
        Returns a list of error messages; empty list means configuration is valid.
        """
        errors: list[str] = []

        if not cls.GROQ_API_KEY:
            errors.append(
                "GROQ_API_KEY is not set. "
                "Obtain an API key from https://console.groq.com/ and add it to .env"
            )
        elif cls.GROQ_API_KEY == "your_groq_api_key_here":
            errors.append(
                "GROQ_API_KEY is still set to the placeholder value. "
                "Replace it with your actual Groq API key in .env"
            )

        if cls.SECRET_KEY in ("dev-secret-change-me", "change_this_to_a_long_random_secret_key_in_production"):
            if cls.FLASK_ENV == "production":
                errors.append(
                    "SECRET_KEY must be set to a strong random value in production."
                )

        return errors

    @classmethod
    def is_groq_configured(cls) -> bool:
        """Return True only if the Groq API key looks valid (non-empty, non-placeholder)."""
        return bool(cls.GROQ_API_KEY) and cls.GROQ_API_KEY not in (
            "",
            "your_groq_api_key_here",
        )


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ":memory:"
    GROQ_API_KEY = "test-key-not-real"
    LOG_LEVEL = "ERROR"


# ──────────────────────────────────────────────────────────────
# Configuration selector
# ──────────────────────────────────────────────────────────────
_CONFIG_MAP: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config() -> type[Config]:
    """Return the appropriate Config class based on FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    return _CONFIG_MAP.get(env, DevelopmentConfig)


# Convenience alias — import this throughout the app
config = get_config()
