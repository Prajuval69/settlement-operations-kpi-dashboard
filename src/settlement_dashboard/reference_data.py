"""Synthetic cutoff, SLA, owner, and request-type reference data."""

from __future__ import annotations

import pandas as pd


def currency_cutoffs() -> pd.DataFrame:
    """Return fictional currency/market cutoff assumptions."""
    rows = [
        ("USD", "North America", "US", "America/New_York", "16:00", 120, 30),
        ("EUR", "Eurozone", "DE", "Europe/Berlin", "16:30", 120, 30),
        ("GBP", "United Kingdom", "GB", "Europe/London", "15:30", 120, 30),
        ("JPY", "Japan", "JP", "Asia/Tokyo", "15:00", 90, 20),
        ("SGD", "Singapore", "SG", "Asia/Singapore", "16:00", 90, 20),
        ("INR", "India", "IN", "Asia/Kolkata", "17:00", 120, 30),
        ("AUD", "Australia", "AU", "Australia/Sydney", "15:30", 90, 20),
        ("CAD", "Canada", "CA", "America/Toronto", "16:00", 120, 30),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "currency",
            "market",
            "country",
            "timezone",
            "cutoff_time",
            "warning_threshold_minutes",
            "at_risk_threshold_minutes",
        ],
    ).assign(business_day_flag=True, assumption_type="SYNTHETIC_DEMO")


def request_types() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("PAYMENT_RELEASE", "Payment release", True),
            ("SSI_UPDATE", "Standing settlement instruction update", True),
            ("TRADE_REPAIR", "Trade repair", True),
            ("CASH_BREAK", "Cash break investigation", True),
            ("CONFIRMATION", "Settlement confirmation", True),
        ],
        columns=["request_type", "request_type_description", "active_flag"],
    )


def owners() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Aarav Mehta", "Team Alpha", "APAC", True),
            ("Maya Chen", "Team Alpha", "APAC", True),
            ("Noah Williams", "Team Beta", "EMEA", True),
            ("Sofia Rossi", "Team Beta", "EMEA", True),
            ("Liam Carter", "Team Gamma", "Americas", True),
            ("Emma Davis", "Team Gamma", "Americas", True),
        ],
        columns=["owner", "team", "region", "active_flag"],
    )


def sla_rules() -> pd.DataFrame:
    base = {
        "PAYMENT_RELEASE": 180,
        "SSI_UPDATE": 360,
        "TRADE_REPAIR": 240,
        "CASH_BREAK": 480,
        "CONFIRMATION": 120,
    }
    multipliers = {"LOW": 1.5, "MEDIUM": 1.0, "HIGH": 0.75, "CRITICAL": 0.5}
    rows = [
        (request_type, priority, max(30, int(minutes * factor)))
        for request_type, minutes in base.items()
        for priority, factor in multipliers.items()
    ]
    return pd.DataFrame(rows, columns=["request_type", "priority", "sla_minutes"]).assign(
        assumption_type="SYNTHETIC_DEMO"
    )

