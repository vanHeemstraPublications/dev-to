---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.9: The Ontology Moves In"
published: false
description: "Episode 9: MVP 1 proved two runtime platforms could share a cluster without sharing code. MVP 2 asks a harder question: can they also share a VOCABULARY without sharing an opinion? This episode opens the new ontology contracts -- Kind, Capability, Purpose, Value, Relationship -- and shows exactly how Space and Mission were extended without breaking a single existing line."
tags: [kotlin, kubernetes, architecture, ontology]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-09.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 9: The Ontology Moves In

---

## A Quiet Knock at the Door

Eight episodes ago, the owner of Agility Game and the owner of Detective Operating System learned to live in the same Kubernetes cluster without sharing a single Gradle module. They built contracts. They built CRDs. They watched a Mission crawl through `Pending -> Running -> Completed` and a Result follow it from `Draft -> Final`. Everyone went home satisfied.

Then `INTENT_MVP_2.md` arrived with a quiet but ambitious subtitle: *Shift-Left Ontology Platform*. And a new tenant moved into the building: the **ontology layer**. Not a new runtime platform competing for the same desk space as Detective Operating System and Agility Game -- something underneath both of them, supplying vocabulary instead of code.

This episode unpacks exactly what moved in, and -- because both owners have been burned by "exciting new platform layer" announcements before -- exactly how little it disturbs the furniture they already had.

---

## SIPOC -- The Ontology Layer

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| OEP foundation team | Domain vocabulary decisions: what is a Kind? a Capability? a Purpose? | Write seven new `@Serializable` Kotlin Multiplatform contracts, each following the same apiVersion/kind/metadata/spec/status skeleton from MVP 1 | New Gradle modules: `contracts/kind`, `contracts/capability`, `contracts/purpose`, `contracts/value`, `contracts/relationship`, plus the bigger `contracts/journey` and `contracts/outcome` | Both runtime platforms -- who can now describe WHAT a Space or Mission represents, not just THAT one exists |
| MVP 1's existing contracts (`Space`, `Mission`) | Two new, fully optional fields: `kindRef`, `capabilityRefs` | Add the fields with default values (`null`, `emptyList()`) so nothing existing breaks | The same `Space` and `Mission` types, now ALSO able to carry ontology metadata | Any code written against the MVP 1 contracts -- which compiles and runs unmodified |
| `contracts/validation` | A real Journey instance, a real CRD YAML file | Round-trip the instance through JSON, then validate it against the CRD's OpenAPI schema | A test that fails if the Kotlin contract and the Kubernetes CRD ever drift apart | Whoever ships the next change to either side -- caught before merge, not after a 2am page |

---

## The Seven New Ontology Contracts

MVP 1 gave us five contracts: `Space`, `Mission`, `Agent`, `Evidence`, `Result`. MVP 2 adds seven more, and -- this is the detail both owners appreciated most -- every single one of them follows the exact same skeleton MVP 1 already established. No new pattern to learn. Just more nouns.

```kotlin
// contracts/kind/src/commonMain/kotlin/io/oep/contracts/kind/Kind.kt

@Serializable
data class KindSpec(
    val name: String,
    val description: String,
)

@Serializable
data class Kind(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: KindSpec,
    val status: KindStatus? = null,
) {
    companion object {
        const val API_VERSION: String = "oep.io/v1alpha1"
        const val KIND: String = "Kind"
    }
}
```

```kotlin
// contracts/capability/src/commonMain/kotlin/io/oep/contracts/capability/Capability.kt

@Serializable
data class CapabilitySpec(
    val name: String,
    val description: String,
)

@Serializable
data class Capability(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: CapabilitySpec,
    val status: CapabilityStatus? = null,
) {
    companion object {
        const val API_VERSION: String = "oep.io/v1alpha1"
        const val KIND: String = "Capability"
    }
}
```

```kotlin
// contracts/purpose/src/commonMain/kotlin/io/oep/contracts/purpose/Purpose.kt

@Serializable
data class PurposeSpec(
    val title: String,
    val description: String,
    val valueRefs: List<String> = emptyList(),
)

@Serializable
data class Purpose(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: PurposeSpec,
    val status: PurposeStatus? = null,
) {
    companion object {
        const val API_VERSION: String = "oep.io/v1alpha1"
        const val KIND: String = "Purpose"
    }
}
```

```kotlin
// contracts/value/src/commonMain/kotlin/io/oep/contracts/value/Value.kt

@Serializable
data class ValueSpec(
    val title: String,
    val description: String,
)

@Serializable
data class Value(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: ValueSpec,
    val status: ValueStatus? = null,
) {
    companion object {
        const val API_VERSION: String = "oep.io/v1alpha1"
        const val KIND: String = "Value"
    }
}
```

```kotlin
// contracts/relationship/src/commonMain/kotlin/io/oep/contracts/relationship/Relationship.kt

@Serializable
data class ResourceRef(
    val kind: String,
    val name: String,
)

@Serializable
data class RelationshipSpec(
    val from: ResourceRef,
    val to: ResourceRef,
    val verb: String,
)

@Serializable
data class Relationship(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: RelationshipSpec,
    val status: RelationshipStatus? = null,
) {
    companion object {
        const val API_VERSION: String = "oep.io/v1alpha1"
        const val KIND: String = "Relationship"
    }
}
```

That `Relationship` contract is worth pausing on: it's the only one of the five small ontology contracts that connects two OTHER resources to each other rather than describing one thing in isolation. `from`, `to`, and a plain string `verb` -- not an enum, just a string -- meaning the vocabulary of *how things relate* is itself extensible without a schema migration. Mission `uses` Agent. Mission `references` Evidence. Mission `produces` Result. Nobody had to add a new Kotlin sealed class for each verb.

---

## Architecture Diagram: Where the Ontology Actually Sits

```
+-----------------------------------------------------------------------+
|                         RUNTIME PLATFORMS                            |
|                                                                       |
|   +-----------------------+        +-----------------------------+   |
|   | Detective Operating   |        |   Agility Game              |   |
|   |       System           |        |  (still architecturally a  |   |
|   |                        |        |   peer, still doesn't ship |   |
|   |  Reads/writes Mission, |        |   code in this repo)        |   |
|   |  Space, Result -- same |        |                             |   |
|   |  as MVP 1               |        |  Could ALSO read Kind/      |   |
|   +-----------+-------------+        |  Capability/Purpose if it   |   |
|               |                      |  wanted to classify ITS     |   |
|               |                      |  own resources the same way |   |
|               |                      +-----------+-----------------+   |
|               |                                  |                    |
+---------------|----------------------------------|---------------------+
                |                                  |
                v                                  v
+-----------------------------------------------------------------------+
|                     REPOSITORY DOMAIN (extended)                     |
|                                                                       |
|   Space (kindRef? + capabilityRefs[] -- both OPTIONAL, both NEW)      |
|   Mission (kindRef? + capabilityRefs[] -- both OPTIONAL, both NEW)    |
|   Agent, Evidence, Result -- UNCHANGED from MVP 1                      |
+---------------------------------+---------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                  ONTOLOGY LAYER (brand new in MVP 2)                 |
|                                                                       |
|   Kind          -- what something IS    (e.g. "refactoring")          |
|   Capability    -- what something CAN DO (e.g. "investigations")      |
|   Purpose       -- WHY it exists         (e.g. "improve-maintainability") |
|   Value         -- the deeper why behind a Purpose (e.g. "code-quality")|
|   Relationship  -- how two resources connect (e.g. Mission uses Agent) |
+---------------------------------+---------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                  OPEN ENGINEERING PLATFORM (foundation)              |
|   Same as MVP 1: contracts, CRDs, schemas, SDKs                       |
+-----------------------------------------------------------------------+

KEY POINT: the ontology layer sits BELOW the Repository Domain, not
beside Detective Operating System or Agility Game. Neither runtime
platform had to change a single line of ITS OWN logic to benefit from it.
```

---

## How `Space` and `Mission` Actually Changed

This is the part that should make both platform owners breathe easy. Here is the literal diff in spirit, not in violence:

```kotlin
// contracts/space/src/commonMain/kotlin/io/oep/contracts/space/Space.kt
// MVP 1 version:
@Serializable
data class SpaceSpec(
    val name: String,
    val purpose: String,
)

// MVP 2 version:
@Serializable
data class SpaceSpec(
    val name: String,
    val purpose: String,
    val kindRef: String? = null,             // <-- NEW, nullable, defaults to null
    val capabilityRefs: List<String> = emptyList(),  // <-- NEW, defaults to empty
)
```

```kotlin
// contracts/mission/src/commonMain/kotlin/io/oep/contracts/mission/Mission.kt
// MVP 1 version:
@Serializable
data class MissionSpec(
    val name: String,
    val purpose: String,
    val spaceRef: String,
    val agentRef: String,
)

// MVP 2 version:
@Serializable
data class MissionSpec(
    val name: String,
    val purpose: String,
    val spaceRef: String,
    val agentRef: String,
    val kindRef: String? = null,
    val capabilityRefs: List<String> = emptyList(),
)
```

Two fields. Both optional. Both default to "nothing." Every `MissionSpec(...)` constructor call anywhere in Detective Operating System's existing Kotlin code -- including the `MissionReconciler` from the previous series -- continues to compile without a single edit, because Kotlin's default parameter values do not require the caller to know they exist.

---

## The Sample Ontology Resources, As Applied

The repository ships real, applied-looking ontology data, not just empty schema definitions:

```yaml
# repositories/kinds/refactoring.yaml
apiVersion: oep.io/v1alpha1
kind: Kind
metadata:
  name: refactoring
  namespace: oep-domain
spec:
  name: refactoring
  description: Investigations and missions that surface code smells and refactoring opportunities.
```

```yaml
# repositories/capabilities/investigations.yaml
apiVersion: oep.io/v1alpha1
kind: Capability
metadata:
  name: investigations
  namespace: oep-domain
spec:
  name: investigations
  description: Ability to investigate a target (e.g. a repository) and surface findings.
```

```yaml
# repositories/purposes/improve-maintainability.yaml
apiVersion: oep.io/v1alpha1
kind: Purpose
metadata:
  name: improve-maintainability
  namespace: oep-domain
spec:
  title: Improve Maintainability
  description: Reduce technical debt and increase the long-term maintainability of a codebase.
  valueRefs:
    - code-quality
```

```yaml
# repositories/relationships/mission-uses-agent.yaml
apiVersion: oep.io/v1alpha1
kind: Relationship
metadata:
  name: analyze-repository-uses-detective
  namespace: oep-domain
spec:
  from:
    kind: Mission
    name: analyze-repository-sample
  to:
    kind: Agent
    name: code-smell-detective-sample
  verb: uses
```

Notice that `Mission uses Agent` relationship is recorded as DATA -- a `Relationship` object sitting in the cluster -- not as a hardcoded assumption baked into `MissionReconciler`'s Kotlin source. Detective Operating System's controller still resolves `agentRef` the exact same imperative way it always did (a plain string lookup, as covered in the prior series). The `Relationship` resource is a parallel, declarative record of the same fact, available to anyone who wants to query "what uses what" without reading Kotlin source code to find out.

---

## The Conversation, Resumed

**OWNER OF AGILITY GAME:** "So if I wanted my 'Play Tutorial Level' Mission to declare itself as `kindRef: onboarding` and `capabilityRefs: [scoring, achievements]`, I could just... add those two fields to my own Mission YAML?"

**OWNER OF DETECTIVE OPERATING SYSTEM:** "You could add them today, with zero coordination, because they were already optional in the CRD schema the moment MVP 2 shipped. My controller wouldn't even notice -- it doesn't read `kindRef` or `capabilityRefs` for anything yet. You'd just be filling in fields nobody's consuming, for your own future benefit."

**OWNER OF AGILITY GAME:** "That sounds suspiciously like free real estate."

**OWNER OF DETECTIVE OPERATING SYSTEM:** "It's better than free real estate. It's free real estate with a Kotlin default parameter making sure nobody's existing house falls down while you build on the empty lot next door."

---

## What's Next: Journey, the Word Both Owners Finally Agree On

In **Episode 10**, we open the contract that the whole MVP 2 architecture actually orbits: `Journey`. Its `JourneyStage` state machine, its `missionRefs` list, and the test suite that mechanically proves the Kotlin contract and the live `journeys.oep.io` CRD can never quietly drift apart.

---

**🔗 Resources**
- **OEP source repository**: the MVP 2 codebase this episode is built from
- **kotlinx.serialization default values**: [kotlinlang.org/docs/serialization.html](https://kotlinlang.org/docs/serialization.html)
- **Kubernetes API versioning conventions**: [kubernetes.io/docs/reference/using-api/api-concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)

---

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one ontology underneath them both.*
