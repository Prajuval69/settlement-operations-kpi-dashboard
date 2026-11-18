# Power BI Data Model

Load CSVs from `outputs/powerbi/`. Set date/timestamp columns to Date/DateTime, flags to True/False, counts/durations to numeric, and percentages to Decimal Number.

## Tables and grain

- `FactOperations`: one row per request (`request_id`).
- `FactExceptions`: one row per exception (`exception_id`); many exceptions can relate to one request.
- `DimDate`: one row per calendar date from 2026-06-01 through 2026-09-18.
- `DimCurrency`: one row per currency with fictional cutoff configuration.
- `DimMarket`: one row per market.
- `DimOwner`: one row per synthetic owner plus `UNASSIGNED`.
- `DimRequestType`: one row per request type.

## Relationships

Use single-direction, one-to-many relationships from dimensions to facts:

```text
DimDate[date]             1 ── * FactOperations[request_date]   (active)
DimDate[date]             1 ── * FactExceptions[exception_date] (active)
DimCurrency[currency]     1 ── * FactOperations[currency]
DimCurrency[currency]     1 ── * FactExceptions[currency]
DimMarket[market]         1 ── * FactOperations[market]
DimMarket[market]         1 ── * FactExceptions[market]
DimOwner[owner]           1 ── * FactOperations[owner]
DimOwner[owner]           1 ── * FactExceptions[owner]
DimRequestType[request_type] 1 ── * FactOperations[request_type]
```

Optionally add an inactive `DimDate[date] -> FactOperations[completion date]` relationship after deriving a completion date in Power Query. Do not relate facts directly or enable bidirectional filters unless a specific analysis proves it necessary.

## Recommended model settings

- Mark `DimDate` as the date table using `DimDate[date]`.
- Sort `month_name` by `month_number`; sort severity by `severity_rank` where used.
- Hide technical flags/foreign keys from report view after measures are built.
- Format rate measures as percentages, duration measures as one decimal minute, and counts as whole numbers.
- Keep fictional cutoff/SLA configuration visible in source notes; it is assumption data, not governed production reference data.

See [dax_measures.md](dax_measures.md) and [dashboard_specification.md](dashboard_specification.md).

