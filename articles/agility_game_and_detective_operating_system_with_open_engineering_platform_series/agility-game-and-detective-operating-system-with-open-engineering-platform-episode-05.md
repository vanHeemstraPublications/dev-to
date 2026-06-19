---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.5"
published: false
description: "Episode 5: Enough YAML. This episode opens the real Kotlin source of the Detective Operating System's controller — MissionReconciler and ResultReconciler — and watches it drive a Mission through Pending, Running, and Completed using a fabric8 SharedIndexInformer. Not one line of this code imports, references, or even knows that Agility Game exists."
tags: [kotlin, kubernetes, controllers, ktor]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-05.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## Episode 5: The Detective's Actual Brain

## Where the Detective Actually Lives

A small but important correction, made gently for anyone who went looking: the repository has a folder called `controllers/detective-operating-system/`, and if you open it, you'll find... a `.gitkeep` file. That's it. That's the whole folder.

The *actual* Detective Operating System controller — the running Kotlin code that watches Missions, talks to a detector, and produces Results — lives at the repository's top level, in `controller/`. This is not a continuity error; it's just how the MVP wave plan happened to land. We mention it here so nobody spends twenty minutes searching `controllers/` wondering where the detective went. He's one directory level up, wearing a trench coat, drinking lukewarm coffee.

## 🗂️ SIPOC — The Controller Runtime

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Kubernetes API server | Watch events for Mission/Space/Agent/Evidence objects | fabric8 SharedIndexInformer delivers onAdd/onUpdate callbacks | Enqueued reconcile work, deduplicated per Mission name | MissionReconciler.reconcileOnce() |
| MissionReconciler | The current Mission object's status.phase | State machine: null→Pending, Pending→Running (after ref validation), Running→Completed/Failed (after calling the detector) | Patched status.phase, status.startedAt, status.completedAt, status.message | The Mission object itself (read by anyone), and FindingsCache (read by ResultReconciler) |
| ResultReconciler | The current Result object's status.phase, and the Mission named in spec.missionRef | State machine: null→Draft, Draft stays Draft until the referenced Mission is Completed, then Draft→Final with findings attached | Patched status.phase, status.publishedAt, and spec.findings | Whoever reads the finished Case File — a human, a dashboard, or yes, hypothetically, Agility Game |

## MissionReconciler: The State Machine, As Written

```kotlin
class MissionReconciler(
    private val client: KubernetesClient,
    private val namespace: String,
    private val detector: DetectorClient,
    private val findingsCache: FindingsCache = FindingsCache(),
    private val clock: Clock = Clock.systemUTC(),
    private val resyncPeriodMillis: Long = DEFAULT_RESYNC_MILLIS,
) : Reconciler {

    override val name: String = "mission"

    override fun start() {
        if (informer != null) return
        informer = client.genericKubernetesResources(MissionResources.MISSION)
            .inNamespace(namespace)
            .inform(object : ResourceEventHandler<GenericKubernetesResource> {
                override fun onAdd(obj: GenericKubernetesResource) = enqueue(obj.metadata?.name)
                override fun onUpdate(old: GenericKubernetesResource, new: GenericKubernetesResource) =
                    enqueue(new.metadata?.name)
                override fun onDelete(obj: GenericKubernetesResource, deletedFinalStateUnknown: Boolean) = Unit
            }, resyncPeriodMillis)
    }

    fun reconcileOnce(missionName: String): MissionPhase? {
        val missions = client.genericKubernetesResources(MissionResources.MISSION).inNamespace(namespace)
        val current = missions.withName(missionName).get() ?: return null
        return when (current.statusPhase()) {
            null, "" -> transitionTo(current, MissionPhase.Pending)
            MissionPhase.Pending.name -> handlePending(current)
            MissionPhase.Running.name -> handleRunning(current)
            MissionPhase.Completed.name, MissionPhase.Failed.name ->
                MissionPhase.valueOf(current.statusPhase()!!)
            else -> transitionTo(current, MissionPhase.Pending)  // unknown phase, self-heal
        }
    }

    private fun handlePending(mission: GenericKubernetesResource): MissionPhase {
        val spaceRef = mission.specString("spaceRef")
        val agentRef = mission.specString("agentRef")
        if (spaceRef.isNullOrBlank() || agentRef.isNullOrBlank()) {
            return MissionPhase.Pending   // stay put, refs not even named yet
        }
        val spaceFound = client.genericKubernetesResources(MissionResources.SPACE)
            .inNamespace(namespace).withName(spaceRef).get() != null
        val agentFound = client.genericKubernetesResources(MissionResources.AGENT)
            .inNamespace(namespace).withName(agentRef).get() != null
        if (!spaceFound || !agentFound) {
            return MissionPhase.Pending   // refs named but not resolvable yet — wait
        }
        return transitionTo(mission, MissionPhase.Running) {
            it["startedAt"] = it["startedAt"] ?: Instant.now(clock).toString()
            it["message"] = "Refs resolved; detector running"
        }
    }

    private fun handleRunning(mission: GenericKubernetesResource): MissionPhase {
        val missionName = mission.metadata?.name.orEmpty()
        val sourceEvidence = client.genericKubernetesResources(MissionResources.EVIDENCE)
            .inNamespace(namespace).list().items
            .firstOrNull { (it.specString("type") ?: "") == "SourceCode" }
        val request = DetectorRequest(
            namespace = namespace,
            missionName = missionName,
            spaceName = mission.specString("spaceRef").orEmpty(),
            agentName = mission.specString("agentRef").orEmpty(),
            repositoryUrl = sourceEvidence?.specSourceString("repo"),
            repositoryRef = sourceEvidence?.specSourceString("path"),
        )
        return try {
            val run = detector.run(request)
            findingsCache.put(namespace, missionName, run.findings.map { it.toJsonObject() })
            transitionTo(mission, MissionPhase.Completed) {
                it["completedAt"] = Instant.now(clock).toString()
                it["message"] = run.summary
            }
        } catch (t: Throwable) {
            transitionTo(mission, MissionPhase.Failed) {
                it["completedAt"] = Instant.now(clock).toString()
                it["message"] = "Detector failed: ${t.message ?: t.javaClass.simpleName}"
            }
        }
    }
}
```

A few things worth pointing at directly:

1. `Pending`** is patient, not lazy.** If `spaceRef`/`agentRef` aren't resolvable yet, the reconciler just stays in `Pending` and waits for the next watch event. There's no busy-loop, no exponential backoff hand-rolled here — the informer's resync period and the natural arrival of new watch events do that work.
2. **The detector call lives entirely inside **`handleRunning`**.** This is the seam where Episode 6 picks up — `detector.run(request)` is an interface call, and the concrete implementation is a complete unknown to this class. It could be `InMemoryDetectorClient` (used in tests) or `HttpDetectorClient` (used in production, talking to a Python service). `MissionReconciler` does not care, and that indifference is the entire design.
3. **Unknown phases self-heal back to **`Pending`**.** If something writes a phase string this reconciler has never heard of — say, hypothetically, a phase Agility Game's controller invented for its own purposes and someone fat-fingered it onto the wrong CRD — Detective Operating System doesn't crash. It resets to `Pending` and logs a warning.

## Architecture Diagram: The Informer-Driven Loop

```
┌──────────────────────────────────────────────────────────────────────┐
│                     KUBERNETES API SERVER                           │
│                                                                      │
│  watch stream: missions.oep.io in namespace oep-domain               │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ onAdd / onUpdate events
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                MissionReconciler (controller/ — Kotlin/JVM)         │
│                                                                      │
│   SharedIndexInformer                                                │
│        │                                                            │
│        │  enqueue(missionName)  — deduplicated via                  │
│        ▼                          ConcurrentHashMap<String,Boolean>  │
│   single-threaded ExecutorService                                    │
│        │                                                            │
│        ▼                                                            │
│   reconcileOnce(missionName)                                         │
│        │                                                            │
│        ├─ null/"" ──────► transitionTo(Pending)                      │
│        ├─ Pending ───────► handlePending()                           │
│        │                     ├─ refs missing/unresolved → stay       │
│        │                     └─ refs OK → transitionTo(Running)       │
│        ├─ Running ───────► handleRunning()                           │
│        │                     ├─ detector.run(request)  ◄── Ep.6      │
│        │                     ├─ success → transitionTo(Completed)     │
│        │                     └─ failure → transitionTo(Failed)        │
│        └─ Completed/Failed ─► no-op, terminal                        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ patchStatus()
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     KUBERNETES API SERVER                           │
│   status.phase updated → triggers ResultReconciler's own watch       │
└──────────────────────────────────────────────────────────────────────┘
```

## ResultReconciler: Waiting Patiently for Someone Else's Work

```kotlin
class ResultReconciler(
    private val client: KubernetesClient,
    private val namespace: String,
    private val findingsSource: FindingsSource = StubFindingsSource(),
    private val clock: () -> Instant = Instant::now,
    private val resyncPeriodMillis: Long = DEFAULT_RESYNC_MILLIS,
) : Reconciler {

    override val name: String = "ResultReconciler"

    /** Visible for tests. Performs one synchronous reconcile pass. */
    fun reconcile(result: GenericKubernetesResource) {
        val ns = result.metadata?.namespace ?: namespace
        val rname = result.metadata?.name ?: return
        val currentPhase = readPhase(result)

        if (currentPhase == ResultPhase.Final) {
            return   // already done, nothing to do, ever again
        }

        if (currentPhase == null) {
            patchStatus(ns, rname, ResultPhase.Draft, publishedAt = null)
            return
        }

        // currentPhase == Draft: check whether the referenced Mission
        // has finished its own, completely separate state machine
        val missionRef = readMissionRef(result)
        // ... look up the Mission, check status.phase == Completed,
        // harvest findings via findingsSource, patch spec.findings,
        // and only then transition Draft -> Final.
    }
}
```

The state machine here is deliberately *dumber* than `MissionReconciler`'s. It has exactly two real states (`Draft`, `Final`), and its only job is to patiently poll whether someone else's resource (`Mission`, by name in `spec.missionRef`) has reached `Completed`. This reconciler does not know *how* the Mission got completed, does not know about `DetectorClient`, does not know about Spaces or Agents. It is, structurally, the same kind of "watch a name, not an object reference" pattern we saw in the contracts back in Episode 2 — `missionRef` is a string, resolved at runtime, not a compiled-in dependency.

## Wiring It Together: Main.kt

```kotlin
fun main() {
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8080
    val registry = ReconcilerRegistry()
    val k8sClient: KubernetesClient? = runCatching { KubernetesClientFactory.create() }.getOrNull()

    if (k8sClient != null) {
        val findingsCache = FindingsCache()
        installMissionReconciler(
            registry, k8sClient, KubernetesClientFactory.namespace(),
            findingsCache = findingsCache,
        )
        registry.register(
            ResultReconciler(
                client = k8sClient,
                namespace = KubernetesClientFactory.namespace(),
                findingsSource = FindingsCacheSource(findingsCache),
            ),
        )
        registry.startAll()
    }

    val server = embeddedServer(CIO, port = port, host = "0.0.0.0") {
        controllerModule(registry) { k8sClient != null }
    }
    server.start(wait = true)
}
```

`installMissionReconciler` (which, per its own doc comment, wires up the concrete `DetectorClient` implementation — `HttpDetectorClient` in production) is the only place in this entire file where the controller reaches outside its own process boundary toward another service. And as Episode 6 will show, that reach is a plain HTTP POST, not an import.

Also worth noting: the Ktor server here exposes exactly two routes, `/healthz` and `/readyz` — the same liveness/readiness convention used by the Python detector service in Episode 6, and by basically every well-behaved Kubernetes workload regardless of language. Agility Game's controller, whenever it exists, will probably expose the exact same two routes, for the exact same reasons, without anyone needing to coordinate on it.

## What's Next: Crossing the Boundary Without Touching Hands

In **Episode 6**, we follow the one outbound call `MissionReconciler` makes — `detector.run(request)` — all the way across the process boundary into a completely separate Python FastAPI service, the **God Object Detector**. We'll see the `DetectorClient` interface, its `HttpDetectorClient` implementation, and the AST-based heuristic on the other side that has never heard of Kotlin, Ktor, or fabric8 in its life.

**🔗 Resources**

- **fabric8 Kubernetes Client**: [github.com/fabric8io/kubernetes-client](https://github.com/fabric8io/kubernetes-client)
- **Kubernetes Informers pattern**: [kubernetes.io/docs/concepts/architecture/controller](https://kubernetes.io/docs/concepts/architecture/controller/)
- **Ktor**: [ktor.io](https://ktor.io)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster.*