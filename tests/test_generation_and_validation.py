from __future__ import annotations

import pandas as pd
import pytest

from settlement_dashboard.generation import generate_operations
from settlement_dashboard.reference_data import currency_cutoffs, owners, request_types, sla_rules
from settlement_dashboard.validation import validate_operations


def test_generation_is_deterministic(config):
    refs = (currency_cutoffs(), sla_rules(), owners(), request_types())
    first = generate_operations(config, *refs)
    second = generate_operations(config, *refs)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 40


def test_generation_has_required_scenarios(config):
    df = generate_operations(config, currency_cutoffs(), sla_rules(), owners(), request_types())
    assert df["currency"].nunique() >= 4
    assert df["request_type"].nunique() >= 3
    assert set(df["priority"]).issubset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})
    assert df["owner"].nunique() >= 4


def test_validation_rejects_invalid_currency(config):
    df = generate_operations(config, currency_cutoffs(), sla_rules(), owners(), request_types())
    df.loc[0, "currency"] = "XXX"
    with pytest.raises(ValueError, match="Invalid currency"):
        validate_operations(df, set(currency_cutoffs()["currency"]), set(request_types()["request_type"]), set(owners()["owner"]))


def test_validation_rejects_completion_before_receipt(config):
    df = generate_operations(config, currency_cutoffs(), sla_rules(), owners(), request_types())
    df.loc[0, "completion_timestamp"] = pd.Timestamp(df.loc[0, "received_timestamp"]) - pd.Timedelta(minutes=1)
    with pytest.raises(ValueError, match="precedes receipt"):
        validate_operations(df, set(currency_cutoffs()["currency"]), set(request_types()["request_type"]), set(owners()["owner"]))

