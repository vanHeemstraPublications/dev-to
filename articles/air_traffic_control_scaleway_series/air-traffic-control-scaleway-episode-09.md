---
title: "Air Traffic Control Scaleway Ep.9"
part: 9
published: false
description: "Episode 9 of the Air Traffic Control series: activate Scaleway Cockpit, configure the Grafana agent, push custom metrics and logs, view them in the managed dashboard, and deactivate cleanly. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, observability, grafana]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-09.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Eyes on the Fleet: Observability with Scaleway Cockpit

*“Thunderbird 5 does not sleep. From its orbital station, it monitors every frequency, every signal, every anomaly. International Rescue does not wait for an emergency to be reported — it watches, continuously, so that it can respond before a situation becomes a crisis.”*
*— John Tracy, Thunderbird 5 Orbital Station*

-----

Welcome to the final episode of the **Scaleway Air Traffic Control Centre**.

Across the previous eight episodes, we built infrastructure: IAM policies, compute instances, bare metal, serverless functions and containers, object storage, managed databases, private networks, and Kubernetes clusters. We provisioned it, configured it, and cleaned it up.

But infrastructure without observability is a fleet flying blind. You cannot know whether a service is healthy, a resource is under pressure, or a failure is about to occur unless you are watching. **Cockpit** is Scaleway’s managed observability platform — a pre-integrated stack built on Grafana, Prometheus, and Loki that gives you metrics, logs, and traces in a single dashboard without any infrastructure to manage.

This episode is also different in one other respect. It is the last of the hands-on activities in the Scaleway Foundations series — and it is designed to develop a skill you will need for everything that follows: the ability to read the documentation, find what you need, and apply it independently. The steps below will guide you, but the detail comes from the Scaleway documentation itself.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Navigate the **Scaleway Product Documentation** website and use it as your primary reference
- Activate **Cockpit** in your Organisation
- Retrieve your **Grafana credentials**
- Generate a **Cockpit token** for data ingestion
- Configure the **Grafana agent** using pre-prepared `conf.yaml` and `docker-compose.yaml` files
- Send **metrics and logs** to your Cockpit from a Docker-hosted agent
- View the incoming data in the **managed Grafana dashboard**
- **Deactivate Cockpit** cleanly when the activity is complete

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own
- ✅ You have configured an SSH key for the `default` project
- ✅ Docker Desktop is running on your machine
- ✅ You have cloned the [`scw-certifications`](https://github.com/scaleway/scw-certifications/) repository — the `09_observability/assets/` folder contains the pre-prepared `conf.yaml` and `docker-compose.yaml` files

> **Note:** For this activity, you will work in your Organisation’s `default` project.

-----

## 📊 SIPOC — How Observability Flows Through the System

|Stage|SIPOC Element|Observability Equivalent                                                                                              |Example                                                               |
|-----|-------------|----------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway Cockpit engine + Grafana agent running in Docker                                                             |Managed Grafana, Prometheus remote write endpoint, Loki log endpoint  |
|**I**|**Input**    |Cockpit token, `conf.yaml` agent configuration, `docker-compose.yaml`                                                 |Token inserted into `conf.yaml`, agent scraping local metrics and logs|
|**P**|**Process**  |Activate Cockpit → Retrieve credentials → Generate token → Configure agent → Start agent → View dashboard → Deactivate|All the hands-on steps in this episode                                |
|**O**|**Output**   |Live metrics and log streams visible in the managed Grafana dashboard                                                 |CPU, memory, and log data from the local agent appearing in Cockpit   |
|**C**|**Consumer** |Platform engineers, SREs, and on-call operators who need visibility into running infrastructure                       |Your browser, your dashboard, your alerting rules                     |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   Cockpit token   ──▶  Activate Cockpit ──▶  Live metrics  ──▶   Platform
Cockpit              conf.yaml             Retrieve creds        and logs in           engineers
engine               docker-               Generate token        Grafana               SREs
                     compose.yaml          Configure agent       dashboard             On-call
Grafana agent                              Start agent                                 operators
(Docker)                                   View dashboard
                                           Deactivate
```

> **Tower to crew:** This episode uses the Scaleway documentation as the authoritative source of truth for all steps. Where the steps below say “follow the documentation”, that is intentional — reading product documentation is a professional skill, and this activity is designed to build it.

-----

## 🛫 Section 1 — Read the Manual: Navigate the Documentation

Before activating anything, find your reference materials.

1. In your browser, navigate to:

```
https://www.scaleway.com/en/docs/
```

1. Place your cursor in the search bar and enter `Cockpit`.
1. In the list of suggestions, select the **Cockpit Quickstart**.

> **Tip:** Every Scaleway product has a Quickstart — a concise, task-oriented guide that covers activation, basic configuration, and first use. When encountering a new Scaleway product for the first time, the Quickstart is always the right starting point. It tells you what you need, what it costs, and how to get from zero to operational in the shortest possible path.

1. Read the **Requirements** section of the Quickstart carefully before proceeding. Confirm that all prerequisites are met.

-----

## 🏗️ Section 2 — Power Up the Radar: Activate Cockpit

Follow the **How to activate your Cockpit** section of the Quickstart.

The activation process enables the Cockpit service for your Organisation’s `default` project. Once active, Cockpit provisions:

- A **Grafana** instance for dashboarding and alerting
- A **Prometheus**-compatible endpoint for metrics ingestion
- A **Loki**-compatible endpoint for log ingestion

> **Tower to crew:** Cockpit is activated per project. If you want observability data from multiple projects in the same dashboard, each project must have Cockpit activated independently and the agent must be configured to push to the correct endpoint for each.

-----

## 🧑‍✈️ Section 3 — Identify the Crew: Retrieve Grafana Credentials

Follow the **How to retrieve your Grafana credentials** section of the Quickstart.

Scaleway generates a Grafana username and password for you when Cockpit is activated. These credentials are used to log into the managed Grafana interface — they are separate from your Scaleway Console login.

> **Tip:** Store these credentials immediately. Unlike an API key, Grafana credentials are not regenerated automatically, and the password may not be retrievable after initial display depending on the Console version you are using.

-----

## 🔒 Section 4 — Authorise the Signal: Generate a Token

Follow the **How to send metrics and logs to your Cockpit** section of the Quickstart up to and including the token generation step.

The token is the authentication credential used by the Grafana agent to push data to your Cockpit endpoints. It grants write access to the metrics and logs pipelines — it does not grant access to the Grafana dashboard itself.

> **Tower confirms:** Tokens and Grafana credentials serve different purposes and authenticate to different systems. The token is a machine credential: it is used by the agent running in Docker. The Grafana credentials are a human credential: they are used by you, in your browser. Keep them separate.

-----

## 💾 Section 5 — Configure the Ground Station: Set Up the Grafana Agent

The Grafana agent is a lightweight telemetry collector that runs alongside your workload, scrapes metrics and log streams, and forwards them to Cockpit’s remote write endpoints.

The `09_observability/assets/` folder of the `scw-certifications` repository contains two pre-prepared files:

|File                 |Purpose                                                               |
|---------------------|----------------------------------------------------------------------|
|`conf.yaml`          |Grafana agent configuration — defines what to scrape and where to push|
|`docker-compose.yaml`|Runs the Grafana agent as a Docker service                            |

### 5.1 — Update the Token

Open `conf.yaml` and replace the token placeholder with the token you generated in Section 4. Follow the [Configuring the Grafana agent](https://www.scaleway.com/en/docs/observability/cockpit/api-cli/configuring-grafana-agent/) documentation page for the exact field names and structure.

> **Note:** The token must be inserted accurately — a missing character or extra space will cause the agent to fail authentication silently, resulting in no data appearing in the dashboard. Double-check the value before starting the agent.

### 5.2 — Start the Agent

Follow the Grafana agent configuration documentation to start the agent using the `docker-compose.yaml` file. Once running, the agent begins scraping local metrics and forwarding them to your Cockpit endpoints.

-----

## 🌐 Section 6 — Watch the Radar: View Metrics in Grafana

Follow the remaining steps in the Quickstart to open the managed Grafana dashboard and verify that data is arriving.

1. Log in to Grafana using the credentials retrieved in Section 3.
1. Navigate to the pre-built dashboards for metrics and logs.
1. Confirm that data from the Grafana agent is visible — you should see time-series metrics and log entries appearing in real time.

> **Tower confirms:** If no data appears after a minute or two, check two things in order: first, confirm the agent container is running (`docker ps`); second, confirm the token in `conf.yaml` matches the one generated in Section 4 exactly. Those two causes account for the overwhelming majority of empty-dashboard situations.

-----

## 🗑️ Section 7 — Power Down the Radar: Deactivate Cockpit

Follow the [Deactivate Cockpit](https://www.scaleway.com/en/docs/observability/cockpit/how-to/deactivate-cockpit/) documentation page to deactivate the service.

Deactivation stops the Cockpit service for the project and removes the managed Grafana instance. Historical data that was pushed to the endpoints is not retained after deactivation.

> ⚠️ **Security Protocol — Restricted:** Deactivating Cockpit deletes the managed Grafana instance and all dashboards, alert rules, and data sources you configured within it. If you have built custom dashboards you wish to retain, export them as JSON before deactivating. Cockpit can be reactivated at any time — the service restarts cleanly, but previous configuration is not restored.

Also stop the Docker agent:

```bash
docker compose down
```

-----

## 🗺️ Observability Architecture — The Radar Map

```
┌────────────────────────────────────────────────────────────────┐
│              ORGANISATION — default project                    │
│                                                                │
│  COCKPIT                                                       │
│  Status:     Active                                            │
│  Grafana:    Managed instance (login with Grafana credentials) │
│  Metrics:    Prometheus-compatible remote write endpoint       │
│  Logs:       Loki-compatible push endpoint                     │
│                                                                │
│  GRAFANA AGENT (Docker)                                        │
│  Config:     09_observability/assets/conf.yaml                 │
│  Runtime:    docker-compose.yaml                               │
│  Auth:       Cockpit token (write access to metrics + logs)    │
│                                                                │
│  DATA FLOW                                                     │
│  Docker agent  ──▶  Cockpit endpoints  ──▶  Grafana dashboard │
│  (scrape)           (Prometheus / Loki)      (browser)         │
└────────────────────────────────────────────────────────────────┘
```

-----

## 📋 Episode Debrief

*“Thunderbird 5 never loses contact with the fleet. Metrics are flowing, logs are captured, and the dashboard is live. Eyes open, frequencies clear. International Rescue stands ready.”*
*— John Tracy, Thunderbird 5 Orbital Station*

In this episode, you have:

- ✅ Navigated the Scaleway Product Documentation website and located the Cockpit Quickstart
- ✅ Activated Cockpit for the `default` project
- ✅ Retrieved your managed Grafana credentials
- ✅ Generated a Cockpit token for agent authentication
- ✅ Updated `conf.yaml` with the token and started the Grafana agent via Docker Compose
- ✅ Verified that metrics and logs are visible in the managed Grafana dashboard
- ✅ Deactivated Cockpit and stopped the Docker agent
- ✅ Mapped the full observability pipeline through the SIPOC model

-----

This is the final episode of the **Air Traffic Control Scaleway Series**.

Across nine episodes, you have built and operated the full breadth of Scaleway’s infrastructure platform: identity and access management, compute instances, bare metal, serverless functions and containers, object storage, managed databases, private networking, managed Kubernetes — and now, observability. Every resource was provisioned deliberately, exercised hands-on, and decommissioned cleanly.

The control tower is yours. Thunderbirds are GO.

-----

## 📡 Further Transmissions

- [Scaleway Cockpit Quickstart](https://www.scaleway.com/en/docs/observability/cockpit/quickstart/)
- [Scaleway Cockpit documentation](https://www.scaleway.com/en/docs/observability/cockpit/)
- [Configuring the Grafana agent](https://www.scaleway.com/en/docs/observability/cockpit/api-cli/configuring-grafana-agent/)
- [Deactivate Cockpit](https://www.scaleway.com/en/docs/observability/cockpit/how-to/deactivate-cockpit/)
- [Grafana documentation](https://grafana.com/docs/)

-----

*Estimated reading time: 10 minutes. Estimated hands-on time: 45–60 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
