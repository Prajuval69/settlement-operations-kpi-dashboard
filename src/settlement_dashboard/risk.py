"""Cutoff, SLA, and aging calculations."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from .config import PipelineConfig


def _utc(value: object) -> pd.Timestamp:
    return pd.Timestamp(value).tz_convert("UTC") if pd.Timestamp(value).tzinfo else pd.Timestamp(value).tz_localize("UTC")


def cutoff_datetime_utc(request_date: object, cutoff_time: str, timezone: str) -> pd.Timestamp:
    """Build a timezone-aware cutoff timestamp for the request's local business date."""
    local_date = pd.Timestamp(request_date).date()
    hour, minute = map(int, cutoff_time.split(":"))
    local = datetime(local_date.year, local_date.month, local_date.day, hour, minute, tzinfo=ZoneInfo(timezone))
    return pd.Timestamp(local).tz_convert("UTC")


def classify_cutoff_risk(minutes_to_cutoff: float, warning_minutes: int, at_risk_minutes: int) -> str:
    if minutes_to_cutoff < 0:
        return "BREACHED"
    if minutes_to_cutoff <= at_risk_minutes:
        return "AT_RISK"
    if minutes_to_cutoff <= warning_minutes:
        return "WATCH"
    return "LOW"


def aging_bucket(age_minutes: float, config: PipelineConfig) -> str:
    age = max(0.0, float(age_minutes))
    for upper, label in zip(config.aging_bucket_edges, config.aging_bucket_labels):
        if age < upper:
            return label
    return config.aging_bucket_labels[-1]


def enrich_operations(operations: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
    """Apply cutoff, SLA, processing, pending, and aging logic."""
    df = operations.copy()
    received = pd.to_datetime(df["received_timestamp"], utc=True)
    completed = pd.to_datetime(df["completion_timestamp"], utc=True, errors="coerce")
    updated = pd.to_datetime(df["updated_at"], utc=True)

    cutoff_values = [
        cutoff_datetime_utc(d, t, z)
        for d, t, z in zip(df["request_date"], df["cutoff_time"], df["timezone"])
    ]
    df["cutoff_datetime_utc"] = pd.to_datetime(cutoff_values, utc=True)
    df["is_pending"] = ~df["status"].isin(config.terminal_statuses)
    evaluation = completed.where(completed.notna(), updated)
    df["evaluation_timestamp"] = evaluation
    df["minutes_to_cutoff"] = ((df["cutoff_datetime_utc"] - evaluation).dt.total_seconds() / 60).round(2)
    df["cutoff_risk"] = [
        classify_cutoff_risk(m, w, a)
        for m, w, a in zip(
            df["minutes_to_cutoff"],
            df["warning_threshold_minutes"],
            df["at_risk_threshold_minutes"],
        )
    ]
    df["cutoff_risk_flag"] = df["cutoff_risk"].isin(["WATCH", "AT_RISK"])
    df["cutoff_breach_flag"] = df["cutoff_risk"].eq("BREACHED")

    df["sla_deadline"] = received + pd.to_timedelta(df["sla_minutes"], unit="m")
    df["processing_minutes"] = ((evaluation - received).dt.total_seconds() / 60).clip(lower=0).round(2)
    df["sla_remaining_minutes"] = ((df["sla_deadline"] - evaluation).dt.total_seconds() / 60).round(2)

    def sla_status(row: pd.Series) -> str:
        remaining = row["sla_remaining_minutes"]
        if row["status"] == "COMPLETED":
            return "COMPLETED_LATE" if remaining < 0 else "COMPLETED_WITHIN_SLA"
        if row["status"] in {"CANCELLED", "REJECTED"}:
            return "NOT_APPLICABLE"
        if remaining < 0:
            return "SLA_BREACHED"
        approaching = min(config.sla_approaching_minutes, max(1, int(row["sla_minutes"] * 0.2)))
        return "APPROACHING_SLA" if remaining <= approaching else "WITHIN_SLA"

    df["sla_status"] = df.apply(sla_status, axis=1)
    df["sla_breach_flag"] = df["sla_status"].isin(["SLA_BREACHED", "COMPLETED_LATE"])
    df["sla_approaching_flag"] = df["sla_status"].eq("APPROACHING_SLA")
    df["age_minutes"] = ((updated - received).dt.total_seconds() / 60).clip(lower=0).round(2)
    df["aging_bucket"] = [
        aging_bucket(age, config) if pending else "NOT_PENDING"
        for age, pending in zip(df["age_minutes"], df["is_pending"])
    ]
    return df

