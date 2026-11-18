# KPI Specification

Rates use safe division and return 0 only when the eligible denominator is zero.

- Volume: total, completed, pending, cancelled/rejected.
- Completion: completed / total, plus completed-request mean and median processing minutes.
- SLA: breach count and breach / eligible requests, where cancelled/rejected are excluded; approaching-SLA count.
- Cutoff: WATCH+AT_RISK count, BREACHED count, and breaches / all applicable requests.
- Exceptions: exception rows, distinct exception-bearing requests, request exception rate, Critical/High rows, escalations, unresolved rows.
- Data quality: incomplete SSI requests, distinct DATA_QUALITY requests, and DATA_QUALITY requests / total requests.
- Workload: request/pending/high-priority/completed counts and completion rate by owner.
- Trends: previous-day volume, day-over-day change/percent, rolling seven-business-day volume, previous-week volume, and week-over-week change.

Exception count can exceed request count because exceptions have a one-to-many grain. `exception_rate_pct` therefore uses distinct exception-bearing requests as its numerator.

