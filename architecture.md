# Architecture

```text
Reference data ─┐
                ├─> deterministic generator ─> validation ─> cutoff/SLA/aging
Configuration ─┘                                      │
                                                     v
                                          exceptions & escalations
                                                     │
                          ┌──────────────────────────┴─────────────────────┐
                          v                                                v
                    KPI/reporting                                    SQLite layer
                          │                                                │
                          ├─ operational CSVs                              ├─ tables
                          ├─ Power BI star schema                          ├─ indexes
                          ├─ daily Markdown review                         └─ views/SQL
                          └─ interactive dashboard snapshot
```

`config.py` owns seed, reporting window, SLA warning threshold, terminal statuses, and aging buckets. `reference_data.py` owns fictional cutoff/SLA/owner/request-type assumptions. `generation.py` creates synthetic source records. `validation.py` blocks malformed inputs. `risk.py` applies timezone-aware cutoff, SLA, duration, and aging rules. `exceptions.py` creates one-to-many exception records. `kpis.py` aggregates operational measures. `database.py` builds and verifies SQLite. `pipeline.py` orchestrates and exports.

The dashboard uses the reviewed output snapshot in `dashboard_app/src/data.json`; it does not connect to live systems. The Power BI assets are CSV/model/DAX specifications only because no valid `.pbix` was created.

