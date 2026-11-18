from __future__ import annotations

import pandas as pd

from settlement_dashboard.config import PipelineConfig
from settlement_dashboard.exceptions import SEVERITY, generate_exceptions
from settlement_dashboard.kpis import daily_kpis, owner_workload
from settlement_dashboard.risk import enrich_operations
from conftest import make_operation


def test_exception_generation_and_severity():
    op = make_operation(
        owner=pd.NA,
        priority="CRITICAL",
        ssi_validation_status="INVALID",
        updated_at=pd.Timestamp("2026-09-18T15:31:00Z"),
    )
    enriched = enrich_operations(op, PipelineConfig())
    operations, exceptions = generate_exceptions(enriched)
    types = set(exceptions["exception_type"])
    assert {"CUTOFF_BREACH", "SLA_BREACH", "MISSING_OWNER", "HIGH_PRIORITY_PENDING", "DATA_QUALITY"}.issubset(types)
    assert "REPEATED_ESCALATION" in types
    assert SEVERITY["CUTOFF_BREACH"] == "Critical"
    assert operations.loc[0, "exception_flag"]
    assert operations.loc[0, "is_escalated"]


def test_kpi_calculation_and_owner_workload():
    first = enrich_operations(
        make_operation(status="COMPLETED", completion_timestamp=pd.Timestamp("2026-09-18T13:00:00Z")),
        PipelineConfig(),
    )
    second = enrich_operations(
        make_operation(request_id="REQ-TEST-0002", owner="Maya Chen", updated_at=pd.Timestamp("2026-09-18T15:01:00Z")),
        PipelineConfig(),
    )
    ops = pd.concat([first, second], ignore_index=True)
    ops, exc = generate_exceptions(ops)
    daily = daily_kpis(ops, exc)
    assert daily.loc[0, "total_requests"] == 2
    assert daily.loc[0, "completed_requests"] == 1
    assert daily.loc[0, "pending_requests"] == 1
    assert daily.loc[0, "completion_rate_pct"] == 50.0
    assert daily.loc[0, "sla_breach_count"] == 1
    workload = owner_workload(ops)
    assert workload["total_requests"].sum() == 2
    assert workload["pending_requests"].sum() == 1


def test_zero_record_kpis_are_empty():
    empty_ops = pd.DataFrame(columns=["request_date"])
    empty_exc = pd.DataFrame(columns=["request_id"])
    result = daily_kpis(empty_ops, empty_exc)
    assert result.empty

