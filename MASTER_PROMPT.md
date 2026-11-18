# MASTER PROMPT — Settlement Operations Cutoff & KPI Monitoring Dashboard

## Objective

Build a complete, production-quality, resume-ready portfolio project called:

**Settlement Operations Cutoff & KPI Monitoring Dashboard**

The project simulates a daily financial-operations monitoring environment using synthetic data. It should identify requests approaching configured currency settlement cutoffs, monitor SLA performance, surface exceptions and escalations, calculate operational KPIs, analyze workload, and produce dashboard-ready data and documentation for Power BI.

This is a portfolio simulation only. Use synthetic data and clearly state that all cutoff times, workflows, thresholds, and operational rules are fictional/demo assumptions and are not official policies of any bank, market, custodian, or financial institution.

---

## First Step — Inspect the Workspace

Before implementing anything:

1. Inspect the complete workspace.
2. Read every `.md` file supplied with this project.
3. Treat this file and the supporting specifications as the source of truth.
4. Identify existing files before creating new ones.
5. Reuse useful existing code where appropriate.
6. Do not delete unrelated user files.

Do not stop at scaffolding.

---

## Preferred Technology

Use a practical analytics/data-engineering stack:

- Python 3.11+
- Pandas
- NumPy
- SQLite
- SQL
- pytest
- Power BI-ready CSV/SQL datasets
- DAX documentation

Optional:
- Pydantic
- openpyxl
- Plotly/matplotlib for supplementary static reporting

Do not introduce unnecessary frameworks.

---

# 1. Synthetic Operations Data

Generate a realistic synthetic daily operations dataset.

Include fields such as:

- request_id
- request_date
- received_timestamp
- client_id
- market
- country
- currency
- request_type
- source_channel
- priority
- cutoff_time
- timezone
- SLA_minutes
- owner
- status
- completion_timestamp
- exception_flag
- escalation_reason
- SSI_validation_status
- created_at
- updated_at

Generate enough records across multiple business dates to support trend analysis.

Intentionally include:

- normal completed requests
- pending requests
- overdue requests
- requests near cutoff
- cutoff breaches
- SLA breaches
- high-priority requests
- exceptions
- escalations
- incomplete SSI statuses
- uneven owner workload

Use a fixed random seed.

---

# 2. Currency Cutoff Reference Data

Create a separate reference table containing synthetic cutoff assumptions.

Fields should include:

- currency
- market
- timezone
- cutoff_time
- warning_threshold_minutes
- business_day_flag

Use several currencies.

Clearly document that these cutoff values are synthetic demonstration values and must not be interpreted as actual market or bank cutoffs.

The system must support changing cutoff times through configuration/reference data rather than hardcoding them throughout the code.

---

# 3. SLA Reference Data

Create configurable SLA rules.

Possible dimensions:

- request_type
- priority
- SLA_minutes

The system should determine the appropriate SLA based on request characteristics.

Document the assumptions.

---

# 4. Cutoff-Risk Engine

Calculate the operational risk associated with each request.

Required calculations:

### Minutes Until Cutoff

Calculate the time between the current/request processing timestamp and the configured cutoff.

Handle:

- before cutoff
- exactly at cutoff
- after cutoff
- date rollover
- timezone conversion

### Cutoff-Risk Flag

Create categories such as:

- LOW
- WATCH
- AT_RISK
- BREACHED

Thresholds must be configurable.

For example:

- LOW: comfortably before cutoff
- WATCH: within warning window
- AT_RISK: very close to cutoff
- BREACHED: cutoff has passed without completion

These are project-specific definitions.

---

# 5. SLA Monitoring

Calculate:

- SLA deadline
- elapsed processing time
- SLA status
- SLA breach
- remaining SLA time

Classify requests into useful operational states such as:

- Within SLA
- Approaching SLA
- SLA Breached
- Completed

Handle completed and pending requests separately.

---

# 6. Exception & Escalation Logic

Identify operational exceptions such as:

- missing SSI validation
- invalid/incomplete request
- cutoff risk
- cutoff breach
- SLA breach
- high-priority pending request
- repeated escalation
- missing owner

Each exception should include:

- exception_id
- request_id
- exception_type
- severity
- detected_at
- status
- owner
- escalation_reason
- resolution_timestamp

Use configurable severity logic.

Do not claim the severity model is an industry-standard banking framework.

---

# 7. Aging Analysis

For pending requests calculate age.

Create configurable aging buckets, for example:

- < 30 minutes
- 30–60 minutes
- 1–2 hours
- 2–4 hours
- 4–8 hours
- 8+ hours

The implementation should avoid negative ages caused by timestamp inconsistencies.

---

# 8. Operational KPIs

Calculate daily and weekly KPIs.

At minimum:

### Volume
- total request volume
- completed volume
- pending volume
- cancelled/rejected volume

### Completion
- completion rate
- average processing time
- median processing time

### SLA
- SLA breach count
- SLA breach rate
- approaching-SLA count

### Cutoff
- cutoff-risk count
- cutoff-breach count
- cutoff-breach rate
- requests by currency nearing cutoff

### Exceptions
- exception count
- exception rate
- critical/high exception count
- escalation count
- unresolved exception count

### Workload
- requests per owner
- pending requests per owner
- high-priority requests per owner

### Data Quality
- incomplete SSI count
- invalid request count
- data-quality exception rate

---

# 9. Daily Operations Reporting

Create a reporting dataset that supports a daily operations review.

It should answer:

- How many requests were received?
- How many were completed?
- What remains pending?
- Which requests are near cutoff?
- Which requests breached cutoff?
- Which requests breached SLA?
- Which currencies have the most risk?
- Which owners have the largest pending workload?
- What exceptions require escalation?
- What changed compared with the previous day?

Where meaningful, include day-over-day comparison metrics.

---

# 10. SQL Layer

Use SQLite or SQL files for operational analysis.

Include queries for:

- daily volume
- pending queue
- cutoff-risk queue
- SLA breaches
- exceptions
- currency-level performance
- owner workload
- daily KPI aggregation

Use sensible indexes.

---

# 11. Power BI Data Model

Prepare clean datasets suitable for Power BI.

Prefer a star-schema-oriented design where practical.

Potential tables:

### FactOperations
One row per operational request.

### FactExceptions
One row per exception.

### DimDate
Calendar/date dimension.

### DimCurrency
Currency reference.

### DimMarket
Market reference.

### DimOwner
Operations owner reference.

### DimRequestType
Request type reference.

Document relationships.

Avoid unnecessary many-to-many relationships.

---

# 12. Power BI Measures

Provide documented DAX measures for:

- Total Requests
- Completed Requests
- Pending Requests
- Completion Rate
- Average Processing Time
- Median Processing Time
- SLA Breaches
- SLA Breach Rate
- Cutoff Risk Requests
- Cutoff Breaches
- Exception Count
- Escalation Count
- Unresolved Exceptions
- High Priority Pending
- Owner Workload

Where useful, include:

- previous day volume
- previous week volume
- day-over-day change
- rolling 7-day volume

Do not create fake `.pbix` files.

If Power BI Desktop is unavailable, create the strongest Power BI-ready assets possible:
- clean datasets
- data model documentation
- DAX measures
- dashboard specification
- optional theme/configuration assets if useful

If actual Power BI automation is available, use it only if it genuinely works.

---

# 13. Dashboard Specification

Design four dashboard pages.

## Page 1 — Operations Overview

Show:

- total requests
- completion rate
- pending requests
- SLA breach rate
- cutoff-risk count
- exception count

Visuals:
- KPI cards
- daily volume trend
- completion trend
- status distribution

## Page 2 — Cutoff & SLA Risk

Show:

- requests nearing cutoff
- cutoff breaches
- SLA breaches
- risk by currency
- risk by market

Include an operational risk table with:

- request ID
- currency
- owner
- cutoff time
- minutes remaining
- SLA status
- priority
- risk level

## Page 3 — Exceptions & Escalations

Show:

- exceptions by severity
- exceptions by type
- escalation volume
- unresolved exceptions
- exception aging
- exception trend

## Page 4 — Workload & Performance

Show:

- owner workload
- pending workload
- average processing time
- completion rate by owner
- volume by request type
- source-channel distribution

The dashboard specification must describe filters/slicers and expected interactions.

---

# 14. Optional Static Preview

If practical, generate a static HTML or image preview of the dashboard using Python.

Do not pretend this is a Power BI report.

The actual dashboard-ready datasets and DAX/model documentation remain the primary deliverables if Power BI Desktop cannot be automated.

---

# 15. Testing

Create comprehensive pytest coverage.

Test:

- cutoff calculation
- exact cutoff boundary
- after-cutoff behavior
- timezone/date handling
- warning thresholds
- risk classification
- SLA deadline calculation
- SLA breach calculation
- completion duration
- aging buckets
- exception generation
- severity classification
- KPI calculations
- daily aggregation
- owner workload
- deterministic synthetic data generation

Include negative and boundary tests.

---

# 16. Data Quality

Validate:

- required columns
- valid timestamps
- valid currencies
- valid statuses
- valid priorities
- valid owners
- non-negative processing times
- valid SLA values
- valid cutoff times

Do not allow malformed data to silently produce misleading KPIs.

---

# 17. Configuration

Centralize configuration for:

- cutoff warning threshold
- at-risk threshold
- SLA thresholds
- aging buckets
- severity rules
- synthetic data seed
- reporting date range

Avoid hardcoded business logic across multiple modules.

---

# 18. Outputs

Generate clean outputs such as:

- `operations.csv`
- `exceptions.csv`
- `daily_kpis.csv`
- `weekly_kpis.csv`
- `cutoff_risk_queue.csv`
- `sla_breach_queue.csv`
- `owner_workload.csv`
- `currency_performance.csv`
- `dashboard_fact_operations.csv`
- `dashboard_fact_exceptions.csv`
- dimension/reference datasets
- SQLite database

Avoid unnecessary duplicates.

---

# 19. Documentation

Create:

- README
- architecture
- business rules
- data dictionary
- database schema
- KPI specification
- cutoff logic
- SLA logic
- Power BI data model
- DAX measures
- dashboard specification
- testing strategy
- setup/run guide
- data-quality/security notes
- resume alignment notes

Documentation must match the actual implementation.

---

# 20. Repository Hygiene

Do not include:

- secrets
- credentials
- `.env` files with secrets
- IDE metadata
- caches
- virtual environments
- temporary files
- unnecessary generated artifacts
- real financial/customer data

Include `.gitignore`.

---

# 21. Final Verification

Before completion:

1. Run the complete data pipeline.
2. Run all tests.
3. Fix failures.
4. Verify KPI calculations.
5. Verify cutoff calculations.
6. Verify SLA calculations.
7. Verify exception queues.
8. Verify SQLite database.
9. Verify Power BI-ready datasets.
10. Verify DAX documentation.
11. Verify dashboard specification.
12. Verify deterministic data generation.
13. Clean temporary files.
14. Confirm no secrets.
15. Confirm synthetic-data disclaimer.
16. Confirm documentation accurately describes what was actually built.

Do not claim a `.pbix` exists unless a valid Power BI file was genuinely created.

## Final Deliverable

Deliver a clean GitHub-ready project that demonstrates practical skills in operations analytics, settlement/cutoff monitoring, SLA management, exception management, SQL, Python automation, KPI reporting, and Power BI data preparation.
