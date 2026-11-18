from __future__ import annotations

import pandas as pd

from settlement_dashboard.config import PipelineConfig
from settlement_dashboard.risk import aging_bucket, classify_cutoff_risk, cutoff_datetime_utc, enrich_operations
from conftest import make_operation


def test_cutoff_risk_boundaries():
    assert classify_cutoff_risk(121, 120, 30) == "LOW"
    assert classify_cutoff_risk(120, 120, 30) == "WATCH"
    assert classify_cutoff_risk(31, 120, 30) == "WATCH"
    assert classify_cutoff_risk(30, 120, 30) == "AT_RISK"
    assert classify_cutoff_risk(0, 120, 30) == "AT_RISK"
    assert classify_cutoff_risk(-1, 120, 30) == "BREACHED"


def test_timezone_and_date_rollover():
    tokyo = cutoff_datetime_utc("2026-09-18", "15:00", "Asia/Tokyo")
    new_york = cutoff_datetime_utc("2026-09-18", "16:00", "America/New_York")
    assert tokyo == pd.Timestamp("2026-09-18T06:00:00Z")
    assert new_york == pd.Timestamp("2026-09-18T20:00:00Z")


def test_exact_cutoff_is_at_risk():
    row = make_operation(updated_at=pd.Timestamp("2026-09-18T14:30:00Z"))  # London is UTC+1
    result = enrich_operations(row, PipelineConfig())
    assert result.loc[0, "minutes_to_cutoff"] == 0
    assert result.loc[0, "cutoff_risk"] == "AT_RISK"


def test_one_minute_before_and_after_cutoff():
    before = enrich_operations(make_operation(updated_at=pd.Timestamp("2026-09-18T14:29:00Z")), PipelineConfig())
    after = enrich_operations(make_operation(updated_at=pd.Timestamp("2026-09-18T14:31:00Z")), PipelineConfig())
    assert before.loc[0, "minutes_to_cutoff"] == 1
    assert before.loc[0, "cutoff_risk"] == "AT_RISK"
    assert after.loc[0, "minutes_to_cutoff"] == -1
    assert after.loc[0, "cutoff_risk"] == "BREACHED"


def test_completed_after_cutoff_and_completed_sla():
    row = make_operation(
        status="COMPLETED",
        completion_timestamp=pd.Timestamp("2026-09-18T15:15:00Z"),
        updated_at=pd.Timestamp("2026-09-18T15:15:00Z"),
    )
    result = enrich_operations(row, PipelineConfig())
    assert result.loc[0, "cutoff_risk"] == "BREACHED"
    assert result.loc[0, "sla_status"] == "COMPLETED_LATE"
    assert result.loc[0, "processing_minutes"] == 195


def test_sla_states_completed_and_pending():
    within = enrich_operations(
        make_operation(status="COMPLETED", completion_timestamp=pd.Timestamp("2026-09-18T13:00:00Z")),
        PipelineConfig(),
    )
    approaching = enrich_operations(make_operation(updated_at=pd.Timestamp("2026-09-18T14:40:00Z")), PipelineConfig())
    breached = enrich_operations(make_operation(updated_at=pd.Timestamp("2026-09-18T15:01:00Z")), PipelineConfig())
    assert within.loc[0, "sla_status"] == "COMPLETED_WITHIN_SLA"
    assert approaching.loc[0, "sla_status"] == "APPROACHING_SLA"
    assert breached.loc[0, "sla_status"] == "SLA_BREACHED"


def test_aging_buckets_and_negative_protection():
    config = PipelineConfig()
    assert aging_bucket(-5, config) == "< 30 minutes"
    assert aging_bucket(29.9, config) == "< 30 minutes"
    assert aging_bucket(30, config) == "30–60 minutes"
    assert aging_bucket(60, config) == "1–2 hours"
    assert aging_bucket(120, config) == "2–4 hours"
    assert aging_bucket(240, config) == "4–8 hours"
    assert aging_bucket(480, config) == "8+ hours"

