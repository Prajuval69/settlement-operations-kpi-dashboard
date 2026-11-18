# Dashboard Specification

The implemented dashboard is `dashboard_app/`. All views share Currency, Market, Request Type, Priority, and Owner filters where those fields exist; the Exceptions view uses Currency, Market, and Owner. Selections recalculate every visible card/chart/table in scope, and Clear all restores the complete population.

## Operations overview

Cards: total, completed, pending, completion rate, SLA breach rate, cutoff risk, exceptions. Visuals: daily total/completed/pending trend, status distribution, and currency volume.

## Cutoff & SLA risk

Visuals: risk/breach/SLA events by currency, SLA breach rate by request type, daily risk trajectory. The action queue includes request, currency, market, owner, priority, cutoff, minutes remaining, cutoff risk, SLA status, and deadline.

## Exceptions & escalations

Visuals: severity, type, daily exception/escalation trend, unresolved aging. The action table includes exception/request IDs, type, severity, owner, detection, status, and escalation reason.

## Workload & performance

Visuals: total and pending workload by owner, completion rate by owner, volume by request type, and source-channel distribution. A scorecard shows owner totals, pending/completed counts, completion rate, and average completed-request processing minutes.

Charts support shared hover/legend/source actions, tables support search/sort/pagination, and the layout adapts to narrow screens. This is a local interactive preview, not a Power BI `.pbix`.

