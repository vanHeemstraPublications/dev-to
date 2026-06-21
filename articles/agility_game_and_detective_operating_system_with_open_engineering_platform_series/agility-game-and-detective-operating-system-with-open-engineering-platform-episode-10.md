---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.10: Journey, the Word Both Owners Finally Agree On"
published: false
description: "Episode 10: Every platform has its own jargon for what a user is actually doing. MVP 2 proposes one word both Agility Game and Detective Operating System can use without flinching: Journey. This episode opens the Journey contract, its five-stage state machine, the matching journeys.oep.io CRD, and the test that mechanically proves the Kotlin and the YAML can never drift apart."
tags: [kotlin, kubernetes, crds, testing]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-10.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 10: Journey, the Word Both Owners Finally Agree On

---

## A Word Negotiation, Settled in Advance

Ask the owner of Detective Operating System what a user is doing and you'll hear "running an investigation." Ask the owner of Agility Game and you'll hear "playing a level," or "completing a quest," depending on which Tuesday it is. Two perfectly reasonable vocabularies, with zero overlap, both describing the same underlying shape: something starts, something happens, something finishes, something is learned.

`INTENT_MVP_2.md` proposes a word neither owner has a strong emotional attachment to, which paradoxically makes it the perfect compromise: Journey. Not "Investigation." Not "Quest." Just the bare scaffolding both of those things actually are, with the flavor text left for each runtime platform to supply on its own terms.

---

## SIPOC -- The Journey Contract

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| The ontology layer (Episode 9) | A purposeRef, a kindRef, a list of capabilityRefs | Describe a Journey's intent without describing its implementation | A JourneySpec that says WHY and WHAT KIND, never HOW | The Investigation Crossplane Composition (Episode 11), which fills in the HOW |
| The Kubernetes API server | An applied Journey CR | Validate it against the journeys.oep.io CRD's OpenAPI schema | A stored, watchable Journey object with a status.stage field | The OEP CLI (Episode 12), which reads and reports on this field |
| contracts/validation | A real Journey instance, the literal CRD YAML | Two checks: JSON round-trip fidelity, AND schema conformance against the actual CRD file on disk | A test that fails the build the moment the Kotlin contract and the CRD schema disagree | Every future contributor touching either file, caught in CI, not in a 2am incident |

---

## The Journey Contract, in Full

```kotlin
// contracts/journey/src/commonMain/kotlin/io/oep/contracts/journey/Journey.kt

@Serializable
enum class JourneyStage {
    Pending,
    Composing,
    Executing,
    Completed,
    Failed,
}

@Serializable
data class ResourceRef(
    val kind: String,
    val name: String,
)

@Serializable
data class LinkedResource(
    val kind: String,
    val name: String,
)

@Serializable
data class JourneySpec(
    val purposeRef: String,
    val kindRef: String,
    val capabilityRefs: List<String> = emptyList(),
    val missionRefs: List<ResourceRef> = emptyList(),
)

@Serializable
data class JourneyStatus(
    val stage: JourneyStage? = null,
    val observedGeneration: Long? = null,
    val conditions: List<Condition>? = null,
    val linkedResources: List<LinkedResource>? = null,
)

@Serializable
data class Journey(
    val apiVersion: String = API_VERSION,
    val kind: String = KIND,
    val metadata: ObjectMeta? = null,
    val spec: JourneySpec,
    val status: JourneyStatus? = null,
) {
    companion object {
        const val API_VERSION: String = "oep.io/v1alpha1"
        const val KIND: String = "Journey"
    }
}
```

Notice what's deliberately absent: there is no `JourneySpec.runtimePlatform` field, no `JourneySpec.detectiveSettings` field, no `JourneySpec.agilityGameSettings` field. The Journey contract has no idea Detective Operating System or Agility Game exist. It just says: here is a purpose, here is a kind, here are some capabilities, and here is a list of Mission references it composes. Whichever runtime platform's controller eventually picks up the linked Missions is the runtime platform's own business, decided entirely by what's actually sitting in `missionRefs`.

---

## The Five-Stage Journey, As a Diagram

```
JOURNEY STAGE STATE MACHINE (status.stage)

  Pending --------> Composing --------> Executing --------> Completed
     |                                       |
     |                                       v
     +-------------------------------------> Failed

  Pending:    Journey exists, nothing has been composed yet
  Composing:  Crossplane is assembling the Space/Agent/Mission chain
              (the Investigation Composition from Episode 11)
  Executing:  The composed Missions are actively running
              (Detective Operating System's MissionReconciler, doing
               the exact same work it did in the original series)
  Completed:  Every linked Mission reached a terminal success state
  Failed:     Something in the chain failed -- composition or execution
```

Compare this five-stage Journey lifecycle to the four-stage MissionPhase lifecycle from the original series (Pending -> Running -> Completed/Failed). They are deliberately NOT the same enum, and that's correct: a Journey's Composing stage describes Crossplane assembling resources, a layer below where Mission's own phase lives. A single Journey could, in principle, fan out into several Missions, each with its OWN MissionPhase, while the Journey's JourneyStage tracks the aggregate picture one level up.

---

## The Matching CRD

```yaml
# crds/journeys.oep.io.yaml (abbreviated)
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: journeys.oep.io
spec:
  group: oep.io
  scope: Namespaced
  names:
    kind: Journey
    listKind: JourneyList
    plural: journeys
    singular: journey
    shortNames:
      - jrny
    categories:
      - oep
      - ontology
  versions:
    - name: v1alpha1
      served: true
      storage: true
      subresources:
        status: {}
      additionalPrinterColumns:
        - name: Purpose
          type: string
          jsonPath: .spec.purposeRef
        - name: Kind
          type: string
          jsonPath: .spec.kindRef
        - name: Stage
          type: string
          jsonPath: .status.stage
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
      schema:
        openAPIV3Schema:
          type: object
          required: [spec]
          properties:
            spec:
              type: object
              required: [purposeRef, kindRef]
              properties:
                purposeRef: { type: string }
                kindRef: { type: string }
                capabilityRefs:
                  type: array
                  items: { type: string }
                missionRefs:
                  type: array
                  items:
                    type: object
                    required: [kind, name]
                    properties:
                      kind: { type: string }
                      name: { type: string }
            status:
              type: object
              x-kubernetes-preserve-unknown-fields: true
              properties:
                stage:
                  type: string
                  enum: [Pending, Composing, Executing, Completed, Failed]
```

Read that `enum: [Pending, Composing, Executing, Completed, Failed]` line against the Kotlin JourneyStage enum from earlier in this episode. Five values, in the same order, meaning the same thing, enforced independently by two completely different runtimes: the Kubernetes API server validating YAML, and the Kotlin compiler validating @Serializable enum cases. If one ever drifted from the other, you would not find out from a thoughtful code review. You would find out from a test failing on purpose.

---

## The Test That Refuses to Let Them Drift Apart

```kotlin
// contracts/validation/src/test/kotlin/io/oep/contracts/validation/JourneyContractCrdTest.kt

class JourneyContractCrdTest {
    private val schema = CrdSchemaLoader.load("journeys.oep.io.yaml")

    @Test
    fun journeyInstanceRoundTripsThroughJson() {
        val instance = Journey(
            metadata = ObjectMeta(name = "audit", namespace = "oep"),
            spec = JourneySpec(
                purposeRef = "improve-quality",
                kindRef = "refactoring",
                capabilityRefs = listOf("investigations"),
                missionRefs = listOf(ResourceRef(kind = "Mission", name = "audit-1")),
            ),
            status = JourneyStatus(
                stage = JourneyStage.Executing,
                observedGeneration = 4L,
                conditions = listOf(Condition(type = "Ready", status = "True")),
                linkedResources = listOf(LinkedResource(kind = "Mission", name = "audit-1")),
            ),
        )
        assertRoundTrip(instance, Journey.serializer())
    }

    @Test
    fun journeyInstanceConformsToCrdSchema() {
        val instance = Journey(
            metadata = ObjectMeta(name = "audit", namespace = "oep"),
            spec = JourneySpec(
                purposeRef = "improve-quality",
                kindRef = "refactoring",
                missionRefs = listOf(ResourceRef(kind = "Mission", name = "audit-1")),
            ),
            status = JourneyStatus(stage = JourneyStage.Pending, observedGeneration = 1L),
        )
        assertConformsToSchema(instance, Journey.serializer(), schema, "Journey")
    }
}
```

Two tests, two different kinds of paranoia, both healthy:

```
journeyInstanceRoundTripsThroughJson:
  Build a Journey in Kotlin -> serialize to JSON -> deserialize back
  -> assert the result equals the original.
  Catches: a kotlinx.serialization bug, a typo in a field name,
  a default value silently swallowing data.

journeyInstanceConformsToCrdSchema:
  Build a Journey in Kotlin -> serialize to JSON -> validate the JSON
  against the ACTUAL OpenAPI schema loaded from crds/journeys.oep.io.yaml
  on disk.
  Catches: the Kotlin contract and the Kubernetes CRD disagreeing about
  what a valid Journey even looks like -- the exact failure mode that
  would otherwise only surface at kubectl apply time, in someone's
  actual cluster, on a bad day.
```

`CrdSchemaLoader.load("journeys.oep.io.yaml")` is doing something almost embarrassingly simple and almost embarrassingly important: it reads the SAME FILE that gets `kubectl apply`'d to a real cluster, and uses it as the ground truth for what a passing Kotlin test even means. There is exactly one schema. It just happens to be checked from two different angles.

---

## The Conversation, Resumed

OWNER OF AGILITY GAME: "If I write my own runtime platform's controller and it watches Journeys with kindRef: onboarding, do I need to write my own version of this validation test?"

OWNER OF DETECTIVE OPERATING SYSTEM: "You'd want to, for your own sanity, but you wouldn't need MY permission or MY test file to do it. You'd load the same journeys.oep.io.yaml -- it's a public CRD applied once to the shared cluster -- and write your own assertConformsToSchema check against whatever Kotlin, TypeScript, or Rust type you use to model a Journey on your side. The schema is the contract. The test is just due diligence anyone can perform independently."

OWNER OF AGILITY GAME: "So the CRD is doing the same job here that it did for Mission and Space back in the first eight episodes."

OWNER OF DETECTIVE OPERATING SYSTEM: "Word for word the same job. We just gave it a bigger word to police."

---

## What's Next: One XR to Rule the Chain

A Journey describes intent: a purpose, a kind, some capabilities, and a list of Mission references it expects to exist. Something still has to turn that intent into an actual Space, Agent, and Mission sitting in the cluster. In Episode 11, we open the Crossplane Investigation Composition, the single XR that assembles the whole chain in one patch-and-transform pipeline, picking up exactly where MVP 1's much smaller XRefactoringSpace left off.

---

**Resources**
- OEP source repository: the MVP 2 codebase this episode is built from
- Kubernetes CRD status subresources: kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions
- OpenAPI v3 schema validation: swagger.io/specification

---

*Agility Game and Detective Operating System with Open Engineering Platform -- two platforms, zero shared dependencies, one ontology underneath them both.*
