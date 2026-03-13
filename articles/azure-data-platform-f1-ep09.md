---
title: "Scuderia Data Ep.9"
published: false
description: "Episode 9: The Cockpit"
part: 9
tags: [databricks, notebooks, workflows, dataengineering]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-09.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🖥️ Episode 9 — The Cockpit (Databricks Notebooks & Jobs)

> *"The cockpit is where the driver and the car become one. Every button, every display, every control is purpose-built for speed and precision."*

You've built the engine, the fuel system, and the pit lane. Now it's time to take the driver's seat — **Databricks Notebooks and Workflows**.

---

## 📓 Notebooks: The Steering Wheel

A Databricks Notebook is your **primary development interface**. It's a live, interactive document where code cells mix with output, markdown documentation, and visualisations.

### Notebook Cell Types
- **Code cells**: Python, SQL, Scala, R — switch mid-notebook with `%python`, `%sql`, `%scala`
- **Markdown cells**: `%md` — documentation between code blocks
- **Shell cells**: `%sh` — bash commands on the driver node
- **File system**: `%fs` — interact with DBFS (Databricks File System)

```python
# %python
df = spark.read.format("delta").load(".../silver/laps/")
display(df.limit(10))

# %sql (switch language in same notebook)
SELECT driver_id, COUNT(*) as lap_count 
FROM delta.`abfss://refined@.../silver/laps/`
GROUP BY driver_id
ORDER BY lap_count DESC
```

### Notebook-Scoped Configuration
```python
# Set Spark config for this session
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")

# Use widgets for parameterized notebooks
dbutils.widgets.text("session_date", "2026-03-12", "Session Date")
session_date = dbutils.widgets.get("session_date")
```

---

## 🔗 dbutils: The Cockpit Controls

`dbutils` is the Databricks utility library — your cockpit controls panel.

| Module | F1 Analogy | Use Case |
|---|---|---|
| `dbutils.fs` | Navigation system | List, copy, move files in ADLS |
| `dbutils.secrets` | Encrypted comms | Retrieve secrets from Key Vault |
| `dbutils.widgets` | Radio presets | Parameterise notebooks |
| `dbutils.notebook` | Pit radio calls | Run child notebooks, pass return values |

```python
# List files in ADLS
dbutils.fs.ls("abfss://raw@scuderiadatastorage.dfs.core.windows.net/")

# Get a secret (no password in code — ever)
storage_key = dbutils.secrets.get(scope="scuderia-kv", key="adls-account-key")

# Call a child notebook and get its result
result = dbutils.notebook.run(
  "/Workflows/bronze_to_silver_laps",
  timeout_seconds=3600,
  arguments={"session_date": "2026-03-12", "env": "prod"}
)
```

---

## 🔄 Databricks Workflows: The Race Schedule

Individual notebooks are powerful, but a data platform needs **orchestrated pipelines**: a sequence of jobs with dependencies, retries, alerting, and scheduling.

**Databricks Workflows** is the built-in orchestration engine — your race schedule.

### Job Structure
```yaml
# Conceptual job definition (also configurable via Terraform/JSON)
job:
  name: "daily_medallion_pipeline"
  schedule: "0 2 * * *"   # Every day at 02:00 UTC
  
  tasks:
    - task_key: "bronze_ingest"
      notebook_path: "/Workflows/ingest_bronze"
      cluster: job_cluster_bronze
      
    - task_key: "silver_transform"
      depends_on: [bronze_ingest]
      notebook_path: "/Workflows/transform_silver"
      cluster: job_cluster_silver
      
    - task_key: "gold_aggregate"
      depends_on: [silver_transform]
      notebook_path: "/Workflows/aggregate_gold"
      cluster: job_cluster_gold
```

### Cluster Policies: The Car Regulations
Cluster policies are admin-defined templates that constrain what users can configure — like FIA regulations that prevent teams building illegal cars.

```json
{
  "node_type_id": {"type": "allowlist", "values": ["Standard_DS3_v2", "Standard_DS4_v2"]},
  "autoscale.min_workers": {"type": "fixed", "value": 2},
  "autoscale.max_workers": {"type": "range", "maxValue": 8},
  "spark_version": {"type": "regex", "pattern": "^13\\.*"},
  "custom_tags.CostCenter": {"type": "fixed", "value": "data-platform"}
}
```

---

## 🏁 Pit Stop Summary

- Notebooks are the **cockpit** — interactive, multi-language, documentation-rich
- `dbutils` is your **controls panel** — filesystem, secrets, widgets, child notebooks
- Databricks **Workflows** orchestrates multi-task pipelines with dependencies
- Use **Cluster Policies** to enforce cost controls and standard configurations
- Parameterise notebooks with `dbutils.widgets` — never hardcode environment values

**Next Episode →** The car is running perfectly. But who decides what data the driver can see? Time for the **Race Strategist: Unity Catalog**.
