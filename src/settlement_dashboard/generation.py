"""Deterministic synthetic operations generator."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from .config import PipelineConfig


def generate_operations(
    config: PipelineConfig,
    cutoffs: pd.DataFrame,
    slas: pd.DataFrame,
    owner_reference: pd.DataFrame,
    request_type_reference: pd.DataFrame,
) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed)
    dates = pd.bdate_range(config.start_date, config.end_date)
    cutoff_rows = cutoffs.to_dict("records")
    owner_names = owner_reference["owner"].tolist()
    request_types = request_type_reference["request_type"].tolist()
    owner_probabilities = np.array([0.27, 0.21, 0.18, 0.14, 0.12, 0.08])
    priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    priority_p = [0.14, 0.56, 0.23, 0.07]
    status_values = ["COMPLETED", "PENDING", "IN_PROGRESS", "ON_HOLD", "CANCELLED", "REJECTED"]
    rows: list[dict[str, object]] = []
    reporting_ts = pd.Timestamp(config.reporting_timestamp_utc)

    for day_index, business_date in enumerate(dates):
        day_is_recent = (dates[-1] - business_date).days <= 7
        for sequence in range(config.records_per_business_day):
            ref = cutoff_rows[int(rng.integers(0, len(cutoff_rows)))]
            request_type = str(rng.choice(request_types))
            priority = str(rng.choice(priorities, p=priority_p))
            owner = str(rng.choice(owner_names, p=owner_probabilities))

            local_date = business_date.date()
            received_hour = int(rng.integers(7, 17))
            received_minute = int(rng.integers(0, 60))
            received_local = datetime(
                local_date.year,
                local_date.month,
                local_date.day,
                received_hour,
                received_minute,
                tzinfo=ZoneInfo(ref["timezone"]),
            )
            received_utc = pd.Timestamp(received_local).tz_convert("UTC")

            if day_is_recent:
                status_p = [0.67, 0.11, 0.10, 0.05, 0.04, 0.03]
            else:
                status_p = [0.91, 0.01, 0.01, 0.01, 0.035, 0.025]
            status = str(rng.choice(status_values, p=status_p))
            sla_minutes = int(
                slas.loc[
                    (slas["request_type"] == request_type) & (slas["priority"] == priority),
                    "sla_minutes",
                ].iloc[0]
            )

            completion = pd.NaT
            if status in {"COMPLETED", "CANCELLED", "REJECTED"}:
                typical = sla_minutes * (0.55 if status == "COMPLETED" else 0.30)
                duration = max(2, int(rng.gamma(2.2, typical / 2.2)))
                if sequence % 17 == 0:
                    duration = int(sla_minutes * 1.35)
                completion = received_utc + pd.Timedelta(minutes=duration)
                updated = completion
            else:
                if day_is_recent:
                    updated = min(reporting_ts, received_utc + pd.Timedelta(minutes=int(rng.integers(20, 720))))
                else:
                    updated = reporting_ts

            ssi_state = str(rng.choice(["VALID", "PENDING", "INVALID"], p=[0.86, 0.10, 0.04]))
            source = str(rng.choice(["SWIFT", "API", "EMAIL", "PORTAL"], p=[0.36, 0.31, 0.18, 0.15]))
            owner_value: object = owner
            if sequence == 3 and day_index % 11 == 0:
                owner_value = pd.NA
            if sequence == 7 and day_index % 13 == 0:
                ssi_state = "INVALID"

            rows.append(
                {
                    "request_id": f"REQ-{business_date:%Y%m%d}-{sequence + 1:04d}",
                    "request_date": business_date.date().isoformat(),
                    "received_timestamp": received_utc,
                    "client_id": f"SYN-CLIENT-{int(rng.integers(1, 181)):04d}",
                    "market": ref["market"],
                    "country": ref["country"],
                    "currency": ref["currency"],
                    "request_type": request_type,
                    "source_channel": source,
                    "priority": priority,
                    "cutoff_time": ref["cutoff_time"],
                    "timezone": ref["timezone"],
                    "warning_threshold_minutes": ref["warning_threshold_minutes"],
                    "at_risk_threshold_minutes": ref["at_risk_threshold_minutes"],
                    "sla_minutes": sla_minutes,
                    "owner": owner_value,
                    "status": status,
                    "completion_timestamp": completion,
                    "ssi_validation_status": ssi_state,
                    "created_at": received_utc,
                    "updated_at": updated,
                }
            )

    return pd.DataFrame(rows)

