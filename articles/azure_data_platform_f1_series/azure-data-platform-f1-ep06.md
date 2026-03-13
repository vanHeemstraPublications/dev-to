---
title: "Scuderia Data Ep.6"
published: false
description: "Episode 6: Pit Lane Bronze"
part: 6
tags: [delta, databricks, datalake, dataengineering]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-06.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🥉 Episode 6 — Pit Lane Bronze (Delta Lake & Raw Ingestion)

> *"When the car comes into the pit lane, it's raw. Worn tyres, dirty aerodynamics, low fuel. The pit crew's job is to change what needs changing — fast, reliably, and without mistakes."*

Welcome to the **pit lane** — the heart of your data refinement process.

In the Scuderia Data metaphor, the pit lane is **Delta Lake**. And the three grades of fuel refined in the pit lane map to the **Medallion Architecture**: Bronze, Silver, and Gold.

This episode covers **Bronze**: the raw ingestion layer.

---

## 🔷 What Is Delta Lake?

Delta Lake is an **open-source storage layer** that adds database-like capabilities to files in your data lake.

Without Delta Lake, your ADLS files are just... files. Parquet files. CSV files. They have no concept of:
- Transactions (what if a write fails halfway?)
- Version history (what did this data look like yesterday?)
- Schema enforcement (what if someone uploads a file with different columns?)
- Concurrent reads and writes (what if 10 jobs read while one job writes?)

**Delta Lake solves all of these.** It wraps your files in a **transaction log** (`_delta_log/`) that tracks every change, enforces the schema, and enables time travel.

| Problem | Without Delta | With Delta |
|---|---|---|
| Failed write | Partial corrupt data | Atomic — all or nothing |
| Concurrent access | Race conditions | MVCC (snapshot isolation) |
| Schema drift | Silent corruption | Schema enforcement + evolution |
| Historical query | Impossible | `VERSION AS OF` time travel |
| Audit trail | None | Full transaction log |

---

## 🏗️ ACID Transactions: The Pit Stop Contract

F1 pit stops have a strict protocol. Every mechanic knows exactly what they must do, and if anything goes wrong, the car doesn't leave the pit box. There are no partial pit stops.

Delta Lake brings this same reliability to data writes:

- **Atomicity**: A write either fully succeeds or fully rolls back. No half-written tables.
- **Consistency**: The table always matches its declared schema.
- **Isolation**: Multiple jobs can read and write without interfering.
- **Durability**: Once committed, data is not lost.

---

## 🥉 The Bronze Layer: Raw Fuel Landing

The Bronze layer is your **raw landing zone**. The design philosophy is simple:

> **Land everything. Transform nothing.**

Bronze tables are:
- An exact copy of source data
- Loaded with minimal transformation (maybe add `ingestion_timestamp`, `source_file_name`)
- Append-only (or upsert for CDC sources)
- Retained forever for reprocessing and audit

```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F

# Read raw JSON from ADLS landing zone
df_raw = (spark.read
  .format("json")
  .option("multiLine", True)
  .load("abfss://raw@scuderiadatastorage.dfs.core.windows.net/telemetry/2026/03/12/")
)

# Add audit columns — the ONLY transformation in Bronze
df_bronze = df_raw.withColumns({
  "_ingested_at": F.current_timestamp(),
  "_source_file": F.input_file_name(),
  "_batch_id": F.lit("batch_2026-03-12_001")
})

# Write to Bronze Delta table — append only
(df_bronze.write
  .format("delta")
  .mode("append")
  .option("mergeSchema", "true")   # Allow new columns from source
  .save("abfss://refined@scuderiadatastorage.dfs.core.windows.net/bronze/telemetry/")
)
```

---

## 📜 The Delta Log: The Pit Stop Record Book

Every Delta table has a `_delta_log/` directory containing JSON files that record every transaction:

```
bronze/telemetry/
├── _delta_log/
│   ├── 00000000000000000000.json   ← CREATE TABLE
│   ├── 00000000000000000001.json   ← First APPEND
│   ├── 00000000000000000002.json   ← Second APPEND
│   └── 00000000000000000010.checkpoint.parquet  ← Checkpoint
├── part-00000-abc123.parquet
└── part-00001-def456.parquet
```

This log enables **time travel**:

```python
# What did the table look like yesterday?
df_yesterday = spark.read.format("delta") \
  .option("versionAsOf", 3) \
  .load("abfss://refined@.../bronze/telemetry/")

# Or by timestamp
df_before_incident = spark.read.format("delta") \
  .option("timestampAsOf", "2026-03-11 09:00:00") \
  .load("abfss://refined@.../bronze/telemetry/")
```

---

## 🧹 Delta Maintenance: Keeping the Pit Lane Clean

Delta tables accumulate old files and transaction log entries. Periodic maintenance keeps performance sharp:

```python
from delta.tables import DeltaTable

dt = DeltaTable.forPath(spark, "abfss://refined@.../bronze/telemetry/")

# OPTIMIZE: compact small files into larger ones (faster reads)
dt.optimize().executeCompaction()

# Z-ORDER: co-locate related data for faster filtered queries
dt.optimize().executeZOrderBy("driver_id", "session_date")

# VACUUM: remove files older than 7 days (168 hours)
dt.vacuum(168)
```

---

## 🏁 Pit Stop Summary

- Delta Lake adds **ACID transactions, time travel, schema enforcement** to your data lake files
- The `_delta_log/` is the immutable record of every change — your pit stop logbook
- **Bronze** = raw landing, append-only, minimal transformation, retain forever
- Use `_ingested_at`, `_source_file` audit columns on every Bronze table
- Run **OPTIMIZE + VACUUM** regularly to maintain performance

**Next Episode →** Bronze is in. Now the pit crew gets to work — refining Bronze into **Silver**.
