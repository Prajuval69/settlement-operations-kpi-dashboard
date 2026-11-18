# Cutoff Logic

`reference_currency_cutoffs.csv` contains one fictional row per currency with market, country, IANA timezone, local cutoff, warning threshold, at-risk threshold, and business-day flag. No cutoff is hardcoded in the risk engine.

For each request, `cutoff_datetime_utc` is built from `request_date + cutoff_time` in the configured timezone and converted to UTC. `minutes_to_cutoff` is cutoff minus the completion timestamp for completed requests, otherwise cutoff minus `updated_at`.

Boundary behavior is covered by tests: one minute before, exact cutoff, one minute after, completed after cutoff, cross-timezone conversion, and local-date construction. Exact cutoff is `AT_RISK`; any negative remainder is `BREACHED`.

These values are synthetic and must never be interpreted as official market or bank cutoffs.

