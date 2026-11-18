"""Operational KPI aggregations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_rate(numerator: float, denominator: float) -> float:
    return round(float(numerator) / float(denominator) * 100, 2) if denominator else 0.0


def _aggregate_period(ops: pd.DataFrame, exc: pd.DataFrame, key: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for period, group in ops.groupby(key, dropna=False):
        ids = set(group["request_id"])
        relevant_exc = exc[exc["request_id"].isin(ids)]
        eligible = group[~group["status"].isin(["CANCELLED", "REJECTED"])]
        completed = group["status"].eq("COMPLETED")
        exception_requests = relevant_exc["request_id"].nunique()
        dq_requests = relevant_exc.loc[relevant_exc["exception_type"] == "DATA_QUALITY", "request_id"].nunique()
        completed_minutes = group.loc[completed, "processing_minutes"]
        rows.append(
            {
                key: period,
                "total_requests": len(group),
                "completed_requests": int(completed.sum()),
                "pending_requests": int(group["is_pending"].sum()),
                "cancelled_rejected_requests": int(group["status"].isin(["CANCELLED", "REJECTED"]).sum()),
                "completion_rate_pct": _safe_rate(completed.sum(), len(group)),
                "average_processing_minutes": round(float(completed_minutes.mean()), 2) if len(completed_minutes) else 0.0,
                "median_processing_minutes": round(float(completed_minutes.median()), 2) if len(completed_minutes) else 0.0,
                "sla_breach_count": int(eligible["sla_breach_flag"].sum()),
                "sla_breach_rate_pct": _safe_rate(eligible["sla_breach_flag"].sum(), len(eligible)),
                "approaching_sla_count": int(group["sla_approaching_flag"].sum()),
                "cutoff_risk_count": int(group["cutoff_risk_flag"].sum()),
                "cutoff_breach_count": int(group["cutoff_breach_flag"].sum()),
                "cutoff_breach_rate_pct": _safe_rate(group["cutoff_breach_flag"].sum(), len(group)),
                "exception_count": len(relevant_exc),
                "exception_request_count": exception_requests,
                "exception_rate_pct": _safe_rate(exception_requests, len(group)),
                "critical_high_exception_count": int(relevant_exc["severity"].isin(["Critical", "High"]).sum()),
                "escalation_count": int(relevant_exc["is_escalated"].sum()),
                "unresolved_exception_count": int(relevant_exc["status"].eq("OPEN").sum()),
                "incomplete_ssi_count": int(group["ssi_validation_status"].ne("VALID").sum()),
                "invalid_request_count": dq_requests,
                "data_quality_exception_rate_pct": _safe_rate(dq_requests, len(group)),
            }
        )
    if not rows:
        return pd.DataFrame(columns=[key])
    return pd.DataFrame(rows).sort_values(key).reset_index(drop=True)


def daily_kpis(operations: pd.DataFrame, exceptions: pd.DataFrame) -> pd.DataFrame:
    daily = _aggregate_period(operations, exceptions, "request_date")
    if daily.empty:
        return daily
    daily["previous_day_volume"] = daily["total_requests"].shift(1)
    daily["day_over_day_change"] = daily["total_requests"] - daily["previous_day_volume"]
    daily["day_over_day_change_pct"] = np.where(
        daily["previous_day_volume"].gt(0),
        (daily["day_over_day_change"] / daily["previous_day_volume"] * 100).round(2),
        np.nan,
    )
    daily["rolling_7_day_volume"] = daily["total_requests"].rolling(7, min_periods=1).sum()
    return daily


def weekly_kpis(operations: pd.DataFrame, exceptions: pd.DataFrame) -> pd.DataFrame:
    ops = operations.copy()
    exc = exceptions.copy()
    ops["week_start"] = pd.to_datetime(ops["request_date"]).dt.to_period("W-SUN").dt.start_time.dt.date.astype(str)
    if not exc.empty:
        exc["week_start"] = pd.to_datetime(exc["request_date"]).dt.to_period("W-SUN").dt.start_time.dt.date.astype(str)
    weekly = _aggregate_period(ops, exc, "week_start")
    weekly["previous_week_volume"] = weekly["total_requests"].shift(1)
    weekly["week_over_week_change"] = weekly["total_requests"] - weekly["previous_week_volume"]
    return weekly


def owner_workload(operations: pd.DataFrame) -> pd.DataFrame:
    labelled = operations.assign(owner=operations["owner"].fillna("UNASSIGNED"))
    result = labelled.groupby("owner", as_index=False).agg(
        total_requests=("request_id", "count"),
        pending_requests=("is_pending", "sum"),
        high_priority_requests=("priority", lambda x: int(x.isin(["HIGH", "CRITICAL"]).sum())),
        completed_requests=("status", lambda x: int(x.eq("COMPLETED").sum())),
        average_processing_minutes=("processing_minutes", "mean"),
    )
    result["completion_rate_pct"] = (result["completed_requests"] / result["total_requests"] * 100).round(2)
    result["average_processing_minutes"] = result["average_processing_minutes"].round(2)
    return result.sort_values(["pending_requests", "total_requests"], ascending=False).reset_index(drop=True)


def currency_performance(operations: pd.DataFrame) -> pd.DataFrame:
    result = operations.groupby(["currency", "market"], as_index=False).agg(
        total_requests=("request_id", "count"),
        pending_requests=("is_pending", "sum"),
        cutoff_risk_count=("cutoff_risk_flag", "sum"),
        cutoff_breach_count=("cutoff_breach_flag", "sum"),
        sla_breach_count=("sla_breach_flag", "sum"),
        completed_requests=("status", lambda x: int(x.eq("COMPLETED").sum())),
    )
    result["completion_rate_pct"] = (result["completed_requests"] / result["total_requests"] * 100).round(2)
    result["cutoff_breach_rate_pct"] = (result["cutoff_breach_count"] / result["total_requests"] * 100).round(2)
    result["sla_breach_rate_pct"] = (result["sla_breach_count"] / result["total_requests"] * 100).round(2)
    return result.sort_values(["cutoff_breach_count", "sla_breach_count"], ascending=False).reset_index(drop=True)
