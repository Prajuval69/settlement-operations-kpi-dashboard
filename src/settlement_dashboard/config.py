"""Central project configuration.

Every threshold in this module is a fictional portfolio assumption.  Nothing in
this project should be interpreted as a real bank, market, or custodian rule.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    seed: int = 20260923
    start_date: str = "2026-06-01"
    end_date: str = "2026-09-18"
    records_per_business_day: int = 24
    reporting_timestamp_utc: str = "2026-09-19T04:00:00Z"
    sla_approaching_minutes: int = 30
    aging_bucket_edges: tuple[int, ...] = (30, 60, 120, 240, 480)
    aging_bucket_labels: tuple[str, ...] = (
        "< 30 minutes",
        "30–60 minutes",
        "1–2 hours",
        "2–4 hours",
        "4–8 hours",
        "8+ hours",
    )
    terminal_statuses: tuple[str, ...] = ("COMPLETED", "CANCELLED", "REJECTED")
    output_dir: Path = field(default_factory=lambda: Path("outputs"))
    database_path: Path = field(default_factory=lambda: Path("outputs/settlement_operations.db"))


DEFAULT_CONFIG = PipelineConfig()
