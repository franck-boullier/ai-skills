---
title: Constraint Vocabulary — ALWAYS / NEVER / ASK BEFORE
description: >-
  Distilled reference for compact-agent-memories. Explains the three-tier
  constraint framework and maps each tier to the specific constraints that
  apply to the orchestrator's execution. Covers identity protection, scope
  enforcement, contradiction handling, and audit-trail requirements.
purpose: reference
tags:
  - constraints
  - rules
  - always-never-ask
  - orchestrator
audience: ai-agent
---

# Constraint Vocabulary

## The Three-Tier Framework

| Tier | Keyword | Meaning |
|------|---------|---------|
| 1 | `NEVER` | Absolute prohibition — no exceptions, no override under any circumstances. Violation causes harm (data corruption, identity modification, unresolvable state). |
| 2 | `ASK BEFORE` | Conditional action — stop, state the intent clearly, get explicit user approval. Used when an action is consequential or irreversible but may be legitimate. |
| 3 | `ALWAYS` | Mandatory behavior — must occur every time without fail, regardless of context or convenience. |

**Rule of thumb:** if violating the constraint could cause harm, use `NEVER` or `ALWAYS`. If it merely makes the orchestration less effective, address it in the skill body, not here.

---

## NEVER Constraints

### Identity protection

- **NEVER modify `SOUL.md`, `RULES.md`, or `IDENTITY.md`.** These files define what the agent *is*. Compaction touches what the agent *has learned*. The boundary is absolute. If compaction reveals a contradiction with identity content, flag it for human review.
- **NEVER auto-resolve a contradiction with an identity file.** Surface it, wait for human instruction, record the outcome in the report.

### Contradiction and data integrity

- **NEVER resolve cross-store contradictions autonomously.** All contradictions found at Step 3 must be presented to the user as a table before any write action. Sub-skills may proceed with content that is independent of the contradiction, but the index rebuild (Step 6) waits until all contradictions are resolved.
- **NEVER rebuild MEMORY.md without a complete picture of changes.** If a sub-skill fails mid-execution, Step 6 does not run. An index built on a partial view would contain stale or incorrect pointers.

### Scope

- **NEVER compact more than one agent's memory tree in a single run** unless the user explicitly names each agent and confirms each one. The default is exactly one agent root per invocation. "Compact all my agents" is not confirmation.
- **NEVER run partial maintenance silently.** If a required sub-skill is missing, halt at Step 0 with the prescribed error message — do not run the available sub-skill and skip the missing one. Partial maintenance produces an inconsistent memory state.

### Index integrity

- **NEVER let MEMORY.md exceed 4 KB after Step 6.** If it does, identify the lowest-value entries (guided by the values hierarchy) and move their details to topical stores before writing.

---

## ASK BEFORE Constraints

- **ASK BEFORE proceeding when the target agent is ambiguous.** If more than one agent root could apply (multiple `agents/` directories, an ambiguous workspace), ask the user to name the exact agent before Step 0. Do not guess or iterate over every agent.
- **ASK BEFORE proceeding with a batch that covers multiple agents** even if the user phrased the request as "all my agents" or "everything". Confirm the explicit list and each agent's path before starting.

---

## ALWAYS Constraints

### Process sequencing

- **ALWAYS run Step 0 (pre-flight) first.** No work begins until both required sub-skills are confirmed present and backend discovery is complete.
- **ALWAYS run Steps 1–3 unconditionally.** Loading identity context, auditing stores, and detecting contradictions are not optional even when no compaction is due.
- **ALWAYS collect the complete change list from sub-skills before Step 6.** The MEMORY.md index rebuild relies on knowing every file written, moved, archived, or deleted during the run.

### Identity loading

- **ALWAYS load `SOUL.md` and `RULES.md` at Step 1** — or use them from context if the orchestrator is itself being called by a higher-level skill. Do not read them mid-run; load once, share context.
- **ALWAYS flag the use of the default values hierarchy** when `SOUL.md` is absent, in the maintenance report.

### Reporting

- **ALWAYS produce a unified maintenance report at Step 7** that accounts for every action taken by both sub-skills and the orchestrator, not just the orchestrator's own actions.
- **ALWAYS surface pending items** — unresolved contradictions, failed writes, malformed files requiring manual repair — in the report, even if the run otherwise completed successfully.

### Sub-skill orchestration

- **ALWAYS pass the `SOUL.md` / `RULES.md` context to sub-skills** via the shared session context — do not ask them to reload from disk.
- **ALWAYS honor each sub-skill's Step 0 pre-flight independently** — each sub-skill checks for its own required dependencies (`format-md-for-progressive-disclosure`). The orchestrator's pre-flight does not substitute for this.
- **ALWAYS skip each sub-skill's Step 1 (identity-load)** when invoking from the orchestrator. The orchestrator's Step 1 already established that context.
