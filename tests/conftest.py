from __future__ import annotations

import pandas as pd
import pytest

from settlement_dashboard.config import PipelineConfig


@pytest.fixture
def config(tmp_path):
    return PipelineConfig(
        start_date="2026-09-14",
        end_date="2026-09-18",
        records_per_business_day=8,
        output_dir=tmp_path / "outputs",
        database_path=tmp_path / "outputs" / "settlement_operations.db",
    )


def make_operation(**overrides):
    base = {
        "request_id": "REQ-TEST-0001",
        "request_date": "2026-09-18",
        "received_timestamp": pd.Timestamp("2026-09-18T12:00:00Z"),
        "client_id": "SYN-CLIENT-0001",
        "market": "United Kingdom",
        "country": "GB",
        "currency": "GBP",
        "request_type": "PAYMENT_RELEASE",
        "source_channel": "API",
        "priority": "HIGH",
        "cutoff_time": "15:30",
        "timezone": "Europe/London",
        "warning_threshold_minutes": 120,
        "at_risk_threshold_minutes": 30,
        "sla_minutes": 180,
        "owner": "Noah Williams",
        "status": "PENDING",
        "completion_timestamp": pd.NaT,
        "ssi_validation_status": "VALID",
        "created_at": pd.Timestamp("2026-09-18T12:00:00Z"),
        "updated_at": pd.Timestamp("2026-09-18T13:00:00Z"),
    }
    base.update(overrides)
    return pd.DataFrame([base])

