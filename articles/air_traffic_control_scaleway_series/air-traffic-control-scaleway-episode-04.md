---
title: "Air Traffic Control Scaleway Ep.4"
part: 4
published: false
description: "Episode 4 of the Air Traffic Control series: deploy serverless functions and containers on Scaleway — write inline Python, build a Docker image, push it to a registry, and invoke both from your terminal. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, serverless, containers]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-04.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Unmanned Missions: Serverless Functions and Containers on Scaleway

*“Thunderbird 3 can reach Space Station Alpha without a human crew aboard. The mission executes, the payload is delivered, and the vehicle returns — all without a pilot in the seat. That is the principle behind every unmanned probe International Rescue has ever launched.”*
*— Brains, Thunderbird Island Research Division*

-----

Welcome back to the **Scaleway Air Traffic Control Centre**.

In Episode 2, we launched a crewed aircraft — a full Compute Instance that required a pilot, an SSH key, and a standing security perimeter. In this episode, we go unmanned.

**Serverless** means no server to provision, no OS to patch, no idle compute to pay for. You supply the code or the container image; the platform handles everything else. Your function executes on demand and disappears when it is done — like a probe that launches, completes its mission, and vacates the runway in seconds.

Scaleway offers two serverless primitives: **Functions** (event-driven code, deployed inline) and **Containers** (packaged Docker images, deployed from a private registry). By the end of this episode, you will have deployed, invoked, and decommissioned both.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Create a **namespace** for a serverless function
- Deploy a **serverless function** using the inline Python editor
- **Invoke** the function via `curl` and inspect the JSON response
- **Delete** the function cleanly
- Create a **namespace** for a serverless container with its associated registry
- Authenticate your **Docker CLI** against the Scaleway Container Registry
- **Build and push** a container image to the registry
- **Deploy** a serverless container from the registry
- **Invoke** the container via `curl`
- **Delete** the container and its namespace

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own
- ✅ You have already generated an API key (from Episode 1)
- ✅ You have [cURL](https://everything.curl.dev/get) installed on your machine
- ✅ Docker is running on your machine

> **Note:** For this activity, you will work in your Organisation’s `default` project.

-----

## 📊 SIPOC — How Serverless Flows Through the System

Two deployment paths. One SIPOC covers both — the pipeline structure is identical; only the artifact type differs.

|Stage|SIPOC Element|Serverless Equivalent                                                                     |Example                                                                    |
|-----|-------------|------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway Serverless Compute engine + Container Registry                                   |The platform runtime and image storage layer                               |
|**I**|**Input**    |Function code or container image, namespace config, runtime selection, resource allocation|Python handler, `caastp` Docker image, `100 mVCPU / 128 MB`                |
|**P**|**Process**  |Create namespace → Write or push artifact → Deploy → Invoke → Delete                      |All the hands-on steps in this episode                                     |
|**O**|**Output**   |A live, invocable endpoint that returns a JSON payload on demand                          |`curl https://<function_endpoint>` returns `{"event": ..., "context": ...}`|
|**C**|**Consumer** |Applications, CI/CD pipelines, API consumers, and event-driven automation                 |Your terminal, your integration layer, your downstream services            |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   Python code     ──▶  Create NS        ──▶  Live HTTPS    ──▶   Terminal
Serverless           or Docker image       Deploy artifact       endpoint              CI/CD
engine               Namespace cfg         Invoke via curl       JSON response         pipelines
                     Runtime choice        Delete cleanly                              Applications
Container            Resource alloc
Registry
```

> **Tower to crew:** Functions and Containers share the same operational pattern — namespace, deploy, invoke, delete. The difference is the artifact: inline code versus a packaged image. Master one and the other follows naturally.

-----

## 🛫 Part 1 — The Inline Probe: Deploy a Serverless Function

A serverless function is the simplest possible unmanned mission. You write the handler, select a runtime, and the platform does the rest. No Dockerfile, no registry, no build pipeline.

### 1.1 — Create a Namespace and Deploy the Function

1. In the **Serverless Compute** menu, select **Functions**.
1. Click **+ Create namespace**.

> **Note:** Alternatively, open the **Create** menu and select **Functions Namespace**.

1. In the **① Name & Description** section, enter a name — for example, `hands-on-serverless-functions`.
1. In the **② Region** section, choose `Paris`.
1. Click **Create namespace and add a function**.
1. In the **① Function Configuration** section, select the latest version of the `Python` runtime.
1. In the **② Function code** section, click **Inline code editor** and enter the following handler:

```python
def handle(event, context):
    return {
        "body": {
            "event": event,
            "context": context,
        },
        "statusCode": 200,
    }
```

This function accepts any incoming event, packages it alongside its execution context, and returns both as a JSON body with a `200 OK` status. It is a diagnostic probe — it tells you exactly what the platform passed in.

1. In the **② Name & Description** section, enter a name — for example, `hands-on-serverless-function`.
1. Leave **③ Provision resources** and **④ Configure scaling** at their default settings.
1. In the **⑤ Advanced options** section, browse the available tabs. Note in particular the option to configure a **privacy policy** for your function — this controls whether the endpoint requires authentication or is publicly invocable. Leave all values at their defaults for now.
1. Review the **Summary** panel on the right — it shows a live cost estimate as you configure the function.
1. Click **Create function**.

> **Note:** Deployment takes a few moments. Track progress in the **Overview** tab — wait for the status to show `Ready` before invoking.

### 1.2 — Invoke the Function

1. In the **Serverless Compute** menu, select **Functions**.
1. Click your **Namespace**, then click your **Function**.
1. In the **Overview** tab, copy the **Function endpoint** URL.
1. In your terminal, invoke the function:

```bash
curl https://<function_endpoint>
```

You will receive a JSON payload containing both the `event` and `context` objects that the platform passed to your handler. The probe has reported back.

> **Tower confirms:** A `200 OK` response with a structured JSON body confirms the function is live, the runtime executed your code, and the endpoint is reachable. If you receive no response or an error, verify that the function status is `Ready` in the Console before retrying.

### 1.3 — Delete the Function

1. In the **Serverless Compute** menu, select **Functions**.
1. Click your **Namespace**, then click your **Function**.
1. In the **Settings** tab, click **Delete function**.

> **Note:** Alternatively, use the **Actions** drop-down menu and choose **Delete function**.

1. Type `DELETE` to confirm.
1. Click **Delete function**.

The probe has been stood down. The namespace remains — we will leave it in place for reference.

-----

## 🏗️ Part 2 — The Packaged Probe: Deploy a Serverless Container

A serverless container is a more self-contained mission vehicle. You build a Docker image, push it to Scaleway’s Container Registry, and deploy it as a managed container. The platform handles orchestration; you control the image.

### 2.1 — Create a Container Namespace

1. In the **Serverless Compute** menu, select **Containers**.
1. Click **+ Deploy container**.

> **Note:** Alternatively, open the **Create** menu and select **Containers Namespace**.

1. In the **① Name & Description** section, enter a name — for example, `hands-on-serverless-containers`.
1. In the **② Region** section, choose `Paris`.
1. Click **Create namespace only**.

> **Note:** Scaleway automatically provisions a private Container Registry namespace alongside your Containers namespace. This is where your images will live.

### 2.2 — Authenticate Docker Against the Registry

Before you can push an image, your Docker CLI must be authorised to write to the Scaleway registry.

1. In the **Containers** menu, select **Container Registry**.
1. Click your **Namespace**, then open the **Overview** tab.
1. Copy the **Registry endpoint**.
1. In your terminal, authenticate using your API secret key:

```bash
docker login <registry_endpoint> -u nologin --password-stdin <<< <your_secret_key>
```

> **Note:** A `Login Succeeded` response confirms that Docker is authenticated. The `-u nologin` flag is correct — Scaleway uses the secret key as the password; the username is a placeholder.

### 2.3 — Build and Push the Container Image

1. In your terminal, build the image and push it to the registry in a single command:

```bash
DOCKER_BUILDKIT=1 docker build ./assets/serverless-containers \
  -t <registry_endpoint>/caastp \
  --platform=linux/amd64 \
  && docker push <registry_endpoint>/caastp
```

> **Note:** The `--platform=linux/amd64` flag ensures the image is built for the correct target architecture regardless of your local machine (Apple Silicon users in particular need this). `DOCKER_BUILDKIT=1` enables the faster BuildKit engine.

1. In the **Containers** menu, select **Container Registry**.
1. Click your registry namespace name.

> **Note:** The registry name is the segment after the `/` in your endpoint. For example, in `rg.fr-par.scw.cloud/hands-on-serverless-containers`, the registry name is `hands-on-serverless-containers`.

1. Select the **Images** tab and verify that `caastp` is listed. The payload pod is loaded and ready for deployment.

### 2.4 — Deploy the Container

1. In the **Serverless Compute** menu, select **Containers**.
1. Click your **Namespace**, then open the **Overview** tab.
1. Click **Deploy container**.
1. Choose **Scaleway** to use the associated Container Registry.
1. Keep **Registry Region** as `Paris`.
1. In the **Registry Namespace** drop-down, select your registry endpoint.

> **Tip:** The Functions registry namespace also appears in this list. Confirm you are selecting the Containers registry — the names are distinct but easy to confuse under time pressure.

1. In the **Image** drop-down, choose `caastp`.
1. In the **Tag** drop-down, choose `latest`.
1. Keep **Port** as `8080`.
1. Name the container `my-container`.
1. In the **CPU** drop-down, choose `100 mVCPU`.
1. In the **Memory** drop-down, choose `128 MB`.
1. Leave all other configuration options at their defaults.
1. Review the **Estimated cost** panel on the right.
1. Click **Deploy container**.

### 2.5 — Invoke the Container

1. In the **Serverless Compute** menu, select **Containers**.
1. Click your **Namespace**, then click your container.
1. In the **Overview** tab, copy the **Container endpoint** URL.
1. In your terminal, invoke the container:

```bash
curl https://<container_endpoint>
```

The container responds over HTTPS on port 8080, routed transparently through the Scaleway serverless layer. No exposed port management, no load balancer configuration, no TLS certificate to provision.

### 2.6 — Delete the Container

1. In the **Serverless Compute** menu, select **Containers**.
1. Click your **Namespace**, then click your container.
1. In the **Settings** tab, click **Delete container**.

> **Note:** Alternatively, use the **Actions** drop-down menu and choose **Delete container**.

1. Type `DELETE` to confirm.
1. Click **Delete container**.

The packaged probe has been stood down. The runway is clear.

-----

## 🗺️ Serverless Architecture — The Deployment Map

Both paths through this episode produce the same operational outcome — a live HTTPS endpoint, invocable on demand, with no standing compute cost. The architecture that delivered them looks like this:

```
┌────────────────────────────────────────────────────────────────┐
│              ORGANISATION — default project                    │
│                                                                │
│  SERVERLESS FUNCTIONS                                          │
│  Namespace: hands-on-serverless-functions (Paris)             │
│  Function:  hands-on-serverless-function                       │
│  Runtime:   Python (latest)                                    │
│  Endpoint:  https://<function_endpoint>                        │
│  Response:  JSON {event, context} — HTTP 200                   │
│                                                                │
│  SERVERLESS CONTAINERS                                         │
│  Namespace: hands-on-serverless-containers (Paris)            │
│  Registry:  rg.fr-par.scw.cloud/<namespace>                   │
│  Image:     caastp:latest (linux/amd64)                        │
│  Container: my-container (100 mVCPU / 128 MB / port 8080)     │
│  Endpoint:  https://<container_endpoint>                       │
└────────────────────────────────────────────────────────────────┘
```

-----

## 📋 Episode Debrief

*“The probe launched, completed its mission, and returned a confirmed signal. No crew. No standing infrastructure. No wasted resources. That is the efficiency International Rescue demands of every unmanned system.”*
*— Jeff Tracy, Thunderbird Island Operations Centre*

In this episode, you have:

- ✅ Created a Functions namespace in the Paris region
- ✅ Deployed an inline Python handler as a serverless function
- ✅ Invoked the function via `curl` and received a structured JSON response
- ✅ Deleted the function cleanly via the Console
- ✅ Created a Containers namespace with its associated Container Registry
- ✅ Authenticated the Docker CLI against the Scaleway registry using your API secret key
- ✅ Built a container image for `linux/amd64` and pushed it to the registry
- ✅ Deployed the container with `100 mVCPU` and `128 MB` memory
- ✅ Invoked the container via `curl` over HTTPS
- ✅ Deleted the container via the Console
- ✅ Mapped the full serverless deployment lifecycle through the SIPOC model

Two unmanned probes deployed, invoked, and stood down. In the next episode, we provision managed storage — adding a persistent data layer to the zones and clearances already in place.

-----

## 📡 Further Transmissions

- [Scaleway Serverless Functions documentation](https://www.scaleway.com/en/docs/serverless/functions/)
- [Scaleway Serverless Containers documentation](https://www.scaleway.com/en/docs/serverless/containers/)
- [Scaleway Container Registry documentation](https://www.scaleway.com/en/docs/containers/container-registry/)
- [Scaleway Serverless — pricing](https://www.scaleway.com/en/pricing/serverless/)
- [Docker BuildKit documentation](https://docs.docker.com/build/buildkit/)

-----

*Estimated reading time: 12 minutes. Estimated hands-on time: 45–60 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
