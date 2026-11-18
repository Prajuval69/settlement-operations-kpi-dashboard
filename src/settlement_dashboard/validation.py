"""Data-quality checks that fail loudly before KPI production."""

from __future__ import annotations

import re

import pandas as pd


REQUIRED_OPERATION_COLUMNS = {
    "request_id",
    "request_date",
    "received_timestamp",
    "currency",
    "request_type",
    "priority",
    "status",
    "sla_minutes",
    "cutoff_time",
    "timezone",
    "updated_at",
}
VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_STATUSES = {"COMPLETED", "PENDING", "IN_PROGRESS", "ON_HOLD", "CANCELLED", "REJECTED"}


def validate_operations(
    df: pd.DataFrame,
    valid_currencies: set[str],
    valid_request_types: set[str],
    valid_owners: set[str],
) -> dict[str, int]:
    missing = REQUIRED_OPERATION_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required operation columns: {sorted(missing)}")
    if df["request_id"].duplicated().any():
        raise ValueError("request_id must be unique")
    if not set(df["currency"]).issubset(valid_currencies):
        raise ValueError("Invalid currency detected")
    if not set(df["request_type"]).issubset(valid_request_types):
        raise ValueError("Invalid request type detected")
    if not set(df["priority"]).issubset(VALID_PRIORITIES):
        raise ValueError("Invalid priority detected")
    if not set(df["status"]).issubset(VALID_STATUSES):
        raise ValueError("Invalid status detected")
    assigned = set(df["owner"].dropna())
    if not assigned.issubset(valid_owners):
        raise ValueError("Invalid owner detected")
    if (pd.to_numeric(df["sla_minutes"], errors="coerce") <= 0).any():
        raise ValueError("SLA values must be positive")
    if not df["cutoff_time"].astype(str).map(lambda x: bool(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", x))).all():
        raise ValueError("Invalid cutoff time detected")
    received = pd.to_datetime(df["received_timestamp"], utc=True, errors="coerce")
    updated = pd.to_datetime(df["updated_at"], utc=True, errors="coerce")
    completed = pd.to_datetime(df["completion_timestamp"], utc=True, errors="coerce")
    if received.isna().any() or updated.isna().any():
        raise ValueError("Required timestamps are invalid")
    if ((completed.notna()) & (completed < received)).any():
        raise ValueError("Completion timestamp precedes receipt")
    if ((updated - received).dt.total_seconds() < 0).any():
        raise ValueError("Updated timestamp precedes receipt")
    return {
        "rows": int(len(df)),
        "missing_owner_rows": int(df["owner"].isna().sum()),
        "invalid_ssi_rows": int(df["ssi_validation_status"].isin(["INVALID", "PENDING"]).sum()),
    }


def validate_enriched_operations(df: pd.DataFrame) -> None:
    if (df["processing_minutes"] < 0).any() or (df["age_minutes"] < 0).any():
        raise ValueError("Negative duration generated")
    if df["sla_status"].isna().any() or df["cutoff_risk"].isna().any():
        raise ValueError("Risk classification is incomplete")

