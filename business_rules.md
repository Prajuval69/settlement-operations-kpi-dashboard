# Business Rules

All rules below are project-specific demo assumptions.

## Cutoff risk

- `LOW`: more than the currency warning threshold remains.
- `WATCH`: at or below the warning threshold, but above the at-risk threshold.
- `AT_RISK`: zero through the at-risk threshold minutes remain; exact cutoff is AT_RISK.
- `BREACHED`: evaluation/completion occurs after cutoff.

The engine evaluates completed requests at completion and open requests at `updated_at`. The local business-date cutoff is converted from the configured IANA timezone to UTC.

## SLA

`sla_deadline = received_timestamp + sla_minutes`. Completed requests are classified `COMPLETED_WITHIN_SLA` or `COMPLETED_LATE`; open requests are `WITHIN_SLA`, `APPROACHING_SLA`, or `SLA_BREACHED`. Cancelled/rejected requests are `NOT_APPLICABLE`. The approaching window is the smaller of 30 minutes and 20% of the applicable SLA.

## Pending and aging

`PENDING`, `IN_PROGRESS`, and `ON_HOLD` are open. Ages use `updated_at - received_timestamp`, clamped at zero, and fall into `< 30 minutes`, `30–60 minutes`, `1–2 hours`, `2–4 hours`, `4–8 hours`, or `8+ hours`.

## Exceptions and escalation

Rules cover cutoff risk/breach, SLA breach, missing or invalid SSI validation, missing owner, high-priority pending, incomplete requests, and data-quality issues. A request with three or more concurrent triggers receives `REPEATED_ESCALATION`. Critical/High exceptions are escalated. See [exception_management.md](exception_management.md).

