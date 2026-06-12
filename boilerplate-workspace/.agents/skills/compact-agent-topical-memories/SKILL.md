---
name: compact-agent-topical-memories
description: >-
  Compacts the seven Tier 2 topical memory stores (decisions/, projects/,
  activities/, lessons/, preferences/, people/, analysis/) for one agent.
  Merges related entries, archives lifecycle-complete records, and prunes
  expired content — preserving all decision reasoning and never resolving
  contradictions autonomously. Use when: a topical store README.md exceeds
  5 KB; a store sub-folder has 10+ files eligible for merge or archive; the
  user says "compact decisions", "archive completed projects", "merge lessons",
  "clean up the projects", or "reorganize memory stores". Also triggered by
  diagnostic phrases ("are there contradictions?", "show stale entries",
  "which projects are not archived?") — diagnostic mode audits without writing
  anything. Invoked by skill-compact-memories for weekly memory maintenance.
  Requires format-md-for-progressive-disclosure sub-skill. Scoped to one agent
  per run — always asks which agent if ambiguous. Does not touch memory/daily/.
compatibility: >-
  Requires an MCP storage backend (local filesystem at minimum;
  git-backed store strongly recommended for rollback) and the
  format-md-for-progressive-disclosure sub-skill (see Step 0).
metadata:
  author: fbo
  version: "0.2-draft"
  status: draft
  skill-target: compact-agent-topical-memories
---

# Compact Agent Topical Memories

Compact the seven Tier 2 topical memory stores for a single agent by merging
related entries, archiving lifecycle-complete records, and pruning expired
content. All operations respect the agent's identity (`SOUL.md`, `RULES.md`)
and store-specific constraints that govern what may or may not be discarded.

This skill handles **topical store compaction only**. It does not touch
`memory/daily/` — that is handled by `skill-compact-daily-memories`. For full
weekly memory maintenance (all stores + MEMORY.md index rebuild), use the
`skill-compact-memories` orchestrator.

See `references/topical-store-architecture.md` for store layouts, MAGI front
matter fields, and archive conventions. Read it before Step 2.

---

## Scope — One Agent Per Run

This skill targets **exactly one agent**: the agent whose root directory contains
`MEMORY.md`, `SOUL.md`, `RULES.md`, and the `memory/` topical stores being
compacted. All store paths are under **that agent's** `memory/` tree.

If more than one agent could apply (ambiguous workspace, multiple roots open),
**ask which agent to compact before Step 0** — do not guess.

**Do not** sweep every agent under `agents/` in one run unless the user explicitly
provides a named list and confirms each one.

---

## Triggers

### Scheduled

- Weekly memory maintenance invoked by the `skill-compact-memories` orchestrator.
- User phrases that clearly name one agent's stores: "Compact this agent's
  decisions", "clean up the lessons for the agent I'm working with now",
  "merge projects under `agents/<name>/memory/`".

### Threshold

- A topical store's `README.md` exceeds 5 KB.
- A topical store sub-folder contains more than 10 files eligible for merge
  or archive.

### Diagnostic (read-only mode)

When triggered by a diagnostic phrase, run **Steps 0–3 only** (pre-flight,
load context, audit, contradiction detection) and return the compaction work
list and contradiction table **without writing any files**. Compaction proceeds
only if the user explicitly confirms after reviewing the report.

Diagnostic phrases: "Are there any contradictions in my decisions?" / "Show me
stale entries in my memory." / "Which projects are completed but not archived?"

---

## Input

| # | Input | Required | Source |
|---|-------|----------|--------|
| 1 | Target stores (all seven by default; specific stores if called with scope). | Yes | Specified by caller or default to all. |
| 2 | Agent's `SOUL.md` — values hierarchy and memory-policy sections. | Yes | Read from agent root. Guides retention and merge judgments. |
| 3 | Agent's `RULES.md` — deletion policy, archiving constraints, approval gates. | Yes | Read from agent root. Governs all compaction decisions. |
| 4 | Available MCP storage backends. | Yes | Discovered at Step 0. See `references/mcp-backend-routing.md`. |

---

## Output

| # | Output | Format | Destination |
|---|--------|--------|-------------|
| 1 | Compacted, merged, or archived topical store files with updated MAGI front matter. | Structured Markdown. | Same topical store paths. |
| 2 | New `analysis/` entries created from recurring lesson patterns (when applicable). | Structured Markdown + MAGI front matter. | `memory/analysis/` |
| 3 | Compaction report: every action taken per store. | Markdown table. | Conversation output (optionally persisted to `memory/maintenance/`). |
| 4 | Contradiction table requiring human resolution (if contradictions found). | Markdown table. | Conversation output — human must resolve before affected entries are written. |

---

## Execution Steps

**Steps must be executed in the exact order below. No step may be skipped,
reordered, or merged without explicit human authorization.** Deviation risks
leaving stores in a partially compacted state.

Steps 0–3 always run. Step 4 runs only when compaction work is identified.
Steps 5–6 always run.

---

### Step 0 — Pre-flight: verify required sub-skill and backend

**Check A — required sub-skill:**

| Sub-skill | Expected path |
|-----------|---------------|
| `format-md-for-progressive-disclosure` | `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/SKILL.md` |

**If missing:** halt immediately and display:

> **`compact-agent-topical-memories` cannot run — required sub-skill missing.**
>
> - **`format-md-for-progressive-disclosure`**
>   Expected: `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/SKILL.md`
>
> **Why required:** Every modified memory file must carry up-to-date MAGI-compliant
> front matter so agents can discover it at Layer 1 without reading the full body.
> Compacting files without updating their front matter produces stale, misleading metadata.
>
> **To install:** copy the skill folder from
> `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/`
> and place `SKILL.md` at the path above. Then re-run `compact-agent-topical-memories`.

**Check B — MCP backend discovery:** List available MCP tools and identify the
highest-priority backend. Cache the result for use at Step 5. Do not re-query later.
See `references/mcp-backend-routing.md` for priority order and introspection method.

---

### Step 1 — Load identity context

Read `SOUL.md` and `RULES.md` from the agent's root to establish:

- **Values hierarchy** — resolves judgment calls when compaction goals conflict.
- **Memory policy** — what the agent considers signal worth keeping vs. noise to prune.
- **Hard constraints** on deletion and archiving — approval gates, PII rules.

**Exception:** when invoked by `compact-memories`, these files are already in
conversation context. Use them from there; do not re-read from disk.

If `SOUL.md` does not contain a values hierarchy, apply the default:
Safety > Honesty > Solutions > Efficiency > Quality > Growth. Flag in report.

**If both `SOUL.md` and `RULES.md` are missing:** halt. Warn the user that
identity context is required for safe compaction.

See `references/soul-rules-context.md` for how to read and apply both files.

---

### Step 2 — Audit target stores

For each target topical store:

1. List all files and sub-folders.
2. Read each file's front matter to extract: `created`, `last-updated`,
   `retention`, `status`, `category`, `tags`.
3. Build a per-store compaction work list using the criteria in
   `references/compaction-rules.md`.

If a store directory does not exist or contains no files: skip it and log
in the compaction report: "`[store]/` not found or empty — no compaction performed."

---

### Step 3 — Detect contradictions

> **When invoked by `compact-memories`:** The orchestrator has already performed
> cross-store contradiction detection. Limit this step to **intra-store
> contradictions only** — entries within the same store that conflict with
> each other.

For standalone invocations, scan across all target stores for entries that
conflict:

- Two decisions record conflicting choices on the same topic.
- A preference entry contradicts a newer preference entry.
- A person record contains information conflicting with a later update.
- Any entry contradicts information in `RULES.md` or `SOUL.md`.

**If contradictions are found, present them before any write action:**

| Entry A | Entry B | Store | Nature of contradiction | Recommended resolution |
|---------|---------|-------|------------------------|------------------------|

Do not resolve contradictions autonomously. Wait for user confirmation before
modifying any affected files. Compaction of non-contradictory stores may
proceed in parallel.

---

### Step 4 — Apply type-specific compaction

For each store, apply the operations from `references/compaction-rules.md`.
Execute all merge/archive/prune actions before updating front matter.

Key points (read `references/compaction-rules.md` for full detail):

- **`decisions/`** — archive entire sub-folders; never discard reasoning;
  link successor to archived entry.
- **`projects/` and `activities/`** — archive entire sub-folders on completion
  or abandonment; no pruning.
- **`lessons/`** — merge when 3+ lessons share a theme; create a new
  `analysis/` entry from the pattern (template in `references/compaction-rules.md`).
- **`preferences/`** — deduplicate; contradictions require human resolution
  before archiving the older entry.
- **`people/`** — check `retention` field before any prune; never delete
  without explicit policy.
- **`analysis/`** — preserve conclusions section verbatim when summarizing.

**After every compaction action on a file**, invoke
`format-md-for-progressive-disclosure` to update its MAGI-compliant front matter.
Pass a context hint describing the compaction applied. The sub-skill preserves
the existing `doc-id`.

---

### Step 5 — Write all changes

Using the highest-priority available MCP backend (cached from Step 0):

1. Write all new and modified files.
2. Write updated `README.md` files for each affected store.

**On write failure:** restore each affected file to its last committed git state
(`git checkout HEAD -- <file>`). If git is unavailable, halt immediately — do
not write further files — and present the user with the list of files modified
before the failure. Log all failures in the compaction report.

See `references/mcp-backend-routing.md` for rollback details and per-backend
write operations.

---

### Step 6 — Report

Produce the compaction report using the table structure defined in
`references/report-template.md`. The report must be a Markdown table with
columns: **Store**, **Action**, **Entry**, **Result**, **Notes**. Append
a one-line summary footer after the table.

Include in the report:

- One row per compaction action (merged, archived, pruned, created, or skipped).
- Contradictions found and their resolution status.
- Analysis entries created from lesson patterns.
- Items requiring human review (pending deletions, unresolved contradictions).
- Whether a default values hierarchy was used (if applicable).
- Any stores skipped (not found, empty, or paused due to unresolved contradictions).

See `references/report-template.md` for the full table template, column
definitions, summary footer format, and the diagnostic mode output structure.

---

## Non-Negotiable Constraints

See `references/constraint-vocabulary.md` for the full ALWAYS / NEVER / ASK BEFORE
framework. Key constraints:

- Never discard decision reasoning — superseded decisions are archived, never deleted.
- Never delete entries without following the RULES.md deletion policy.
- Never modify `SOUL.md`, `RULES.md`, or `IDENTITY.md`.
- Never resolve contradictions autonomously.
- Never prune `people/` entries without an explicit `retention` field.
- Always invoke `format-md-for-progressive-disclosure` after modifying any file.
- Always present contradictions before writing any affected file.
- Always maintain an audit trail in the compaction report.

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| `format-md-for-progressive-disclosure` not found. | Halt at Step 0. Display missing skill path and install instructions. |
| `SOUL.md` or `RULES.md` missing (not both). | Apply defaults for the missing file. Flag in report. Continue. |
| Both `SOUL.md` and `RULES.md` missing. | Halt. Identity context required for safe compaction. |
| Store file has no front matter or is malformed. | Skip the file. Log in report as requiring manual repair. |
| No entries eligible for compaction in any store. | Report "Topical stores are healthy — no compaction needed." |
| Target store directory does not exist or is empty. | Skip that store. Log: "`[store]/` not found or empty." Continue with remaining stores. |
| Merge would exceed 1 MiB (Firestore limit). | Split into numbered files (e.g., `decision-auth-01.md`, `-02.md`). Log split in report. |
| Write failure mid-batch. | Restore affected files via git or halt and list modified files. Do not leave stores partially compacted. |
| User does not respond to contradiction prompt. | Pause compaction for the affected store. Proceed with stores that have no pending contradictions. |
| `retention` field missing from a file's front matter. | Treat as no expiry (keep indefinitely). Log gap in report. |

---

## Sub-skills

| Sub-skill | Status | Expected path | When invoked |
|-----------|--------|---------------|--------------|
| `format-md-for-progressive-disclosure` | **Required** | `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/SKILL.md` | Step 4 — after every merge, archive, or prune action. |

---

## Reference Files

| File | Read at | Purpose |
|------|---------|---------|
| `references/topical-store-architecture.md` | Steps 2–4 | Store layouts, MAGI front matter fields, archive conventions, legacy flat-file handling |
| `references/compaction-rules.md` | Steps 2–4 | Per-store merge/archive/prune conditions, sub-folder handling, analysis entry template |
| `references/soul-rules-context.md` | Step 1 | How to extract and apply SOUL.md + RULES.md for compaction decisions |
| `references/mcp-backend-routing.md` | Steps 0, 5 | Backend priority, introspection, per-backend writes, rollback |
| `references/constraint-vocabulary.md` | Before execution | Full ALWAYS / NEVER / ASK BEFORE constraint list |
| `references/report-template.md` | Step 6 (also Step 3) | Compaction report table structure, contradiction table, diagnostic mode output |

---

## See Also

- `skill-compact-memories` — Orchestrator for full weekly memory maintenance.
- `skill-compact-daily-memories` — Companion skill for `memory/daily/` reorganization.
- `skill-save-agent-memories` — Creates the entries this skill later compacts.
