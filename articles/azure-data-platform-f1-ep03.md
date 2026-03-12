---
title: "Scuderia Data Ep.3"
published: false
description: "Episode 3: Fuel Logistics"
part: 3
tags: [azure, adf, dataengineering, pipelines]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-03.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🚛 Episode 3 — Fuel Logistics

> *"The best fuel in the world is useless if it never reaches the car."*

Your fuel tank (ADLS Gen2) is ready and waiting. But raw data doesn't teleport itself from SAP, Salesforce, IoT devices, or REST APIs into your lake. You need a **logistics system** — and that's **Azure Data Factory (ADF)**.

ADF is the fuel truck fleet of your data platform. It *moves* data. It doesn't transform it deeply (that's Spark's job), but it knows every road, every connection type, and every schedule.

---

## 🔄 What ADF Does (and Doesn't Do)

| ADF Does | ADF Doesn't Do |
|---|---|
| Connects to 90+ data sources | Complex business-logic transformations |
| Copies data (bulk & incremental) | Machine learning |
| Schedules and orchestrates pipelines | Deep data quality checks |
| Triggers Databricks notebooks/jobs | Serve data to end users |
| Monitors pipeline runs | Replace Spark for big transforms |

Think of ADF as the **logistics manager**, not the engineer. It coordinates movement. Databricks does the heavy manufacturing.

---

## 🧱 ADF Core Concepts

### Linked Services — The Fuel Truck Models
A Linked Service is a **connection definition** — it tells ADF how to connect to a system. Each source or destination system needs one.

```json
{
  "name": "ls_adls_scuderia",
  "type": "AzureBlobFS",
  "typeProperties": {
    "url": "https://scuderiadatastorage.dfs.core.windows.net",
    "accountKey": { "type": "AzureKeyVaultSecret", "secretName": "adls-key" }
  }
}
```

### Datasets — The Fuel Manifests
A Dataset describes the **shape and location** of data at a linked service. It's the cargo manifest for your fuel truck.

### Pipelines — The Delivery Route
A Pipeline is a **sequence of activities** — Copy, Execute Notebook, Delete, Validation, and more. It's the delivery route the truck follows.

### Triggers — The Dispatch Schedule
Triggers define **when** a pipeline runs:
- **Schedule trigger**: Every day at 02:00
- **Tumbling window**: Time-partitioned batches
- **Event trigger**: Fires when a file arrives in ADLS
- **Manual**: On-demand

---

## 📐 Ingestion Patterns

### Full Load (One-Time or Periodic Snapshot)
Load everything from source each time. Simple, but expensive at scale.

```
Source System → [Copy Activity] → ADLS /raw/entity/snapshot_date=2026-03-12/
```

### Incremental Load (Watermark-Based)
Only load rows newer than the last run. Use a watermark column (e.g., `updated_at`).

```
last_watermark = read from control table
new_data = SELECT * FROM source WHERE updated_at > last_watermark
copy new_data → ADLS
update control table with new watermark
```

### Event-Driven (File Arrival)
An event trigger fires when a file lands in a watched container. Ideal for partner data feeds, SFTP drops, and IoT batches.

---

## 🔀 ADF vs Databricks for Orchestration

A common question: *should I orchestrate with ADF or with Databricks Workflows?*

| Use ADF when... | Use Databricks Workflows when... |
|---|---|
| Ingesting from external systems | Orchestrating Spark jobs end-to-end |
| Non-Spark activities (Logic Apps, Functions) | ML pipelines and model training |
| Pre-existing ADF investment | Pure lakehouse workloads |
| SQL Server, SAP, Oracle connectors | Teams living entirely in Databricks |

In practice, many platforms use **both**: ADF for ingestion orchestration, Databricks Workflows for transformation orchestration.

---

## 🏁 Pit Stop Summary

- ADF is the **fuel logistics system** — it moves data, not transforms it
- Core components: Linked Services, Datasets, Pipelines, Triggers
- Key patterns: Full load, incremental watermark, event-driven
- ADF and Databricks Workflows are **complementary**, not competing

**Next Episode →** The fuel is in the tank. Now let's meet the race car — **Azure Databricks** itself.
