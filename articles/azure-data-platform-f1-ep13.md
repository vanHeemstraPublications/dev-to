---
title: "Scuderia Data Ep.13 — Race Broadcast (Power BI, Synapse & Serving Data)"
series: Scuderia Data — Azure Databricks & the F1 Data Platform
part: 13
tags: powerbi, synapse, databricks, analytics
---

# 📺 Episode 13 — Race Broadcast

> *"The engineers in the garage see raw telemetry. The pit wall sees aggregated strategy data. The world watching on TV sees a clean graphic: 'Hamilton P1, +4.2s to Verstappen'. Same data, three different consumers."*

All the work you've done — ingestion, refinement, aggregation, governance, ML — is for one purpose: **delivering insights to consumers**. The Gold layer is ready. Now it needs to reach the people who need it.

This is the **race broadcast layer**: Power BI, Databricks SQL, and Azure Synapse Analytics.

---

## 👥 Know Your Audience

Different consumers have different needs — exactly like the different audiences watching an F1 race:

| Audience | F1 Analogy | Tool | Access Pattern |
|---|---|---|---|
| Data Engineers | Race engineers (raw telemetry) | Databricks Notebooks | Spark / Delta direct |
| Data Analysts | Pit wall strategists | Databricks SQL | SQL queries on Gold tables |
| Business Users | Team principal | Power BI | Pre-built dashboards |
| External Apps | TV broadcast graphics | REST APIs / Synapse | Endpoints and views |

---

## 🔶 Databricks SQL: The Analysts' Cockpit

Databricks SQL gives your SQL-native analysts a clean query interface over your Delta tables — without needing to understand Spark, clusters, or Python.

### SQL Warehouses: The Analyst's Race Car
```sql
-- Query Gold directly from Databricks SQL
SELECT
  driver_name,
  team_name,
  MIN(fastest_lap_seconds) AS season_fastest_lap,
  AVG(avg_lap_seconds) AS season_avg_lap,
  SUM(pit_stop_count) AS total_pit_stops
FROM scuderia_prod.reporting.gold_driver_performance
WHERE session_date BETWEEN '2026-01-01' AND '2026-03-12'
GROUP BY driver_name, team_name
ORDER BY season_fastest_lap ASC;
```

SQL Warehouses:
- **Auto-scaling**: Scale workers up during peak query load, down to zero when idle
- **Photon**: C++ vectorised engine — faster than Spark for SQL-only workloads
- **Query History**: Every query logged, with performance metrics
- **Alerts**: Schedule queries and alert when a threshold is crossed

### Dashboards in Databricks SQL
Databricks SQL includes a native dashboard builder — create visualisations directly from SQL queries, no external tool required.

---

## 📊 Power BI: The TV Broadcast

For business stakeholders who live in the Microsoft ecosystem, **Power BI** is the dashboard of choice.

### Connection Options

**Option 1: Azure Databricks Connector (DirectQuery or Import)**
```
Power BI Desktop → Get Data → Azure Databricks
Server: adb-<workspace-id>.azuredatabricks.net
HTTP Path: /sql/1.0/warehouses/<warehouse-id>
Authentication: Azure Active Directory
```

- **DirectQuery**: Every Power BI visual sends a live query to Databricks — always fresh, but Databricks must be running
- **Import**: Data is copied into Power BI's in-memory engine — faster for dashboards, but refreshes on a schedule

**Best practice**: Use **Import** for large Gold tables with scheduled refreshes, **DirectQuery** for operational monitoring where freshness matters most.

### Power BI Dataset Architecture
```
ADLS Gen2 (Gold layer)
    │
    ▼  (Databricks SQL Warehouse)
Gold Delta Tables
    │
    ▼  (Power BI Connector)
Power BI Premium Dataset
    │
    ├── Dashboard: Championship Standings
    ├── Dashboard: Race Strategy Analysis  
    └── Dashboard: Team Performance YTD
```

---

## 🏛️ Azure Synapse Analytics: The Commentary Booth

Where does Synapse fit if you already have Databricks? It's the **commentary booth** — serving a slightly different audience.

| Use Databricks when... | Use Synapse Analytics when... |
|---|---|
| Data engineers and scientists | SQL-only analysts and DBAs |
| Python/Scala/ML workloads | T-SQL heavy workloads |
| Lakehouse-first architecture | Data warehouse + lake hybrid |
| Heavy Spark processing | Serverless SQL over ADLS (cheap reads) |
| Unity Catalog governance | Azure Purview governance |

**Synapse Serverless SQL** is particularly useful: it lets you run SQL directly against Delta files in ADLS with no cluster to manage and pay per-query pricing:

```sql
-- Synapse Serverless SQL: query Delta files in ADLS directly
SELECT TOP 100 *
FROM OPENROWSET(
  BULK 'https://scuderiadatastorage.dfs.core.windows.net/curated/driver_performance_summary/',
  FORMAT = 'DELTA'
) AS [result]
WHERE session_date >= '2026-01-01'
ORDER BY fastest_lap_seconds ASC;
```

---

## ⚡ Caching Strategy: Pre-Warming the Broadcast Feed

For dashboards accessed frequently by many users, pre-cache critical Gold tables:

```python
# Cache a Gold table in Databricks SQL warehouse memory
spark.sql("CACHE TABLE scuderia_prod.reporting.gold_driver_performance")

# Or use Delta's file caching
spark.conf.set("spark.databricks.io.cache.enabled", "true")
```

---

## 🏁 Pit Stop Summary

- Different consumers need different tools: **Databricks SQL** for analysts, **Power BI** for business users, **Synapse** for SQL-warehouse teams
- Use **Import mode** in Power BI for performance; **DirectQuery** for freshness
- **Synapse Serverless SQL** is cost-effective for ad-hoc SQL over ADLS files
- Cache Gold tables to keep dashboards fast under heavy load
- Unity Catalog governs access at the table and column level — even for Power BI users

**Final Episode →** We've built the entire platform. Now let's step back and see the **Championship Architecture** — the complete Lakehouse pattern.
