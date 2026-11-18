-- All values queried here come from the synthetic portfolio dataset.

-- Daily volume and completion
SELECT request_date,
       COUNT(*) AS total_requests,
       SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_requests,
       SUM(is_pending) AS pending_requests
FROM operations
GROUP BY request_date
ORDER BY request_date;

-- Pending queue
SELECT * FROM vw_pending_queue
ORDER BY priority DESC, age_minutes DESC;

-- Cutoff-risk queue
SELECT * FROM vw_cutoff_risk_queue
ORDER BY CASE cutoff_risk WHEN 'BREACHED' THEN 1 WHEN 'AT_RISK' THEN 2 WHEN 'WATCH' THEN 3 ELSE 4 END,
         minutes_to_cutoff;

-- SLA breaches
SELECT * FROM vw_sla_breach_queue
ORDER BY sla_remaining_minutes;

-- Open exceptions
SELECT exception_id, request_id, exception_type, severity, owner, detected_at, escalation_reason
FROM exceptions
WHERE status = 'OPEN'
ORDER BY severity_rank DESC, exception_age_minutes DESC;

-- Currency-level performance
SELECT * FROM vw_currency_performance
ORDER BY cutoff_breach_count DESC, sla_breach_count DESC;

-- Owner workload
SELECT * FROM vw_owner_workload
ORDER BY pending_requests DESC, total_requests DESC;

-- Persisted daily KPI aggregation
SELECT * FROM daily_kpis ORDER BY request_date;

