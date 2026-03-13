---
title: "Scuderia Data Ep.8"
published: false
description: "Episode 8: Gold Aggregation"
part: 8
tags: [delta, databricks, analytics, dataengineering]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-08.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🥇 Episode 8 — Gold Aggregation (Business-ready data)

> *"The race strategist doesn't look at raw telemetry. They look at a dashboard: tyre degradation curve, gap to leader, pit window. Aggregated. Actionable. Now."*

Bronze is the raw fuel. Silver is the refined fuel. **Gold is the fuel that's already in the engine, mixed to race specification, ready to go.**

The Gold layer contains **business-domain aggregations** — pre-computed metrics, dimensional models, feature tables, and reporting datasets. It is optimised for consumption by dashboards, ML models, and APIs — not for re-processing.

---

## 🥇 Gold Design Principles

| Principle | What It Means |
|---|---|
| **Business-oriented** | Named and structured for business consumers, not engineers |
| **Aggregated** | Pre-computed GROUP BY, window functions, KPIs |
| **Denormalized** | Joins are pre-done — consumers don't write JOINs |
| **Domain-partitioned** | Organised by business domain (Sales, Operations, Finance) |
| **SLA-backed** | Refreshed on a schedule; consumers can depend on it |
| **Read-optimised** | Z-ordered, compacted, Bloom filter indexed |

---

## 🏗️ Gold Table Patterns

### Pattern 1: Aggregate Metrics Table
Pre-computed KPIs refreshed on a schedule.

```python
from pyspark.sql import functions as F

# Read from Silver
df_silver_laps = spark.read.format("delta").load(".../silver/laps/")
df_silver_drivers = spark.read.format("delta").load(".../silver/drivers/")

# Build Gold: Driver Performance Summary
df_gold = (df_silver_laps
  .join(df_silver_drivers, on="driver_id", how="left")
  .groupBy("driver_id", "driver_name", "team_name", "session_date")
  .agg(
    F.min("lap_time_seconds").alias("fastest_lap_seconds"),
    F.avg("lap_time_seconds").alias("avg_lap_seconds"),
    F.count("lap_number").alias("total_laps"),
    F.sum(F.when(F.col("pit_stop"), 1).otherwise(0)).alias("pit_stop_count")
  )
  .withColumn("_refreshed_at", F.current_timestamp())
)

# Overwrite Gold (full refresh pattern)
(df_gold.write
  .format("delta")
  .mode("overwrite")
  .option("overwriteSchema", "true")
  .partitionBy("session_date")
  .save(".../gold/driver_performance_summary/")
)
```

### Pattern 2: Slowly Changing Dimensions (SCD Type 2)
Track history of dimension changes — e.g., a driver changes teams.

```python
from delta.tables import DeltaTable

# SCD2: when a team changes, expire old record and insert new one
(DeltaTable.forPath(spark, ".../gold/dim_drivers/")
  .alias("target")
  .merge(
    df_updates.alias("source"),
    "target.driver_id = source.driver_id AND target.is_current = true"
  )
  .whenMatchedUpdate(
    condition="target.team_name != source.team_name",
    set={
      "is_current": "false",
      "valid_to": "source.effective_date"
    }
  )
  .whenNotMatchedInsert(values={
    "driver_id": "source.driver_id",
    "driver_name": "source.driver_name",
    "team_name": "source.team_name",
    "is_current": "true",
    "valid_from": "source.effective_date",
    "valid_to": "null"
  })
  .execute()
)
```

### Pattern 3: Feature Table (for ML)
Gold tables that serve as input to ML model training and scoring.

```python
# Build a feature table for tyre degradation model
df_features = (df_silver_laps
  .withColumn("lap_delta_seconds",
    F.col("lap_time_seconds") - F.lag("lap_time_seconds", 1).over(
      Window.partitionBy("driver_id", "stint_number").orderBy("lap_number")
    ))
  .withColumn("tyre_age_laps",
    F.row_number().over(
      Window.partitionBy("driver_id", "stint_number").orderBy("lap_number")
    ))
  .select("driver_id", "session_date", "tyre_compound", "tyre_age_laps", 
          "lap_time_seconds", "lap_delta_seconds", "fuel_load_kg")
)

df_features.write.format("delta").mode("overwrite").save(".../gold/features/tyre_degradation/")
```

---

## ⚡ Gold Performance Optimisation

Gold tables must be **fast to query**. Apply these optimisations:

```python
from delta.tables import DeltaTable

dt = DeltaTable.forPath(spark, ".../gold/driver_performance_summary/")

# Z-ORDER on the most common filter columns
dt.optimize().executeZOrderBy("driver_id", "session_date")

# Add Bloom filter for high-cardinality string lookups
spark.sql("""
  ALTER TABLE delta.`abfss://...gold/driver_performance_summary/`
  SET TBLPROPERTIES (
    'delta.dataSkippingNumIndexedCols' = '5',
    'delta.bloomFilter.columns' = 'driver_id,team_name'
  )
""")
```

---

## 📐 The Full Medallion Architecture: One View

```
Source Systems
     │
     ▼  (ADF copy / Streaming)
┌─────────┐
│  BRONZE  │  Raw, append-only, minimal transformation
│  (raw)   │  Retain forever. Time travel for reprocessing.
└────┬─────┘
     │  (Spark MERGE + DQ checks)
     ▼
┌─────────┐
│  SILVER  │  Cleaned, typed, deduplicated, conformed
│(refined) │  Row-level truth. Scrutineered.
└────┬─────┘
     │  (Spark aggregations, Window functions, Joins)
     ▼
┌─────────┐
│   GOLD   │  Aggregated, denormalized, business-domain ready
│(curated) │  Served to Power BI, ML models, APIs
└─────────┘
```

---

## 🏁 Pit Stop Summary

- Gold = **business-ready data products**: aggregated, denormalized, read-optimised
- Use **full overwrite** for small Gold tables, **MERGE** for large dimensional models
- Implement **SCD Type 2** for dimensions that change over time
- Gold tables double as **feature tables** for ML pipelines
- Apply **Z-ORDER + Bloom filters** for query performance
- Gold tables have **SLAs** — consumers depend on them being fresh and correct

**Next Episode →** The fuel system is complete. Now let's sit in the cockpit — **Databricks Notebooks and Jobs**.
