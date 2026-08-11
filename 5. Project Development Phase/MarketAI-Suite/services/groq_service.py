"""
MarketAI Suite — Centralised Groq AI Service
=============================================
ALL Groq API calls must go through this service.
The API key is never exposed to routes or the frontend.

Usage
-----
    from services.groq_service import groq_service
    result = groq_service.generate(system_prompt, user_prompt)
"""

from __future__ import annotations

import time
from typing import Any

from groq import Groq, APIError, APITimeoutError, APIConnectionError, AuthenticationError, RateLimitError
from config import config
from utils.logger import get_logger
from utils.helpers import parse_ai_json

log = get_logger("groq_service")


class GroqServiceError(Exception):
    """Raised when the Groq service cannot fulfil a request."""

    def __init__(self, message: str, code: str = "GROQ_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class GroqService:
    """
    Wrapper around the Groq Python SDK.

    Attributes
    ----------
    _client : Groq  — lazily-initialised Groq client
    model   : str   — model name from config
    """

    def __init__(self) -> None:
        self._client: Groq | None = None
        self.model: str = config.GROQ_MODEL
        self.max_tokens: int = config.GROQ_MAX_TOKENS
        self.temperature: float = config.GROQ_TEMPERATURE
        self.timeout: int = config.GROQ_TIMEOUT

    # ──────────────────────────────────────────────────────────
    # Internal client initialisation
    # ──────────────────────────────────────────────────────────

    def _get_client(self) -> Groq:
        """Return (and lazily initialise) the Groq client."""
        if self._client is None:
            if not config.is_groq_configured():
                raise GroqServiceError(
                    "GROQ_API_KEY is not configured. "
                    "Add your API key to the .env file and restart the application. "
                    "Obtain a key at https://console.groq.com/",
                    code="GROQ_NOT_CONFIGURED",
                )
            # The Groq client reads GROQ_API_KEY from environment automatically,
            # but we pass it explicitly to be consistent and testable.
            self._client = Groq(api_key=config.GROQ_API_KEY, timeout=self.timeout)
            log.info("Groq client initialised (model=%s)", self.model)
        return self._client

    # ──────────────────────────────────────────────────────────
    # Core generation method
    # ──────────────────────────────────────────────────────────

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        """
        Send a chat completion request and return the raw text response.

        Parameters
        ----------
        system_prompt : Role/context instructions for the model
        user_prompt   : The actual user query / task
        temperature   : Override the default temperature (0.0–1.0)
        max_tokens    : Override the default max_tokens
        model         : Override the configured model name

        Returns
        -------
        str — The model's text response (stripped)

        Raises
        ------
        GroqServiceError on any API or network failure
        """
        client = self._get_client()
        _model = model or self.model
        _temperature = temperature if temperature is not None else self.temperature
        _max_tokens = max_tokens or self.max_tokens

        log.info("Groq request | model=%s max_tokens=%d temperature=%.2f", _model, _max_tokens, _temperature)
        start = time.time()

        try:
            completion = client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=_temperature,
                max_tokens=_max_tokens,
            )
            elapsed = time.time() - start
            response_text = completion.choices[0].message.content or ""
            log.info(
                "Groq response received | elapsed=%.2fs chars=%d",
                elapsed,
                len(response_text),
            )
            return response_text.strip()

        except AuthenticationError as exc:
            log.error("Groq AuthenticationError — check GROQ_API_KEY in .env")
            raise GroqServiceError(
                "Invalid Groq API key. Please verify your GROQ_API_KEY in the .env file.",
                code="GROQ_AUTH_ERROR",
            ) from exc

        except RateLimitError as exc:
            log.warning("Groq RateLimitError: %s", exc)
            raise GroqServiceError(
                "Groq API rate limit reached. Please wait a moment and try again.",
                code="GROQ_RATE_LIMIT",
            ) from exc

        except APITimeoutError as exc:
            log.error("Groq APITimeoutError after %ds", self.timeout)
            raise GroqServiceError(
                f"The AI request timed out after {self.timeout} seconds. Please try again.",
                code="GROQ_TIMEOUT",
            ) from exc

        except APIConnectionError as exc:
            log.error("Groq APIConnectionError: %s", exc)
            raise GroqServiceError(
                "Could not connect to the Groq API. Check your network connection.",
                code="GROQ_CONNECTION_ERROR",
            ) from exc

        except APIError as exc:
            log.error("Groq APIError: status=%s message=%s", exc.status_code, exc.message)
            if exc.status_code == 404:
                raise GroqServiceError(
                    f"Model '{_model}' was not found. "
                    "Update GROQ_MODEL in .env to a valid model name (e.g. llama-3.3-70b-versatile).",
                    code="GROQ_MODEL_NOT_FOUND",
                ) from exc
            raise GroqServiceError(
                f"Groq API error ({exc.status_code}): {exc.message}",
                code="GROQ_API_ERROR",
            ) from exc

        except Exception as exc:
            log.error("Unexpected error calling Groq: %s", exc, exc_info=True)
            raise GroqServiceError(
                "An unexpected error occurred while communicating with the AI service.",
                code="GROQ_UNEXPECTED_ERROR",
            ) from exc

    # ──────────────────────────────────────────────────────────
    # JSON generation helper
    # ──────────────────────────────────────────────────────────

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        required_keys: list[str] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict | list:
        """
        Generate a response and parse it as JSON.

        Raises
        ------
        GroqServiceError if the AI response cannot be parsed as JSON.
        """
        raw = self.generate(system_prompt, user_prompt, temperature=temperature, max_tokens=max_tokens)
        parsed, error = parse_ai_json(raw, required_keys=required_keys)
        if error:
            log.error("JSON parse failure: %s | raw_preview=%s", error, raw[:500])
            raise GroqServiceError(
                f"The AI returned a response that could not be parsed: {error}",
                code="GROQ_PARSE_ERROR",
            )
        return parsed

    # ──────────────────────────────────────────────────────────
    # Health / status
    # ──────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Return non-sensitive configuration status for the health endpoint."""
        return {
            "configured": config.is_groq_configured(),
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
        }


# ──────────────────────────────────────────────────────────────
# Singleton — import this throughout the application
# ──────────────────────────────────────────────────────────────
groq_service = GroqService()
