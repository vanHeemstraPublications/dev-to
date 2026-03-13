---
title: "Scuderia Data Ep.11"
published: false
description: "Episode 11: Telemetry"
part: 11
tags: [azure, monitoring, databricks, observability]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-11.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 📡 Episode 11 — Telemetry (Monitoring, Observability & Alerting)

> *"An F1 car sends 300 data points per second back to the garage. If you're not monitoring your data platform with the same intensity, you're racing blind."*

Modern F1 teams receive telemetry from over 300 sensors on every car: tyre temperatures, brake bias, fuel pressure, G-forces, traction control events. The garage sees everything in real time.

Your data platform deserves the same treatment. **Observability** means knowing — at all times — whether your pipelines are healthy, your clusters are efficient, and your data quality is holding.

---

## 📊 The Four Telemetry Pillars

| Pillar | F1 Analogy | What to Monitor |
|---|---|---|
| **Infrastructure** | Engine temperature, fuel pressure | Cluster CPU, memory, disk |
| **Pipeline** | Lap time, sector times | Job duration, failure rate, throughput |
| **Data Quality** | Tyre wear rate | Row counts, null rates, schema drift |
| **Cost** | Fuel consumption | DBUs consumed, VM costs per job |

---

## 🔧 Azure Monitor: The Garage Wall Display

Azure Monitor is your **garage wall of screens** — centralised collection of metrics and logs from every Azure service.

### Databricks Diagnostic Logs → Log Analytics
```bash
# Enable diagnostic settings via Azure CLI
az monitor diagnostic-settings create \
  --name "databricks-to-log-analytics" \
  --resource /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Databricks/workspaces/<ws> \
  --workspace /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<law> \
  --logs '[
    {"category": "dbfs", "enabled": true},
    {"category": "clusters", "enabled": true},
    {"category": "jobs", "enabled": true},
    {"category": "notebook", "enabled": true}
  ]'
```

### Key KQL Queries for Databricks
```kusto
// Job failure rate over last 7 days
DatabricksJobs
| where TimeGenerated > ago(7d)
| where ActionName == "runFailed"
| summarize FailureCount = count() by JobName = tostring(RequestParams.jobName), bin(TimeGenerated, 1d)
| order by TimeGenerated desc

// Cluster cost by tag
AzureMetrics
| where MetricName == "DatabricksUnitsConsumed"
| summarize TotalDBUs = sum(Total) by ClusterName = tostring(split(ResourceId, "/")[-1])
| order by TotalDBUs desc
```

---

## 🚨 Alerting: The Warning Lights

Set up alerts so the pit wall knows before the driver does:

```python
# In a Databricks notebook — data quality alert
from pyspark.sql import functions as F

df_silver = spark.read.format("delta").load(".../silver/laps/")

# Check row count drop (more than 20% fewer rows than yesterday)
today_count = df_silver.filter(F.col("session_date") == "2026-03-12").count()
yesterday_count = df_silver.filter(F.col("session_date") == "2026-03-11").count()

if today_count < yesterday_count * 0.8:
    # Send alert — integrate with Azure Monitor custom metrics or Teams webhook
    import requests
    requests.post(
        "https://outlook.office.com/webhook/...",
        json={"text": f"⚠️ Data volume drop detected! Today: {today_count}, Yesterday: {yesterday_count}"}
    )
```

---

## 💰 Cost Observability: The Fuel Budget

DBU (Databricks Unit) consumption is your fuel budget. Monitor it:

```sql
-- Query system tables for cluster DBU cost (Unity Catalog)
SELECT
  cluster_name,
  SUM(dbu_count) AS total_dbus,
  SUM(dbu_count * 0.55) AS estimated_cost_usd  -- adjust to your DBU price
FROM system.billing.usage
WHERE usage_date >= CURRENT_DATE - 30
GROUP BY cluster_name
ORDER BY total_dbus DESC
```

---

## 🏁 Pit Stop Summary

- Monitor **four pillars**: infrastructure, pipeline, data quality, cost
- Use **Azure Monitor + Log Analytics** for centralised observability
- Set **row count alerts** — the most practical data quality signal
- Monitor **DBU consumption** by cluster — it's your fuel budget
- Use **system tables** in Unity Catalog for native Databricks cost analytics

**Next Episode →** Now that the car is monitored and governed, let's head to the wind tunnel — **MLflow and AutoML**.
