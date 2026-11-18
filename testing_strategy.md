# Testing Strategy

Run `pytest`. The suite covers:

- cutoff LOW/WATCH/AT_RISK/BREACHED boundaries, including exactly at cutoff and ±1 minute;
- timezone conversion for Tokyo/New York and local-date cutoff construction;
- completed-after-cutoff, completed-late, open approaching, and open breached SLA behavior;
- processing duration and all aging bucket boundaries, including negative-age protection;
- exception types, demo severity mapping, repeated escalation, and escalation flags;
- KPI counts/rates, owner workload, and zero-record behavior;
- fixed-seed determinism and multi-currency/type/owner coverage;
- invalid currency and completion-before-receipt rejection;
- end-to-end CSV, Power BI, manifest, SQLite view, row-count, and integrity checks.

The final verification also runs the full 1,920-row pipeline, compares key independent calculations, inspects every dashboard tab, exercises a currency filter and reset, checks browser console warnings/errors, and checks normal/mobile rendering.

