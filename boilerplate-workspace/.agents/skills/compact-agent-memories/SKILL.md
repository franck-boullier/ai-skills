---
name: compact-agent-memories
description: >-
  Weekly memory maintenance orchestrator for a single agent. Audits all eight
  Tier 2 memory stores, detects cross-store contradictions, delegates daily-log
  reorganization to compact-agent-daily-memories and topical-store compaction to
  compact-agent-topical-memories, rebuilds the MEMORY.md index (enforcing the
  4 KB limit), and produces a unified maintenance report. Use this skill — not
  the sub-skills directly — when full weekly maintenance is needed: MEMORY.md
  index approaching 4 KB, both daily and topical stores need attention, or the
  user says "run memory maintenance for [agent-name]", "compact this agent's
  memory", or "run weekly maintenance". Scoped to one agent per invocation.
compatibility: >-
  Requires file-system access, MCP tool support (local filesystem minimum;
  git-backed store strongly recommended), and both sub-skills:
  compact-agent-daily-memories and compact-agent-topical-memories. Git recommended
  for rollback.
metadata:
  author: fbo
  version: "0.1-draft"
  status: draft
  skill-target: compact-agent-memories
---

# Compact Agent Memory (Orchestrator)

Single entry point for full weekly memory maintenance **for one agent at a time**.
Coordinates compaction across that agent's Tier 2 memory stores — loading identity
context once, detecting cross-store contradictions, delegating to specialized
sub-skills, rebuilding the `MEMORY.md` index, and producing a unified report.

**What this skill does NOT do directly:**

- Daily log reorganization → delegated to `compact-agent-daily-memories`
- Topical store merge / archive / prune → delegated to `compact-agent-topical-memories`

**When to use sub-skills directly instead:**

| Goal | Use |
|------|-----|
| Reorganize only daily logs | `compact-agent-daily-memories` directly |
| Compact only specific topical stores | `compact-agent-topical-memories` directly |
| Full weekly maintenance (all stores + index) | **`compact-agent-memories`** (this skill) |

See `references/memory-architecture.md` for the full Tier 2 store inventory, the 4 KB rule, and the MEMORY.md index structure. Read it before Step 2.

---

## Scope — One Agent Per Run

This skill targets **exactly one agent**: the agent whose root directory contains
`MEMORY.md`, `SOUL.md`, `RULES.md`, and the `memory/` tree. All paths are under
that agent's root.

If more than one agent could apply (ambiguous workspace, multiple `agents/` roots),
**ask which agent to compact before Step 0** and do not guess. See the ASK BEFORE
constraint in `references/constraint-vocabulary.md`.

---

## Step 0 — Pre-flight: verify required sub-skills and discover backend

Complete both checks before any other action:

### Check A — required sub-skills

| Sub-skill | Expected path |
|-----------|---------------|
| `compact-agent-daily-memories` | `skills/skills-libraries/fbo-skills/advanced-skills/compact-agent-daily-memories/SKILL.md` |
| `compact-agent-topical-memories` | `skills/skills-libraries/fbo-skills/advanced-skills/compact-agent-topical-memories/SKILL.md` |

If both are present: proceed to Check B.

If any sub-skill is missing, halt immediately and display:

> **`compact-agent-memories` cannot run — required sub-skill(s) missing.**
>
> The following sub-skill(s) were not found:
>
> - **`compact-agent-daily-memories`**
>   Expected: `skills/skills-libraries/fbo-skills/advanced-skills/compact-agent-daily-memories/SKILL.md`
> - **`compact-agent-topical-memories`**
>   Expected: `skills/skills-libraries/fbo-skills/advanced-skills/compact-agent-topical-memories/SKILL.md`
>
> **Why both are required:** This skill is an orchestrator. Running partial
> maintenance without both sub-skills produces an inconsistent memory state —
> one store type compacted, the other not. Install the missing skill(s) at the
> paths above, then re-run `compact-agent-memories`.

### Check B — MCP backend discovery

Query the MCP tool listing and cache the result. This cached list determines which
backend is used for all writes in this run, including the Step 6 `MEMORY.md` write.
See `references/mcp-backend-routing.md` for the priority order and per-backend
operations. Do not repeat this query later in the run.

---

## Step 1 — Load identity context (once)

Read `SOUL.md` and `RULES.md` from the agent's root directory. Extract and hold in
context:

- The **values hierarchy** — what matters most when deciding what to keep, condense,
  or discard during compaction and index pruning.
- The **memory policy** — what is signal worth preserving vs. noise to omit.
- **Hard constraints** from `RULES.md` — data retention, deletion, and archiving rules
  that sub-skills must respect.

This read happens **once**. Sub-skills must not reload these files — they operate on
the context established here. See `references/identity-context.md` for what to
extract and how to apply each section.

**If `SOUL.md` or `RULES.md` is missing:** halt at Step 1. Warn the user and do not
proceed. Without identity context, compaction decisions may incorrectly prune
high-value entries or violate data-handling rules. See the halt behavior in
`references/identity-context.md`.

**If `SOUL.md` is present but lacks a values hierarchy:** apply the default hierarchy
(Safety, Honesty, Solutions, Efficiency, Quality, Growth — highest to lowest) and flag
this substitution in the Step 7 report.

---

## Step 2 — Audit all memory stores

1. Read and measure the `MEMORY.md` index (bytes).
2. Inventory `memory/daily/` — identify any completed calendar months not yet folded
   into monthly sub-folders, and any completed quarters not yet folded into quarterly
   sub-folders.
3. Inventory the seven topical stores: `activities/`, `analysis/`, `projects/`,
   `decisions/`, `preferences/`, `people/`, `lessons/` — identify stores with
   merge-eligible, archive-eligible, expired, or oversized content.
4. Determine which sub-skills need to run:
   - **`compact-agent-daily-memories`**: run if any monthly or quarterly reorganization
     is due.
   - **`compact-agent-topical-memories`**: run if any topical store has content
     requiring merge, archive, prune, or oversize handling.

See `references/memory-architecture.md` for store types and reorganization thresholds.

---

## Step 3 — Cross-store contradiction detection

Scan across **all** memory stores — daily and topical — for entries that conflict with
each other or with the MEMORY.md index:

- A fact in the index contradicts a newer topical store entry.
- Two topical store entries record conflicting decisions or preferences.
- A daily log entry contradicts an established decision or preference.
- Any entry contradicts content in `RULES.md` or `SOUL.md`.

**If contradictions are found**, present them to the user using the contradiction table
from `references/maintenance-report-template.md` **before any write action**.

Do not resolve contradictions autonomously. Sub-skills may proceed with content that is
independent of the contradiction. Hold Step 6 (index rebuild) until all contradictions
are resolved or explicitly deferred by the user.

**If no contradictions are found**, proceed directly to Step 4.

---

## Step 4 — Delegate to compact-agent-daily-memories (when due)

If daily reorganization is due (identified in Step 2):

1. Read `compact-agent-daily-memories/SKILL.md`.
2. Follow its execution steps with these two adjustments:
   - **Honor its Step 0 (pre-flight):** it independently verifies
     `format-md-for-progressive-disclosure`, a transitive dependency the
     orchestrator's Step 0 does not check. If that verification fails, the
     sub-skill halts — honor that halt.
   - **Skip its Step 1 (identity-load):** `SOUL.md` is already in context from
     the orchestrator's Step 1. The sub-skill reads from context, not from disk.
3. The sub-skill handles monthly and quarterly folder creation, file moves, and README
   synthesis.
4. Collect the complete list of all files written or modified by the sub-skill.

If daily reorganization is **not** due, skip this step and note it in the Step 7 report.

---

## Step 5 — Delegate to compact-agent-topical-memories (when due)

If topical store compaction is due (identified in Step 2):

1. Read `compact-agent-topical-memories/SKILL.md`.
2. Follow its execution steps with these two adjustments:
   - **Honor its Step 0 (pre-flight):** it independently verifies
     `format-md-for-progressive-disclosure`, a transitive dependency the
     orchestrator's Step 0 does not check. If that verification fails, the
     sub-skill halts — honor that halt.
   - **Skip its Step 1 (identity-load):** `SOUL.md` and `RULES.md` are already
     in context from the orchestrator's Step 1. The sub-skill reads from context,
     not from disk.
3. The sub-skill handles merge, archive, prune, and front matter updates across all
   seven topical stores.
4. Collect the complete list of all files written, modified, archived, or deleted.

If topical compaction is **not** due, skip this step and note it in the Step 7 report.

---

## Step 6 — Rebuild the MEMORY.md index

Using the full picture of all changes made in Steps 4–5 (including the cached
pre-flight backend from Step 0):

1. Remove pointers to deleted or merged files.
2. Add pointers to new consolidated or summary files.
3. Update stable facts that changed during compaction (environment, active projects,
   recent decisions).
4. Verify size: measure the resulting index. If it exceeds 4 KB:
   - Identify the lowest-value *prose entries*, guided by the values hierarchy from `SOUL.md`. Navigation links (README.md pointers) cannot be shortened without changing the storage configuration — do not remove or shorten them.
   - Move their details to the appropriate topical stores, keeping only pointers in
     the index.
   - Repeat until the index is under 4 KB.
5. Write the updated `MEMORY.md` to the agent's root directory using the
   highest-priority available backend (cached from Step 0).

See `references/mcp-backend-routing.md` for write operations and rollback behavior on
failure. See `references/memory-architecture.md` for the target index structure.

**If all backend writes fail:** halt before overwriting the existing `MEMORY.md`.
Report the failure, list all attempted backends, confirm sub-skill changes remain in
place, and instruct the user. The stores are compacted; the index is not yet updated.

---

## Step 7 — Report unified maintenance summary

Present the consolidated report using the template in
`references/maintenance-report-template.md`. Always include:

- **Daily reorganization:** monthly and quarterly folders created, periods covered,
  any gaps (or "not due").
- **Topical stores:** entries merged, archived, pruned, and created per store
  (or "not due").
- **Contradictions:** found, resolved, and any pending human review.
- **MEMORY.md index:** size before and after; entries added, removed, updated,
  demoted.
- **Items requiring human review:** pending contradictions, failed writes, malformed
  files.

Optionally persist the report to `memory/maintenance/YYYY-MM-DD-maintenance.md`.
If persisted, invoke `format-md-for-progressive-disclosure` on it afterward with
context hint: `"Weekly memory maintenance report for agent <agent-name>, YYYY-MM-DD.
Category: maintenance-report. Audience: ai-agent."`

---

## Non-Negotiable Constraints

See `references/constraint-vocabulary.md` for the full ALWAYS / NEVER / ASK BEFORE
framework. Key constraints:

- **NEVER modify `SOUL.md`, `RULES.md`, or `IDENTITY.md`.** These are identity files.
  Contradictions with identity are flagged for human review, not auto-resolved.
- **NEVER resolve cross-store contradictions autonomously.** Surface at Step 3 before
  any writes.
- **NEVER rebuild MEMORY.md unless all sub-skills completed successfully.** A partial
  picture produces a corrupt index.
- **NEVER let MEMORY.md exceed 4 KB after Step 6.**
- **NEVER compact more than one agent per run** without explicit per-agent user
  confirmation.
- **NEVER run partial maintenance silently.** Missing sub-skill → halt at Step 0.
- **ALWAYS load identity context once at Step 1.** Sub-skills use it from context —
  they do not re-read from disk.
- **ALWAYS produce a unified report at Step 7**, even when no compaction was performed.
- **ALWAYS run Steps 0–3 unconditionally.** Steps 4–5 are conditional; Steps 0–3 and
  Steps 6–7 always run.

---

## Edge Cases & Error Handling

| Situation | Behavior |
|-----------|----------|
| Required sub-skill missing | Halt at Step 0. Display missing path(s) and install instructions. Do not run the available sub-skill alone. |
| Target agent is ambiguous | Ask before Step 0. Name exactly one agent root. Do not guess or iterate. |
| `SOUL.md` or `RULES.md` missing | Halt at Step 1. Warn the user. Do not proceed without identity context. |
| Neither daily nor topical compaction is due | Report "Memory is healthy — no maintenance needed" with index size and next scheduled maintenance. Steps 4–5 skipped. |
| A sub-skill fails mid-execution | Roll back that sub-skill's changes using git (`git checkout HEAD -- <file>`); if git is unavailable, halt and present modified file list for manual restoration. Do not proceed to Step 6. |
| MEMORY.md index cannot reach < 4 KB | Report the shortfall. Present the lowest-value *prose entries* (not navigation links) and ask the user which to demote to topical stores. If the 4 KB budget is consumed entirely by navigation links and mandatory structural sections, report this to the user — it indicates the storage root path is very long and no further compaction is possible without changing the storage configuration. |
| Cross-store contradiction found at Step 3 | Surface all contradictions before proceeding. Hold Step 6 until all are resolved or deferred. |
| `MEMORY.md` missing or unparseable at Step 2 | Halt. Report the path and error. Do not proceed — rebuilding from scratch without a valid baseline risks data loss. Ask user to restore from git or provide a replacement. |
| All backend writes fail at Step 6 | Halt before overwriting existing `MEMORY.md`. Report failure, list backends tried, confirm sub-skill changes are intact. Write pending index to `MEMORY.md.pending` if possible. |

---

## Sub-skills

| Sub-skill | Status | Expected path | Invoked at |
|-----------|--------|---------------|-----------|
| `compact-agent-daily-memories` | Required | `skills/skills-libraries/fbo-skills/advanced-skills/compact-agent-daily-memories/SKILL.md` | Step 4, when daily reorganization is due |
| `compact-agent-topical-memories` | Required | `skills/skills-libraries/fbo-skills/advanced-skills/compact-agent-topical-memories/SKILL.md` | Step 5, when topical compaction is due |

Both sub-skills depend on `format-md-for-progressive-disclosure` (enforced by their
own Step 0 pre-flight). The orchestrator does not check this transitive dependency
directly — each sub-skill manages it.

---

## Reference Files

- `references/memory-architecture.md` — Three-tier model, all eight Tier 2 store types, 4 KB rule, MEMORY.md index structure. **Read before Steps 2 and 6.**
- `references/identity-context.md` — What to extract from SOUL.md and RULES.md, default values hierarchy, immutability rules. **Read at Step 1.**
- `references/mcp-backend-routing.md` — Backend priority order, introspection, MEMORY.md write operations, rollback. **Read at Step 0 and Step 6.**
- `references/constraint-vocabulary.md` — ALWAYS / NEVER / ASK BEFORE framework with orchestrator-specific constraints. **Read before any execution.**
- `references/maintenance-report-template.md` — Contradiction table format, unified report structure, persistence guidance. **Read at Steps 3 and 7.**

---

## See Also

- `compact-agent-daily-memories` — Sub-skill for daily log reorganization; can also be run standalone.
- `compact-agent-topical-memories` — Sub-skill for topical store compaction; can also be run standalone.
- `save-agent-memory` — Creates the memory entries this skill later maintains.
- `format-md-for-progressive-disclosure` — Applied by sub-skills to every README they write.
