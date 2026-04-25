---
title: "Globetrotters IAM 🌍 Ep.6"
part: 6
published: false
description: "Episode 6: The queue manager at the checkpoint does not check passports. They count the queues, direct travellers to the next available officer, and notice when one booth goes dark. GMF PRD LDAP LB-T is that dispatcher — routing test workloads to city-a or city-b, maintaining high availability, and keeping test traffic in its designated lane."
tags: [iam, ldap, highavailability, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrottters_identy_and_access_management_series/globetrotters-iam-episode-06.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: The Checkpoint Dispatcher

> *“The queue manager does not examine credentials. They ensure every traveller reaches an officer — and that when one booth closes, the queue redistributes without chaos.”*

-----

## The Person Who Keeps the Lines Moving 🚦

Imagine a busy border crossing with twelve passport control booths. The queue manager stands at the entrance of the hall, watching the queues build. Booth seven is falling behind — the officer is dealing with a complex case. The queue manager redirects the next ten travellers to booths three and nine. Booth four goes dark — the officer left for a break. The queue manager stops directing anyone there.

The travellers do not know which booth they were sent to. They do not care. They presented their documents, the check was performed, and they walked through. The queue manager made the routing decision silently and efficiently.

**GMF PRD LDAP LB-T** is that queue manager. Every LDAP query from our Test Factory solution arrives at the load balancer. The load balancer decides whether to route it to AUTH GMF PRD city-a or AUTH GMF PRD city-b. If city-a is down, the load balancer stops routing there until it recovers. If city-b is slow, the load balancer adjusts. The caller — our Test Factory solution — never knows which server answered the query.

This is the **Starting Point** in ACME’s IAM topology. Our entry door. Episode 6 is about that door.

-----

## 🗂️ SIPOC — The Checkpoint Dispatcher

|**Suppliers**                               |**Inputs**                                    |**Process**                                                                                         |**Outputs**                                             |**Customers**                                                             |
|--------------------------------------------|----------------------------------------------|----------------------------------------------------------------------------------------------------|--------------------------------------------------------|--------------------------------------------------------------------------|
|Test Factory solution / other test workloads|LDAPS connection request on port 636          |TLS termination (or pass-through) → health check → select available backend → proxy the LDAP session|Transparent LDAP session to one of the backend servers  |Test Factory — receives LDAP responses as if from a single server         |
|AUTH GMF PRD city-a                         |Health check responses (LDAP ping / TCP check)|Load balancer monitors backend health continuously                                                  |Routing table: city-a = healthy / degraded / unavailable|LB-T routing algorithm — city-a receives queries when healthy             |
|AUTH GMF PRD city-b                         |Health check responses                        |Same health monitoring                                                                              |Routing table: city-b = healthy / degraded / unavailable|LB-T routing algorithm — city-b is the failover when city-a is unavailable|

-----

## What “Load Balancer” Means for LDAP 🔄

HTTP load balancers are familiar territory. LDAP load balancers work on the same principle but at the TCP/session layer, because LDAP is a stateful, persistent-connection protocol:

1. The client opens a TCP connection to the load balancer’s IP on port 636
1. TLS handshake completes with the load balancer’s certificate
1. The load balancer selects a backend server (city-a or city-b) based on current load and health
1. The LDAP session is proxied to that backend for its duration
1. The client performs its bind, search, and compare operations against that backend
1. The session closes; the next connection may be routed to a different backend

For short-lived LDAP queries (bind + one search + close), the routing decision happens once per connection. For long-lived connections (persistent bind sessions used by some middleware), the load balancer maintains the session affinity for the duration.

-----

## The High Availability Design: Two Booths, One Queue 🏛️

ACME’s dual-DC design for the production LDAP infrastructure:

```
                    ┌─────────────────────────────┐
                    │    GMF PRD LDAP LB-T         │
                    │   ★ STARTING POINT           │
                    │   port 636 (LDAPS)            │
                    └──────────┬──────────┬─────────┘
                               │          │
                    Health     │          │    Health
                    check: OK  │          │    check: OK
                               │          │
               ┌───────────────▼┐        ┌▼───────────────┐
               │ AUTH GMF PRD   │        │ AUTH GMF PRD   │
               │   city-a       │◄──────►│   city-b       │
               │  (CITY-A DC)   │LDAP    │  (CITY-B DC)   │
               │  gds-city-a    │REPLICA │  gds-city-b    │
               └────────────────┘        └────────────────┘
```

### Normal operation (both backends healthy)

The load balancer distributes queries between city-a and city-b. The algorithm depends on the LB implementation — round-robin, least-connections, or weighted — but from the caller’s perspective, responses are equivalent: both backends hold the same replicated directory data.

### Failover: CITY-A data centre unavailable

```
CITY-A DC goes down:
  AUTH GMF PRD city-a → health check fails

GMF PRD LDAP LB-T:
  city-a health: FAIL → stop routing to city-a
  city-b health: OK   → all queries route to city-b

Result: no client-visible outage (brief reconnection for in-flight sessions)
        all LDAP queries served from city-b
        monitoring alerts: "city-a backend offline"
```

### Failover: both DCs unavailable

If both backends are simultaneously unavailable (a full infrastructure outage), the load balancer returns a connection refused or timeout. This is the LDAP HA boundary: the load balancer cannot serve directory queries it does not have.

From a Test Factory perspective, this means our solution must handle LDAP connection failures gracefully — logging a clear error, surfacing it in test results, and not masking the failure as a test failure rather than an infrastructure failure.

-----

## The “T” in LDAP LB-T: Test Lane Designation 🧪

The suffix “T” in GMF PRD LDAP LB-T explicitly designates this load balancer as the **test-designated entry point** for LDAP services. This is not cosmetic naming. It serves a deliberate architectural purpose:

**Traffic separation.** Production services that need LDAP authentication use a different load balancer (or direct connection to the LDAP servers). Test workloads use LDAP LB-T. If test workloads produce high query volumes, degrade the LDAP connection pool, or trigger rate limits, the impact is isolated to the test lane — production LDAP traffic is unaffected.

**Access control.** The LDAP LB-T may have different ACLs applied than the production LDAP load balancer. Test service accounts (`grp-ldap-bind-t`) are specifically provisioned with access through the T-lane. A production service account may not be able to bind through LDAP LB-T, and conversely, a test service account may not be able to bind through the production LDAP load balancer.

**Monitoring and observability.** Operations teams can apply separate monitoring thresholds to LDAP LB-T vs. the production load balancer. A spike in query volume on LDAP LB-T during a test run is expected and unremarkable. The same spike on the production LDAP load balancer would trigger an alert.

**Scope confirmation.** Despite the “T” designation, LDAP LB-T queries the **production GMF directory** (AUTH GMF PRD city-a/b). This means test workloads authenticate against real production identities. The test designation is about the traffic path, not about using a separate test identity store. Our service account `uid=svc-testfactory-prod` is a real entry in the production GMF directory.

-----

## Connection Flow: Test Factory to LDAP LB-T 🔗

The full connection path for our solution’s LDAP operations:

```
Step 1: DNS resolution
  LDAP LB-T hostname → IP address
  (e.g., ldap-lb-t.gmf.acme.com → 10.x.x.x)

Step 2: TCP connection
  Test Factory container → port 636 on LDAP LB-T

Step 3: TLS handshake
  LDAP LB-T presents its X.509 certificate
  Test Factory validates: does this cert chain to ACME Root CA?
  If yes: TLS session established
  If no: connection refused (Episode 7 covers the PKI in detail)

Step 4: LDAP bind
  Test Factory sends: DN=uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
                      Password=[from secrets vault]
  LDAP LB-T proxies to city-a or city-b
  AUTH GMF PRD verifies the credential

Step 5: LDAP search (if needed)
  Test Factory sends: SEARCH (uid=target-user) ATTRIBUTES memberOf, accountStatus
  LDAP LB-T proxies search to same backend as the bind
  AUTH GMF PRD returns matching entries

Step 6: Session close
  Test Factory sends UNBIND
  LDAP session terminates
  TCP connection closes
```

-----

## Operational Concerns for the Test Factory 🔧

**Connection pool sizing.** Each test execution thread that needs LDAP access opens its own bind session (or draws from a connection pool). If 20 parallel test threads each open a persistent LDAP session, we have 20 connections into LDAP LB-T — all consuming backend connection pool slots on city-a/b. Size the connection pool conservatively and use connection reuse where possible.

**Timeout configuration.** Network latency between the test execution container and LDAP LB-T varies. LDAP operations should have explicit timeouts configured — both the connection timeout (how long to wait for TCP connect) and the operation timeout (how long to wait for a bind or search response). Unbounded LDAP waits cause test hangs.

**Health check interpretation.** If our solution receives an LDAP error during test execution, the error code distinguishes infrastructure problems from authentication failures:

|LDAP Result Code       |Meaning                                          |Action                                                                            |
|-----------------------|-------------------------------------------------|----------------------------------------------------------------------------------|
|`0`                    |Success                                          |Proceed                                                                           |
|`49`                   |Invalid credentials                              |Service account password wrong / expired — alert operations                       |
|`32`                   |No such object                                   |DN does not exist in the directory — SailPoint provisioning may not have completed|
|`53`                   |Unwilling to perform                             |Account disabled — check `accountStatus` in directory                             |
|`52e` (Windows LDAP)   |Account disabled (Active Directory specific code)|Escalate to operations                                                            |
|`-1` / connection error|Backend unreachable                              |Both DCs may be down — escalate to operations                                     |

**Test isolation at the LDAP level.** Because LDAP LB-T queries the production GMF directory, our test workloads must never attempt to create, modify, or delete user objects or group memberships during test execution. LDAP writes from our solution must be limited to whatever scope is explicitly granted by ACLs — typically read-only bind and search.

-----

## The PRD/ACC Separation Revisited 🏗️

The ACME topology includes AUTH GMF ACC — the acceptance LDAP server. For clarity:

|Path                     |Entry point           |Backend              |Serves                                 |
|-------------------------|----------------------|---------------------|---------------------------------------|
|Production test workloads|**GMF PRD LDAP LB-T** |AUTH GMF PRD city-a/b|Production identities in the GMF domain|
|Acceptance workloads     |(ACC equivalent entry)|AUTH GMF ACC         |Acceptance-environment identities      |

Our Test Factory solution operates in the production lane via LDAP LB-T, authenticating against the production GMF directory. This is intentional: the system under test (SUT) uses production identities, and our test workloads must authenticate using those same production-grade identities and group structures to simulate real traffic accurately.

-----

In **Episode 7**, we examine the security layer that wraps everything: PKI, TLS, mTLS, the ACME Root CA, and why the trust chain from Keyfactor to LDAP LB-T is the thread that holds the whole topology together.

-----

**🔗 Resources**

- **LDAP load balancing (HAProxy LDAP backend)**: [haproxy.com/documentation](https://www.haproxy.com/documentation)
- **LDAP connection handling best practices**: [ldap.com/ldap-operation-types](https://ldap.com/ldap-operation-types/)
- **Network load balancer HA patterns**: [cloudflare.com/learning/performance/what-is-load-balancing](https://www.cloudflare.com/learning/performance/what-is-load-balancing/)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time.*
