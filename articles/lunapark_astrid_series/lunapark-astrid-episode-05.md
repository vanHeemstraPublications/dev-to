---
title: "Astrid Lunapark 🎡 Ep.5"
published: false
description: "Episode 5: Every magical amusement park has a safety inspector who checks every ride before it opens, every visitor before they board, and every action before it happens. Astrid’s SecurityInterceptor is that inspector — five layers deep, from hard-block policy rules that no wristband can override, all the way to the tamper-proof audit log that makes every decision permanent. Safety makes the magic possible."
tags: [rust, security, ai, agents]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/astrid-lunapark-episode-05.png"
series: "Lunapark Astrid Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## Episode 5: The Safety Inspector — The Five-Layer Security Model

> *“All the adversity I’ve faced in my life, all my troubles and obstacles, have strengthened me. You may not realize it when it happens, but a kick in the teeth may be the best thing in the world for you — unless it’s a path traversal attack, in which case the kernel blocks it outright.”*
> — *Adapted from Walt Disney, with one very important footnote*

-----

## The Inspector Arrives ✅

The most magnificent ride in the world is useless — and dangerous — without safety checks. The roller coaster that goes upside down at 90 km/h is a wonder of engineering, but the safety harness is what makes it possible to enjoy. Without the harness, there is no ride — there is only a disaster waiting to happen.

Astrid’s **security model** is that harness. It does not limit what the agent can do; it makes it possible to trust the agent enough to *let* it do things. The kernel enforces five layers of security on every action the agent proposes. Pass all five and the action executes. Fail any one and the action is blocked — and the attempt is permanently recorded.

Every Astrianaut can choose how tight the harness is. But the harness is always on.

-----

## 🗂️ SIPOC — The Safety Inspector’s Process

|**Suppliers**           |**Inputs**                                                                              |**Process**                                                       |**Outputs**                                                              |**Customers**                                                        |
|------------------------|----------------------------------------------------------------------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------|---------------------------------------------------------------------|
|The AI agent            |A proposed action: write a file, make an HTTP request, execute a command                |`SecurityInterceptor::intercept()` — five sequential checks       |Allow (action executes) or Deny (action blocked + logged)                |The agent — which learns what it is permitted to do                  |
|The policy configuration|Admin-defined deny lists, allowed paths, allowed hosts                                  |Layer 1: Policy check — hard blocks that cannot be overridden     |A block with no appeal, no token, no human override                      |Every capsule — policy rules apply to all, always                    |
|The capability store    |Valid ed25519 signed tokens scoped to resource patterns                                 |Layer 2: Token check — does a valid token cover this action?      |A fast-path allow if a valid token exists                                |Trusted agents — they earn capability tokens and use them efficiently|
|The budget enforcer     |Per-session and per-workspace spending limits                                           |Layer 3: Budget check — is there credit available?                |A block if budget is exhausted, an atomically reserved hold if proceeding|Cost control — the agent cannot spend beyond its allocated budget    |
|The human               |An approval decision: Allow Once / Allow Session / Allow Workspace / Allow Always / Deny|Layer 4: Approval — no token? Ask the human. Queue if unavailable.|A decision (possibly with a newly minted token for Layer 2 next time)    |The agent — which proceeds or stops based on human judgment          |
|The audit system        |Every decision from all five layers                                                     |Layer 5: Audit — every outcome logged, signed, and hash-chained   |A permanent, tamper-evident record                                       |Compliance, debugging, accountability, trust-building                |

-----

## The Five Layers: The Harness Straps 🔒

The README shows it as a beautiful diagram. Let us walk each layer in detail:

```
Agent proposes action
       │
  [1. Policy]    Hard blocks. "sudo" is ALWAYS denied. Path traversal is ALWAYS denied.
       │         Admin-controlled deny lists, allowed paths, denied hosts.
       │         CANNOT be overridden by tokens or approvals. Ever.
       │
  [2. Token]     Does a valid ed25519 capability token cover this action?
       │         Scoped to resource patterns via globset matching.
       │         Time-bounded. Linked to the audit entry that created it.
       │
  [3. Budget]    Is the session within its spending limit?
       │         Per-action and per-session limits, enforced atomically.
       │         Dual-budget: session budget AND workspace budget must both allow.
       │         Reservation-based: cost is held during approval, refunded on denial.
       │
  [4. Approval]  No token? Ask the human.
       │         Allow Once / Allow Session / Allow Workspace / Allow Always / Deny.
       │         "Allow Always" mints a signed capability token for next time.
       │         "Allow Session" creates a scoped allowance that auto-matches future calls.
       │         Human unavailable? The action QUEUES, not silently skips.
       │
  [5. Audit]     Every decision — allowed, denied, deferred — is logged.
                 Each entry is signed by the runtime's ed25519 key.
                 Each entry contains the content hash of the previous.
                 Tamper with the history and the chain breaks.
```

This is real, tested code. `SecurityInterceptor` in `crates/astrid-approval/src/interceptor/mod.rs` implements exactly this flow.

-----

## Layer 1: Policy — The Hard Rules 📋

Policy is the layer that nothing can override. The park’s absolute safety rules. No acrobatics on the roller coaster. No smoking in the haunted house. No `sudo`. No path traversal. These rules are configured by the administrator and enforced before any token or approval check.

```rust
// Conceptual policy check (from astrid-approval)
pub struct PolicyConfig {
    /// Commands that are always denied, regardless of tokens or approvals
    pub denied_commands:  Vec<String>,      // ["sudo", "su", "passwd"]
    /// Network hosts that are always blocked
    pub denied_hosts:     Vec<String>,      // ["169.254.*", "10.*"] (link-local, internal)
    /// Filesystem paths the agent is allowed to access
    pub allowed_paths:    Vec<PathPattern>, // ["workspace://", "~/.astrid/public/"]
    /// Filesystem paths that are always blocked
    pub denied_paths:     Vec<PathPattern>, // ["~/.ssh/", "/etc/"]
}

impl PolicyCheck {
    pub fn check(&self, action: &Action) -> PolicyDecision {
        // Path traversal: absolute block regardless of anything
        if action.contains_path_traversal() {
            return PolicyDecision::Deny {
                reason: "Path traversal patterns (../) are always denied",
                permanent: true,  // Cannot be appealed
            };
        }

        // sudo/su: absolute block
        if let Action::Command { cmd, .. } = action {
            if self.config.denied_commands.contains(cmd) {
                return PolicyDecision::Deny {
                    reason: format!("Command '{}' is in the permanent deny list", cmd),
                    permanent: true,
                };
            }
        }

        PolicyDecision::Allow  // Policy clears; proceed to Token check
    }
}
```

-----

## Layer 2: Token — The Wristband Scanner 🎟️

If the action passes the policy check, the kernel looks for a valid ed25519 capability token. A token is a cryptographically signed permission that was minted in a previous session — either by the human saying “Allow Always” or by an administrator granting permanent access to a resource pattern.

```rust
// Capability token structure
pub struct CapabilityToken {
    pub id:          TokenId,
    pub principal:   PrincipalId,    // Who this token belongs to (v2 format)
    pub resource:    GlobPattern,    // "workspace://**/*.rs" — which resources
    pub action:      ActionPattern,  // "fs:write" — which actions
    pub not_before:  u64,            // Valid from this timestamp
    pub expires_at:  Option<u64>,    // Optional expiry
    pub audit_ref:   AuditEntryId,   // Links to the audit entry that created it
    pub signature:   ed25519::Signature, // The kernel's cryptographic signature
}

// Token validation
impl CapabilityStore {
    pub fn has_capability(
        &self,
        principal: &PrincipalId,
        action:    &Action,
    ) -> Option<&CapabilityToken> {
        self.tokens
            .iter()
            // Token must belong to THIS principal (cross-principal check — fail closed)
            .filter(|t| t.principal == *principal)
            // Token must not be expired
            .filter(|t| t.expires_at.map_or(true, |exp| exp > now_ms()))
            // Token's resource pattern must match the requested resource
            .filter(|t| t.resource.matches(action.resource()))
            // Token's action pattern must cover the requested action
            .filter(|t| t.action.matches(action.kind()))
            .next()
    }
}
```

Token present and valid? The action proceeds without asking the human. This is how an agent can work overnight — the human granted tokens in a previous session, and now the agent can work autonomously within those boundaries.

-----

## Layer 3: Budget — The Ticket Machine 🎫

Every session has a spending budget. Every workspace has a budget too. Both must have available credit for an action to proceed. The budget uses a *reservation* pattern that is delightfully clever:

```rust
// The budget reservation dance:
//
// 1. When an action arrives, reserve (hold) the estimated cost
// 2. Send to approval (Layer 4) while the hold is active
// 3. If approved: deduct the actual cost, release the hold
// 4. If denied: REFUND the reservation — it was never really spent
// 5. If async-cancelled: also REFUND — cancelled before completing

pub struct BudgetEnforcer {
    session_budget:   AtomicU64,    // This conversation's credit
    workspace_budget: AtomicU64,    // The workspace's total credit (shared)
}

impl BudgetEnforcer {
    pub fn reserve(&self, cost: u64) -> BudgetResult {
        // DUAL BUDGET: both must have credit
        let session_ok   = self.session_budget.fetch_sub(cost, Ordering::SeqCst);
        let workspace_ok = self.workspace_budget.fetch_sub(cost, Ordering::SeqCst);

        if session_ok < cost || workspace_ok < cost {
            // Refund both — out of budget
            if session_ok >= cost   { self.session_budget.fetch_add(cost, ..); }
            if workspace_ok >= cost { self.workspace_budget.fetch_add(cost, ..); }
            BudgetResult::Exhausted
        } else {
            BudgetResult::Reserved(ReservationGuard { cost })
        }
    }
}
```

Budget exhausted = the park’s token machine is empty. The agent cannot spend what it does not have.

-----

## Layer 4: Approval — The Gate Attendant 👋

No token? Time to ask the human. The approval system presents the proposed action and waits for a decision:

```
╔══════════════════════════════════════════════════════╗
║             ASTRID APPROVAL REQUEST                  ║
╠══════════════════════════════════════════════════════╣
║  The agent wants to:                                 ║
║  WRITE FILE: workspace://src/main.rs                 ║
║                                                      ║
║  Content preview:                                    ║
║  fn main() {                                         ║
║      println!("Hello, Astrid!");                     ║
║  }                                                   ║
║                                                      ║
║  [1] Allow Once      — just this time               ║
║  [2] Allow Session   — all writes to this file today ║
║  [3] Allow Workspace — all writes to src/ always    ║
║  [4] Allow Always    — mint a capability token       ║
║  [5] Deny            — block this action             ║
╚══════════════════════════════════════════════════════╝
```

Each option creates a different outcome:

|Decision       |What happens                                                                     |Token created?                 |
|---------------|---------------------------------------------------------------------------------|-------------------------------|
|Allow Once     |This specific action executes. Nothing saved.                                    |No                             |
|Allow Session  |An `Allowance` is stored in memory. Future matching calls auto-pass this session.|No                             |
|Allow Workspace|An `Allowance` stored persistently for this workspace.                           |No                             |
|Allow Always   |A signed ed25519 capability token is minted and saved to disk.                   |**Yes** ← skips Layer 4 forever|
|Deny           |Action blocked. Budget reservation refunded.                                     |No                             |

The “human unavailable” case is handled gracefully:

```rust
// If the human does not respond within the timeout,
// the action is QUEUED — not silently skipped.
// The agent waits. When the human returns and decides,
// the queued action either executes or is discarded.
// Silent skipping would hide the problem. Queuing surfaces it.
```

-----

## Layer 5: Audit — The Permanent Record 📚

Every decision — not just denials, every decision — is written to the audit trail. The trail uses a hash chain: each entry contains the cryptographic hash of the previous entry. Modify entry 47 and entry 48’s `prev_hash` no longer matches. The forgery is immediately detectable.

```rust
pub struct AuditEntry {
    /// When this event happened
    pub timestamp:    u64,

    /// What was attempted
    pub action:       AuditAction,

    /// Who attempted it
    pub principal:    PrincipalId,

    /// What the interceptor decided
    pub decision:     Decision,

    /// Optional payload for forensic replay (added in v0.6.0)
    pub params:       Option<serde_json::Value>,

    /// Blake3 hash of this entry's serialised content
    pub entry_hash:   [u8; 32],

    /// Hash of the previous entry — forms the chain
    pub prev_hash:    [u8; 32],

    /// The runtime's ed25519 signature of this entry
    pub signature:    ed25519::Signature,
}
```

The chain means:

- Entries cannot be deleted without breaking the chain
- Entries cannot be modified without breaking the chain
- Entries cannot be reordered without breaking the chain
- The sequence of decisions is cryptographically provable

For an AI agent that operates autonomously — writing code, calling APIs, managing files — this is the accountability layer that makes trust possible. *Every* action the agent ever took is recorded, signed, and permanent.

-----

## The Security Tests: Every Scenario Covered 🔬

The test suite for the security model covers every scenario:

```
SecurityInterceptor tests:
  ✓ policy_block_sudo
  ✓ policy_block_path_traversal_dotdot
  ✓ policy_block_denied_host
  ✓ budget_exhaustion_blocks_action
  ✓ budget_reservation_refunded_on_denial
  ✓ budget_refunded_on_async_cancellation
  ✓ capability_token_authorization
  ✓ capability_token_wrong_principal_denied
  ✓ allow_session_allowance_minting
  ✓ allow_always_token_minting
  ✓ audit_chain_integrity_check
  ✓ audit_tamper_detection
```

Each test exercises a specific path through the five layers. The security model is not aspirational documentation — it is tested, running code.

-----

## Operating Modes: The Harness Settings 🎢

The four operating modes control how tightly the harness is applied for each session:

```toml
# ~/.astrid/workspace.toml
[agent]
mode = "guided"   # Change this to alter the harness tightness

# mode = "safe"
#   Layer 4 fires for EVERY action outside the workspace
#   Maximum human control
#   Best for: sensitive data, learning what the agent does

# mode = "guided"
#   Layer 4 skips for reads (auto-allowed)
#   Layer 4 fires for writes and external actions
#   Best for: everyday use, trusted workspace

# mode = "autonomous"
#   Capability tokens govern everything
#   Layer 4 only fires for actions with no token
#   Best for: trusted agents with established token grants

# mode = "yolo"
#   All guardrails off
#   AUDIT STILL RUNS (Layer 5 always runs)
#   Best for: development, trusted environments only
```

Note: `mode = "yolo"` still writes to the audit trail. Layer 5 is not optional. Even the most daring Astrianaut leaves footprints.

-----

In **Episode 6**, we visit the wristband office. We explore capability tokens in full depth — how they are created, how they are scoped, how the approval system mints them, and how the budget system manages the spending limits that bound every session.

*The safety inspector gives a thumbs up. The rides are safe to board!* 👍

-----

**🔗 Resources**

- **`SecurityInterceptor` source**: [github.com/unicity-astrid/astrid/blob/main/crates/astrid-approval/src/interceptor/mod.rs](https://github.com/unicity-astrid/astrid/blob/main/crates/astrid-approval/src/interceptor/mod.rs)
- **Security model documentation**: [github.com/unicity-astrid/astrid#the-security-model](https://github.com/unicity-astrid/astrid#the-security-model)
- **Companion Repository**: [github.com/the-software-journey/astrid](https://github.com/the-software-journey/astrid)

-----

*🎡 Astrid Lunapark Series — where every episode is a new attraction, and the magic never stops.*
