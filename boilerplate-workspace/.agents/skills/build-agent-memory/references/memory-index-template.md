# Memory Index Template

Use this template in **Step 6** to create `MEMORY.md`. Two template variants are provided:
select the correct one based on `[MEMORY-MODE]` confirmed in Step 0.

---

## Shared Placeholder Table

Both variants share these placeholders. Resolve all of them before writing.

| Placeholder | Replace with |
| --- | --- |
| `[STORAGE-TYPE]` | Confirmed backend type from Step 2 (e.g., `Local filesystem`) |
| `[STORAGE-PROVIDER]` | Confirmed provider from Step 2 (e.g., `Local filesystem`, `GitHub`) |
| `[STORAGE-LOCATION]` | Fully qualified path confirmed in Step 2 (workspace-relative or absolute) |
| `[MEMORY-STORE-ROOT]` | Fully qualified path to the Tier 2 store root (e.g., `memories/` at workspace root for workspace mode; `memories/` inside the agent dir for agent mode) |
| `[ROOT-PREFIX]` | Path prefix used to resolve all markdown link targets in `MEMORY.md`. **Version-controlled store:** use a repo-relative path (e.g. `memories/`) — never an absolute machine path, which breaks every link on clone or OS change. **Local filesystem outside git:** absolute path is acceptable. Recommended default: the store folder name relative to the repo root (e.g. `memories/`). |
| `YYYY-MM-DD` | Today's date |
| `[Primary domain category N — e.g., ...]` | Section heading for the Nth confirmed category from Step 3 |
| `[categoryN]` | Directory name for the Nth confirmed category from Step 3 (e.g., `decisions`) |
| `[storeN]` | Directory name for each remaining topical store from Step 3 |

**Additional placeholder — agent mode only:**

| Placeholder | Replace with |
| --- | --- |
| `[AGENT-MEMORY-ROOT]` | Same value as `[MEMORY-STORE-ROOT]` — the root of the agent's `memories/` tree |

**Additional placeholder — workspace mode only:**

| Placeholder | Replace with |
| --- | --- |
| `[WORKSPACE-NAME]` | The repository or workspace name (e.g., `everhaus-strymin`) |

**Rule:** After Step 7 creates the directory structure, every section body must contain a
live README.md link. No placeholder text may remain.

---

## Template A — Agent Mode (`[MEMORY-MODE]` = `agent`)

Use when creating a `MEMORY.md` for a specific named agent that has `IDENTITY.md`,
`SOUL.md`, and `RULES.md` already in place.

```markdown
---
# NOTE: `format-md-for-progressive-disclosure` will add MAGI frontmatter fields.
# Keep `root_prefix` as a first-class configuration key.
root_prefix: [ROOT-PREFIX]
---

# Memory

## Memory Architecture

This file is the memory index. Keep it under 4 KB. Details live in the topical memory stores linked below.

**Storage backend:** [STORAGE-TYPE] — [STORAGE-PROVIDER] / [STORAGE-LOCATION] (confirmed during setup on YYYY-MM-DD; do not change without running a new connectivity test)

**Path convention:** All markdown link targets in this file are relative to `root_prefix`. Resolve full paths as: `{root_prefix}{link_target}`.

**Read on startup:** This file + any active project or decision file referenced in current work.

**Write after:** decisions, corrections, new projects, new people, lessons learned, recurring patterns.

**Memory hygiene:** Weekly — prune daily logs older than 90 days, check index size, verify no contradictions.

**Write:** `skill-save-agent-memories`

**Compact:** `compact-agent-memories`

## Dedicated memory

This agent's **own** Tier 2 store — everything below lives under `[AGENT-MEMORY-ROOT]` (the path confirmed in **Storage backend** above). Do not put org-wide or cross-agent facts here when a shared store exists; use **Shared memory** instead for those categories.

## Environment

[Onboarding: tech stack, team members, current priorities]

## [Primary domain category 1 — e.g., Active Projects]

- [[category1]/README.md]([category1]/README.md)

## [Primary domain category 2 — e.g., Recent Decisions]

- [[category2]/README.md]([category2]/README.md)

## [Primary domain category 3 — e.g., User Preferences]

- [[category3]/README.md]([category3]/README.md)

## Topical Memories

- [[store1]/README.md]([store1]/README.md)
- [[store2]/README.md]([store2]/README.md)
- [[store3]/README.md]([store3]/README.md)

## Daily Logs

- [Daily log index](daily/README.md)

> **Bootstrap pointer — established once, never modified.** This section is written during Step 6 and must not be changed after setup. Individual daily session files (`YYYY-MM-DD.md`) must never add pointers here. All daily log navigation flows downward from this pointer through `memories/daily/README.md`. See `daily-vs-topical-memory.md` for the full rule set.

## Shared memory [include only when multi-agent context applies; omit entirely otherwise]

Organizational memory shared with other agents (not duplicated in **Dedicated memory**).

- [Shared memory index]([SHARED-MEMORY-PATH]/README.md)
- This agent has [read-only / read-write for: category1, category2]
```

---

## Template B — Workspace Mode (`[MEMORY-MODE]` = `workspace`)

Use when creating a `MEMORY.md` at the repository root, shared by all agents in the
workspace. No `IDENTITY.md` / `SOUL.md` / `RULES.md` are required. There is no
"Dedicated memory" section — this file IS the shared workspace layer.

```markdown
---
# NOTE: `format-md-for-progressive-disclosure` will add MAGI frontmatter fields.
# Keep `root_prefix` as a first-class configuration key.
root_prefix: [ROOT-PREFIX]
---

# Workspace Memory — [WORKSPACE-NAME]

## Memory Architecture

This file is the workspace memory index — shared by all agents operating in this
repository. Keep it under 4 KB. Details live in the topical memory stores linked below.

**Scope:** Workspace-wide — any agent in `[WORKSPACE-NAME]` may read and write here.

**Storage backend:** [STORAGE-TYPE] — [STORAGE-PROVIDER] / [STORAGE-LOCATION] (confirmed during setup on YYYY-MM-DD; do not change without running a new connectivity test)

**Path convention:** All markdown link targets in this file are relative to `root_prefix`. Resolve full paths as: `{root_prefix}{link_target}`.

**Read on startup:** This file + any active project or decision file referenced in current work.

**Write after:** decisions, corrections, new projects, new people, lessons learned, recurring patterns.

**Memory hygiene:** Weekly — prune daily logs older than 90 days, check index size, verify no contradictions.

**Write:** `skill-save-agent-memories`

**Compact:** `compact-agent-memories`

## Workspace Environment

[Onboarding: workspace purpose, repository structure, team members, tech stack, key dates, current priorities. Fill in during the first onboarding session.]

## [Primary domain category 1 — e.g., Active Projects]

- [[category1]/README.md]([category1]/README.md)

## [Primary domain category 2 — e.g., Key Decisions]

- [[category2]/README.md]([category2]/README.md)

## [Primary domain category 3 — e.g., Workspace Preferences]

- [[category3]/README.md]([category3]/README.md)

## Topical Memories

- [[store1]/README.md]([store1]/README.md)
- [[store2]/README.md]([store2]/README.md)
- [[store3]/README.md]([store3]/README.md)

## Daily Logs

- [Daily log index](daily/README.md)

> **Bootstrap pointer — established once, never modified.** This section is written during Step 6 and must not be changed after setup. Individual daily session files (`YYYY-MM-DD.md`) must never add pointers here. All daily log navigation flows downward from this pointer through `memories/daily/README.md`. Daily log entries should note which agent authored the session. See `daily-vs-topical-memory.md` for the full rule set.
```

> **Note:** The workspace-mode template has no "Shared memory" section. The workspace
> `MEMORY.md` itself IS the shared layer. When individual agents in this workspace have
> their own `MEMORY.md`, those agents' files include a "Shared memory" pointer back to
> this workspace `MEMORY.md`.
