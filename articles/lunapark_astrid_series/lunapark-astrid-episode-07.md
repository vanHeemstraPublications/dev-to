---
title: "Astrid Lunapark 🎡 Ep.7"
published: false
description: "Episode 7: In any great amusement park, the map shows you every attraction, every path, every shortcut. But the real park is beneath it — the actual ground, the real buildings, the permanent infrastructure. Astrid’s VFS overlay works the same way: a copy-on-write layer that gives the agent its own magical map of the filesystem, while the real files stay safe underneath. Write all you like — it’s all just temporary paint until you commit."
tags: [rust, filesystem, ai, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/astrid-lunapark-episode-07.png"
series: "Lunapark Astrid Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: The Park Map — VFS and the Copy-on-Write Overlay

> *“The way to get started is to quit talking and begin doing — but in Astrid’s VFS, ‘begin doing’ means writing to the ephemeral upper layer, not the permanent lower one. The real ground is safely protected.”*

-----

## The Map Comes to Life 🗺️

Every visitor to a grand park receives a map. On this map, every path is clearly drawn, every attraction is labelled, every shortcut is indicated. You can write on the map, fold it, annotate it — and the park itself remains unchanged. The real paths are real. The real buildings are real. Your annotations are just on the paper.

Astrid’s **VFS overlay** is that map — taken to a magical extreme.

The agent receives its own view of the filesystem: the **workspace** as the read-only foundation (the real ground) and an **ephemeral upper layer** as the writable surface (the paper overlay). Every write the agent makes goes onto the paper. The real files underneath are untouched. When the session ends, the agent can choose: *commit* the paper marks permanently to the real ground, or *discard* the entire paper layer and walk away as if nothing happened.

This is **copy-on-write** (COW) overlay, and it is what makes Astrid’s agent sessions reversible, safe, and composable.

-----

## 🗂️ SIPOC — The Park Map System

|**Suppliers**           |**Inputs**                                                       |**Process**                                                                          |**Outputs**                                                           |**Customers**                                             |
|------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------------|----------------------------------------------------------------------|----------------------------------------------------------|
|The workspace           |The agent’s persistent workspace directory on the real filesystem|Mounted as the **read-only lower layer** of the overlay                              |A stable foundation that cannot be accidentally corrupted by the agent|The agent — reads real workspace files through the overlay|
|The tmpdir (session)    |A temporary directory created fresh at session start             |Mounted as the **writable upper layer**                                              |Every agent write goes here, not to the real workspace                |The agent — writes land here safely and reversibly        |
|The session end decision|“commit” or “discard” choice                                     |Commit: apply the upper-layer diff to the lower workspace; Discard: delete the tmpdir|Either permanently updated workspace or a perfectly clean slate       |The workspace — either updated or unchanged               |
|Path validation         |Any path the agent tries to access                               |`../../etc/passwd` → VFS layer rejects before touching host filesystem               |Path traversal attempts caught at the VFS layer                       |The host system — completely protected from path traversal|

-----

## The Two Layers: Foundation and Fresco 🏛️

Think of the overlay as a Renaissance fresco: the wall (the workspace) is permanent plaster. The fresco (the upper layer) is applied on top. The artist paints on the fresco. If they are not satisfied, they can remove the fresh layer before it sets and start again. The wall is untouched.

```
┌────────────────────────────────────────────────────────────────────┐
│                      ASTRID VFS OVERLAY                           │
│                                                                    │
│  Upper Layer (writable — ephemeral tmpdir)                        │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ src/main.rs  ← MODIFIED (write went here, not to workspace) │   │
│  │ output.txt   ← NEW (created by agent, not in workspace)     │   │
│  └────────────────────────────────────────────────────────────┘   │
│                          │ COW merge                               │
│  Lower Layer (read-only — real workspace)                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ src/main.rs  ← ORIGINAL (agent reads this if not modified) │   │
│  │ src/lib.rs   ← ORIGINAL (unchanged, agent sees it here)    │   │
│  │ Cargo.toml   ← ORIGINAL (unchanged)                        │   │
│  │ README.md    ← ORIGINAL                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  From the agent's perspective: ONE seamless view of the project   │
└────────────────────────────────────────────────────────────────────┘
```

When the agent reads `src/main.rs`, the VFS checks: is there a modified version in the upper layer? Yes → return that. No → return the original from the workspace. The agent sees a single coherent filesystem. The complexity is invisible.

-----

## Path Safety: The Map That Refuses Impossible Directions 🔒

The VFS layer is also the first line of defence against path traversal attacks — attempts to escape the workspace by navigating to parent directories:

```rust
// Path validation in the VFS (simplified from crates/astrid-vfs)

pub fn validate_path(raw_path: &str) -> Result<SafePath, VfsError> {
    // Reject any path containing ../ sequences
    // This check happens BEFORE the path ever touches the host filesystem
    if raw_path.contains("../") || raw_path.contains("..\\") {
        return Err(VfsError::PathTraversal {
            attempted: raw_path.to_string(),
            reason: "Path traversal patterns (../) are not permitted",
        });
    }

    // Canonicalise the path and verify it stays within the workspace root
    let canonical = std::fs::canonicalize(raw_path)
        .map_err(|e| VfsError::Io(e))?;

    if !canonical.starts_with(&WORKSPACE_ROOT) {
        return Err(VfsError::OutOfBounds {
            attempted: canonical.display().to_string(),
            root:      WORKSPACE_ROOT.display().to_string(),
        });
    }

    Ok(SafePath(canonical))
}
```

An agent that tries `../../etc/passwd` gets a VFS error before the path ever reaches the operating system. The map refuses to show a route that leads off the park grounds.

-----

## The VFS Schemes: Speaking the Map’s Language 🗣️

Astrid uses URI-like scheme prefixes to identify filesystem locations, making it clear where a path lives:

```
workspace://src/main.rs
  │          │
  scheme     path within the workspace
  "workspace://" = the agent's workspace directory

home://my-agent/.config/settings.toml
  │           │
  scheme      path within the principal's home
  "home://"   = ~/.astrid/home/{principal}/

temp://output/results.json
  │         │
  scheme    path within the session's temp area
  "temp://" = the ephemeral upper layer directly
```

Each scheme maps to a different root directory on the host filesystem. The scheme is resolved by the VFS before any capability check — so an agent that tries to access `home://other-agent/secret.toml` gets a VFS error based purely on the capability check, not host filesystem permissions.

-----

## Capability-Based File Handles 🎟️

The VFS does not use raw string paths at the file handle level. Instead, it uses capability-based typed handles that carry the permission proof with them:

```rust
// File access requires a typed handle that encodes the capability

/// A handle to a directory — proves you have access to list/read it
pub struct DirHandle {
    inner: Arc<DirHandleInner>,
    // The capability that grants access to this directory
    capability: CapabilityGrant,
}

/// A handle to a file — proves you have the specific access type
pub struct FileHandle {
    inner: Arc<FileHandleInner>,
    // READ or WRITE — encoded in the handle, checked once at open time
    mode: FileMode,
}

// Usage pattern: capability checked ONCE when opening, not on every read/write
pub fn open_file(
    path:       &SafePath,
    mode:       FileMode,
    capability: &CapabilityToken,
) -> Result<FileHandle, VfsError> {
    // Check: does this capability token cover this path + mode?
    if !capability.covers(path, mode) {
        return Err(VfsError::NotPermitted { path: path.to_string() });
    }
    // Open the file. From here on, reads/writes are fast — no repeated checks.
    Ok(FileHandle::new(path, mode))
}
```

Once you have a `FileHandle`, reading and writing is fast — the capability was checked once when the handle was created. The file handle itself is the proof of access.

-----

## Session Lifecycle: The Fresco’s Fate 🎨

A session has a clear lifecycle with the VFS overlay:

```rust
// Session lifecycle with VFS overlay

pub struct Session {
    overlay: OverlayVfs,
    tmpdir:  TempDir,   // auto-cleaned on Drop if not committed
}

impl Session {
    /// Called when the agent starts chatting
    pub fn open(workspace: &Path, principal: &PrincipalId) -> Result<Session, VfsError> {
        let tmpdir  = TempDir::new()?;  // Fresh upper layer
        let overlay = OverlayVfs::new(
            lower: workspace.to_owned(),      // Read-only foundation
            upper: tmpdir.path().to_owned(),  // Writable surface
        )?;
        Ok(Session { overlay, tmpdir })
    }

    /// At session end: the agent (or operator) decides
    pub fn commit(self) -> Result<WorkspaceDiff, VfsError> {
        // Apply upper-layer changes to the lower workspace
        let diff = compute_diff(&self.overlay.upper, &self.overlay.lower)?;
        apply_diff(&diff, &self.overlay.lower)?;
        Ok(diff)  // Returns: what changed, for the audit trail
    }

    pub fn discard(self) {
        // self goes out of scope here
        // TempDir::drop() deletes the tmpdir automatically
        // The workspace is unchanged. It is as if nothing happened.
    }
}
```

The `discard()` path is zero-cost and instantaneous — the temp directory is deleted, and the workspace is bit-for-bit identical to how the session started. Perfect for exploratory sessions, experiments, or error recovery.

-----

## Multi-Principal Isolation: Every Agent’s Own Map 👥

In v0.6.0, the VFS added per-principal overlay registries — a critical multi-tenancy enhancement:

```rust
// Before v0.6.0:
// A single Kernel.overlay_vfs shared by everyone
// Agent A's writes could potentially interfere with Agent B's view
// (Not a safety issue, but a coherence issue)

// After v0.6.0:
// Kernel.overlay_registry: Arc<OverlayVfsRegistry>
// Each principal gets their own OverlayVfs on first access
// Agent A's writes are invisible to Agent B's overlay
// Agent B's writes are invisible to Agent A's overlay
// The underlying workspace is still shared (the real park ground)
// But each agent's temporary writes are strictly isolated

pub struct OverlayVfsRegistry {
    overlays: DashMap<PrincipalId, OverlayVfs>,
    max_principals: usize,  // Default 1024 — bounded to prevent memory exhaustion
}

impl OverlayVfsRegistry {
    pub fn get_or_create(&self, principal: &PrincipalId) -> Arc<OverlayVfs> {
        self.overlays
            .entry(principal.clone())
            .or_insert_with(|| OverlayVfs::new_for_principal(principal))
            .clone()
    }
}
```

-----

## The Complete VFS Picture: The Map Has Everything 🗺️

A complete filesystem interaction through the VFS stack:

```
Agent (in WASM capsule):
  fs::write("workspace://src/new_feature.rs", content)
          │
          ▼
[WASM boundary — astrid_write_file syscall]
          │
          ▼
[Capability check — does the capsule's token cover workspace://src/**?]
          │
          ├─ No  → VfsError::NotPermitted
          ▼
[Path validation — any ../? Any out-of-bounds?]
          │
          ├─ Yes → VfsError::PathTraversal
          ▼
[VFS overlay resolution — workspace:// → real path]
          │
          ▼
[Write to UPPER LAYER (tmpdir/src/new_feature.rs)]
          │
          ▼
[Read from lower layer (workspace/src/new_feature.rs) → not affected]
          │
[Session end: commit → tmpdir diff applied to workspace]
          │   OR
          └─ discard → tmpdir deleted, workspace pristine]
```

Seven layers of indirection between the WASM capsule’s `fs::write` and an actual file being touched. Every layer adds safety. None of them are avoidable. All of them are automatic.

The park map is thorough. The park grounds are safe.

-----

In **Episode 8**, we visit the construction yard — the final episode! Writing your own capsule from scratch, building it, installing it, exploring `Distro.toml` for custom park configurations, MCP capsules, and the OpenClaw JavaScript ecosystem.

*The park’s cartographer stamps the map: COMPLETE. But there is always a new attraction to discover!* 🗺️

-----

**🔗 Resources**

- **VFS Overlay**: [github.com/unicity-astrid/astrid#two-sandboxes](https://github.com/unicity-astrid/astrid#two-sandboxes)
- **CHANGELOG v0.6.0 VFS changes**: [github.com/unicity-astrid/astrid/blob/main/CHANGELOG.md](https://github.com/unicity-astrid/astrid/blob/main/CHANGELOG.md)
- **Companion Repository**: [github.com/the-software-journey/astrid](https://github.com/the-software-journey/astrid)

-----

*🎡 Astrid Lunapark Series — where every episode is a new attraction, and the magic never stops.*
