---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.6"
published: false
description: "Episode 6: Detective Operating System is Kotlin. The God Object Detector is Python. They never link against each other, never share a class, never even run in the same process. This episode follows the DetectorClient interface across an HTTP boundary into a FastAPI service running a pure AST heuristic — the single cleanest proof in the whole repository that OEP's no-dependencies promise actually holds up."
tags: [python, kotlin, fastapi, microservices]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-06.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: Crossing the Boundary Without Touching Hands

## The Cleanest Proof in the Whole Repository

Everything up to this point has been about Detective Operating System and Agility Game avoiding dependencies on *each other*. This episode is, in some ways, an even better demonstration of the principle — because it shows OEP's own controller deliberately avoiding a dependency on its **own detection logic**, which happens to live in a different programming language entirely.

`docs/ARCHITECTURE.md` states the rule outright: *"Python is used only for the God Object Detector and must stay behind a service boundary."* Not "behind an interface." Behind a **service boundary** — meaning a network call, not a function call. If Detective Operating System's Kotlin controller and the Python detector can stay this decoupled while solving the exact same problem together, two entirely separate runtime platforms have no excuse.

## 🗂️ SIPOC — Crossing the Service Boundary

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| MissionReconciler (Kotlin) | A DetectorRequest (namespace, mission name, repo URL, optional ref) | Call detector.run(request) through the DetectorClient interface | A DetectorRun (summary string + list of DetectorFinding) | MissionReconciler.handleRunning() — turns this into a status patch |
| HttpDetectorClient (Kotlin, the concrete implementation) | The DetectorRequest, serialised as JSON | POST to $OEP_DETECTOR_URL/detect using Ktor's HTTP client | An HTTP response containing findings[] and detectorVersion | MissionReconciler, via the DetectorClient interface — never sees the HTTP details |
| god-object-detector (Python/FastAPI) | The JSON body: { repository: { url, ref }, options } | Materialise the repo, walk its AST, score every class, filter by severity | JSON response: { findings: [...], detectorVersion } | HttpDetectorClient, parsing the response back into Kotlin types |

## The Interface That Makes This Possible

```kotlin
// controller/src/main/kotlin/io/oep/controller/mission/DetectorClient.kt

data class DetectorFinding(
    val ruleId: String,
    val severity: String,
    val summary: String,
    val kind: String? = null,
    val path: String? = null,
    val className: String? = null,
    val score: Double? = null,
    val rationale: String? = null,
    val metrics: Map<String, Double> = emptyMap(),
)

data class DetectorRun(
    val summary: String,
    val findings: List<DetectorFinding>,
)

/**
 * Abstraction over the God Object Detector service.
 * The interface is intentionally blocking — the reconciler invokes it
 * from its own worker thread.
 */
fun interface DetectorClient {
    fun run(request: DetectorRequest): DetectorRun
}

data class DetectorRequest(
    val namespace: String,
    val missionName: String,
    val spaceName: String,
    val agentName: String,
    val repositoryUrl: String? = null,
    val repositoryRef: String? = null,
)
```

`fun interface` — a single abstract method, nothing more. `MissionReconciler` (Episode 5) was written against this interface, and *only* this interface. There are, accordingly, two implementations sitting side by side in the same package:

```kotlin
/**
 * Canned in-process detector used until the real Python service is wired
 * up. Sleeps briefly to simulate work and returns a single hard-coded
 * finding. Used in tests where no actual HTTP detector is required.
 */
class InMemoryDetectorClient(
    private val workDelayMillis: Long = 1_000L,
    private val finding: DetectorFinding = DEFAULT_FINDING,
) : DetectorClient {
    override fun run(request: DetectorRequest): DetectorRun {
        if (workDelayMillis > 0) Thread.sleep(workDelayMillis)
        return DetectorRun(
            summary = "Detected 1 candidate via ${finding.ruleId} (stub)",
            findings = listOf(finding),
        )
    }
}
```

`InMemoryDetectorClient` exists purely so `MissionReconcilerTest.kt` can test the whole Pending→Running→Completed state machine without a Python process running anywhere. This, incidentally, is the same trick Agility Game's owner could use to write tests against a Detective Operating System Mission's lifecycle without ever spinning up the real detector — or even the real Detective Operating System controller, for that matter, if they just want to simulate one.

## HttpDetectorClient: Where the Boundary Actually Gets Crossed

```kotlin
class HttpDetectorClient(
    private val baseUrl: String = System.getenv("OEP_DETECTOR_URL")
        ?: DEFAULT_BASE_URL,
    engine: HttpClientEngine? = null,
) : DetectorClient, AutoCloseable {

    private val httpClient: HttpClient = if (engine != null) {
        HttpClient(engine) { install(ContentNegotiation) { json(JSON_FORMAT) } }
    } else {
        HttpClient(CIO) { install(ContentNegotiation) { json(JSON_FORMAT) } }
    }

    override fun run(request: DetectorRequest): DetectorRun {
        val url = request.repositoryUrl
            ?: error("HttpDetectorClient requires repositoryUrl on the DetectorRequest")

        val body = DetectRequestJson(
            repository = RepositoryJson(url = url, ref = request.repositoryRef),
            options = JsonObject(emptyMap()),
        )
        val response: DetectResponseJson = runBlocking {
            val raw: HttpResponse = httpClient.post("$baseUrl/detect") {
                contentType(ContentType.Application.Json)
                setBody(body)
            }
            if (!raw.status.isSuccess()) {
                error("detector returned HTTP ${raw.status.value}: ${raw.bodyAsText().take(200)}")
            }
            raw.body()
        }
        val findings = response.findings.map { it.toDetectorFinding() }
        return DetectorRun(
            summary = "Detected ${findings.size} god-object candidate(s) via god-object-detector ${response.detectorVersion}",
            findings = findings,
        )
    }

    companion object {
        const val DEFAULT_BASE_URL: String =
            "http://god-object-detector.oep-system.svc.cluster.local:8000"
    }
}

@Serializable
internal data class DetectRequestJson(
    val repository: RepositoryJson,
    val options: JsonObject = JsonObject(emptyMap()),
)

@Serializable
internal data class RepositoryJson(val url: String, val ref: String? = null)

@Serializable
internal data class DetectResponseJson(
    val findings: List<FindingJson> = emptyList(),
    val detectorVersion: String,
)
```

Read `DEFAULT_BASE_URL` carefully: `god-object-detector.oep-system.svc.cluster.local`. That is Kubernetes Service DNS — a name resolved entirely by `kube-dns`/`CoreDNS` (see the *Who Are You CoreDNS?* series in this same publication for the deep dive on exactly how). Detective Operating System's Kotlin code does not know or care what IP address that resolves to, what pod is behind it, how many replicas exist, or what language they're written in. It POSTs JSON to a name, and Kubernetes makes that name mean something.

## Architecture Diagram: The Full Cross-Language Round Trip

```
┌────────────────────────────────────────────────────────────────────┐
│        oep-system NAMESPACE (deploy/ — Episode 7 territory)        │
│                                                                    │
│  ┌──────────────────────────┐        ┌───────────────────────────┐ │
│  │   oep-controller          │        │   god-object-detector      │ │
│  │   (Kotlin / JVM / Ktor)   │        │   (Python / FastAPI)        │ │
│  │                            │        │                           │ │
│  │  MissionReconciler          │        │  POST /detect              │ │
│  │       │                    │        │       │                   │ │
│  │       ▼                    │        │       ▼                   │ │
│  │  detector.run(request)      │        │  materialize_repository()  │ │
│  │       │                    │        │       │                   │ │
│  │       ▼                    │   HTTP │       ▼                   │ │
│  │  HttpDetectorClient         │  POST  │  scan_path() — pure Python │ │
│  │       │                    │  JSON  │  `ast` module walk          │ │
│  │       │  POST :8000/detect ─┼───────►│       │                   │ │
│  │       │                    │        │       ▼                   │ │
│  │       │  ◄──────────────────┼────────┤  compute_score() per class │ │
│  │       ▼                    │  200   │       │                   │ │
│  │  DetectResponseJson         │  OK    │       ▼                   │ │
│  │       │                    │        │  severity_for(score)       │ │
│  │       ▼                    │        │       │                   │ │
│  │  DetectorFinding[]           │        │       ▼                   │ │
│  │                            │        │  DetectResponse(findings)  │ │
│  └──────────────────────────┘        └───────────────────────────┘ │
│         Service DNS: god-object-detector.oep-system.svc.cluster.local │
└────────────────────────────────────────────────────────────────────┘

  Zero shared classes. Zero shared build files. Zero imports across
  the boundary. The ONLY thing both sides agree on is a JSON shape —
  exactly the same "contract, not code" pattern from Episode 2,
  just crossing a language barrier instead of a platform-ownership one.
```

## What's Actually on the Python Side

```python
# services/god-object-detector/app/main.py

from fastapi import FastAPI, HTTPException
from .models import DetectRequest, DetectResponse
from .repo import materialize_repository, RepositoryMaterializationError, UnsupportedRepositoryScheme
from .scanner import scan_path
from . import __version__

DETECTOR_VERSION: str = __version__
app = FastAPI(title="OEP God Object Detector", version=DETECTOR_VERSION)

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/readyz")
def readyz() -> dict[str, str]:
    return {"status": "ready"}

@app.post("/detect", response_model=DetectResponse)
def detect(request: DetectRequest) -> DetectResponse:
    try:
        with materialize_repository(request.repository) as root:
            findings = scan_path(root)
    except UnsupportedRepositoryScheme as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryMaterializationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return DetectResponse(findings=findings, detectorVersion=DETECTOR_VERSION)
```

```python
# services/god-object-detector/app/models.py — Pydantic v2, LOCKED contract

class Repository(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str
    ref: str | None = None

class DetectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repository: Repository
    options: dict[str, Any] = Field(default_factory=dict)

class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["GodObject"] = "GodObject"
    path: str
    className: str
    severity: Literal["low", "medium", "high"]
    score: float
    rationale: str
    metrics: dict[str, float] = Field(default_factory=dict)

class DetectResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    findings: list[Finding] = Field(default_factory=list)
    detectorVersion: str
```

The module docstring is unambiguous about how seriously this contract is taken: *"These models are LOCKED by Wave 6.1 — Waves 6.2 (heuristic), 6.3 (container), and 7 (controller HTTP wiring) build on them. Add fields only, do not rename or remove existing ones."* This is the Python-side mirror of the same discipline the Kotlin contracts module practices in Episode 2 — additive evolution, never breaking changes, because *somebody on the other side of an HTTP call is depending on this shape staying put.*

## The Actual Heuristic — No Shared Code, Just Shared Math

```python
# services/god-object-detector/app/scanner.py
#
# AST-based God Object heuristic for Python sources.
# Pure functions over the standard library `ast` module —
# no third-party static analysis, no Kotlin, no JVM anywhere near it.

LOC_WEIGHT = 200.0
METHOD_WEIGHT = 20.0
FIELD_WEIGHT = 15.0
IMPORT_WEIGHT = 25.0

def compute_score(loc: int, methods: int, fields: int, imports_referenced: int) -> float:
    """Composite God Object score; weights are deliberately simple."""
    return (
        loc / LOC_WEIGHT
        + methods / METHOD_WEIGHT
        + fields / FIELD_WEIGHT
        + imports_referenced / IMPORT_WEIGHT
    )

def severity_for(score: float) -> Severity | None:
    """Map a composite score to a severity band, or None if sub-threshold."""
    if score >= 3.0:
        return "high"
    if score >= 2.0:
        return "medium"
    if score >= 1.0:
        return "low"
    return None
```

A class with 400 lines, 12 methods, 6 fields, and 5 distinct imported names referenced inside it scores `400/200 + 12/20 + 6/15 + 5/25 = 2.0 + 0.6 + 0.4 + 0.2 = 3.2` — comfortably into `"high"` severity. Note for the curious: this is a different, and considerably more nuanced, heuristic than the simple "`>30 methods OR >1000 lines`" rule sketched in the early planning document (`flows/FLOW-MVP-003-run-investigation.md`). Plans evolve; the locked Pydantic contract and the actual `scanner.py` are what ships and what this series describes.

## Why Neither Detective Operating System Nor Agility Game Should Touch This Code

**OWNER OF AGILITY GAME:** "Could I reuse the God Object Detector for my own gamified code-review minigame?"

**OWNER OF DETECTIVE OPERATING SYSTEM:** "You don't even have to ask me. POST a JSON body matching `DetectRequest` to whatever URL the Service resolves to, and you'll get a `DetectResponse` back. I won't know it was you. The detector won't know it was you. The only thing either of us cares about is whether your JSON matches the locked Pydantic shape."

**OWNER OF AGILITY GAME:** "What if I want to change how God Objects are scored?"

**OWNER OF DETECTIVE OPERATING SYSTEM:** "Then you'd be changing a service I also depend on, which is the one thing OEP's layering explicitly tries to prevent two unrelated runtime platforms from doing to each other. Fork it. Run your own. The contract is public; the implementation doesn't have to be shared."

## What's Next: Deploying Two Strangers Into the Same Cluster

In **Episode 7**, we look at how `deploy/` actually gets both `oep-controller` and `god-object-detector` running side by side in the `oep-system` namespace — two completely independent Kubernetes Deployments, two Service objects, two sets of RBAC, connected by nothing but the DNS name we just watched `HttpDetectorClient` dial.

**🔗 Resources**

- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Pydantic v2**: [docs.pydantic.dev](https://docs.pydantic.dev)
- **Ktor HTTP client**: [ktor.io/docs/client-create-new-application.html](https://ktor.io/docs/client-create-new-application.html)
- **Python **`ast`** module**: [docs.python.org/3/library/ast.html](https://docs.python.org/3/library/ast.html)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster.*