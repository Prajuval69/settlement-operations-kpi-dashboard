"""Operational exception and escalation generation."""

from __future__ import annotations

import pandas as pd


SEVERITY = {
    "CUTOFF_BREACH": "Critical",
    "SLA_BREACH": "High",
    "MISSING_OWNER": "High",
    "REPEATED_ESCALATION": "High",
    "HIGH_PRIORITY_PENDING": "High",
    "CUTOFF_RISK": "Medium",
    "MISSING_SSI_VALIDATION": "Medium",
    "DATA_QUALITY": "Medium",
    "INCOMPLETE_REQUEST": "Low",
}
SEVERITY_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


def _reasons(row: pd.Series) -> list[tuple[str, str]]:
    reasons: list[tuple[str, str]] = []
    if row["cutoff_risk"] in {"WATCH", "AT_RISK"} and row["is_pending"]:
        reasons.append(("CUTOFF_RISK", f"Pending request is {row['cutoff_risk'].lower()} relative to the demo cutoff"))
    if row["cutoff_breach_flag"]:
        reasons.append(("CUTOFF_BREACH", "Evaluation or completion occurred after the configured demo cutoff"))
    if row["sla_breach_flag"]:
        reasons.append(("SLA_BREACH", "Request exceeded its configured demo SLA"))
    if row["ssi_validation_status"] != "VALID":
        reasons.append(("MISSING_SSI_VALIDATION", f"SSI state is {row['ssi_validation_status']}"))
    if pd.isna(row["owner"]):
        reasons.append(("MISSING_OWNER", "No operations owner is assigned"))
    if row["priority"] in {"HIGH", "CRITICAL"} and row["is_pending"]:
        reasons.append(("HIGH_PRIORITY_PENDING", f"{row['priority'].title()} priority request remains open"))
    if row["status"] in {"ON_HOLD", "REJECTED"}:
        reasons.append(("INCOMPLETE_REQUEST", f"Request status is {row['status']}"))
    if row["ssi_validation_status"] == "INVALID" or pd.isna(row["owner"]):
        reasons.append(("DATA_QUALITY", "Required operational reference data is invalid or missing"))
    return reasons


def generate_exceptions(operations: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    records: list[dict[str, object]] = []
    counter = 1
    for _, row in operations.iterrows():
        reasons = _reasons(row)
        if len(reasons) >= 3:
            reasons.append(("REPEATED_ESCALATION", "Request triggered three or more concurrent exception rules"))
        for exception_type, reason in reasons:
            severity = SEVERITY[exception_type]
            is_escalated = SEVERITY_RANK[severity] >= 3 or exception_type == "REPEATED_ESCALATION"
            unresolved = bool(row["is_pending"] or exception_type in {"MISSING_OWNER", "MISSING_SSI_VALIDATION", "DATA_QUALITY"})
            detected = row["evaluation_timestamp"]
            records.append(
                {
                    "exception_id": f"EXC-{counter:07d}",
                    "request_id": row["request_id"],
                    "request_date": row["request_date"],
                    "currency": row["currency"],
                    "market": row["market"],
                    "exception_type": exception_type,
                    "severity": severity,
                    "severity_rank": SEVERITY_RANK[severity],
                    "detected_at": detected,
                    "status": "OPEN" if unresolved else "RESOLVED",
                    "owner": row["owner"],
                    "escalation_reason": reason if is_escalated else pd.NA,
                    "is_escalated": is_escalated,
                    "escalation_timestamp": detected if is_escalated else pd.NaT,
                    "escalation_owner": row["owner"] if is_escalated and pd.notna(row["owner"]) else ("Duty Manager" if is_escalated else pd.NA),
                    "resolution_timestamp": pd.NaT if unresolved else row["completion_timestamp"],
                    "exception_age_minutes": row["age_minutes"] if unresolved else 0.0,
                }
            )
            counter += 1
    columns = [
        "exception_id", "request_id", "request_date", "currency", "market", "exception_type",
        "severity", "severity_rank", "detected_at", "status", "owner", "escalation_reason",
        "is_escalated", "escalation_timestamp", "escalation_owner", "resolution_timestamp",
        "exception_age_minutes",
    ]
    exceptions = pd.DataFrame(records, columns=columns)
    flagged = set(exceptions["request_id"]) if not exceptions.empty else set()
    enriched = operations.copy()
    enriched["exception_flag"] = enriched["request_id"].isin(flagged)
    escalation_reasons = (
        exceptions.loc[exceptions["is_escalated"]]
        .groupby("request_id")["escalation_reason"]
        .agg(lambda x: " | ".join(sorted(set(x.dropna().astype(str)))))
    ) if not exceptions.empty else pd.Series(dtype="object")
    enriched["escalation_reason"] = enriched["request_id"].map(escalation_reasons)
    enriched["is_escalated"] = enriched["escalation_reason"].notna()
    return enriched, exceptions

