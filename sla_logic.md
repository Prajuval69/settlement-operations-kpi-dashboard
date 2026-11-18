# SLA Logic

`reference_sla_rules.csv` stores a fictional SLA for every request-type/priority combination. `sla_deadline` is receipt plus configured minutes.

- Completed: duration ends at completion; state is `COMPLETED_WITHIN_SLA` or `COMPLETED_LATE`.
- Open: duration ends at `updated_at`; state is `WITHIN_SLA`, `APPROACHING_SLA`, or `SLA_BREACHED`.
- Cancelled/rejected: `NOT_APPLICABLE`.

`processing_minutes`, `sla_remaining_minutes`, `sla_breach_flag`, and `sla_approaching_flag` are exported. Validation rejects non-positive SLAs and completion/update timestamps before receipt; duration calculations are also clamped to prevent negative analytical values.

