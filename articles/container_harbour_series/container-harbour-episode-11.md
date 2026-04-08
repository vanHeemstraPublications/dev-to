---
title: "Welcome to Container Harbour! 🚢 Ep.11"
part: 11
published: false
description: "Episode 11: The Health Inspector Visits — Liveness and Readiness Probes. Is your app alive? Is it READY? Are you SURE? Kubernetes sends in the inspectors."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-11.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 11: The Health Inspector Visits 🩺

### The App That Was "Running" But Absolutely Not Running 😤

Here is a scenario I have personally lived through. The app is deployed. All Pods show `1/1 Running`. The dashboard is green. Everyone goes home happy.

Three hours later: users can't log in. Support tickets. Slack messages. Everyone coming back.

The Pods? Still showing `1/1 Running`.

But the app? The app is stuck in a startup loop. It started. It initialised. It hit a database connection issue. It's running its event loop but every request returns HTTP 503. It's ALIVE but it's doing ABSOLUTELY NOTHING USEFUL.

Kubernetes doesn't know any of this. Kubernetes checked: "Is the process running?" Answer: yes. Kubernetes is satisfied. Kubernetes is WRONG.

This is why probes exist. This is why probes MATTER. Let's fix this. 🎯

---

## The SIPOC of Health Probes 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who defines the probes? | You, in the Pod spec |
| **Input** | What triggers a probe? | The kubelet on the node, on a schedule |
| **Process** | What happens? | kubelet runs the check (HTTP/TCP/exec), evaluates success/failure |
| **Output** | What comes out? | Pod is restarted (liveness) or removed from Service endpoints (readiness) |
| **Consumer** | Who benefits? | End users who get healthy Pods; Services that only route to ready Pods |

---

## Three Types of Probes, Three Questions 🔍

| Probe | Question | On failure |
|---|---|---|
| **Liveness** | "Is this container alive?" | Restart the container |
| **Readiness** | "Is this container ready for traffic?" | Remove from Service endpoints |
| **Startup** | "Has this container finished starting?" | Give it more time before liveness kicks in |

---

## Liveness Probe: "Are You Even Alive?" 💓

The liveness probe answers: "Should we restart this container?"

```yaml
spec:
  containers:
  - name: web-app
    image: my-app:latest

    livenessProbe:
      httpGet:                      # Method 1: HTTP GET
        path: /healthz              # Hit this endpoint
        port: 8080
        httpHeaders:
        - name: Custom-Header
          value: liveness-check
      initialDelaySeconds: 15       # Wait 15s before first check (startup time)
      periodSeconds: 20             # Check every 20 seconds
      timeoutSeconds: 5             # Fail if no response within 5 seconds
      failureThreshold: 3           # Restart after 3 consecutive failures
      successThreshold: 1           # 1 success = alive (default)
```

```yaml
    # Method 2: TCP Socket (does the port respond?)
    livenessProbe:
      tcpSocket:
        port: 5432                  # Great for databases that don't have HTTP
      initialDelaySeconds: 30
      periodSeconds: 10

    # Method 3: Exec (run a command inside the container)
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy              # App writes this file when healthy
      initialDelaySeconds: 5
      periodSeconds: 5
```

---

## Readiness Probe: "Are You READY For Traffic?" 🚦

The readiness probe answers: "Should the Service send traffic to this Pod?"

A Pod can be alive (liveness passes) but not ready (readiness fails). For example: the app started, but it's still loading its cache, or warming up connections, or running database migrations.

```yaml
    readinessProbe:
      httpGet:
        path: /ready                # Different endpoint from /healthz!
        port: 8080
      initialDelaySeconds: 5        # Can be shorter than liveness
      periodSeconds: 10
      failureThreshold: 3
      successThreshold: 1
```

```bash
# When readiness fails:
kubectl get pods
# NAME             READY   STATUS    RESTARTS
# web-app-abc123   0/1     Running   0         <- 0/1 = not ready! Running but excluded from traffic.

kubectl get endpoints web-app
# NAME      ENDPOINTS
# web-app   10.244.2.8:80   <- Pod abc123 is NOT listed here. Traffic goes elsewhere.
```

The Service sees `0/1 Ready` and stops routing to that Pod. The Pod isn't restarted — it's just isolated until it recovers. Beautiful. 🎯

---

## Startup Probe: "Give Me a Minute, Will You?!" ⏰

For slow-starting applications (JVM apps, legacy monoliths, anything that takes ages to boot), the startup probe buys time before liveness kicks in:

```yaml
    # Startup probe: runs INSTEAD of liveness until it succeeds
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30          # Allow up to 30 * 10 = 300 seconds to start
      periodSeconds: 10             # Check every 10 seconds

    # Liveness probe: kicks in AFTER startup probe succeeds
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      periodSeconds: 15
      failureThreshold: 3
```

Without startup probe, a slow app might fail liveness before it's even ready and get stuck in a restart loop. With startup probe, Kubernetes waits patiently, THEN starts watching with liveness. Elegant. 🧠

---

## Building a Health Endpoint: What Should /healthz Return? 🏗️

Here's a minimal health endpoint in Python/Flask that your liveness probe can call:

```python
# app.py
from flask import Flask, jsonify
import psycopg2
import os
import time

app = Flask(__name__)
startup_time = time.time()

@app.route('/healthz')
def liveness():
    """Liveness: Is the app process running and not deadlocked?"""
    return jsonify({"status": "alive", "uptime": time.time() - startup_time}), 200

@app.route('/ready')
def readiness():
    """Readiness: Is the app fully operational and ready for traffic?"""
    checks = {}
    status_code = 200

    # Check database connectivity
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            connect_timeout=3
        )
        conn.close()
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        status_code = 503

    # Check if we've finished initialising
    if time.time() - startup_time < 10:  # Still warming up
        checks['startup'] = 'warming_up'
        status_code = 503
    else:
        checks['startup'] = 'complete'

    return jsonify({"status": "ready" if status_code == 200 else "not_ready", "checks": checks}), status_code

@app.route('/')
def index():
    return "Hello from Container Harbour!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

```yaml
# Deployment using all three probes:
spec:
  containers:
  - name: api
    image: my-api:latest
    ports:
    - containerPort: 8080
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 20
      periodSeconds: 5
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 0       # Startup probe handles the delay
      periodSeconds: 15
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 10
      failureThreshold: 3
```

---

## Watching Probes in Action 👀

```bash
# Watch probe failures triggering restarts:
kubectl get pods --watch
# NAME             READY   RESTARTS
# web-app-abc123   1/1     0
# web-app-abc123   0/1     0          <- readiness failed, removed from traffic
# web-app-abc123   0/1     1          <- liveness failed 3 times, restarted
# web-app-abc123   1/1     1          <- restarted, healthy again

# See probe events in pod description:
kubectl describe pod web-app-abc123
# Events:
#   Warning  Unhealthy  Liveness probe failed: HTTP probe failed with statuscode: 503
#   Warning  Unhealthy  Readiness probe failed: Get "http://10.244.1.5:8080/ready": dial tcp connection refused
#   Normal   Killing    Container web-app failed liveness probe, will be restarted

# Check restart count history:
kubectl get pods -o custom-columns='NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount'
```

---

## The Harbourmaster's Log — Entry 11 📋

*Deployed health inspectors to all containers today. The results were... illuminating.*

*Three containers were "running" but their health endpoints returned 503. They had been silently failing for weeks. The Service was still routing traffic to them. Users were getting intermittent errors that nobody could reproduce.*

*Added readiness probes. Those three containers immediately dropped out of the Service endpoints. The intermittent errors stopped.*

*Then we fixed the underlying issues. The containers passed their readiness probes. Traffic resumed.*

*It took an afternoon. It fixed a problem that had been logged for six weeks as "cannot reproduce."*

*The health inspector, it turns out, is more useful than the five-page incident report.* 🎩

---

## Your Mission 🎯

1. Build a simple web app with `/healthz` and `/ready` endpoints
2. Make `/ready` return 503 for the first 20 seconds, then 200
3. Deploy it with all three probes configured
4. Watch `kubectl get pods --watch` as the startup probe runs, then readiness transitions from `0/1` to `1/1`

**Bonus:** Deliberately break the liveness endpoint (return 500 after N requests). Watch the Pod get restarted automatically.

---

## Next Time 🎬

**Episode 12**: Rush Hour at the Harbour — **Autoscaling**. Traffic doubles overnight. Do you wake up at 3am to manually scale? No. HPA does it for you. 📈

---

**🎯 Key Takeaways:**

- **Liveness probe**: "Is the container alive?" → Failure = restart the container
- **Readiness probe**: "Is the container ready for traffic?" → Failure = remove from Service endpoints
- **Startup probe**: "Has the container finished starting?" → Buys time for slow starters
- `0/1 Running` = Pod running but not ready. Check readiness probe and its endpoint.
- `RESTARTS > 0` = liveness has been failing. Check logs from the previous instance with `--previous`.
- Your `/healthz` and `/ready` endpoints should be FAST (<1 second response time). Probes time out!
- `periodSeconds`, `failureThreshold`, `initialDelaySeconds` — tune these. Defaults are rarely right.
- Always have probes in production. Always. 🩺
