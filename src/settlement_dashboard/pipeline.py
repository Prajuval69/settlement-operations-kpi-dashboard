"""End-to-end synthetic settlement-operations pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import DEFAULT_CONFIG, PipelineConfig
from .database import build_database, verify_database
from .exceptions import generate_exceptions
from .generation import generate_operations
from .kpis import currency_performance, daily_kpis, owner_workload, weekly_kpis
from .reference_data import currency_cutoffs, owners, request_types, sla_rules
from .risk import enrich_operations
from .validation import validate_enriched_operations, validate_operations


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%dT%H:%M:%SZ")


def _date_dimension(start: str, end: str) -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="D")
    return pd.DataFrame(
        {
            "date": dates.date.astype(str),
            "year": dates.year,
            "quarter": "Q" + dates.quarter.astype(str),
            "month_number": dates.month,
            "month_name": dates.strftime("%B"),
            "week_of_year": dates.isocalendar().week.astype(int).to_numpy(),
            "day_of_week": dates.strftime("%A"),
            "is_business_day": (dates.dayofweek < 5),
        }
    )


def run_pipeline(config: PipelineConfig = DEFAULT_CONFIG) -> dict[str, object]:
    output_dir = Path(config.output_dir)
    powerbi_dir = output_dir / "powerbi"
    output_dir.mkdir(parents=True, exist_ok=True)
    powerbi_dir.mkdir(parents=True, exist_ok=True)

    cutoffs = currency_cutoffs()
    slas = sla_rules()
    owner_ref = owners()
    type_ref = request_types()
    raw = generate_operations(config, cutoffs, slas, owner_ref, type_ref)
    quality = validate_operations(
        raw,
        set(cutoffs["currency"]),
        set(type_ref["request_type"]),
        set(owner_ref["owner"]),
    )
    operations = enrich_operations(raw, config)
    validate_enriched_operations(operations)
    operations, exceptions = generate_exceptions(operations)

    daily = daily_kpis(operations, exceptions)
    weekly = weekly_kpis(operations, exceptions)
    workload = owner_workload(operations)
    currency = currency_performance(operations)
    cutoff_queue = operations[operations["cutoff_risk"].isin(["WATCH", "AT_RISK", "BREACHED"])].copy()
    cutoff_queue = cutoff_queue.sort_values(["cutoff_breach_flag", "minutes_to_cutoff"], ascending=[False, True])
    sla_queue = operations[operations["sla_breach_flag"]].sort_values("sla_remaining_minutes")

    exports = {
        "operations.csv": operations,
        "exceptions.csv": exceptions,
        "daily_kpis.csv": daily,
        "weekly_kpis.csv": weekly,
        "cutoff_risk_queue.csv": cutoff_queue,
        "sla_breach_queue.csv": sla_queue,
        "owner_workload.csv": workload,
        "currency_performance.csv": currency,
        "reference_currency_cutoffs.csv": cutoffs,
        "reference_sla_rules.csv": slas,
        "reference_owners.csv": owner_ref,
        "reference_request_types.csv": type_ref,
    }
    for name, frame in exports.items():
        _write_csv(frame, output_dir / name)

    fact_operations = operations.copy()
    fact_operations["owner"] = fact_operations["owner"].fillna("UNASSIGNED")
    fact_exceptions = exceptions.copy()
    fact_exceptions["owner"] = fact_exceptions["owner"].fillna("UNASSIGNED")
    fact_exceptions["exception_date"] = pd.to_datetime(fact_exceptions["detected_at"], utc=True).dt.date.astype(str)
    dim_date = _date_dimension(config.start_date, config.end_date)
    dim_currency = cutoffs[["currency", "market", "country", "timezone", "cutoff_time", "warning_threshold_minutes", "at_risk_threshold_minutes"]]
    dim_market = cutoffs[["market", "country"]].drop_duplicates().sort_values("market")
    dim_owner = pd.concat(
        [owner_ref, pd.DataFrame([{"owner": "UNASSIGNED", "team": "Unassigned", "region": "Unassigned", "active_flag": True}])],
        ignore_index=True,
    )
    powerbi_exports = {
        "FactOperations.csv": fact_operations,
        "FactExceptions.csv": fact_exceptions,
        "DimDate.csv": dim_date,
        "DimCurrency.csv": dim_currency,
        "DimMarket.csv": dim_market,
        "DimOwner.csv": dim_owner,
        "DimRequestType.csv": type_ref,
    }
    for name, frame in powerbi_exports.items():
        _write_csv(frame, powerbi_dir / name)

    build_database(
        Path(config.database_path), operations, exceptions, daily, weekly,
        cutoffs, slas, owner_ref, type_ref,
    )
    db_counts = verify_database(Path(config.database_path))

    latest = daily.iloc[-1].to_dict()
    top_currency = currency.iloc[0]
    top_owner = workload.iloc[0]
    report = f"""# Daily Operations Review — {latest['request_date']}

> Synthetic portfolio simulation only. Cutoffs, SLAs, owners, clients, and operational rules are fictional demo assumptions; this report is not connected to a bank or production settlement system.

## Headline KPIs

- Requests received: {int(latest['total_requests'])}
- Completed: {int(latest['completed_requests'])} ({latest['completion_rate_pct']:.2f}%)
- Pending: {int(latest['pending_requests'])}
- SLA breaches: {int(latest['sla_breach_count'])} ({latest['sla_breach_rate_pct']:.2f}% of eligible requests)
- Cutoff risk (WATCH or AT_RISK): {int(latest['cutoff_risk_count'])}
- Cutoff breaches: {int(latest['cutoff_breach_count'])}
- Exceptions: {int(latest['exception_count'])} across {int(latest['exception_request_count'])} requests
- Unresolved exceptions: {int(latest['unresolved_exception_count'])}
- Day-over-day volume change: {int(latest['day_over_day_change']) if pd.notna(latest['day_over_day_change']) else 'n/a'}

## Operational Focus

- Highest aggregate cutoff-breach count across the full demo period: {top_currency['currency']} ({int(top_currency['cutoff_breach_count'])}).
- Largest aggregate pending workload across the full demo period: {top_owner['owner']} ({int(top_owner['pending_requests'])}).
- Use `cutoff_risk_queue.csv`, `sla_breach_queue.csv`, and `exceptions.csv` for request-level follow-up.

## Reproducibility

Generated from fixed seed `{config.seed}` at synthetic as-of `{config.reporting_timestamp_utc}` by `python -m settlement_dashboard.pipeline`.
"""
    (output_dir / "daily_operations_report.md").write_text(report, encoding="utf-8")
    manifest = {
        "classification": "SYNTHETIC_DEMO_ONLY",
        "seed": config.seed,
        "reporting_timestamp_utc": config.reporting_timestamp_utc,
        "date_range": {"start": config.start_date, "end": config.end_date},
        "quality": quality,
        "database_counts": db_counts,
        "latest_business_day_kpis": latest,
        "output_files": sorted([str(path.relative_to(output_dir)) for path in output_dir.rglob("*") if path.is_file()]),
    }
    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_CONFIG.output_dir))
    args = parser.parse_args()
    out = Path(args.output_dir)
    config = PipelineConfig(output_dir=out, database_path=out / "settlement_operations.db")
    manifest = run_pipeline(config)
    print(json.dumps(manifest, indent=2, default=str))


if __name__ == "__main__":
    main()
