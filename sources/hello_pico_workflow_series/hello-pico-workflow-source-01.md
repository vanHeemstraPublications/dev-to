Yes. I would make “Hello, Pico!” the reference vertical slice for the whole Open Engineering runtime: enough behavior to exercise Rust, PyO3, Python, Wrangler, Crossplane, Kubernetes, Manifold, MQTT and Home Assistant, but still small enough that every stage is understandable.

The key is that “Hello, Pico!” should do more than print a string.

Target behavior

Our first Pico will have persistent-ish runtime state:

{
  "id": "hello-pico",
  "version": "0.1.0",
  "status": "ready",
  "message": "Hello, Pico!",
  "event_count": 0,
  "last_run": null
}

It accepts a hello event:

{
  "type": "hello",
  "name": "Willem"
}

and changes to:

{
  "id": "hello-pico",
  "version": "0.1.0",
  "status": "ready",
  "message": "Hello, Willem! I am Pico hello-pico.",
  "event_count": 1,
  "last_run": "..."
}

The state transition itself lives in Rust. Python exposes the runtime/API. Manifold hosts it. Wrangler manages its lifecycle. Crossplane creates the Kubernetes resources. MQTT publishes Pico state. Home Assistant shows it and can optionally trigger another hello event.

That exercises essentially the complete architecture.

⸻

1. Architecture we are building

Use this division:

                    AUTHOR / OPERATOR
                          │
                          ▼
                     ┌─────────┐
                     │ Wrangler│
                     └────┬────┘
                          │ create/update Pico XR
                          ▼
                Kubernetes API / Minikube
                          │
                   ┌──────▼───────┐
                   │  Crossplane  │
                   └──────┬───────┘
                          │ Composition
              ┌───────────┼────────────┐
              ▼           ▼            ▼
          ConfigMap   Deployment    Service
                          │
                          ▼
                 ┌────────────────┐
                 │    Manifold    │
                 │ Python runtime │
                 │       │        │
                 │      PyO3      │
                 │       │        │
                 │ Rust Pico Core │
                 └───────┬────────┘
                         │
                         │ MQTT events/state
                         ▼
                    ┌──────────┐
                    │Mosquitto │
                    └────┬─────┘
                         │
                         ▼
                 ┌────────────────┐
                 │ Home Assistant │
                 │                │
                 │ Hello Pico     │
                 │ Status: Ready  │
                 │ Message: ...   │
                 │ Events: 12     │
                 │ Last Run: ...  │
                 └────────────────┘

For this first course, one Pico = one Manifold runtime pod.

That’s intentionally simpler than the ultimate Manifold architecture. Later we can move many Picos into a persistent actor network without changing pico.yaml or Wrangler’s external model.

Crossplane 2.3 is currently the latest documented Crossplane release, and v2 makes namespaced XRs the normal pattern. A namespaced XR can compose resources in its own namespace, which fits Picos extremely well. 

⸻

2. Create the repository

I’d use:

hello-pico/
├── Cargo.toml
├── Cargo.lock
├── pyproject.toml
├── uv.lock
├── rust-toolchain.toml
├── Justfile
├── Dockerfile
│
├── crates/
│   ├── pico-core/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   │
│   └── pico-native/
│       ├── Cargo.toml
│       └── src/lib.rs
│
├── python/
│   ├── manifold/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── mqtt.py
│   │   └── settings.py
│   │
│   └── wrangler/
│       ├── __init__.py
│       └── cli.py
│
├── definitions/
│   └── pico.yaml
│
├── tests/
│   ├── test_native.py
│   ├── test_manifold.py
│   └── test_integration.py
│
├── platform/
│   ├── crossplane/
│   │   ├── function.yaml
│   │   ├── rbac.yaml
│   │   ├── xrd.yaml
│   │   └── composition.yaml
│   │
│   ├── home-assistant/
│   │   ├── namespace.yaml
│   │   ├── mosquitto.yaml
│   │   └── home-assistant.yaml
│   │
│   └── namespace.yaml
│
└── scripts/
    └── smoke-test.sh

⸻

3. Define the Pico declaratively

definitions/pico.yaml:

apiVersion: pico.open-engineering.io/v1alpha1
kind: Pico
metadata:
  name: hello-pico
  namespace: open-engineering
spec:
  id: hello-pico
  version: 0.1.0
  runtime:
    image: open-engineering/hello-pico:0.1.0
  state:
    status: ready
    message: "Hello, Pico!"
  handlers:
    - event: hello
      action: greet
  channels:
    mqtt:
      stateTopic: openengineering/pico/hello-pico/state
      commandTopic: openengineering/pico/hello-pico/command
      availabilityTopic: openengineering/pico/hello-pico/availability

Notice something important:

This contains no Deployment, Service, container port or replica count.

That’s the separation we want:

Pico Definition
      ↓
what it IS
Crossplane Composition
      ↓
how it RUNS

⸻

4. Implement the Rust Pico core

crates/pico-core/src/lib.rs:

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PicoState {
    pub id: String,
    pub version: String,
    pub status: String,
    pub message: String,
    pub event_count: u64,
    pub last_run: Option<DateTime<Utc>>,
}
pub struct HelloPico {
    state: PicoState,
}
impl HelloPico {
    pub fn new(id: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            state: PicoState {
                id: id.into(),
                version: version.into(),
                status: "ready".into(),
                message: "Hello, Pico!".into(),
                event_count: 0,
                last_run: None,
            },
        }
    }
    pub fn hello(&mut self, name: &str) -> PicoState {
        self.state.event_count += 1;
        self.state.last_run = Some(Utc::now());
        self.state.message =
            format!("Hello, {name}! I am Pico {}.", self.state.id);
        self.state.clone()
    }
    pub fn state(&self) -> PicoState {
        self.state.clone()
    }
}

Unit test:

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn hello_event_changes_state() {
        let mut pico = HelloPico::new("hello-pico", "0.1.0");
        let state = pico.hello("Willem");
        assert_eq!(
            state.message,
            "Hello, Willem! I am Pico hello-pico."
        );
        assert_eq!(state.event_count, 1);
        assert!(state.last_run.is_some());
    }
}

Run:

cargo test --workspace

This is Gate 1.

No Python, Kubernetes, MQTT or Crossplane is involved yet.

⸻

5. Add the PyO3 boundary

The PyO3 crate should be thin.

Conceptually:

Python
    HelloPico
       │
      PyO3
       │
       ▼
pico_core::HelloPico

pico-native owns the PyO3 object and protects Rust state with a mutex:

use pico_core::HelloPico as CorePico;
use pyo3::prelude::*;
use std::sync::Mutex;
#[pyclass]
struct HelloPico {
    inner: Mutex<CorePico>,
}
#[pymethods]
impl HelloPico {
    #[new]
    fn new(id: String, version: String) -> Self {
        Self {
            inner: Mutex::new(CorePico::new(id, version)),
        }
    }
    fn hello(&self, name: String) -> PyResult<String> {
        let mut pico = self
            .inner
            .lock()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err(
                "Pico state lock poisoned"
            ))?;
        serde_json::to_string(&pico.hello(&name))
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(e.to_string())
            })
    }
    fn state(&self) -> PyResult<String> {
        let pico = self
            .inner
            .lock()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err(
                "Pico state lock poisoned"
            ))?;
        serde_json::to_string(&pico.state())
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(e.to_string())
            })
    }
}
#[pymodule]
fn pico_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<HelloPico>()?;
    Ok(())
}

PyO3’s recommended packaging path remains maturin; maturin develop is specifically intended for this development loop. 

Run:

uv sync
source .venv/bin/activate
maturin develop

Then:

python - <<'PY'
from pico_native import HelloPico
pico = HelloPico("hello-pico", "0.1.0")
print(pico.state())
print(pico.hello("Willem"))
print(pico.state())
PY

Expected second message:

Hello, Willem! I am Pico hello-pico.

That’s Gate 2.

⸻

6. Add the Manifold runtime

Now Python becomes the host environment.

Install:

uv add fastapi uvicorn paho-mqtt pydantic-settings
uv add --dev pytest httpx ruff

The Manifold runtime exposes:

GET  /health
GET  /state
POST /events/hello

For example:

from fastapi import FastAPI
from pydantic import BaseModel
from pico_native import HelloPico
import json
app = FastAPI(title="Open Engineering Manifold")
pico = HelloPico(
    id="hello-pico",
    version="0.1.0",
)
class HelloEvent(BaseModel):
    name: str
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/state")
def state():
    return json.loads(pico.state())
@app.post("/events/hello")
def hello(event: HelloEvent):
    result = json.loads(pico.hello(event.name))
    publish_state(result)
    return result

Now locally:

uv run uvicorn manifold.app:app \
  --host 0.0.0.0 \
  --port 8080

Test:

curl http://localhost:8080/state

Then:

curl \
  -X POST \
  http://localhost:8080/events/hello \
  -H 'Content-Type: application/json' \
  -d '{"name":"Willem"}'

Expected:

{
  "id": "hello-pico",
  "version": "0.1.0",
  "status": "ready",
  "message": "Hello, Willem! I am Pico hello-pico.",
  "event_count": 1,
  "last_run": "..."
}

Notice the responsibility split:

FastAPI
  │
  │ HTTP/event transport
  ▼
Manifold
  │
  │ execution
  ▼
PyO3
  │
  ▼
Rust Pico
  │
  ▼
state transition

⸻

7. Add MQTT to Manifold

This is the right connection to Home Assistant.

Don’t make the Pico know anything about Home Assistant.

Instead:

Pico
 ↓
event/state
 ↓
Manifold
 ↓
MQTT
 ↓
Home Assistant

Use:

openengineering/pico/hello-pico/state
openengineering/pico/hello-pico/command
openengineering/pico/hello-pico/availability

Manifold publishes its state after every transition:

client.publish(
    "openengineering/pico/hello-pico/state",
    json.dumps(state),
    retain=True,
)

and subscribes to:

openengineering/pico/hello-pico/command

For example:

{
  "type": "hello",
  "name": "Home Assistant"
}

becomes:

if payload["type"] == "hello":
    state = json.loads(
        pico.hello(payload["name"])
    )
    publish_state(state)

That gives us both directions:

Pico ───── state ─────► Home Assistant
Pico ◄──── event ───── Home Assistant

⸻

8. Publish Home Assistant MQTT discovery

This is nicer than manually defining every HA sensor.

Home Assistant currently enables MQTT discovery by default once its MQTT integration is configured, using the default homeassistant discovery prefix. 

Manifold therefore publishes:

homeassistant/device/hello-pico/config

with a retained discovery message representing the Pico.

Expose:

Hello Pico
├── Status
├── Message
├── Version
├── Event Count
└── Last Run

The common state topic is:

openengineering/pico/hello-pico/state

Home Assistant device discovery is particularly suitable here because current HA guidance recommends device discovery where one device provides multiple components. 

So Pico becomes a Home Assistant Device, not five unrelated sensors.

That’s exactly the semantic model we want.

⸻

9. Test the Python binding

tests/test_native.py:

import json
from pico_native import HelloPico
def test_hello_event():
    pico = HelloPico("hello-pico", "0.1.0")
    result = json.loads(
        pico.hello("Willem")
    )
    assert result["event_count"] == 1
    assert result["message"] == (
        "Hello, Willem! I am Pico hello-pico."
    )

Run:

uv run pytest

⸻

10. Add our canonical development command

Now:

develop:
	maturin develop
	uv run pytest
check:
	cargo fmt --check
	cargo clippy --workspace --all-targets -- -D warnings
	cargo test --workspace
	uv run ruff check .
	uv run pytest
build:
	maturin build --release

Or preferably:

just develop
just check
just build

At this point OpenCode/Qwen3 gets a very clean instruction:

Implement the next Hello Pico feature. Do not consider the task complete until just check succeeds.

⸻

11. Build the actual wheel

Now leave development mode.

maturin build --release

You get roughly:

target/wheels/
└── hello_pico-0.1.0-...whl

Test the artifact, not source:

uv venv /tmp/hello-pico-test
source /tmp/hello-pico-test/bin/activate
pip install target/wheels/*.whl
python - <<'PY'
from pico_native import HelloPico
p = HelloPico("hello-pico", "0.1.0")
print(p.hello("Wheel"))
PY

This is Gate 3.

⸻

12. Build the Linux container

Since your development machine is Apple Silicon/macOS, do not copy your locally built macOS extension into Kubernetes.

Build the PyO3 wheel in Linux inside the Docker build.

Conceptually:

FROM python:3.13-slim AS builder
RUN apt-get update \
 && apt-get install -y curl build-essential \
 && curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip install maturin uv
WORKDIR /app
COPY . .
RUN maturin build --release
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/target/wheels /wheels
RUN pip install /wheels/*.whl
COPY python ./python
ENV PYTHONPATH=/app/python
CMD [
  "uvicorn",
  "manifold.app:app",
  "--host",
  "0.0.0.0",
  "--port",
  "8080"
]

Now start Minikube.

⸻

13. Start Minikube

On the Mac Mini:

minikube start \
  --driver=docker \
  --cpus=6 \
  --memory=12288

I’d give it around 12 GB initially because you’re going to run:

Crossplane
Crossplane Function
Manifold/Pico
Mosquitto
Home Assistant

plus Kubernetes itself.

Check:

kubectl get nodes

Expected:

NAME       STATUS   ROLES
minikube   Ready    control-plane

⸻

14. Build the image directly into Minikube

Use Minikube’s image build rather than an external registry:

minikube image build \
  -t open-engineering/hello-pico:0.1.0 \
  .

Verify:

minikube image ls | grep hello-pico

This gives us Gate 4: Linux OCI artifact exists inside the target runtime.

⸻

15. Install Crossplane

As of 19 August 2026, Crossplane’s current docs are v2.3. Crossplane recommends its Helm installation path. 

Run:

helm repo add crossplane-stable \
  https://charts.crossplane.io/stable
helm repo update

Then:

helm upgrade --install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace

Wait:

kubectl wait \
  --for=condition=Available \
  deployment/crossplane \
  -n crossplane-system \
  --timeout=180s

Check:

kubectl get pods -n crossplane-system

⸻

16. Install the Crossplane templating function

I would use function-go-templating.

It keeps the course readable because the Composition looks like Kubernetes YAML rather than a forest of patch transforms.

The project is specifically intended for composing Crossplane resources using Go/Helm-style templates. 

The latest surfaced 0.12 release is v0.12.3, released in June 2026. 

platform/crossplane/function.yaml:

apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-go-templating
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-go-templating:v0.12.3

Apply:

kubectl apply \
  -f platform/crossplane/function.yaml

Wait:

kubectl get functions

until:

INSTALLED=True
HEALTHY=True

Crossplane v2 compositions now use function pipelines for composition. 

⸻

17. Create the Open Engineering namespace

apiVersion: v1
kind: Namespace
metadata:
  name: open-engineering

Apply:

kubectl apply \
  -f platform/namespace.yaml

⸻

18. Define Pico as a Crossplane API

Now Open Engineering gets a real Kubernetes API:

pico.open-engineering.io/v1alpha1
kind: Pico

The XRD is namespaced.

That is intentional: Crossplane v2 recommends namespaced XRs for most APIs and allows them to compose resources within that namespace. 

Conceptually:

apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: picos.pico.open-engineering.io
spec:
  scope: Namespaced
  group: pico.open-engineering.io
  names:
    kind: Pico
    plural: picos
  defaultCompositionRef:
    name: pico-manifold
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                id:
                  type: string
                version:
                  type: string
                runtime:
                  type: object
                  properties:
                    image:
                      type: string
              required:
                - id
                - version
                - runtime

Apply:

kubectl apply \
  -f platform/crossplane/xrd.yaml

Verify:

kubectl get xrd

Wait for:

ESTABLISHED=True

⸻

19. Let Crossplane create the Manifold workload

The composition takes this:

kind: Pico
spec:
  id: hello-pico
  version: 0.1.0
  runtime:
    image: open-engineering/hello-pico:0.1.0

and creates:

Pico
 │
 ├── ConfigMap
 │     Pico configuration
 │
 ├── Deployment
 │     Manifold runtime
 │
 └── Service
       runtime API

This is where Crossplane provides real architectural value.

Crossplane compositions are explicitly intended to take one composite resource and turn it into multiple Kubernetes resources. 

⸻

20. Give Crossplane Kubernetes RBAC

Crossplane can create some Kubernetes resources itself, including Deployments, but its documentation says additional resource types may need explicitly aggregated RBAC. 

For clarity, grant exactly what this composition requires:

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: open-engineering-pico-crossplane
  labels:
    rbac.crossplane.io/aggregate-to-crossplane: "true"
rules:
  - apiGroups:
      - ""
    resources:
      - configmaps
      - services
    verbs:
      - "*"
  - apiGroups:
      - apps
    resources:
      - deployments
    verbs:
      - "*"

Apply:

kubectl apply \
  -f platform/crossplane/rbac.yaml

The aggregation label is important; Crossplane’s documentation specifically calls that out. 

⸻

21. Create the Composition

Pico becomes:

XR
 │
 ▼
Composition
 │
 ├── ConfigMap
 ├── Deployment
 └── Service

The Deployment uses:

image:
open-engineering/hello-pico:0.1.0

and gets environment variables such as:

PICO_ID=hello-pico
PICO_VERSION=0.1.0
MQTT_HOST=mosquitto.home-automation.svc.cluster.local
MQTT_PORT=1883

Also set:

imagePullPolicy: IfNotPresent

because the image exists inside Minikube rather than a public registry.

⸻

22. Install Mosquitto inside Minikube

Create:

namespace: home-automation

and deploy:

Mosquitto
port 1883

For the first course I’d permit anonymous MQTT inside this isolated Minikube cluster only.

Do not carry that configuration into production.

The internal DNS becomes:

mosquitto.home-automation.svc.cluster.local

That’s the hostname Manifold uses.

⸻

23. Install Home Assistant into Minikube

Use Home Assistant Container, not Home Assistant OS.

That’s an important distinction.

Home Assistant officially supports a container installation where you supply the container orchestration environment yourself; the trade-off is that Container installations don’t have HA OS Apps/Supervisor. 

That is fine because Kubernetes is our supervisor.

So:

Home Assistant Supervisor
        X
Kubernetes
        ✓

Deploy:

homeassistant/home-assistant

as a Deployment with:

replicas: 1
port: 8123

and a PVC:

/home-assistant/config

Use the current official image source:

ghcr.io/home-assistant/home-assistant:stable

⸻

24. Start Home Assistant

Wait:

kubectl get pods \
  -n home-automation

You should see:

home-assistant-...   Running
mosquitto-...        Running

Then:

kubectl port-forward \
  -n home-automation \
  svc/home-assistant \
  8123:8123

Open:

http://localhost:8123

Complete HA’s first-start setup.

⸻

25. Connect Home Assistant to MQTT

Inside Home Assistant:

Settings
→ Devices & services
→ Add Integration
→ MQTT

Broker:

mosquitto.home-automation.svc.cluster.local

Port:

1883

Home Assistant’s current MQTT integration supports an externally managed Mosquitto broker, and MQTT discovery is enabled by default. 

At this point HA is ready, but Hello Pico doesn’t exist yet.

That’s desirable.

We want Wrangler to cause its existence.

⸻

26. Wrangler now enters the architecture

This is the important semantic distinction:

kubectl
    generic Kubernetes tool
Wrangler
    Pico lifecycle tool

Wrangler should ultimately implement commands like:

wrangler pico create definitions/pico.yaml
wrangler pico get hello-pico
wrangler pico describe hello-pico
wrangler pico event hello-pico hello --name Willem
wrangler pico delete hello-pico

For MVP, Wrangler can use the Kubernetes Python client underneath.

But learners should never need to know that.

Wrangler owns:

Pico lifecycle
Pico validation
Pico conventions
Pico deployment
Pico inspection
Pico events

⸻

27. Create the Pico through Wrangler

Run:

wrangler pico create \
  definitions/pico.yaml

Underneath, this creates:

apiVersion: pico.open-engineering.io/v1alpha1
kind: Pico
metadata:
  name: hello-pico
  namespace: open-engineering
...

Crossplane sees it.

Then the actual chain happens:

Wrangler
   ↓
Pico XR
   ↓
Crossplane
   ↓
Composition
   ↓
ConfigMap
Deployment
Service
   ↓
Manifold starts
   ↓
PyO3 loads
   ↓
Rust Pico created

This is the central moment of the course.

⸻

28. Watch Crossplane reconcile it

Run:

kubectl get picos \
  -n open-engineering

Eventually:

NAME         SYNCED   READY
hello-pico   True     True

Then:

kubectl get all \
  -n open-engineering

You should see:

deployment/hello-pico
pod/hello-pico-...
service/hello-pico

And:

kubectl describe pico \
  hello-pico \
  -n open-engineering

Crossplane should report the composed resources.

⸻

29. Verify Manifold

Port-forward it:

kubectl port-forward \
  -n open-engineering \
  svc/hello-pico \
  8080:8080

Then:

curl http://localhost:8080/health

Expected:

{
  "status": "ok"
}

And:

curl http://localhost:8080/state

Expected:

{
  "id": "hello-pico",
  "version": "0.1.0",
  "status": "ready",
  "message": "Hello, Pico!",
  "event_count": 0,
  "last_run": null
}

We have now reached Gate 5:

Rust → PyO3 → Python → OCI → Crossplane → Kubernetes → Manifold works.

⸻

30. Home Assistant should discover Pico automatically

Manifold publishes its MQTT discovery definition and current state at startup.

Within Home Assistant:

Settings
→ Devices & services
→ MQTT

you should now find:

Hello Pico

with entities:

Status
ready
Message
Hello, Pico!
Version
0.1.0
Event Count
0
Last Run
unknown

This fulfills the earlier Open Engineering goal that the first Pico culminates in a declaratively composed Pico visible in Home Assistant, rather than merely terminal output.

⸻

31. Send the first real event through Wrangler

Now run:

wrangler pico event \
  hello-pico \
  hello \
  --name Willem

Wrangler sends:

{
  "type": "hello",
  "name": "Willem"
}

to Manifold.

Manifold executes:

Python
 ↓
PyO3
 ↓
Rust HelloPico::hello()

Rust returns:

{
  "message":
    "Hello, Willem! I am Pico hello-pico.",
  "event_count": 1,
  "last_run": "..."
}

Manifold publishes the changed state to MQTT.

Home Assistant changes automatically to:

Message
Hello, Willem! I am Pico hello-pico.
Event Count
1
Last Run
2026-08-19 ...

No polling.

No HA → REST API scraping.

It’s an actual event-driven system.

⸻

32. Make Home Assistant able to say Hello too

For the illustrative version, I’d add one more component:

button.hello_pico_say_hello

Its MQTT command topic is:

openengineering/pico/hello-pico/command

Pressing it sends:

{
  "type": "hello",
  "name": "Home Assistant"
}

Now the state becomes:

Hello, Home Assistant! I am Pico hello-pico.

and:

event_count = 2

This gives us a complete event cycle:

               ┌───────────────┐
               │Home Assistant │
               └───────┬───────┘
                       │
                       │ hello event
                       ▼
                   Mosquitto
                       │
                       ▼
                    Manifold
                       │
                       ▼
                     PyO3
                       │
                       ▼
                   Rust Pico
                       │
                 state transition
                       │
                       ▼
                    Manifold
                       │
                       ▼
                   Mosquitto
                       │
                       ▼
               ┌───────────────┐
               │Home Assistant │
               │ Event Count 2 │
               └───────────────┘

That’s an excellent teaching demo.

⸻

33. Add persistence after the basic version works

The next illustrative extension should be Pico state persistence.

Initially:

Pod restart
    ↓
state resets

Then introduce:

Manifold
   │
   ▼
/data/pico-state.json
   │
   ▼
PersistentVolumeClaim

So:

kubectl delete pod ...

followed by:

wrangler pico get hello-pico

still reports:

event_count: 7
message: ...
last_run: ...

This demonstrates one of the defining Pico ideas:

A Pico is a long-lived reactive entity, not merely a function invocation.

⸻

34. Add readiness to the Crossplane composition

The Deployment needs:

readinessProbe:
  httpGet:
    path: /health
    port: 8080

and:

livenessProbe:
  httpGet:
    path: /health
    port: 8080

Then Crossplane should not show:

READY=True

until the actual Manifold runtime is ready.

This gives you another important chain:

Rust loaded
 ↓
PyO3 loaded
 ↓
Manifold started
 ↓
health endpoint ready
 ↓
Kubernetes Deployment ready
 ↓
Crossplane Pico READY=True

So Pico Ready actually means something.

⸻

35. The final just interface

I would finish the repository with:

just setup

Install Rust/Python dependencies.

just develop

Run maturin develop.

just test

Run Cargo and Python tests.

just check

Run all formatting/lint/tests.

just build

Build the wheel.

just image

Build the Linux image into Minikube.

just platform

Install:

Crossplane
Composition Function
Home Assistant
Mosquitto
just deploy

Equivalent to:

wrangler pico create definitions/pico.yaml
just smoke

Verify:

XR Ready
Pod Ready
/health
/state
MQTT state

And:

just destroy

Deletes Hello Pico while retaining the platform.

⸻

36. OpenCode/Qwen3 workflow around all of this

This is where your current local AI setup becomes particularly valuable.

In Warp:

Pane 1                    Pane 2
opencode                  just check
   │
   ▼                      kubectl ...
MLXServe                  wrangler ...
   │
   ▼
Qwen3

Give Qwen3 tasks like:

Add persistent event counting to Hello Pico. Implement the logic in pico-core, expose only the necessary interface through pico-native, update Manifold, add tests, and run just check. Do not modify the Crossplane API unless necessary.

Then later:

Add MQTT Home Assistant discovery for Pico status, message, version, event count and last run. Run the integration tests and just check.

Then:

Update the Crossplane Composition to add health probes. Render or validate the Composition and verify Hello Pico reaches READY=True.

The LLM is therefore helping implement each lesson, while deterministic gates certify the result.

⸻

37. The full “Hello, Pico!” course progression

The course now naturally becomes:

PART I
The Pico
pico.yaml
    ↓
identity + state + events
PART II
Rust
HelloPico
    ↓
deterministic state machine
PART III
PyO3
Rust
    ↕
Python
PART IV
Manifold
Python runtime
    ↓
events + state + API
PART V
Packaging
maturin
    ↓
wheel
    ↓
OCI image
PART VI
Kubernetes
Minikube
    ↓
runtime environment
PART VII
Crossplane
Pico XR
    ↓
Composition
    ↓
runtime resources
PART VIII
Wrangler
Pico lifecycle
    ↓
create / inspect / event / delete
PART IX
Messaging
Pico
 ↕
MQTT
PART X
Home Assistant
Pico becomes visible
and interactive
PART XI
Persistence
Pod dies
Pico survives

And the finished learner journey becomes beautifully simple:

wrangler pico create definitions/pico.yaml

then open Home Assistant and see:

Hello Pico
Status: Ready
Version: 0.1.0
Message: Hello, Pico!
Event Count: 0

Then:

wrangler pico event \
  hello-pico \
  hello \
  --name Willem

and without refreshing architecture, redeploying anything or directly touching Home Assistant:

Hello Pico
Status: Ready
Version: 0.1.0
Message: Hello, Willem! I am Pico hello-pico.
Event Count: 1
Last Run: now

That one state change demonstrates almost the entire Open Engineering stack.

Crossplane is declarative infrastructure/composition; Kubernetes supplies the runtime substrate; Wrangler owns lifecycle; Manifold owns execution; the Pico owns identity and state; Rust provides the deterministic engine; PyO3 bridges it into the orchestration ecosystem; MQTT carries events; and Home Assistant becomes the human-facing operational view. The technologies are not appearing merely because they’re on our technology list—each one now has a visible, testable responsibility in the “Hello, Pico!” story. 
