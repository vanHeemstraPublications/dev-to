---
title: "🏠 The Manifold Runtime"
series: "Hello Pico Workflow"
part: 6
organization: "the-software-s-journey"
tags: [open-engineering, pico, manifold, fastapi, python]
---

## 🏠 The Manifold Runtime

Up to now, everything's lived at the command line — `cargo test`, a one-off Python REPL session. This episode is where Python stops being a script and becomes a *host environment*: something long-running, reachable over HTTP, that other systems can actually talk to. That host is Manifold.

First, the dependencies:

```bash
uv add fastapi uvicorn paho-mqtt pydantic-settings
uv add --dev pytest httpx ruff
```

`fastapi` and `uvicorn` for the runtime itself, `paho-mqtt` for the MQTT connection we'll wire up next episode, `pydantic-settings` for configuration, and `pytest`/`httpx`/`ruff` for testing and linting along the way.

The Manifold runtime exposes exactly three endpoints for now:

```
GET  /health
GET  /state
POST /events/hello
```

Here's the whole thing, small enough to read in one sitting:

```python
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
```

That's the whole responsibility split laid bare in about fifteen lines: FastAPI handles HTTP and event transport, Manifold owns execution, and the actual work happens exactly where it did back in Episodes 4 and 5 — Rust, via PyO3. Nothing new is being decided here about *what* a hello event does; this file just gives the outside world a door to knock on.

```
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
```

Run it locally:

```bash
uv run uvicorn manifold.app:app \
  --host 0.0.0.0 \
  --port 8080
```

Then check it's alive:

```bash
curl http://localhost:8080/state
```

And send it its first real event over HTTP:

```bash
curl \
  -X POST \
  http://localhost:8080/events/hello \
  -H 'Content-Type: application/json' \
  -d '{"name":"Willem"}'
```

Expected response:

```json
{
  "id": "hello-pico",
  "version": "0.1.0",
  "status": "ready",
  "message": "Hello, Willem! I am Pico hello-pico.",
  "event_count": 1,
  "last_run": "..."
}
```

I want to flag one thing here for anyone reading closely: this file calls `publish_state(result)`, a function that doesn't exist yet. That's on purpose — it's next episode's job.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| FastAPI | HTTP requests to `/health`, `/state`, `/events/hello` | Route each request to the corresponding handler | A running HTTP API on port 8080 | `curl`, and eventually Wrangler and Home Assistant |
| Manifold's `hello()` handler | A validated `HelloEvent` (a `name` field) | Call into the PyO3-wrapped Rust core, parse the JSON result | The Pico's updated state, returned as the HTTP response | The calling client, and (next episode) MQTT |
| `pico_native.HelloPico` (from Episode 5) | Method calls from Manifold | Execute the actual Rust state transition | A JSON string representing the new state | Manifold's handler functions |

Next stop: wiring Manifold up to MQTT, so state changes stop being something you only see by polling.
