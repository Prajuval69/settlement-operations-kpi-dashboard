# Daily Operations Review — 2026-09-18

> Synthetic portfolio simulation only. Cutoffs, SLAs, owners, clients, and operational rules are fictional demo assumptions; this report is not connected to a bank or production settlement system.

## Headline KPIs

- Requests received: 24
- Completed: 13 (54.17%)
- Pending: 11
- SLA breaches: 7 (29.17% of eligible requests)
- Cutoff risk (WATCH or AT_RISK): 2
- Cutoff breaches: 14
- Exceptions: 38 across 19 requests
- Unresolved exceptions: 32
- Day-over-day volume change: 0

## Operational Focus

- Highest aggregate cutoff-breach count across the full demo period: JPY (127).
- Largest aggregate pending workload across the full demo period: Aarav Mehta (28).
- Use `cutoff_risk_queue.csv`, `sla_breach_queue.csv`, and `exceptions.csv` for request-level follow-up.

## Reproducibility

Generated from fixed seed `20260923` at synthetic as-of `2026-09-19T04:00:00Z` by `python -m settlement_dashboard.pipeline`.
