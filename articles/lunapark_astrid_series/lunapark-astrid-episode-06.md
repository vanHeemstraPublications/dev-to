---
title: "Astrid Lunapark 🎡 Ep.6"
published: false
description: "Episode 6: In any great amusement park, the wristband is the token of trust. Wear the right wristband and every ride opens for you — no queue, no waiting, no asking the attendant again and again. Astrid’s capability tokens are exactly those wristbands: ed25519 signed, time-bounded, resource-scoped, and minted the moment the human says ‘yes, always.’ Come discover how trust is earned, encoded, and cryptographically enforced."
tags: [rust, security, ai, cryptography]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/astrid-lunapark-episode-06.png"
series: "Lunapark Astrid Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: The Magic Wristbands — Capability Tokens and Approval

> *“I always like to look on the optimistic side of life, but I am realistic enough to know that a wristband should be cryptographically signed before I trust it at the VIP entrance.”*
> — *A very security-conscious park visitor*

-----

## The Wristband Office Opens 🎟️

On special park days — birthday parties, corporate events, VIP visits — the guests receive wristbands. Not just any wristband: one with a unique code, a coloured stripe indicating which attractions are included, and a timestamp showing when it expires. The attendant at the roller coaster scans the wristband in half a second and the gate swings open. No questions. No forms. No waiting for the manager.

That is capability tokens in Astrid.

In Episode 5, we saw how the approval system (Layer 4) handles the human-in-the-loop decision. When the human answers “Allow Always,” something special happens: the kernel *mints a capability token*. From that moment forward, the agent can perform that action without asking the human again. The wristband does the talking.

-----

## 🗂️ SIPOC — The Wristband Office

|**Suppliers**          |**Inputs**                                                     |**Process**                                                                                              |**Outputs**                                                                    |**Customers**                                                   |
|-----------------------|---------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|----------------------------------------------------------------|
|Human approval decision|“Allow Always” response to an approval request                 |Kernel mints a new ed25519-signed `CapabilityToken` with resource pattern, principal, and optional expiry|A signed token saved to the capability store and disk                          |The agent — which uses the token on every future matching action|
|Administrator          |A direct capability grant via `caps grant <agent> <capability>`|The kernel creates a token with the specified scope and saves it                                         |A pre-granted capability — agent can perform this action from the first session|Automated agents that start fully trusted                       |
|The capability store   |A proposed action + a `PrincipalId`                            |`find_capability(principal, action)` — searches by principal first (fail-closed cross-principal check)   |A matching token if found, or `None` to trigger the approval system            |Layer 2 of the security interceptor                             |

-----

## The Token’s Anatomy: Reading the Wristband 🔬

A capability token is a small, precisely structured piece of data that contains everything needed to verify it is legitimate and applies to the current action:

```rust
pub struct CapabilityToken {
    /// Unique identifier for this token
    pub id: TokenId,  // UUID-like

    /// Which principal (agent) this token belongs to
    /// (Added in v0.6.0 — tokens are now principal-scoped!)
    pub principal: PrincipalId,

    /// Which resources this token covers
    /// Uses globset matching:
    ///   "workspace://**/*.rs"  — any .rs file in the workspace
    ///   "workspace://src/**"   — anything under src/
    ///   "workspace://"         — the entire workspace
    pub resource: GlobPattern,

    /// Which actions are covered
    ///   "fs:write"             — file write operations
    ///   "fs:*"                 — all filesystem operations
    ///   "http:api.github.com"  — HTTP to GitHub specifically
    pub action: ActionPattern,

    /// When this token becomes valid (Unix timestamp in milliseconds)
    pub not_before: u64,

    /// When this token expires (None = no expiry)
    pub expires_at: Option<u64>,

    /// Links back to the audit entry that created this token
    /// If the audit entry is tampered with, this link breaks
    pub audit_ref: AuditEntryId,

    /// The kernel's runtime ed25519 signature
    /// Generated when the token is minted, never regenerated
    pub signature: ed25519::Signature,
}
```

The `principal` field was added in v0.6.0 — a significant security improvement. Before this, a token for Agent A could theoretically be used by Agent B if they shared a store. Now tokens are principal-scoped and the check fails closed: Agent B’s principal doesn’t match Agent A’s token, even if the resource and action patterns do.

-----

## Minting a Token: The “Allow Always” Ceremony 🪄

When the human says “Allow Always,” the following ceremony takes place:

```rust
// Inside the approval manager, when ApprovalDecision::AllowAlways is received:

pub fn mint_capability_token(
    &self,
    principal:  &PrincipalId,
    action:     &Action,
    audit_ref:  AuditEntryId,
) -> Result<CapabilityToken, CryptoError> {
    let token = CapabilityToken {
        id:          TokenId::new_v4(),
        principal:   principal.clone(),
        resource:    action.resource_pattern(),   // Derived from the specific resource
        action:      action.kind_pattern(),       // Derived from the action type
        not_before:  now_ms(),
        expires_at:  None,                        // By default: no expiry
        audit_ref,
        signature:   Signature::default(),        // Placeholder for now
    };

    // Sign the entire token with the kernel's runtime ed25519 private key
    let serialised = serde_json::to_vec(&token)?;
    let signature  = self.signing_key.sign(&serialised);

    let signed_token = CapabilityToken { signature, ..token };

    // Save to the capability store (in-memory)
    // and persist to disk (in the principal's token store)
    self.store.insert(signed_token.clone());
    self.persist_token(&signed_token)?;

    Ok(signed_token)
}
```

The token is now on disk. The next time the agent wants to write to `workspace://src/main.rs`, Layer 2 of the security model finds this token, verifies the signature, checks the principal, checks the expiry, and if all is well — the action proceeds without ever reaching Layer 4. The human is not disturbed. The wristband does the work.

-----

## Allow Session vs. Allow Always: Two Types of Wristband 💛

There is an important distinction between the two most permissive approval responses:

### Allow Session — The Day Pass

```rust
pub struct Allowance {
    /// Which principal holds this allowance
    pub principal: PrincipalId,

    /// What scope this allowance covers
    pub scope: AllowanceScope,

    /// When it auto-expires
    pub expires: AllowanceExpiry::EndOfSession,
}

// AllowanceScope can match broad patterns:
// "all writes to workspace://src/**"
// "all HTTP requests to api.github.com"
```

An `Allowance` lives in memory. It does not persist to disk. When the session ends and the last connection closes, `clear_all_session_allowances()` wipes it clean. Next session, the agent starts fresh — but can earn the allowance again just by asking once.

This is the day visitor’s coloured wristband. Today only. Tomorrow, new wristband.

### Allow Always — The Season Pass

A `CapabilityToken` persists to disk, signed cryptographically. It survives session restarts, process restarts, even OS reboots. It is only gone when explicitly revoked.

```bash
# Revoke a capability token
astrid caps revoke <token-id>

# Or revoke all tokens for an agent
astrid caps revoke --principal <agent-name> --all
```

The season pass, good until explicitly cancelled.

-----

## Globset Matching: How the Wristband Covers Multiple Rides 🗺️

Capability tokens use **globset** patterns — the same pattern language that `.gitignore` uses — to specify which resources a token covers. This allows a single token to cover a meaningful scope without being overly broad:

```rust
// Examples of resource patterns and what they cover:

"workspace://src/**/*.rs"
// Covers: workspace://src/main.rs ✓
//         workspace://src/lib.rs  ✓
//         workspace://src/utils/helper.rs ✓
//         workspace://tests/test.rs ✗ (not under src/)
//         workspace://config.toml  ✗ (not .rs)

"workspace://src/**"
// Covers: workspace://src/main.rs ✓
//         workspace://src/utils/helper.rs ✓
//         workspace://src/config.toml ✓ (any file under src/)
//         workspace://tests/test.rs ✗ (not under src/)

"http:api.github.com"
// Covers: HTTP requests to api.github.com ✓
//         HTTP requests to github.com ✗ (different host)
//         HTTP requests to evil.com ✗ (definitely not)

"http:*.github.com"
// Covers: api.github.com ✓
//         raw.githubusercontent.com ✗ (not *.github.com)
//         uploads.github.com ✓

// The overly-broad (admin-only) wildcard:
"*"
// Covers: everything
// REQUIRES: --unsafe-admin flag as of v0.6.0
// Previously: could be granted without acknowledgement
// Now: explicit opt-in required
```

The `--unsafe-admin` requirement for bare `*` was added in v0.6.0 precisely because it is too easy to accidentally grant universal admin-equivalent access. Now you have to mean it.

-----

## The Budget System: Counting Your Tokens 💰

Alongside capability tokens, the budget system ensures agents cannot run up an unlimited bill. The dual-budget model is one of the cleverer designs in Astrid:

```
SESSION BUDGET:   The credit allotted to this conversation.
                  Starts fresh every session.
                  Tracks per-action costs (e.g. token counts for LLM calls).

WORKSPACE BUDGET: The credit allotted to the workspace overall.
                  Shared across all sessions.
                  Prevents "run 100 parallel sessions each with their own budget"
                  from bypassing the workspace-level limit.

BOTH must have credit for an action to proceed.
```

```rust
// Budget configuration in workspace.toml
[agent.budget]
session_limit   = 10_000   # LLM tokens per conversation
workspace_limit = 100_000  # LLM tokens per month across all sessions

// Or using cost units for mixed workloads:
[agent.budget.costs]
llm_token    = 1
file_write   = 10
http_request = 5
```

The reservation-based pattern from Episode 5 means: if the action requires 500 tokens of budget, those 500 are held (reserved) during the approval wait. If the human denies the action, the 500 are refunded. If the action is cancelled asynchronously, the 500 are also refunded. Budget is always accurate.

-----

## Gradual Trust: The Astrid Philosophy 🌱

The capability system is designed for gradual, earned trust. A brand-new agent starts with minimal capabilities. As the human works with it, they grant permissions:

```
Session 1:
  Agent: "May I write to workspace://src/main.rs?"
  Human: "Allow Session"
  → Agent writes the file. Session allowance created.

Session 1 (later):
  Agent: "May I write to workspace://src/lib.rs?"
  Human: "Allow Session"  (same scope — auto-matches via AllowanceScope)
  → No second prompt needed. Allowance already covers all src/ writes.

Session 2:
  Agent: "May I write to workspace://src/utils.rs?"
  Human: "Allow Always"  (now trusting this completely)
  → A signed CapabilityToken minted for "workspace://src/**" writes.

Session 3 and all future sessions:
  Agent writes to workspace://src/**
  → No prompts. Token found. Verified. Proceeding.
  → Human not disturbed. Agent works freely within the boundary.
```

The trust expands as the relationship develops. The harness does not disappear — it just becomes lighter as it is earned.

-----

## Principal Profiles: The Season Pass System 🏅

Every identity in the park has a profile that aggregates their capabilities:

```toml
# ~/.astrid/etc/profiles/my-agent.toml
# (Note: deliberately outside home/! Capsules cannot read their own policy.)

[profile]
enabled = true
groups  = ["developer"]

[grants]
# Grant specific capabilities beyond what the group provides
"fs:write:workspace://reports/**" = { reason = "Generates weekly reports" }
"http:api.github.com"            = { reason = "GitHub integration" }

[revokes]
# Remove capabilities the group would otherwise provide
"process:spawn"                  = { reason = "This agent should not spawn subprocesses" }

[quotas]
session_tokens   = 10_000
workspace_tokens = 100_000
```

Groups carry capability bundles. Individual `grants` and `revokes` adjust the group baseline. The profile is the season pass card — it summarises exactly what this agent is allowed to do, persistently, across every session.

-----

In **Episode 7**, we unfold the park map. The VFS (Virtual Filesystem) overlay is Astrid’s magical copy-on-write layer that gives every agent its own view of the world — while protecting the real files underneath.

*The wristband glitters in the sunlight. Every ride is open to you!* ✨

-----

**🔗 Resources**

- **Capability tokens**: [github.com/unicity-astrid/astrid#the-security-model](https://github.com/unicity-astrid/astrid#the-security-model)
- **CHANGELOG v0.6.0**: [github.com/unicity-astrid/astrid/blob/main/CHANGELOG.md](https://github.com/unicity-astrid/astrid/blob/main/CHANGELOG.md)
- **Companion Repository**: [github.com/the-software-journey/astrid](https://github.com/the-software-journey/astrid)

-----

*🎡 Astrid Lunapark Series — where every episode is a new attraction, and the magic never stops.*
