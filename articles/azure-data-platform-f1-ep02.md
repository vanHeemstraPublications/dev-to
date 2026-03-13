---
title: "Scuderia Data Ep.2"
published: false
description: "Episode 2: The Fuel Tank"
part: 2
tags: [azure, storage, dataengineering, databricks]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-02.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛢️ Episode 2 — The Fuel Tank (Azure Data Lake Storage Gen2)

> *"An F1 car without a fuel tank is just an expensive sculpture."*

Before the engine can fire, before the wheels turn, before any lap time is posted — you need **fuel**. And you need somewhere to store it.

In your Azure Data Platform, **Azure Data Lake Storage Gen2 (ADLS Gen2)** is your fuel tank. It is the foundational storage layer that holds every byte of raw, refined, and aggregated data in your platform.

---

## ⛽ What Is "Fuel" in Data Terms?

In F1, fuel is a highly engineered mixture of hydrocarbons — but it arrives at the factory in raw form and gets refined before it ever touches the engine.

Your data is the same:

| Fuel State | Data Equivalent | Example |
|---|---|---|
| Raw crude oil | Landing zone data | JSON logs from APIs, CSV exports, IoT streams |
| Refined race fuel | Cleaned data | Deduplicated, typed, validated records |
| Fuel in the tank | Stored data | Parquet files in ADLS Gen2 |
| Fuel in the engine | Active data | Data loaded into a Spark cluster |

The fuel tank doesn't care what the fuel is used for. It just holds it safely, reliably, and at scale.

---

## 🗄️ ADLS Gen2: What Makes It Special?

ADLS Gen2 is not just Azure Blob Storage with a different name. It has two critical characteristics that make it the right choice for a data platform:

### 1. Hierarchical Namespace (HNS)

Normal blob storage is a flat key-value store — like a pile of boxes with labels. ADLS Gen2 with HNS enabled is a **true filesystem** — directories, subdirectories, and atomic rename operations.

This matters enormously because:
- You can rename directories without copying millions of files
- You can set permissions at the directory level (not just the file level)
- Data pipeline tools work naturally with folder structures

### 2. Fine-Grained Access Control

ADLS Gen2 supports both **RBAC** (role-based, coarse-grained) and **ACLs** (access control lists, fine-grained, POSIX-style).

This means you can say:
- "The Bronze pipeline can write to `/raw/`"
- "The Silver pipeline can read `/raw/` and write to `/refined/`"
- "Business analysts can only read `/gold/`"

---

## 📁 The Tank Layout: Container Structure

Your fuel tank needs internal structure. You don't pour all the fuel into one unlabelled barrel. A standard ADLS Gen2 layout for a Databricks platform looks like this:

```
storage-account/
│
├── raw/                    ← Bronze landing zone (crude oil arrives here)
│   ├── source-system-a/
│   │   └── 2026/03/12/
│   └── source-system-b/
│
├── refined/                ← Silver zone (cleaned & validated)
│   └── domain/
│       └── entity/
│
├── curated/                ← Gold zone (business-ready aggregations)
│   └── reporting-domain/
│
├── sandbox/                ← Engineers' test area (not for production)
└── archive/                ← Historical data, cold storage tier
```

Each of `raw/`, `refined/`, and `curated/` maps directly to a **Medallion Architecture tier** — which we'll cover in Episodes 6–8.

---

## 💰 Storage Tiers: Fuel Economy

Not all fuel is used at the same rate. Some data is accessed every minute; some is archived and accessed once a year.

ADLS Gen2 has three storage tiers — choose based on access frequency:

| Tier | F1 Analogy | Use Case | Cost |
|---|---|---|---|
| Hot | Fuel in the engine bay | Active queries, recent data | Higher |
| Cool | Fuel in the main tank | Data accessed monthly | Medium |
| Archive | Fuel drums in the warehouse | Compliance, historical | Very low |

You can configure **lifecycle management policies** to automatically move data from Hot → Cool → Archive based on age.

---

## 🔒 Security: Locking the Fuel Store

In F1, you don't let random people near the fuel rig. Same principle applies:

- **Managed Identity**: Databricks and ADF authenticate to ADLS using Azure Managed Identity — no passwords, no keys stored in code
- **Private Endpoints**: Route all traffic from Databricks to ADLS through the Azure backbone, never over the public internet
- **Encryption**: ADLS encrypts all data at rest (AES-256) and in transit (TLS 1.2+) automatically
- **Soft Delete**: Accidentally deleted files can be recovered within a configurable retention window

---

## 🧰 Hands-On: Key CLI Commands

```bash
# Create a storage account with HNS enabled
az storage account create \
  --name scuderiadatastorage \
  --resource-group rg-scuderia-data \
  --location westeurope \
  --sku Standard_LRS \
  --kind StorageV2 \
  --enable-hierarchical-namespace true

# Create Bronze container
az storage fs create \
  --name raw \
  --account-name scuderiadatastorage

# Assign Storage Blob Data Contributor to Databricks managed identity
az role assignment create \
  --assignee <databricks-managed-identity-object-id> \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/scuderiadatastorage
```

---

## 🏁 Pit Stop Summary

- ADLS Gen2 is your **fuel tank** — the foundational storage layer
- Enable **Hierarchical Namespace** for filesystem semantics
- Structure containers around **Bronze / Silver / Gold** zones
- Use **storage tiers** to manage cost vs access speed
- Authenticate with **Managed Identity**, never with keys in code

**Next Episode →** The fuel needs to get *into* the tank from somewhere. That's the job of the fuel trucks — **Azure Data Factory**.
