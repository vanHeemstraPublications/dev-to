---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.2"
published: false
description: "Episode 2: Before either platform owner writes a single controller, OEP makes them agree on a vocabulary. This episode opens the contracts/ module — plain Kotlin Multiplatform @Serializable data classes for Space, Mission, Agent, Evidence, and Result — and shows exactly why a shared data shape is not the same thing as a shared dependency."
tags: [kotlin, kubernetes, architecture, multiplatform]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-02.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

## Episode 2: The Contracts Are the Treaty

## A Vocabulary, Not a Library

The owner of Agility Game has a reasonable fear: "If I 'depend on the contracts,' aren't I just depending on Detective Operating System's code with extra steps?"

No. And the distinction matters enough to spend a whole episode on it.

A **contract** in OEP is a plain Kotlin Multiplatform data class, annotated `@Serializable`, with no behaviour, no controller logic, no dependency on Kubernetes client libraries, no dependency on Ktor, no dependency on anything except `kotlinx.serialization`. It describes the **shape of data**, not the **code that processes it**. Detective Operating System's controller happens to consume these shapes. Agility Game could consume the exact same shapes from a Unity backend written in C#, a Python script, or a bash function that greps JSON — because the actual wire format is just JSON flowing through the Kubernetes API, and the Kotlin contract is merely the typed mirror of that JSON for anyone who happens to be writing Kotlin.

## 🗂️ SIPOC — The Contracts Module

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| OEP foundation team | Domain vocabulary decisions (what is a Mission? what is a Space?) | Write @Serializable Kotlin Multiplatform data classes with kotlinx.serialization | Five small Gradle modules: contracts/space, contracts/mission, contracts/agent, contracts/evidence, contracts/result | Any runtime platform — Detective Operating System today, Agility Game whenever it wants |
| contracts/state | Cross-cutting types (ObjectMeta, MissionPhase, ResultPhase) | Single shared module for the small set of types every contract needs | Reusable envelope and enum types | Every other contract module (a dependency within the foundation layer, not across runtime platforms) |
| kotlinx.serialization | Annotated data classes | Generate serializers at compile time (no reflection) | JSON-compatible Kotlin objects, safely deserializable from the Kubernetes API | Both runtime platforms, independently, without ever sharing a build |

## The Contracts Directory, As It Actually Exists

```
contracts/
├── space/
│   └── src/commonMain/kotlin/io/oep/contracts/space/Space.kt
├── mission/
│   └── src/commonMain/kotlin/io/oep/contracts/mission/Mission.kt
├── agent/
│   └── src/commonMain/kotlin/io/oep/contracts/agent/Agent.kt
├── evidence/
│   └── src/commonMain/kotlin/io/oep/contracts/evidence/Evidence.kt
├── result/
│   └── src/commonMain/kotlin/io/oep/contracts/result/Result.kt
└── state/
    └── src/commonMain/kotlin/io/oep/contracts/state/
        ├── ObjectMeta.kt
        └── Phases.kt
```

Every single one of these lives under `src/commonMain` — the Kotlin Multiplatform source set that compiles to JVM, Native, and JS alike (see the *Twister Game of Kotlin Multiplatform* series for the long version of why that matters). The practical consequence here: these contracts are not JVM-only. Detective Operating System happens to run on the JVM. Agility Game, if it were a native iOS or web game client, could still consume `commonMain`-compiled contract code without anyone porting anything.

## The Shared Envelope: ObjectMeta

Every OEP resource — Space, Mission, Agent, Evidence, Result — wraps the same minimal mirror of Kubernetes' own `ObjectMeta`:

```kotlin
package io.oep.contracts.state

import kotlinx.serialization.Serializable

/**
 * Minimal subset of Kubernetes `ObjectMeta` used by all OEP envelope types.
 * Only fields needed by the v1alpha1 contracts are modelled; unknown fields
 * are tolerated by serializers configured with `ignoreUnknownKeys = true`.
 */
@Serializable
data class ObjectMeta(
    val name: String? = null,
    val namespace: String? = null,
    val generation: Long? = null,
    val resourceVersion: String? = null,
    val uid: String? = null,
    val creationTimestamp: String? = null,
    val labels: Map<String, String>? = null,
    val annotations: Map<String, String>? = null,
)
```

Read that doc comment again: *"unknown fields are tolerated by serializers configured with *`ignoreUnknownKeys = true`*."* This is the single most important sentence in the entire contracts module for our two platform owners. It means: if Detective Operating System's owner adds a brand-new annotation to a Mission tomorrow, Agility Game's deserializer does not explode. It just ignores the field it doesn't recognise and moves on with its day.

## The Phases: A Shared Enum, Not a Shared State Machine

```kotlin
package io.oep.contracts.state

import kotlinx.serialization.Serializable

@Serializable
enum class MissionPhase {
    Pending,
    Running,
    Completed,
    Failed,
}

@Serializable
enum class ResultPhase {
    Draft,
    Final,
}
```

Notice what is *not* here: no logic for *how* a Mission transitions from `Pending` to `Running`. That logic lives entirely inside Detective Operating System's controller (Episode 5). The contract only states the vocabulary of possible phases — the legal moves on the board, not the rules of who's allowed to make them or when. Agility Game's owner, building a completely different runtime, could define their own custom phase enum for their own custom resource kind and never touch `MissionPhase` at all. They only need `MissionPhase` if they actually want to read or display a Detective Operating System Mission's status — and at that point, reading a shared, well-documented enum is a feature, not a coupling.

## Mission: The Contract Detective Operating System Actually Runs On

```kotlin
package io.oep.contracts.mission

import io.oep.contracts.state.MissionPhase
import io.oep.contracts.state.ObjectMeta
import kotlinx.serialization.Serializable

@Serializable
data class MissionSpec(
    val name: String,
    val purpose: String,
    val spaceRef: String,
    val agentRef: String,
)

@Serializable
data class MissionStatus(
    val phase: MissionPhase? = null,
    val startedAt: String? = null,
    val completedAt: String? = null,
    val message: String? = null,
)

@Serializable
data class Mission(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: MissionSpec,
    val status: MissionStatus? = null,
) {
    companion object {
        const val API_VERSION: String = "oep.io/v1alpha1"
        const val KIND: String = "Mission"
    }
}
```

`spaceRef` and `agentRef` are plain strings — names of other Kubernetes resources, resolved at reconcile time by Detective Operating System's controller (we'll watch this happen live in Episode 5). They are not Kotlin object references. There is no `lateinit var space: Space` anywhere. The Mission contract does not "have" a Space; it merely *names* one, the same way a postcard names a street address without literally containing the house.

## Space, Agent, Evidence, Result: The Rest of the Cast

```kotlin
// contracts/space — Space.kt
@Serializable
data class SpaceSpec(val name: String, val purpose: String)

@Serializable
data class SpaceStatus(val observedGeneration: Long? = null)

@Serializable
data class Space(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: SpaceSpec,
    val status: SpaceStatus? = null,
) {
    companion object { const val API_VERSION = "oep.io/v1alpha1"; const val KIND = "Space" }
}

// contracts/agent — Agent.kt
@Serializable
data class AgentSpec(
    val name: String,
    val purpose: String,
    val skills: List<String>,
)

@Serializable
data class Agent(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: AgentSpec,
    val status: AgentStatus? = null,
) {
    companion object { const val API_VERSION = "oep.io/v1alpha1"; const val KIND = "Agent" }
}

// contracts/evidence — Evidence.kt
@Serializable
enum class EvidenceType { SourceCode }

@Serializable
data class EvidenceSource(val repo: String, val path: String)

@Serializable
data class EvidenceSpec(
    val name: String,
    val purpose: String,
    val type: EvidenceType,
    val source: EvidenceSource,
    val data: JsonObject? = null,
)

// contracts/result — Result.kt
@Serializable
enum class ResultKind { CaseFile }

@Serializable
data class ResultSpec(
    val name: String,
    val purpose: String,
    val missionRef: String,
    val kind: ResultKind,
    val findings: List<JsonObject>? = null,
)
```

A pattern emerges: every contract has the same four-part skeleton — `apiVersion`, `kind`, `metadata`, `spec`, optional `status`. This is not Kotlin convention; it is **Kubernetes** convention. OEP's contracts are typed mirrors of Kubernetes objects, which is precisely why the next episode — CRDs — slots in so naturally. The Kotlin data class and the Kubernetes YAML schema are describing the exact same thing from two different altitudes.

## Architecture Diagram: Where Contracts Sit

```
                    BOTH RUNTIME PLATFORMS
        ┌─────────────────────┐    ┌──────────────────────┐
        │ Detective Operating │    │   Agility Game       │
        │       System        │    │  (hypothetical, not  │
        │  (Kotlin/JVM/Ktor)  │    │   shipped here)      │
        └──────────┬──────────┘    └───────────┬──────────┘
                   │                           │
                   │  import contracts.mission │
                   │  import contracts.space   │
                   │  import contracts.agent   │
                   ▼                           ▼
        ┌──────────────────────────────────────────────────┐
        │           contracts/ (Kotlin Multiplatform)      │
        │                                                  │
        │   Space.kt    Mission.kt    Agent.kt             │
        │   Evidence.kt   Result.kt                        │
        │   state/ObjectMeta.kt   state/Phases.kt          │
        │                                                  │
        │   @Serializable data classes — NO behaviour,     │
        │   NO Kubernetes client, NO Ktor, NO controller   │
        │   logic. Pure, inert, typed JSON shapes.         │
        └──────────────────────────────────────────────────┘
                              │
                              │ compiles via kotlinx.serialization
                              ▼
                  Plain JSON on the wire, identical to
                  what `kubectl get mission -o json` shows

  KEY INSIGHT: both platforms depend DOWNWARD on the contracts module.
  Neither platform depends SIDEWAYS on the other platform's module.
  There is no line on this diagram connecting the two boxes at the top.
```

## Testing the Treaty: Serialization Round-Trips

The contracts module ships its own tests — for example `MissionSerializationTest.kt` — that prove the contract survives a JSON round-trip exactly as Kubernetes would send it:

```kotlin
// contracts/mission/src/commonTest/kotlin/io/oep/contracts/mission/MissionSerializationTest.kt
// (representative shape, not verbatim — illustrates the pattern)

import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals

class MissionSerializationTest {

    private val json = Json { ignoreUnknownKeys = true }

    @Test
    fun `mission round-trips through JSON unchanged`() {
        val mission = Mission(
            spec = MissionSpec(
                name = "Analyze Repository",
                purpose = "Analyze a source repository to surface code smells.",
                spaceRef = "refactoring",
                agentRef = "code-smell-detective",
            )
        )

        val encoded = json.encodeToString(Mission.serializer(), mission)
        val decoded = json.decodeFromString(Mission.serializer(), encoded)

        assertEquals(mission, decoded)
    }

    @Test
    fun `unknown future fields do not break deserialization`() {
        // Simulates Detective OS's owner adding a brand-new field
        // that Agility Game's older contract version has never heard of.
        val futureJson = """
            {
              "apiVersion": "oep.io/v1alpha1",
              "kind": "Mission",
              "spec": {
                "name": "Analyze Repository",
                "purpose": "Find code smells",
                "spaceRef": "refactoring",
                "agentRef": "code-smell-detective",
                "totallyNewFieldNobodyToldAgilityGameAbout": "surprise!"
              }
            }
        """.trimIndent()

        // This does NOT throw, thanks to ignoreUnknownKeys = true
        val decoded = json.decodeFromString(Mission.serializer(), futureJson)
        assertEquals("Analyze Repository", decoded.spec.name)
    }
}
```

That second test is the whole episode in miniature. Both platform owners can evolve their own corner of the system independently, because the contract format is explicitly engineered to tolerate the other side knowing less than the full current truth.

## What's Next: CRDs — Papering the Cluster

In **Episode 3**, we leave the JVM entirely and look at the **Kubernetes CustomResourceDefinitions** — the YAML files in `crds/` that make `Space`, `Mission`, `Agent`, `Evidence`, and `Result` into first-class Kubernetes API objects. We'll see why a CRD is, if anything, an even *stronger* decoupling boundary than the Kotlin contracts themselves — because at that layer, neither platform needs to speak Kotlin at all.

**🔗 Resources**

- **kotlinx.serialization**: [github.com/Kotlin/kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization)
- **Kotlin Multiplatform source sets**: see Episode 2 of *Twister Game of Kotlin Multiplatform* in this same publication
- **Kubernetes object conventions** (apiVersion/kind/metadata/spec/status): [kubernetes.io/docs/concepts/overview/working-with-objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster.*
