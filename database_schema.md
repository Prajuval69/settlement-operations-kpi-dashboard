# Database Schema

`outputs/settlement_operations.db` is rebuilt on every pipeline run.

Tables: `operations`, `exceptions`, `daily_kpis`, `weekly_kpis`, `reference_currency_cutoffs`, `reference_sla_rules`, `reference_owners`, and `reference_request_types`.

Indexes cover request ID/date, currency, owner, status, priority, received timestamp, and exception status/severity/detection/request. Reference tables use primary keys and positive-value checks. SQLite foreign keys are enabled; fact tables intentionally retain snapshot-style flat columns for portable analytics.

Views: `vw_pending_queue`, `vw_cutoff_risk_queue`, `vw_sla_breach_queue`, `vw_owner_workload`, and `vw_currency_performance`.

`sql/operational_queries.sql` includes daily volume, pending/cutoff/SLA queues, open exceptions, currency performance, owner workload, and persisted daily KPI queries. The pipeline runs `PRAGMA integrity_check` and records table counts in `run_manifest.json`.

