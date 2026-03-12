---
title: "Scuderia Data Ep.5"
published: false
description: "Episode 5: The Engine"
part: 5
tags: [spark, databricks, dataengineering, bigdata]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-05.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# ⚙️ Episode 5 — The Engine

> *"You don't need to be an engine builder to be a world champion driver. But understanding how your engine works makes you faster."*

Apache Spark is the **power unit** inside the Databricks race car. You don't build it yourself — Databricks hands you a tuned, production-ready engine. But understanding how it works will make you a better driver.

---

## 🔥 Why Spark? The Problem It Solves

Before Spark, processing large datasets meant:
1. Loading data onto one machine
2. Waiting a very long time
3. Running out of RAM and crashing

Spark's answer: **don't process data on one machine — distribute it across hundreds**.

This is exactly like the difference between one mechanic trying to rebuild an entire car alone versus a 50-person pit crew each responsible for a specific component. The pit crew finishes in 2.4 seconds. The solo mechanic takes 2 hours.

---

## 🏎️ Spark's Architecture: The V10 Explained

### Driver (The Race Driver)
The **Driver** is the brain of a Spark job. It:
- Parses your code (Python/SQL/Scala)
- Builds an execution plan (the race strategy)
- Coordinates all the workers
- Collects the final result

There is **one Driver** per Spark application — exactly like one driver per car.

### Executors (The Mechanics)
**Executors** are the worker nodes that do the actual computation. Each executor:
- Holds a slice of the data in memory (its **partition**)
- Executes the tasks assigned by the Driver
- Reports results back

More executors = more parallel work = faster processing.

### Partitions (The Fuel Barrels)
Spark doesn't process a 100GB file as one lump. It splits it into **partitions** — chunks of data that can be processed in parallel. Each partition goes to one executor task.

```
100GB file
├── Partition 1 (200MB) → Executor 1, Task 1
├── Partition 2 (200MB) → Executor 1, Task 2
├── Partition 3 (200MB) → Executor 2, Task 1
└── ... 500 partitions across 10 executors
```

**Rule of thumb**: Aim for partition sizes of 100–200MB after reading.

---

## 📊 DataFrames: The Race Telemetry Sheet

The primary way you interact with Spark in Databricks is through **DataFrames** — a distributed table with named columns and types.

```python
from pyspark.sql import functions as F

# Read from ADLS (your fuel tank)
df = spark.read.parquet("abfss://raw@scuderiadatastorage.dfs.core.windows.net/laps/")

# Transform (refine the fuel)
df_clean = (df
  .filter(F.col("lap_time_seconds") > 0)
  .withColumn("lap_time_formatted", 
              F.format_string("%d:%06.3f", 
                             (F.col("lap_time_seconds") / 60).cast("int"),
                             F.col("lap_time_seconds") % 60))
  .select("driver_id", "lap_number", "lap_time_seconds", "lap_time_formatted")
)

# Write to Silver zone
df_clean.write.format("delta").mode("append").save(
  "abfss://refined@scuderiadatastorage.dfs.core.windows.net/laps/"
)
```

This looks like pandas. But it executes across a cluster of machines in parallel.

---

## 🦥 Lazy Evaluation: The Deferred Strategy Call

Spark is **lazy** — it doesn't execute anything until you force it to.

When you write `df_clean = df.filter(...).withColumn(...)`, Spark builds an **execution plan** but doesn't run it yet. This is like the race strategist building the full race plan — all the tyre stops, fuel windows, DRS zones — before the race starts.

Only when you call an **action** (like `.write`, `.show()`, `.count()`) does Spark actually execute the plan. And because it has the full plan up front, it can optimise it.

This is called the **Catalyst Optimizer** — Spark's internal engine for making your queries faster automatically.

---

## 🔀 Transformations vs Actions

| Type | Examples | What It Does |
|---|---|---|
| **Transformation** (lazy) | `.filter()`, `.select()`, `.join()`, `.groupBy()` | Adds a step to the plan |
| **Action** (triggers execution) | `.show()`, `.count()`, `.write`, `.collect()` | Runs the whole plan |

Best practice: **chain transformations, trigger actions as rarely as possible**.

---

## 💡 Spark SQL: The SQL Driver's Seat

Not everyone wants to write Python. Spark SQL lets you write standard SQL against DataFrames:

```python
# Register as a temp view
df_clean.createOrReplaceTempView("laps")

# Query with SQL
spark.sql("""
  SELECT 
    driver_id,
    MIN(lap_time_seconds) AS fastest_lap,
    AVG(lap_time_seconds) AS average_lap
  FROM laps
  GROUP BY driver_id
  ORDER BY fastest_lap ASC
""").show()
```

This is the same engine underneath — the same Catalyst optimizer, the same distributed execution.

---

## ⚡ Photon: The Turbo Boost

Databricks ships a proprietary C++ vectorised query engine called **Photon** that runs alongside Spark on SQL Warehouses. It can be 2–8x faster than vanilla Spark for SQL workloads.

Think of it as the **turbo boost system** — same fuel, same car, just more power per litre when you need it.

---

## 🏁 Pit Stop Summary

- Spark distributes processing across many machines in parallel — like a **pit crew instead of one mechanic**
- Driver coordinates, Executors process, Partitions are the data chunks
- DataFrames are your primary interface — distributed, typed, optimised
- Spark is **lazy**: it plans before it executes
- Use **Spark SQL** for SQL-native workflows; use **DataFrames** for programmatic transforms
- **Photon** gives extra performance for SQL on Databricks SQL Warehouses

**Next Episode →** The fuel is in the car and the engine is running. Time for the **pit lane** — where we refine raw data into Bronze using **Delta Lake**.
