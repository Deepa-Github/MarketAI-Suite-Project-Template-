"""
MarketAI Suite — Input Validators
===================================
Centralised validation helpers used by route handlers.
All validators return (is_valid: bool, error_message: str | None).
"""

from __future__ import annotations

import re
import os
from typing import Any


# ──────────────────────────────────────────────────────────────
# Generic helpers
# ──────────────────────────────────────────────────────────────

def require_fields(data: dict, required: list[str]) -> tuple[bool, str | None]:
    """Check that all required keys are present and non-empty in *data*."""
    missing = [f for f in required if not data.get(f, "")]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, None


def max_length(value: str, limit: int, field_name: str = "Field") -> tuple[bool, str | None]:
    if len(value) > limit:
        return False, f"{field_name} must not exceed {limit} characters."
    return True, None


def is_valid_email(email: str) -> tuple[bool, str | None]:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, f"'{email}' is not a valid email address."
    return True, None


def is_positive_number(value: Any, field_name: str = "Value") -> tuple[bool, str | None]:
    try:
        num = float(value)
        if num < 0:
            raise ValueError
    except (TypeError, ValueError):
        return False, f"{field_name} must be a positive number."
    return True, None


def is_in_range(value: Any, min_val: float, max_val: float, field_name: str = "Value") -> tuple[bool, str | None]:
    try:
        num = float(value)
        if not (min_val <= num <= max_val):
            return False, f"{field_name} must be between {min_val} and {max_val}."
    except (TypeError, ValueError):
        return False, f"{field_name} must be a number."
    return True, None


# ──────────────────────────────────────────────────────────────
# File upload validators
# ──────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {"csv"}
MAX_CSV_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_csv_upload(file) -> tuple[bool, str | None]:
    """Validate a Flask file upload object for CSV ingestion."""
    if not file or file.filename == "":
        return False, "No file selected for upload."
    if not is_allowed_file(file.filename):
        return False, "Only CSV files are supported. Please upload a .csv file."
    return True, None


# ──────────────────────────────────────────────────────────────
# Campaign validator
# ──────────────────────────────────────────────────────────────

def validate_campaign_input(data: dict) -> tuple[bool, str | None]:
    required = ["product_name", "product_description", "target_audience", "campaign_objective"]
    ok, err = require_fields(data, required)
    if not ok:
        return False, err
    ok, err = max_length(data.get("product_name", ""), 200, "Product name")
    if not ok:
        return False, err
    ok, err = max_length(data.get("product_description", ""), 2000, "Product description")
    if not ok:
        return False, err
    return True, None


# ──────────────────────────────────────────────────────────────
# Sales pitch validator
# ──────────────────────────────────────────────────────────────

def validate_sales_pitch_input(data: dict) -> tuple[bool, str | None]:
    required = ["product_name", "product_description", "customer_name", "customer_industry", "pain_points"]
    ok, err = require_fields(data, required)
    if not ok:
        return False, err
    ok, err = max_length(data.get("product_name", ""), 200, "Product name")
    if not ok:
        return False, err
    return True, None


# ──────────────────────────────────────────────────────────────
# Lead scoring validator
# ──────────────────────────────────────────────────────────────

REQUIRED_LEAD_COLUMNS = {"name", "email", "company"}


def validate_lead_csv_columns(columns: list[str]) -> tuple[bool, str | None]:
    cols_lower = {c.strip().lower() for c in columns}
    missing = REQUIRED_LEAD_COLUMNS - cols_lower
    if missing:
        return False, f"CSV is missing required columns: {', '.join(sorted(missing))}"
    return True, None


def validate_manual_lead(data: dict) -> tuple[bool, str | None]:
    required = ["name", "email", "company"]
    ok, err = require_fields(data, required)
    if not ok:
        return False, err
    ok, err = is_valid_email(data.get("email", ""))
    if not ok:
        return False, err
    return True, None


# ──────────────────────────────────────────────────────────────
# Segmentation validator
# ──────────────────────────────────────────────────────────────

def validate_segmentation_input(data: dict) -> tuple[bool, str | None]:
    required = ["business_description", "target_market"]
    return require_fields(data, required)


# ──────────────────────────────────────────────────────────────
# Strategy validator
# ──────────────────────────────────────────────────────────────

def validate_strategy_input(data: dict) -> tuple[bool, str | None]:
    required = ["business_name", "industry", "marketing_objective"]
    return require_fields(data, required)


# ──────────────────────────────────────────────────────────────
# Sanitisation helper
# ──────────────────────────────────────────────────────────────

def sanitise_string(value: str, max_len: int = 5000) -> str:
    """Strip leading/trailing whitespace and truncate to max_len."""
    return str(value).strip()[:max_len]
