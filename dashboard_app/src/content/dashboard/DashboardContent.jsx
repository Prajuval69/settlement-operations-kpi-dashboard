import React from "react";
import { Chart, DataComponent, DataTable, Filters, MetricCard, Section, useDataApp, useDashboardTabs } from "../../data-app-public.jsx";
import "./dashboard.css";

const tabs = [
  { id: "overview", label: "Operations overview", filterIds: ["currency", "market", "request_type", "priority", "owner"] },
  { id: "risk", label: "Cutoff & SLA risk", filterIds: ["currency", "market", "request_type", "priority", "owner"] },
  { id: "exceptions", label: "Exceptions & escalations", filterIds: ["currency", "market", "owner"] },
  { id: "workload", label: "Workload & performance", filterIds: ["currency", "market", "request_type", "priority", "owner"] },
];

const integer = new Intl.NumberFormat();
const decimal = new Intl.NumberFormat(undefined, { maximumFractionDigits: 1 });
const percent = value => `${decimal.format(value)}%`;
const bool = value => value === true || value === "True" || value === 1 || value === "1";

function group(rows, field, calculations) {
  const groups = new Map();
  rows.forEach(row => {
    const key = row[field] ?? "UNASSIGNED";
    if (!groups.has(key)) groups.set(key, { [field]: key });
    const result = groups.get(key);
    Object.entries(calculations).forEach(([name, calculator]) => {
      result[name] = (result[name] ?? 0) + Number(calculator(row) || 0);
    });
  });
  return [...groups.values()];
}

function dailyRows(rows) {
  return group(rows, "request_date", {
    totalRequests: () => 1,
    completedRequests: row => row.status === "COMPLETED" ? 1 : 0,
    pendingRequests: row => bool(row.is_pending) ? 1 : 0,
    slaBreaches: row => bool(row.sla_breach_flag) ? 1 : 0,
    cutoffRisk: row => ["WATCH", "AT_RISK"].includes(row.cutoff_risk) ? 1 : 0,
    cutoffBreaches: row => row.cutoff_risk === "BREACHED" ? 1 : 0,
  }).sort((a, b) => a.request_date.localeCompare(b.request_date));
}

function MetricGrid({ rows, exceptions }) {
  const total = rows.length;
  const completed = rows.filter(row => row.status === "COMPLETED").length;
  const pending = rows.filter(row => bool(row.is_pending)).length;
  const eligible = rows.filter(row => !["CANCELLED", "REJECTED"].includes(row.status));
  const sla = eligible.filter(row => bool(row.sla_breach_flag)).length;
  const risk = rows.filter(row => ["WATCH", "AT_RISK"].includes(row.cutoff_risk)).length;
  const values = [
    ["metric-total", "Total requests", integer.format(total), "operations"],
    ["metric-completed", "Completed", integer.format(completed), "operations"],
    ["metric-pending", "Pending", integer.format(pending), "operations"],
    ["metric-completion", "Completion rate", percent(total ? completed / total * 100 : 0), "operations"],
    ["metric-sla", "SLA breach rate", percent(eligible.length ? sla / eligible.length * 100 : 0), "operations"],
    ["metric-risk", "Cutoff risk", integer.format(risk), "operations"],
    ["metric-exceptions", "Exceptions", integer.format(exceptions.length), "exceptions"],
  ];
  return <div className="kpi-grid">
    {values.map(([id, title, value, queryId]) => <MetricCard key={id} id={id} title={title}
      queryId={queryId} value={value} sourceRows={queryId === "exceptions" ? exceptions : rows}
      displayRows={[{ value }]} />)}
  </div>;
}

function ChartCard({ id, queryId, title, description, rows, sourceRows, spec, chartProps, height = 270 }) {
  return <DataComponent variant="card" id={id} queryId={queryId} title={title} kind="chart"
    chart={spec} description={description} displayRows={rows} sourceRows={sourceRows}>
    {rows.length ? <Chart spec={spec} rows={rows} height={height} {...chartProps(id)} />
      : <p className="empty-state">No records match this view.</p>}
  </DataComponent>;
}

function Overview({ operations, exceptions, chartProps }) {
  const trend = dailyRows(operations);
  const statuses = group(operations, "status", { requests: () => 1 }).sort((a, b) => b.requests - a.requests);
  const currencies = group(operations, "currency", { requests: () => 1 }).sort((a, b) => b.requests - a.requests);
  return <>
    <MetricGrid rows={operations} exceptions={exceptions} />
    <Section id="overview-trends" title="Daily operating flow" columns={2} spacing="after-metrics">
      <ChartCard id="daily-trend" queryId="operations" title="Request volume and disposition"
        description="Daily counts recomputed from the currently filtered request population."
        rows={trend} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "line", x: "request_date", y: "totalRequests", fields: ["totalRequests", "completedRequests", "pendingRequests"], showLegend: true, startAtZero: true }} />
      <ChartCard id="status-distribution" queryId="operations" title="Status distribution"
        rows={statuses} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "horizontalBar", x: "status", y: "requests", startAtZero: true, showLegend: false }} />
    </Section>
    <Section id="overview-currency" title="Portfolio mix" spacing="content">
      <ChartCard id="currency-volume" queryId="operations" title="Request volume by currency"
        rows={currencies} sourceRows={operations} chartProps={chartProps} height={250}
        spec={{ type: "bar", x: "currency", y: "requests", startAtZero: true, showLegend: false }} />
    </Section>
  </>;
}

function Risk({ operations, chartProps }) {
  const currency = group(operations, "currency", {
    cutoffRisk: row => ["WATCH", "AT_RISK"].includes(row.cutoff_risk) ? 1 : 0,
    cutoffBreaches: row => row.cutoff_risk === "BREACHED" ? 1 : 0,
    slaBreaches: row => bool(row.sla_breach_flag) ? 1 : 0,
  }).sort((a, b) => b.cutoffBreaches - a.cutoffBreaches);
  const requestTypes = group(operations, "request_type", {
    slaBreaches: row => bool(row.sla_breach_flag) ? 1 : 0,
    requests: () => 1,
  }).map(row => ({ ...row, slaBreachRatePct: row.requests ? row.slaBreaches / row.requests * 100 : 0 }));
  const trend = dailyRows(operations);
  const detail = operations.filter(row => bool(row.is_pending) || bool(row.sla_breach_flag) || row.cutoff_risk !== "LOW")
    .sort((a, b) => Number(a.minutes_to_cutoff) - Number(b.minutes_to_cutoff));
  return <>
    <Section id="risk-summary" title="Where cutoff and SLA pressure is concentrated" columns={2} spacing="none">
      <ChartCard id="currency-risk" queryId="operations" title="Risk events by currency"
        rows={currency} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "bar", x: "currency", y: "cutoffRisk", fields: ["cutoffRisk", "cutoffBreaches", "slaBreaches"], showLegend: true, startAtZero: true }} />
      <ChartCard id="sla-by-request-type" queryId="operations" title="SLA breach rate by request type"
        rows={requestTypes} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "horizontalBar", x: "request_type", y: "slaBreachRatePct", yLabel: "SLA breach rate (%)", startAtZero: true, showLegend: false, valueDecimals: 1 }} />
    </Section>
    <Section id="risk-history" title="Risk trajectory" spacing="content">
      <ChartCard id="risk-trend" queryId="operations" title="Daily cutoff and SLA events"
        rows={trend} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "line", x: "request_date", y: "cutoffRisk", fields: ["cutoffRisk", "cutoffBreaches", "slaBreaches"], showLegend: true, startAtZero: true }} />
    </Section>
    <Section id="risk-queue-section" title="Operational risk queue" spacing="content">
      <DataComponent variant="card" id="risk-detail" queryId="operations" kind="table"
        title="Requests requiring review" description="Pending, cutoff-risk, cutoff-breached, or SLA-breached records in the filtered population."
        displayRows={detail} sourceRows={operations}>
        <DataTable rows={detail} rowKey="request_id" columns={[
          { key: "request_id", label: "Request", presentation: "identity" }, { key: "currency", label: "Currency" },
          { key: "market", label: "Market" }, { key: "owner", label: "Owner" },
          { key: "priority", label: "Priority", presentation: "status" }, { key: "cutoff_time", label: "Cutoff" },
          { key: "minutes_to_cutoff", label: "Minutes remaining" }, { key: "cutoff_risk", label: "Cutoff risk", presentation: "status" },
          { key: "sla_status", label: "SLA status", presentation: "status" }, { key: "sla_deadline", label: "SLA deadline" },
        ]} />
      </DataComponent>
    </Section>
  </>;
}

function Exceptions({ exceptions, chartProps }) {
  const severity = group(exceptions, "severity", { exceptions: () => 1 }).sort((a, b) => b.exceptions - a.exceptions);
  const types = group(exceptions, "exception_type", { exceptions: () => 1 }).sort((a, b) => b.exceptions - a.exceptions);
  const aging = exceptions.filter(row => row.status === "OPEN").map(row => ({ ...row,
    aging_bucket: Number(row.exception_age_minutes) < 60 ? "< 1 hour" : Number(row.exception_age_minutes) < 240 ? "1–4 hours" : Number(row.exception_age_minutes) < 480 ? "4–8 hours" : "8+ hours" }));
  const agingSummary = group(aging, "aging_bucket", { exceptions: () => 1 });
  const trend = group(exceptions, "request_date", {
    exceptions: () => 1, escalations: row => bool(row.is_escalated) ? 1 : 0,
  }).sort((a, b) => a.request_date.localeCompare(b.request_date));
  return <>
    <Section id="exception-summary" title="Exception profile" columns={2} spacing="none">
      <ChartCard id="exceptions-by-severity" queryId="exceptions" title="Exceptions by severity"
        rows={severity} sourceRows={exceptions} chartProps={chartProps}
        spec={{ type: "bar", x: "severity", y: "exceptions", startAtZero: true, showLegend: false }} />
      <ChartCard id="exceptions-by-type" queryId="exceptions" title="Exceptions by type"
        rows={types} sourceRows={exceptions} chartProps={chartProps}
        spec={{ type: "horizontalBar", x: "exception_type", y: "exceptions", startAtZero: true, showLegend: false }} />
    </Section>
    <Section id="exception-diagnostics" title="Escalation and aging" columns={2} spacing="content">
      <ChartCard id="exception-trend" queryId="exceptions" title="Daily exceptions and escalations"
        rows={trend} sourceRows={exceptions} chartProps={chartProps}
        spec={{ type: "line", x: "request_date", y: "exceptions", fields: ["exceptions", "escalations"], showLegend: true, startAtZero: true }} />
      <ChartCard id="exception-aging" queryId="exceptions" title="Unresolved exception aging"
        rows={agingSummary} sourceRows={aging} chartProps={chartProps}
        spec={{ type: "bar", x: "aging_bucket", y: "exceptions", startAtZero: true, showLegend: false }} />
    </Section>
    <Section id="exception-queue" title="Exception action queue" spacing="content">
      <DataComponent variant="card" id="exception-detail" queryId="exceptions" kind="table"
        title="Exceptions and escalations" displayRows={exceptions} sourceRows={exceptions}>
        <DataTable rows={exceptions} rowKey="exception_id" columns={[
          { key: "exception_id", label: "Exception", presentation: "identity" }, { key: "request_id", label: "Request" },
          { key: "exception_type", label: "Type" }, { key: "severity", label: "Severity", presentation: "status" },
          { key: "owner", label: "Owner" }, { key: "detected_at", label: "Detected" },
          { key: "status", label: "Status", presentation: "status" }, { key: "escalation_reason", label: "Escalation reason" },
        ]} />
      </DataComponent>
    </Section>
  </>;
}

function Workload({ operations, chartProps }) {
  const owners = group(operations, "owner", {
    totalRequests: () => 1, pendingRequests: row => bool(row.is_pending) ? 1 : 0,
    completedRequests: row => row.status === "COMPLETED" ? 1 : 0,
    processingMinutes: row => row.status === "COMPLETED" ? Number(row.processing_minutes) : 0,
  }).map(row => ({ ...row,
    completionRatePct: row.totalRequests ? row.completedRequests / row.totalRequests * 100 : 0,
    averageProcessingMinutes: row.completedRequests ? row.processingMinutes / row.completedRequests : 0,
  })).sort((a, b) => b.pendingRequests - a.pendingRequests);
  const requestTypes = group(operations, "request_type", { requests: () => 1 }).sort((a, b) => b.requests - a.requests);
  const channels = group(operations, "source_channel", { requests: () => 1 }).sort((a, b) => b.requests - a.requests);
  return <>
    <Section id="workload-distribution" title="Capacity and assignment" columns={2} spacing="none">
      <ChartCard id="owner-workload" queryId="operations" title="Requests and pending workload by owner"
        rows={owners} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "bar", x: "owner", y: "totalRequests", fields: ["totalRequests", "pendingRequests"], showLegend: true, startAtZero: true }} />
      <ChartCard id="owner-performance" queryId="operations" title="Completion rate by owner"
        rows={owners} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "horizontalBar", x: "owner", y: "completionRatePct", yLabel: "Completion rate (%)", startAtZero: true, showLegend: false, valueDecimals: 1 }} />
    </Section>
    <Section id="workload-mix" title="Request mix" columns={2} spacing="content">
      <ChartCard id="request-type-volume" queryId="operations" title="Volume by request type"
        rows={requestTypes} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "horizontalBar", x: "request_type", y: "requests", startAtZero: true, showLegend: false }} />
      <ChartCard id="source-channel-volume" queryId="operations" title="Source-channel distribution"
        rows={channels} sourceRows={operations} chartProps={chartProps}
        spec={{ type: "bar", x: "source_channel", y: "requests", startAtZero: true, showLegend: false }} />
    </Section>
    <Section id="owner-table-section" title="Owner performance detail" spacing="content">
      <DataComponent variant="card" id="owner-performance-table" queryId="operations" kind="table"
        title="Workload scorecard" displayRows={owners} sourceRows={operations}>
        <DataTable rows={owners} searchable={false} columns={[
          { key: "owner", label: "Owner", presentation: "identity" }, { key: "totalRequests", label: "Requests" },
          { key: "pendingRequests", label: "Pending" }, { key: "completedRequests", label: "Completed" },
          { key: "completionRatePct", label: "Completion rate (%)" }, { key: "averageProcessingMinutes", label: "Avg processing minutes" },
        ]} />
      </DataComponent>
    </Section>
  </>;
}

export function DashboardContent() {
  const { activeTabId } = useDashboardTabs(tabs);
  const { snapshot, appTitle, setAppTitle, reviewedRows, chartProps, queries, filters, setFilter } = useDataApp();
  const operations = reviewedRows("operations", ["request_date"]);
  const exceptions = reviewedRows("exceptions", ["request_date"]);
  const tab = tabs.some(item => item.id === activeTabId) ? activeTabId : "overview";
  return <article className="settlement-dashboard">
    <header className="dashboard-heading">
      <div>
        <p className="dashboard-kicker">Synthetic portfolio simulation · as of 19 Sep 2026 04:00 UTC</p>
        <h1 id="settlement-dashboard-title" contentEditable suppressContentEditableWarning
          onBlur={event => setAppTitle(event.currentTarget.textContent || appTitle)}>{appTitle}</h1>
      </div>
      <p className="dashboard-disclaimer">Demo assumptions only—no real bank systems, client data, or official market cutoffs.</p>
    </header>
    <Filters sticky filters={snapshot.filters.filter(filter => tabs.find(item => item.id === tab).filterIds.includes(filter.id))}
      queries={queries} values={filters} onChange={setFilter} />
    {tab === "overview" && <Overview operations={operations} exceptions={exceptions} chartProps={chartProps} />}
    {tab === "risk" && <Risk operations={operations} chartProps={chartProps} />}
    {tab === "exceptions" && <Exceptions exceptions={exceptions} chartProps={chartProps} />}
    {tab === "workload" && <Workload operations={operations} chartProps={chartProps} />}
  </article>;
}
