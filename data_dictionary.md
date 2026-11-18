# Data Dictionary

## FactOperations

Identity/dimensions: `request_id`, `request_date`, `client_id`, `market`, `country`, `currency`, `request_type`, `source_channel`, `priority`, `owner`, `status`, `ssi_validation_status`.

Timestamps/configuration: `received_timestamp`, `completion_timestamp`, `created_at`, `updated_at`, `evaluation_timestamp`, `cutoff_time`, `cutoff_datetime_utc`, `timezone`, `warning_threshold_minutes`, `at_risk_threshold_minutes`, `sla_minutes`, `sla_deadline`.

Derived measures/flags: `minutes_to_cutoff`, `cutoff_risk`, `cutoff_risk_flag`, `cutoff_breach_flag`, `processing_minutes`, `sla_remaining_minutes`, `sla_status`, `sla_breach_flag`, `sla_approaching_flag`, `is_pending`, `age_minutes`, `aging_bucket`, `exception_flag`, `is_escalated`, `escalation_reason`.

## FactExceptions

`exception_id`, `request_id`, `request_date`, `exception_date`, `currency`, `market`, `exception_type`, `severity`, `severity_rank`, `detected_at`, `status`, `owner`, `escalation_reason`, `is_escalated`, `escalation_timestamp`, `escalation_owner`, `resolution_timestamp`, `exception_age_minutes`.

## Dimensions

`DimDate`, `DimCurrency`, `DimMarket`, `DimOwner`, and `DimRequestType` are documented in [powerbi_data_model.md](powerbi_data_model.md). Boolean CSV values load as TRUE/FALSE; timestamp strings are ISO-like UTC outputs.

