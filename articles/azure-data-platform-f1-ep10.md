---
title: "Scuderia Data Ep.10"
published: false
description: "Episode 10: Race Strategy"
part: 10
tags: [databricks, unitycatalog, governance, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-10.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🧠 Episode 10 — Race Strategy

> *"The race strategist knows everything: who has access to what data, what changed, when, and why. Without strategy, drivers go rogue. Without governance, data goes wrong."*

Every F1 team has a **race strategist** — the person who monitors all variables, decides who gets which information, and ensures no critical decision is made without the right data at the right time.

In Azure Databricks, that role belongs to **Unity Catalog**: the unified governance layer for all your data assets.

---

## 🗂️ The Three-Level Namespace

Unity Catalog organises your data world into three levels — exactly like an F1 team's organisational chart:

```
Catalog (the Team)
└── Schema / Database (the Department)
    └── Table / View / Volume (the Asset)
```

```sql
-- Full three-part name: catalog.schema.table
SELECT * FROM scuderia_prod.telemetry.silver_laps;
SELECT * FROM scuderia_prod.reporting.gold_driver_performance;
SELECT * FROM scuderia_dev.sandbox.experimental_features;
```

This means you can have `dev`, `staging`, and `prod` catalogs — separate environments, same query patterns.

---

## 🔐 Access Control: The Pit Lane Passes

In F1, different people have different levels of access to the car and data:
- **Engineers** can read raw telemetry and write to any zone
- **Analysts** can read Silver and Gold, but not Bronze
- **External partners** can see only their own data

Unity Catalog enforces this with **privilege grants**:

```sql
-- Grant an analyst read access to Gold only
GRANT SELECT ON SCHEMA scuderia_prod.reporting TO `analyst-group@scuderia.com`;

-- Grant a data engineer full access to Bronze
GRANT ALL PRIVILEGES ON SCHEMA scuderia_prod.raw TO `data-engineers@scuderia.com`;

-- Grant a specific table to an external partner
GRANT SELECT ON TABLE scuderia_prod.partner.lap_times_partner 
  TO `external-partner@partnerteam.com`;

-- Revoke access immediately when someone leaves
REVOKE ALL PRIVILEGES ON CATALOG scuderia_prod FROM `former-employee@scuderia.com`;
```

---

## 🔍 Data Lineage: The Incident Investigation

When something goes wrong in a race, the FIA reviews **video footage** of every moment — who touched the car, when, and what happened. Data lineage is your video footage.

Unity Catalog automatically tracks **data lineage** — which tables were read to produce which tables:

```
API Source → Bronze laps → Silver laps → Gold driver summary → Power BI report
```

This means when a business analyst says "these numbers look wrong", you can trace backwards through every transformation to find exactly where the error was introduced.

---

## 🏷️ Data Classification: The FIA Technical Regulations

Unity Catalog supports **tags** on catalogs, schemas, tables, and columns. Use tags for:
- Data classification (PII, Confidential, Public)
- Domain ownership (owned by: telemetry-team)
- Data product maturity (status: gold, experimental)

```sql
-- Tag a column as PII
ALTER TABLE scuderia_prod.silver.drivers 
  ALTER COLUMN email SET TAGS ('pii' = 'true', 'classification' = 'confidential');

-- Tag an entire table
ALTER TABLE scuderia_prod.gold.driver_performance 
  SET TAGS ('domain' = 'racing-analytics', 'data-product-status' = 'gold');
```

---

## 👁️ Row-Level Security & Column Masking

Sometimes a query should return different results for different users — like a driver only seeing their own telemetry.

```sql
-- Row filter: each driver only sees their own laps
CREATE ROW FILTER driver_filter ON scuderia_prod.silver.laps
  USING (driver_id = CURRENT_USER() OR IS_MEMBER('race-engineers'));

-- Column mask: hide precise fuel loads from non-engineers
CREATE COLUMN MASK fuel_mask ON scuderia_prod.silver.laps (fuel_load_kg)
  USING (CASE WHEN IS_MEMBER('race-engineers') THEN fuel_load_kg ELSE NULL END);
```

---

## 📊 Unity Catalog Architecture

```
Unity Catalog Metastore (one per Azure region)
├── Catalog: scuderia_prod
│   ├── Schema: raw (Bronze)
│   ├── Schema: refined (Silver)
│   └── Schema: reporting (Gold)
├── Catalog: scuderia_dev
│   └── Schema: sandbox
└── Storage Credentials & External Locations
    └── Managed Identity → ADLS Gen2
```

One Metastore serves **all workspaces** in the region. Governance is centralised, not per-workspace.

---

## 🏁 Pit Stop Summary

- Unity Catalog is the **race strategist**: governance, access control, lineage, classification
- Three-level namespace: **Catalog → Schema → Table**
- Grant privileges at any level — catalog, schema, table, or column
- Automatic **data lineage** traces every transformation end-to-end
- Use **tags** for PII marking, domain ownership, and data product classification
- **Row filters and column masks** enable fine-grained, user-aware access

**Next Episode →** The strategist monitors everything. But who monitors the car itself? Welcome to the **Telemetry System**: Azure Monitor + Databricks Observability.
