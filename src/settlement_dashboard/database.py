"""SQLite persistence and analytical views."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE reference_currency_cutoffs (
    currency TEXT PRIMARY KEY,
    market TEXT NOT NULL,
    country TEXT NOT NULL,
    timezone TEXT NOT NULL,
    cutoff_time TEXT NOT NULL,
    warning_threshold_minutes INTEGER NOT NULL CHECK (warning_threshold_minutes > 0),
    at_risk_threshold_minutes INTEGER NOT NULL CHECK (at_risk_threshold_minutes >= 0),
    business_day_flag INTEGER NOT NULL,
    assumption_type TEXT NOT NULL
);
CREATE TABLE reference_sla_rules (
    request_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    sla_minutes INTEGER NOT NULL CHECK (sla_minutes > 0),
    assumption_type TEXT NOT NULL,
    PRIMARY KEY (request_type, priority)
);
CREATE TABLE reference_owners (
    owner TEXT PRIMARY KEY,
    team TEXT NOT NULL,
    region TEXT NOT NULL,
    active_flag INTEGER NOT NULL
);
CREATE TABLE reference_request_types (
    request_type TEXT PRIMARY KEY,
    request_type_description TEXT NOT NULL,
    active_flag INTEGER NOT NULL
);
"""

INDEX_SQL = """
CREATE UNIQUE INDEX idx_operations_request_id ON operations(request_id);
CREATE INDEX idx_operations_request_date ON operations(request_date);
CREATE INDEX idx_operations_currency ON operations(currency);
CREATE INDEX idx_operations_owner ON operations(owner);
CREATE INDEX idx_operations_status ON operations(status);
CREATE INDEX idx_operations_priority ON operations(priority);
CREATE INDEX idx_operations_received ON operations(received_timestamp);
CREATE INDEX idx_exceptions_status ON exceptions(status);
CREATE INDEX idx_exceptions_severity ON exceptions(severity);
CREATE INDEX idx_exceptions_detected ON exceptions(detected_at);
CREATE INDEX idx_exceptions_request_id ON exceptions(request_id);
"""

VIEW_SQL = """
CREATE VIEW vw_pending_queue AS
SELECT request_id, request_date, currency, market, owner, priority, status,
       received_timestamp, age_minutes, aging_bucket, cutoff_risk, sla_status
FROM operations WHERE is_pending = 1;

CREATE VIEW vw_cutoff_risk_queue AS
SELECT request_id, request_date, currency, market, owner, priority, cutoff_time,
       cutoff_datetime_utc, minutes_to_cutoff, cutoff_risk, sla_status
FROM operations WHERE cutoff_risk IN ('WATCH', 'AT_RISK', 'BREACHED');

CREATE VIEW vw_sla_breach_queue AS
SELECT request_id, request_date, request_type, currency, owner, priority,
       sla_deadline, sla_remaining_minutes, sla_status, status
FROM operations WHERE sla_breach_flag = 1;

CREATE VIEW vw_owner_workload AS
SELECT COALESCE(owner, 'UNASSIGNED') AS owner,
       COUNT(*) AS total_requests,
       SUM(is_pending) AS pending_requests,
       SUM(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS high_priority_requests,
       ROUND(AVG(processing_minutes), 2) AS average_processing_minutes
FROM operations GROUP BY COALESCE(owner, 'UNASSIGNED');

CREATE VIEW vw_currency_performance AS
SELECT currency, market, COUNT(*) AS total_requests,
       SUM(is_pending) AS pending_requests,
       SUM(cutoff_risk_flag) AS cutoff_risk_count,
       SUM(cutoff_breach_flag) AS cutoff_breach_count,
       SUM(sla_breach_flag) AS sla_breach_count
FROM operations GROUP BY currency, market;
"""


def _sqlite_ready(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in result.columns:
        if pd.api.types.is_datetime64_any_dtype(result[column]):
            result[column] = result[column].astype("string")
        elif pd.api.types.is_bool_dtype(result[column]):
            result[column] = result[column].astype(int)
    return result


def build_database(
    path: Path,
    operations: pd.DataFrame,
    exceptions: pd.DataFrame,
    daily: pd.DataFrame,
    weekly: pd.DataFrame,
    cutoffs: pd.DataFrame,
    slas: pd.DataFrame,
    owners: pd.DataFrame,
    request_types: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA_SQL)
        _sqlite_ready(cutoffs).to_sql("reference_currency_cutoffs", connection, if_exists="append", index=False)
        _sqlite_ready(slas).to_sql("reference_sla_rules", connection, if_exists="append", index=False)
        _sqlite_ready(owners).to_sql("reference_owners", connection, if_exists="append", index=False)
        _sqlite_ready(request_types).to_sql("reference_request_types", connection, if_exists="append", index=False)
        _sqlite_ready(operations).to_sql("operations", connection, if_exists="replace", index=False)
        _sqlite_ready(exceptions).to_sql("exceptions", connection, if_exists="replace", index=False)
        _sqlite_ready(daily).to_sql("daily_kpis", connection, if_exists="replace", index=False)
        _sqlite_ready(weekly).to_sql("weekly_kpis", connection, if_exists="replace", index=False)
        connection.executescript(INDEX_SQL)
        connection.executescript(VIEW_SQL)


def verify_database(path: Path) -> dict[str, int]:
    with sqlite3.connect(path) as connection:
        tables = {
            name: int(connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])
            for name in [
                "operations", "exceptions", "daily_kpis", "weekly_kpis",
                "reference_currency_cutoffs", "reference_sla_rules",
                "reference_owners", "reference_request_types",
            ]
        }
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity check failed: {integrity}")
    return tables

