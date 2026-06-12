---
title: Constraint Vocabulary — ALWAYS / NEVER / ASK BEFORE
description: >-
  Distilled reference for compact-topical-memories. Explains the three-tier
  constraint framework and maps each tier to the specific constraints that
  govern topical store compaction.
purpose: reference
tags:
  - constraints
  - rules
  - always-never-ask
audience: ai-agent
last-updated: 2026-04-05
---

# Constraint Vocabulary

## The Three-Tier Framework

| Tier | Keyword | Meaning |
|------|---------|---------|
| 1 | `NEVER` | Absolute prohibition — no exceptions, no override. Violation causes data loss, broken audit trails, or unsafe autonomous action. |
| 2 | `ASK BEFORE` | Conditional action — stop, state intent, wait for explicit user approval before writing anything. |
| 3 | `ALWAYS` | Mandatory behavior — must occur on every applicable action without fail. |

**Rule of thumb:** if violating the constraint could cause *harm* (data loss,
PII exposure, unresolvable contradiction), it's a `NEVER` or `ALWAYS`. If it
merely makes the skill *less effective*, it belongs in the soul, not here.

---

## NEVER Constraints (data integrity and safety)

- **NEVER discard decision reasoning.** A superseded decision must be archived
  (moved to `decisions/archive/`), not deleted. The full reasoning trail is permanent.
  The successor decision must link to the archived entry.

- **NEVER delete any entry without following the RULES.md deletion policy.**
  If RULES.md requires human approval for deletion, halt and present the list
  before writing anything. Autonomous deletion is only permitted when RULES.md
  explicitly authorizes it for the specific category.

- **NEVER modify SOUL.md, RULES.md, or IDENTITY.md.** These are identity files.
  If compaction reveals a contradiction with identity, flag it for human review —
  do not modify the identity files.

- **NEVER resolve contradictions autonomously.** Present all contradictions to
  the user before writing anything. The skill may recommend a resolution but must
  not act without explicit confirmation.

- **NEVER prune a `people/` entry without an explicit retention policy.**
  A missing `retention` field means "keep indefinitely." Do not delete PII
  entries without checking the `retention` frontmatter field first.

- **NEVER compact multiple agents in a single run** unless the user has explicitly
  named each agent and confirmed each one. Scope is always exactly one agent.

---

## ALWAYS Constraints (process integrity)

- **ALWAYS invoke `format-md-for-progressive-disclosure`** after modifying any
  file. Every modified file must carry up-to-date MAGI-compliant front matter.
  Compacting files without updating their front matter produces stale,
  misleading metadata that breaks agent discovery.

- **ALWAYS run Step 0 (pre-flight) before any other action.** If the required
  sub-skill is missing, halt immediately with the prescribed error message.

- **ALWAYS run Steps 1–3** (load identity context, audit, contradiction detection)
  before Step 4. These steps are unconditional; Step 4 is conditional on finding
  compaction work.

- **ALWAYS maintain an audit trail.** Every merge, archive, and prune action
  must appear in the Step 6 compaction report with its outcome.

- **ALWAYS check for an explicit retention policy before pruning PII entries.**
  `people/` entries without a `retention` field are treated as permanent.

- **ALWAYS present contradictions to the user before writing anything** to the
  stores involved. Compaction of stores without pending contradictions may
  proceed in parallel.

---

## ASK BEFORE Constraints (human confirmation gates)

- **ASK BEFORE proceeding** when more than one agent could apply (ambiguous
  workspace, multiple root directories open). Identify the exact agent whose
  stores to compact before Step 0.

- **ASK BEFORE any prune action** when RULES.md requires human approval for
  deletion. Present the complete list of entries proposed for deletion, including
  file path, retention date, and reason. Wait for explicit per-entry or bulk
  confirmation before proceeding.

- **ASK BEFORE resuming** on a store whose contradiction table has not been
  resolved. Proceed with unaffected stores only.
