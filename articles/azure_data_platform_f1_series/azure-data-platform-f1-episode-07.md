---
title: "Scuderia Data Ep.7"
published: false
description: "Episode 7: Silver Refinement"
part: 7
tags: [delta, databricks, dataengineering, etl]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-07.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🥈 Episode 7 — Silver Refinement (Delta Lake Transformations)

> *"Raw race fuel burns, but it burns dirty. Race engineers refine it to the precise specification the engine needs — clean, consistent, and perfectly measured."*

Bronze is landed. Now the pit crew gets serious.

The **Silver layer** is where your data gets **cleaned, validated, deduplicated, and conformed**. It is still a faithful representation of the source data — no business aggregations yet — but it is now fit for purpose: correctly typed, consistently named, and free of duplicates.

---

## 🥈 Silver Design Principles

| Principle | What It Means |
|---|---|
| **Cleaned** | Nulls handled, invalid values corrected or quarantined |
| **Typed** | Columns have correct data types (not everything is a string) |
| **Deduplicated** | One record per business key — no duplicates from retries |
| **Conformed** | Column names match enterprise naming standards |
| **Enriched** | Light lookups added (e.g., resolve IDs to names from reference data) |
| **Not Aggregated** | Still row-level data — no GROUP BY yet |

---

## 🔄 MERGE: The Upsert Operation

The most important pattern in Silver is **MERGE** (upsert): update if the record exists, insert if it doesn't. This handles:
- Source system resending corrected records
- CDC (Change Data Capture) streams
- Idempotent reprocessing

```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F

# Read from Bronze
df_bronze = spark.read.format("delta").load(
  "abfss://refined@scuderiadatastorage.dfs.core.windows.net/bronze/laps/"
)

# Transform: clean and type
df_silver = (df_bronze
  .filter(F.col("lap_time_seconds").isNotNull())
  .filter(F.col("lap_time_seconds").between(60, 200))  # Sanity range: 1–3.3 min
  .withColumn("lap_time_seconds", F.col("lap_time_seconds").cast("double"))
  .withColumn("session_date", F.to_date(F.col("session_timestamp")))
  .withColumn("driver_id", F.trim(F.upper(F.col("driver_id"))))  # Conform
  .drop("_source_file", "_batch_id")  # Remove Bronze audit cols
  .withColumn("_updated_at", F.current_timestamp())
)

# MERGE into Silver target
silver_table = DeltaTable.forPath(
  spark, 
  "abfss://refined@scuderiadatastorage.dfs.core.windows.net/silver/laps/"
)

(silver_table.alias("target")
  .merge(
    df_silver.alias("source"),
    "target.driver_id = source.driver_id AND target.lap_number = source.lap_number AND target.session_date = source.session_date"
  )
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .execute()
)
```

---

## 🚨 Data Quality: The Technical Scrutineers

In F1, before a car can race, the FIA Technical Scrutineers inspect it. They check dimensions, weight, fuel samples, and safety equipment. Cars that don't pass are excluded.

Your Silver layer needs **data quality checks** — scrutineering for your data.

### Option 1: Delta Constraints (Engine-Level Rules)
Delta Lake supports table-level constraints that reject violating rows at write time:

```python
spark.sql("""
  ALTER TABLE delta.`abfss://refined@.../silver/laps/`
  ADD CONSTRAINT valid_lap_time CHECK (lap_time_seconds BETWEEN 60 AND 200)
""")
```

If a row violates this constraint, the entire write fails — ACID atomicity means no partial inserts.

### Option 2: Expectation Framework (Soft Quarantine)
For cases where you want to capture bad data rather than reject it:

```python
# Tag rows that fail quality checks
df_with_dq = df_silver.withColumn(
  "_dq_issues",
  F.array(
    F.when(F.col("lap_time_seconds") < 60, F.lit("LAP_TOO_FAST")).otherwise(F.lit(None)),
    F.when(F.col("driver_id").isNull(), F.lit("NULL_DRIVER_ID")).otherwise(F.lit(None))
  )
)

# Split: good records → Silver, bad records → quarantine
df_good = df_with_dq.filter(F.size(F.array_remove(F.col("_dq_issues"), None)) == 0)
df_bad  = df_with_dq.filter(F.size(F.array_remove(F.col("_dq_issues"), None)) > 0)

df_good.write.format("delta").mode("append").save(".../silver/laps/")
df_bad.write.format("delta").mode("append").save(".../quarantine/laps/")
```

---

## 📐 Schema Enforcement vs Schema Evolution

Delta Lake gives you two modes:

| Mode | Behaviour | When to Use |
|---|---|---|
| **Enforcement** (default) | Rejects writes with unexpected columns | Production Silver tables |
| **Evolution** (`mergeSchema=true`) | Adds new columns automatically | Bronze landing only |

In Silver, enforce the schema strictly. New columns should be a conscious decision, not an accident.

---

## 🏁 Pit Stop Summary

- Silver = cleaned, typed, deduplicated, conformed — but **not yet aggregated**
- **MERGE** (upsert) is the primary Silver write pattern — handles corrections and reprocessing
- Add **data quality checks** — either hard constraints (Delta) or soft quarantine (tagging)
- Enforce schema strictly in Silver; allow evolution in Bronze
- Silver is the **single source of truth** for row-level data

**Next Episode →** Silver is refined and ready. Now the engineers blend it into the perfect race-day mixture — the **Gold layer**.
