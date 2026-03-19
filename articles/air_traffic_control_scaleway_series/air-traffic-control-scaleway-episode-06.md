---
title: "Air Traffic Control Scaleway Ep.6"
part: 6
published: false
description: "Episode 6 of the Air Traffic Control series: provision a Managed Redis database on Scaleway, wire it to a Serverless Container via environment variables, and invoke the live endpoint. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, managed-databases, redis]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-06.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Mission Memory: Managed Databases on Scaleway

*“Every International Rescue operation depends on what came before it. Rescue coordinates, equipment manifests, mission histories — all stored, all retrievable, all protected. Without that persistent memory, every mission starts from zero. That is not how International Rescue operates.”*
*— Tin-Tin Kyrano, Thunderbird Island Operations*

-----

Welcome back to the **Scaleway Air Traffic Control Centre**.

In Episode 4, we deployed stateless probes — functions and containers that execute and leave nothing behind. In this episode, we add memory. **Managed Databases** give your workloads a persistent state layer: a database that survives container restarts, pod evictions, and deployment cycles without any of the operational overhead of self-managed infrastructure.

Our mission in this episode is precise: provision a **Managed Redis instance**, build a container image that connects to it, push that image to a private registry, and deploy it as a **Serverless Container** — wired to the database through environment variables.

When the container receives a request, it reads from and writes to Redis. The database persists. The container is ephemeral. The architecture is clean.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Provision a **Managed Redis Database Instance** on Scaleway
- Configure the database with a username, password, and public endpoint
- Create a **Serverless Containers namespace** with environment variables pre-loaded
- Authenticate the **Docker CLI** against the Scaleway Container Registry
- Build a container image from the activity assets and push it to the registry
- **Deploy** the container and verify it connects to the Redis instance
- **Invoke** the live container endpoint via `curl`
- **Delete** all resources cleanly

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own
- ✅ Docker Desktop is running on your machine

> **Note:** For this activity, you will work in your Organisation’s `default` project.

-----

## 📊 SIPOC — How Managed Databases Flow Through the System

|Stage|SIPOC Element|Managed Database Equivalent                                                                                |Example                                                                   |
|-----|-------------|-----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway Managed Databases engine + Container Registry + Serverless Compute                                |Redis service, private registry, serverless runtime                       |
|**I**|**Input**    |Redis version, node type, credentials, container image, environment variables                              |`RED1-MICRO`, `hands-on-redis`, `REDIS` / `USERNAME` / `PASSWORD` env vars|
|**P**|**Process**  |Provision Redis → Create namespace → Authenticate Docker → Build and push image → Deploy container → Invoke|All the hands-on steps in this episode                                    |
|**O**|**Output**   |A live Serverless Container backed by a persistent Managed Redis instance, invocable via HTTPS             |`curl <endpoint>` returns a response from a container reading Redis state |
|**C**|**Consumer** |Applications, APIs, and services that require persistent key-value state across requests                   |Your terminal, your application layer, your integration tests             |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   Redis version   ──▶  Provision Redis  ──▶  Live HTTPS    ──▶   Applications
Managed              Node type            Create NS             endpoint              APIs
Databases            Credentials          Auth Docker           backed by             Services
                     Container image      Build & push          persistent
Container            Env vars             Deploy container      Redis state
Registry             (REDIS /             Invoke
                     USERNAME /
Serverless           PASSWORD)
Compute
```

> **Tower to crew:** The environment variables `REDIS`, `USERNAME`, and `PASSWORD` are the wiring harness between the container and the database. They are set at the namespace level — every container deployed into this namespace inherits them automatically. No credentials in the image. No secrets in the source code.

-----

## 🛫 Section 1 — Install the Memory Unit: Provision Redis

A Redis instance is an in-memory key-value store — fast, lightweight, and ideal for session state, caching, and message queuing. Scaleway manages the infrastructure; you manage the data.

### 1.1 — Create the Redis Database Instance

1. In the **Managed Databases** section of the side menu, select **Redis**.
1. Click **Create Redis Database Instance**.
1. For the **Availability Zone**, select `Amsterdam 1`.
1. In the **Choose a Redis version** section, select the latest available Redis version.
1. In the **Select a configuration** section, select **Standalone** mode.
1. In the **Choose your node type** section, select `RED1-MICRO`.
1. In the **Configure your network** section, leave **Public network** selected.
1. Define a **username** and **password** for the database.

> **Tip:** Store these credentials immediately — you will need them when configuring the Containers namespace in the next section. A password manager or a temporary local note both work; the Console will not show the password again after creation.

1. Set the database name to `hands-on-redis`.
1. Open **Advanced options** and clear the **TLS certificate** toggle.
1. Review the estimated cost.
1. Click **Create Redis Database Instance**.

### 1.2 — Copy the Public Endpoint

Once the Database Instance status changes to `Ready`, open the **Overview** tab and copy the **public endpoint**.

> **Tip:** Store the endpoint alongside your credentials. The format is `<host>:<port>` — you will paste it directly into the namespace environment variable in the next section.

> **Tower confirms:** TLS has been disabled for this hands-on activity to reduce configuration overhead. In any production deployment, TLS must be enabled and the certificate validated by the connecting application. Clearance without encryption is not clearance — it is an open channel.

-----

## 🏗️ Section 2 — Wire the Cockpit: Create the Containers Namespace

The namespace is the deployment boundary for your container. It also carries the environment variables that wire the container to the Redis instance — credentials injected at the platform level, not baked into the image.

### 2.1 — Create the Namespace

1. In the **Serverless** section of the side menu, select **Containers**. The **Namespaces** tab displays.
1. Click **Create namespace**.
1. Set the name to `hands-on-redis`.
1. Set the region to `Amsterdam`.
1. In the **Environment variables** section, add the following three variables. Take care not to introduce trailing spaces — hidden whitespace in credentials produces authentication failures that are difficult to diagnose:

|Variable  |Value                                                 |
|----------|------------------------------------------------------|
|`REDIS`   |The public endpoint copied from the Redis Overview tab|
|`USERNAME`|The username you set when creating the database       |
|`PASSWORD`|The password you set when creating the database       |

1. Click **Create namespace**.

-----

## 🧑‍✈️ Section 3 — Authenticate the Ground Crew: Connect Docker to the Registry

Before the image can be pushed, the Docker CLI must be authorised to write to the Scaleway Container Registry namespace that was automatically provisioned alongside your Containers namespace.

1. In the **Containers** section of the side menu, select **Container Registry**. The **Container Registry namespaces dashboard** displays.
1. In the **Namespaces** tab, select the namespace associated with your `hands-on-redis` deployment.

> **Tip:** Multiple namespaces may be listed. Select the one with the most recent modification timestamp — it corresponds to the namespace you just created.

1. In your terminal, authenticate Docker against the registry:

```bash
docker login <CONTAINER_NAMESPACE_REGISTRY_ENDPOINT> \
  -u nologin \
  --password-stdin <<< <SCW_SECRET_KEY>
```

> **Note:** Replace `<CONTAINER_NAMESPACE_REGISTRY_ENDPOINT>` with the registry endpoint from the **Namespace settings** tab, and `<SCW_SECRET_KEY>` with your Scaleway API secret key. The `-u nologin` flag is correct — Scaleway uses the secret key as the credential; the username is a fixed placeholder.

A `Login Succeeded` response confirms the Docker CLI is authorised to push.

-----

## 💾 Section 4 — Load the Payload: Build and Push the Container Image

With Docker authenticated, we build the image from the activity assets and push it to the registry.

1. In your terminal, navigate to the `06_databases/assets` folder of the cloned repository.
1. Build the image and push it in a single command:

```bash
DOCKER_BUILDKIT=1 docker build ./ \
  -t <CONTAINER_NAMESPACE_REGISTRY_ENDPOINT>/redis \
  --platform=linux/amd64 \
  && docker push <CONTAINER_NAMESPACE_REGISTRY_ENDPOINT>/redis
```

> **Note:** The `--platform=linux/amd64` flag ensures the image targets the correct server architecture. This is essential on Apple Silicon machines, where the local build architecture is `arm64` and will not run on `amd64` serverless infrastructure without this flag.

1. Return to the Console and open the **Images** tab of your Container Registry namespace. Verify that the `redis` image is listed.

The payload is in the hold. The mission vehicle is ready for deployment.

-----

## 🔑 Section 5 — Launch the Probe: Deploy and Invoke the Container

The image is in the registry. The namespace holds the credentials. It is time to deploy.

### 5.1 — Deploy the Container

1. In the **Serverless** section of the side menu, select **Containers**.
1. Select the `hands-on-redis` namespace.
1. Click **Deploy container**.
1. Choose **Scaleway** to use an image from your Scaleway Container Registry.
1. Open the **Registry namespace** drop-down and select the registry namespace you created for the Redis database.
1. Leave the default port as is.
1. Open the **Container** drop-down and select `redis`.
1. Open the **Tag** drop-down and select `latest`.
1. Set the container name to `redis-container`.
1. In the **Resources** section, allocate `70 mVCPU` of CPU and `128 MB` of memory.
1. Leave all other configuration options at their defaults.
1. Review the estimated cost.
1. Click **Deploy container**.

### 5.2 — Invoke the Container

1. In the **Overview** tab of your container, copy the **endpoint URL**.
1. Wait for the container status to change from `Deploying` to `Running`.
1. In your terminal, invoke the endpoint:

```bash
curl <endpoint>
```

A successful response confirms that the container is live, the runtime executed, and — through the environment variables injected at the namespace level — the container has the credentials it needs to reach the Redis instance.

> **Tower confirms:** The container is stateless. The Redis instance is stateful. Together, they form a complete unit: the container handles the request logic; Redis holds the state that persists between invocations. This separation is the architectural discipline that makes serverless backends scalable.

-----

## 🗑️ Section 6 — End of Mission: Delete All Resources

Once the invocation is confirmed, decommission all resources created in this episode.

Delete in the following order to avoid dependency errors:

1. **Container** — delete `redis-container` from the `hands-on-redis` namespace
1. **Containers namespace** — delete `hands-on-redis` from Serverless Containers
1. **Container Registry namespace** — delete the associated registry
1. **Redis Database Instance** — delete `hands-on-redis` from Managed Databases

> ⚠️ **Security Protocol — Restricted:** Deleting the Redis Database Instance is irreversible. All stored data is permanently destroyed. Confirm that no data in the instance is needed before proceeding.

-----

## 🗺️ Managed Database Architecture — The Mission Memory Map

```
┌────────────────────────────────────────────────────────────────┐
│              ORGANISATION — default project                    │
│                                                                │
│  MANAGED DATABASE                                              │
│  hands-on-redis (RED1-MICRO, Standalone, AMS-1)               │
│  Endpoint:  <host>:<port>  (Public network, TLS disabled)      │
│  Auth:      USERNAME / PASSWORD                                │
│                                                                │
│  CONTAINER REGISTRY                                            │
│  Namespace: hands-on-redis (Amsterdam)                         │
│  Image:     redis:latest (linux/amd64)                         │
│                                                                │
│  SERVERLESS CONTAINER                                          │
│  Namespace: hands-on-redis (Amsterdam)                         │
│  Container: redis-container (70 mVCPU / 128 MB)               │
│  Env vars:  REDIS / USERNAME / PASSWORD                        │
│  Endpoint:  https://<container_endpoint>                       │
│                                                                │
│  DATA FLOW                                                     │
│  curl <endpoint>  ──▶  redis-container  ──▶  hands-on-redis   │
│                         (stateless)           (stateful)       │
└────────────────────────────────────────────────────────────────┘
```

-----

## 📋 Episode Debrief

*“Memory secured. Credentials protected. The container knows where to look, and the database is ready to answer. International Rescue never loses its mission records.”*
*— Tin-Tin Kyrano, Thunderbird Island Operations*

In this episode, you have:

- ✅ Provisioned a `RED1-MICRO` Managed Redis Database Instance in `Amsterdam 1`
- ✅ Configured standalone mode with a username, password, and public endpoint
- ✅ Created a Serverless Containers namespace with `REDIS`, `USERNAME`, and `PASSWORD` environment variables
- ✅ Authenticated the Docker CLI against the Scaleway Container Registry
- ✅ Built a `linux/amd64` container image from the activity assets and pushed it to the registry
- ✅ Deployed the container with `70 mVCPU` and `128 MB` of memory
- ✅ Invoked the live endpoint via `curl` and confirmed a successful response
- ✅ Deleted all resources in the correct dependency order
- ✅ Mapped the full managed database integration pipeline through the SIPOC model

The memory unit is installed. In the next episode, we turn to networking — configuring Virtual Private Clouds, Private Networks, and the routing rules that connect everything we have built so far.

-----

## 📡 Further Transmissions

- [Scaleway Managed Databases — Redis documentation](https://www.scaleway.com/en/docs/managed-databases/redis/)
- [Scaleway Serverless Containers documentation](https://www.scaleway.com/en/docs/serverless/containers/)
- [Scaleway Container Registry documentation](https://www.scaleway.com/en/docs/containers/container-registry/)
- [Redis data types reference](https://redis.io/docs/data-types/)
- [Docker BuildKit documentation](https://docs.docker.com/build/buildkit/)

-----

*Estimated reading time: 11 minutes. Estimated hands-on time: 45–60 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
