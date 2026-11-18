"""Build the reviewed Data-app snapshot from pipeline CSV outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def records(name: str) -> list[dict[str, object]]:
    frame = pd.read_csv(OUTPUTS / name)
    frame = frame.astype(object).where(pd.notna(frame), None)
    return frame.to_dict(orient="records")


def source(label: str, file_name: str, sql: str, definitions: list[dict[str, object]]) -> dict[str, object]:
    return {
        "label": label,
        "files": [f"outputs/{file_name}"],
        "sql": sql,
        "filters": ["Synthetic demo records from 2026-06-01 through 2026-09-18"],
        "caveats": [
            "All records, cutoff times, SLAs, owners, clients, and workflow rules are fictional portfolio assumptions.",
            "This artifact has no connection to bank systems or production settlement data.",
        ],
        "metricDefinitions": definitions,
        "evidenceFlow": [
            {"title": "Generate", "detail": "Run python -m settlement_dashboard.pipeline with seed 20260923."},
            {"title": "Validate", "detail": "Reject malformed timestamps, currencies, statuses, priorities, owners, SLA values, and cutoff times."},
            {"title": "Aggregate", "detail": "Calculate timezone-aware cutoff risk, SLA states, aging, exceptions, and KPI outputs."},
        ],
    }


def main() -> None:
    snapshot = {
        "surface": "dashboard",
        "title": "Settlement operations cutoff & KPI monitoring",
        "generatedAt": "2026-09-19T04:00:00Z",
        "status": "fixture",
        "buildStatus": "complete",
        "filters": [
            {"id": "currency", "label": "Currency", "field": "currency", "defaultValue": "all", "queryIds": ["operations", "exceptions"]},
            {"id": "market", "label": "Market", "field": "market", "defaultValue": "all", "queryIds": ["operations", "exceptions"]},
            {"id": "request_type", "label": "Request type", "field": "request_type", "defaultValue": "all", "queryIds": ["operations"]},
            {"id": "priority", "label": "Priority", "field": "priority", "defaultValue": "all", "queryIds": ["operations"]},
            {"id": "owner", "label": "Owner", "field": "owner", "defaultValue": "all", "queryIds": ["operations", "exceptions"]},
        ],
        "queries": {
            "daily": {
                "rows": records("daily_kpis.csv"),
                "source": source(
                    "Synthetic daily operational KPI output",
                    "daily_kpis.csv",
                    "SELECT * FROM daily_kpis ORDER BY request_date",
                    [
                        {"label": "Completion rate", "definition": "Completed requests divided by all requests for the business date.", "formula": "completed_requests / total_requests", "componentIds": ["overview-kpis", "daily-trend"]},
                        {"label": "SLA breach rate", "definition": "SLA-breached eligible requests divided by eligible requests for the business date.", "componentIds": ["overview-kpis", "sla-trend"]},
                        {"label": "Cutoff risk count", "definition": "Requests classified WATCH or AT_RISK; BREACHED is reported separately.", "componentIds": ["overview-kpis", "risk-trend"]},
                    ],
                ),
                "methods": [{"language": "Python", "code": "daily_kpis(operations, exceptions)"}],
            },
            "operations": {
                "rows": records("operations.csv"),
                "source": source(
                    "Synthetic request-level operations output",
                    "operations.csv",
                    "SELECT * FROM operations",
                    [
                        {"label": "Minutes to cutoff", "definition": "Configured local cutoff converted to UTC minus the completion or evaluation timestamp, in minutes.", "componentIds": ["risk-detail"]},
                        {"label": "Processing minutes", "definition": "Elapsed minutes from receipt to completion for completed requests, otherwise receipt to evaluation time; clamped at zero.", "componentIds": ["owner-performance"]},
                    ],
                ),
                "methods": [{"language": "Python", "code": "enrich_operations(raw_operations, PipelineConfig())"}],
            },
            "exceptions": {
                "rows": records("exceptions.csv"),
                "source": source(
                    "Synthetic exception and escalation output",
                    "exceptions.csv",
                    "SELECT * FROM exceptions",
                    [
                        {"label": "Exception count", "definition": "Count of generated exception records; a request can have more than one exception.", "componentIds": ["exception-summary", "exception-detail"]},
                        {"label": "Exception age", "definition": "Age of an unresolved exception at the synthetic reporting timestamp; resolved exceptions are zero.", "componentIds": ["exception-aging"]},
                    ],
                ),
                "methods": [{"language": "Python", "code": "generate_exceptions(enriched_operations)"}],
            },
            "currency": {
                "rows": records("currency_performance.csv"),
                "source": source(
                    "Synthetic currency performance aggregation",
                    "currency_performance.csv",
                    "SELECT * FROM vw_currency_performance",
                    [{"label": "Cutoff breach rate", "definition": "Cutoff-breached requests divided by all requests for the currency.", "componentIds": ["currency-risk"]}],
                ),
            },
            "owners": {
                "rows": records("owner_workload.csv"),
                "source": source(
                    "Synthetic owner workload aggregation",
                    "owner_workload.csv",
                    "SELECT * FROM vw_owner_workload",
                    [{"label": "Owner workload", "definition": "Request counts grouped by assigned synthetic owner; missing ownership is shown as UNASSIGNED.", "componentIds": ["owner-workload", "owner-performance"]}],
                ),
            },
        },
    }
    destination = OUTPUTS / "dashboard_snapshot.json"
    destination.write_text(json.dumps(snapshot, indent=2, allow_nan=False), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
