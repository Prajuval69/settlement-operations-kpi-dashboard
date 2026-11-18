# DAX Measures

These measures match the exported column names in `outputs/powerbi/`. Boolean CSV fields should be loaded as True/False. Exception Count is a row count; Exception Request Count is distinct requests with one or more exceptions.

```DAX
Total Requests =
COUNTROWS(FactOperations)

Completed Requests =
CALCULATE([Total Requests], FactOperations[status] = "COMPLETED")

Pending Requests =
CALCULATE([Total Requests], FactOperations[is_pending] = TRUE())

Cancelled / Rejected Requests =
CALCULATE(
    [Total Requests],
    FactOperations[status] IN {"CANCELLED", "REJECTED"}
)

Completion Rate =
DIVIDE([Completed Requests], [Total Requests])

Average Processing Minutes =
CALCULATE(
    AVERAGE(FactOperations[processing_minutes]),
    FactOperations[status] = "COMPLETED"
)

Median Processing Minutes =
CALCULATE(
    MEDIAN(FactOperations[processing_minutes]),
    FactOperations[status] = "COMPLETED"
)

SLA Eligible Requests =
CALCULATE(
    [Total Requests],
    NOT (FactOperations[status] IN {"CANCELLED", "REJECTED"})
)

SLA Breaches =
CALCULATE([Total Requests], FactOperations[sla_breach_flag] = TRUE())

SLA Breach Rate =
DIVIDE([SLA Breaches], [SLA Eligible Requests])

Approaching SLA =
CALCULATE([Total Requests], FactOperations[sla_approaching_flag] = TRUE())

Cutoff Risk Requests =
CALCULATE(
    [Total Requests],
    FactOperations[cutoff_risk] IN {"WATCH", "AT_RISK"}
)

Cutoff Breaches =
CALCULATE([Total Requests], FactOperations[cutoff_risk] = "BREACHED")

Cutoff Breach Rate =
DIVIDE([Cutoff Breaches], [Total Requests])

Exception Count =
COUNTROWS(FactExceptions)

Exception Request Count =
DISTINCTCOUNT(FactExceptions[request_id])

Exception Request Rate =
DIVIDE([Exception Request Count], [Total Requests])

Escalation Count =
CALCULATE([Exception Count], FactExceptions[is_escalated] = TRUE())

Unresolved Exceptions =
CALCULATE([Exception Count], FactExceptions[status] = "OPEN")

Critical / High Exceptions =
CALCULATE(
    [Exception Count],
    FactExceptions[severity] IN {"Critical", "High"}
)

High Priority Pending =
CALCULATE(
    [Total Requests],
    FactOperations[is_pending] = TRUE(),
    FactOperations[priority] IN {"HIGH", "CRITICAL"}
)

Owner Workload = [Total Requests]

Incomplete SSI Count =
CALCULATE(
    [Total Requests],
    FactOperations[ssi_validation_status] <> "VALID"
)

Previous Day Volume =
CALCULATE([Total Requests], DATEADD(DimDate[date], -1, DAY))

Day-over-Day Change =
[Total Requests] - [Previous Day Volume]

Day-over-Day Change % =
DIVIDE([Day-over-Day Change], [Previous Day Volume])

Previous Week Volume =
CALCULATE([Total Requests], DATEADD(DimDate[date], -7, DAY))

Rolling 7-Day Volume =
CALCULATE(
    [Total Requests],
    DATESINPERIOD(DimDate[date], MAX(DimDate[date]), -7, DAY)
)
```

Calendar-day time-intelligence measures above differ from the exported `daily_kpis.csv` rolling seven-business-day column. Use the version appropriate to the report label and do not compare them as though they share a denominator.
