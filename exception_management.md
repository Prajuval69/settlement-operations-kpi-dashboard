# Exception & Escalation Management

`FactExceptions` has one row per generated exception, so one request can create several rows. Types are `CUTOFF_RISK`, `CUTOFF_BREACH`, `SLA_BREACH`, `MISSING_SSI_VALIDATION`, `MISSING_OWNER`, `HIGH_PRIORITY_PENDING`, `INCOMPLETE_REQUEST`, `DATA_QUALITY`, and `REPEATED_ESCALATION`.

Demo severity mapping:

| Severity | Types |
| --- | --- |
| Critical | CUTOFF_BREACH |
| High | SLA_BREACH, MISSING_OWNER, HIGH_PRIORITY_PENDING, REPEATED_ESCALATION |
| Medium | CUTOFF_RISK, MISSING_SSI_VALIDATION, DATA_QUALITY |
| Low | INCOMPLETE_REQUEST |

Critical/High records are escalated. Open operational requests keep applicable exceptions open; missing owner/SSI/data-quality conditions stay open until corrected. Resolved exception records retain resolution timestamps. This mapping is not an industry or bank standard.

