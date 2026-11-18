# Settlement Operations Cutoff & KPI Monitoring Dashboard

A complete synthetic-data portfolio project for monitoring operational requests against configurable currency cutoffs and SLAs. It generates reproducible request data, classifies cutoff/SLA risk, creates exception and escalation queues, calculates daily/weekly KPIs, persists an analytical SQLite model, exports a Power BI-ready star schema, and includes a four-page interactive dashboard.

> All records, clients, owners, cutoff times, SLAs, severity mappings, workflows, and thresholds are fictional demo assumptions. The project has no connection to real bank systems, production settlement data, or real client data.

## Live dashboard

[Open the interactive Settlement Operations dashboard](https://prajuval69.github.io/settlement-operations-kpi-dashboard/)

## Quick start

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m settlement_dashboard.pipeline
pytest
```

The pipeline writes reproducible assets to `outputs/`, including `settlement_operations.db`, operational queues, KPI tables, a daily Markdown review, and Power BI fact/dimension CSVs. The source-backed interactive dashboard is in `dashboard_app/`; its verified split build is `dashboard_app/dist/index.html` and must be served over HTTP.

## Project map

- `src/settlement_dashboard/` — generation, validation, cutoff/SLA, exception, KPI, database, and pipeline modules.
- `tests/` — unit, boundary, determinism, KPI, and end-to-end tests.
- `sql/operational_queries.sql` — operational analysis examples backed by SQLite views/tables.
- `outputs/` — generated datasets, report, manifest, and SQLite database.
- `outputs/powerbi/` — `FactOperations`, `FactExceptions`, and dimensions.
- `dashboard_app/` — four-tab interactive Data app built from reviewed synthetic outputs.

## Implemented capabilities

- 1,920 deterministic requests across 80 business days and eight currencies.
- Timezone-aware cutoff datetimes and LOW/WATCH/AT_RISK/BREACHED classification.
- Completed-vs-pending SLA assessment, remaining time, duration, and aging buckets.
- Multiple exceptions per request, configurable severity mapping, escalations, and resolution state.
- Daily/weekly KPIs, owner workload, currency performance, risk queues, and day-over-day/rolling metrics.
- SQLite tables, indexes, views, integrity verification, and operational SQL.
- Power BI-ready star schema and documented DAX measures; no fabricated `.pbix` file.
- Interactive Operations Overview, Cutoff & SLA Risk, Exceptions & Escalations, and Workload & Performance views.

See [setup_and_run.md](setup_and_run.md), [business_rules.md](business_rules.md), and [powerbi_data_model.md](powerbi_data_model.md).

