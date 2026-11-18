from __future__ import annotations

import json
import sqlite3

import pandas as pd

from settlement_dashboard.pipeline import run_pipeline


def test_pipeline_outputs_and_sqlite(config):
    manifest = run_pipeline(config)
    out = config.output_dir
    expected = [
        "operations.csv", "exceptions.csv", "daily_kpis.csv", "weekly_kpis.csv",
        "cutoff_risk_queue.csv", "sla_breach_queue.csv", "owner_workload.csv",
        "currency_performance.csv", "settlement_operations.db", "run_manifest.json",
        "powerbi/FactOperations.csv", "powerbi/FactExceptions.csv", "powerbi/DimDate.csv",
        "powerbi/DimCurrency.csv", "powerbi/DimMarket.csv", "powerbi/DimOwner.csv",
        "powerbi/DimRequestType.csv",
    ]
    for name in expected:
        assert (out / name).exists(), name
    operations = pd.read_csv(out / "operations.csv")
    assert len(operations) == 40
    assert not operations["cutoff_risk"].isna().any()
    assert not operations["sla_status"].isna().any()
    with sqlite3.connect(config.database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM operations").fetchone()[0]
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        view_count = connection.execute("SELECT COUNT(*) FROM vw_pending_queue").fetchone()[0]
    assert count == len(operations)
    assert integrity == "ok"
    assert view_count == int(operations["is_pending"].sum())
    assert manifest["classification"] == "SYNTHETIC_DEMO_ONLY"
    stored = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert stored["seed"] == config.seed

