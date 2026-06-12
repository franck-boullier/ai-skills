---
title: Constraint Vocabulary — ALWAYS / NEVER / ASK BEFORE
description: >-
  Distilled reference for compact-agent-daily-memories. Explains the three-tier
  constraint framework used in this skill's Non-Negotiable Constraints section,
  and maps each tier to the specific constraints that apply to daily memory
  reorganization.
purpose: reference
tags:
  - constraints
  - rules
  - always-never-ask
audience: ai-agent
---

# Constraint Vocabulary

## The Three-Tier Framework

| Tier | Keyword | Meaning |
|------|---------|---------|
| 1 | `NEVER` | Absolute prohibition — no exceptions, no override under any circumstances. Violation causes harm (data loss, broken navigation chain, audit-trail destruction). |
| 2 | `ASK BEFORE` | Conditional action — stop, state the intent, get explicit user approval. Used when an action is consequential or irreversible but may be legitimate. |
| 3 | `ALWAYS` | Mandatory behavior — must occur every time without fail, regardless of context. |

**Rule of thumb:** if violating the constraint could cause *harm*, use `NEVER` or `ALWAYS`. If it merely makes the agent *less effective*, it belongs in the soul, not the rules.

## Constraints Specific to compact-agent-daily-memories

### NEVER constraints (data destruction / audit trail)

- **NEVER delete a daily log file.** Reorganization means *moving* files into sub-folders, never destroying them. The full session audit trail must be preserved.
- **NEVER include content in a summary that cannot be traced to an actual daily file.** If a file is missing, acknowledge the gap — do not fabricate content.
- **NEVER re-read individual daily files at the quarterly synthesis level.** Quarterly summaries are derived *only* from monthly `README.md` files — they are the source of truth at that level.
- **NEVER modify `MEMORY.md`.** The bootstrap pointer to `memory/daily/README.md` is established once at agent setup and is immutable from this skill's perspective.
- **NEVER touch topical stores** (`decisions/`, `projects/`, `lessons/`, `preferences/`, `people/`, `activities/`, `analysis/`). This skill is scoped exclusively to `memory/daily/`.
- **NEVER reorganize multiple agents' `memory/daily/` trees in a single run** unless the user has explicitly named each agent and confirmed each one. Scope is always exactly one agent.

### ALWAYS constraints (process integrity)

- **ALWAYS invoke `format-md-for-progressive-disclosure`** after writing any monthly or quarterly README body. Never leave a new README without MAGI-compliant front matter — the progressive disclosure chain breaks silently without it.
- **ALWAYS log every move, folder creation, and file write** in the Step 6 report. The audit trail in the report is the human-readable record of what changed.
- **ALWAYS run Step 0 (pre-flight) before any other step.** If the required sub-skill is missing, halt immediately with the prescribed error message.
- **ALWAYS run Steps 1–2 (load context + audit).** Even when no reorganization is due, the audit still runs. Steps 3–5 are conditional; Steps 0–2 and Step 6 are not.

### ASK BEFORE constraint (scope ambiguity)

- **ASK BEFORE proceeding** when more than one agent could apply (ambiguous workspace, multiple roots). Identify the exact agent whose `memory/daily/` to reorganize before Step 0 and do not guess.
