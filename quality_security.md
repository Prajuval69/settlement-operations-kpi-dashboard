# Quality & Security

The project uses generated identifiers and fictional clients/owners only. It contains no credentials, secrets, real customer data, account details, live endpoints, or production-system connections.

Pre-enrichment validation checks required columns, unique request IDs, allowed currencies/request types/priorities/statuses/owners, positive SLAs, valid `HH:MM` cutoffs, parseable timestamps, and non-negative event ordering. Post-enrichment validation checks non-negative durations and complete risk classifications. SQLite integrity, output counts, deterministic generation, and boundary rules are tested.

`.gitignore` excludes environments, caches, logs, IDE metadata, and dashboard dependencies. The generated SQLite database contains synthetic data only. No `.pbix` is claimed or fabricated.

