"""Independent post-run verification for generated deliverables."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def main() -> None:
    expected = {
        "operations.csv", "exceptions.csv", "daily_kpis.csv", "weekly_kpis.csv",
        "cutoff_risk_queue.csv", "sla_breach_queue.csv", "owner_workload.csv",
        "currency_performance.csv", "reference_currency_cutoffs.csv",
        "reference_sla_rules.csv", "reference_owners.csv", "reference_request_types.csv",
        "daily_operations_report.md", "run_manifest.json", "settlement_operations.db",
        "powerbi/FactOperations.csv", "powerbi/FactExceptions.csv", "powerbi/DimDate.csv",
        "powerbi/DimCurrency.csv", "powerbi/DimMarket.csv", "powerbi/DimOwner.csv",
        "powerbi/DimRequestType.csv",
    }
    present = {str(path.relative_to(OUT)).replace("\\", "/") for path in OUT.rglob("*") if path.is_file()}
    missing = expected - present
    assert not missing, f"Missing outputs: {sorted(missing)}"

    ops = pd.read_csv(OUT / "operations.csv")
    exc = pd.read_csv(OUT / "exceptions.csv")
    daily = pd.read_csv(OUT / "daily_kpis.csv")
    assert len(ops) == 1920 and ops["request_id"].is_unique
    assert len(exc) > 0 and exc["exception_id"].is_unique
    assert len(daily) == 80
    assert set(ops["cutoff_risk"]) <= {"LOW", "WATCH", "AT_RISK", "BREACHED"}
    assert (ops["processing_minutes"] >= 0).all() and (ops["age_minutes"] >= 0).all()
    assert int(daily["total_requests"].sum()) == len(ops)
    assert int(ops["status"].eq("COMPLETED").sum()) == int(daily["completed_requests"].sum())
    assert int(ops["sla_breach_flag"].sum()) == int(daily["sla_breach_count"].sum())
    assert int(ops["cutoff_breach_flag"].sum()) == int(daily["cutoff_breach_count"].sum())
    assert int(exc["is_escalated"].sum()) == int(daily["escalation_count"].sum())

    with sqlite3.connect(OUT / "settlement_operations.db") as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT COUNT(*) FROM operations").fetchone()[0] == len(ops)
        assert connection.execute("SELECT COUNT(*) FROM exceptions").fetchone()[0] == len(exc)
        assert connection.execute("SELECT COUNT(*) FROM vw_pending_queue").fetchone()[0] == int(ops["is_pending"].sum())

    manifest = json.loads((OUT / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["classification"] == "SYNTHETIC_DEMO_ONLY"
    assert manifest["database_counts"]["operations"] == len(ops)
    assert "Total Requests" in (ROOT / "dax_measures.md").read_text(encoding="utf-8")
    assert not list(ROOT.rglob("*.pbix")), "Unexpected PBIX file found"
    print(json.dumps({
        "files_verified": len(expected),
        "operations": len(ops),
        "exceptions": len(exc),
        "business_days": len(daily),
        "sqlite_integrity": "ok",
        "reconciliations": "passed",
    }, indent=2))


if __name__ == "__main__":
    main()

