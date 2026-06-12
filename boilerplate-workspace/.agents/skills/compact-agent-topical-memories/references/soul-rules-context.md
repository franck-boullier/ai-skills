---
title: Identity Context — SOUL.md and RULES.md for Compaction
description: >-
  Distilled reference for compact-topical-memories. Explains how to read the
  agent's SOUL.md (values hierarchy, memory policy) and RULES.md (hard
  constraints on deletion and archiving) and apply them to compaction decisions.
  Covers the default values hierarchy, orchestrator vs. direct invocation
  handling, and what each document governs.
purpose: reference
tags:
  - soul
  - rules
  - identity
  - values-hierarchy
  - memory-policy
  - compaction-guidance
audience: ai-agent
last-updated: 2026-04-05
---

# Identity Context — SOUL.md and RULES.md for Compaction

## Why Identity Context Matters

Topical store compaction requires judgment — what counts as "related enough to
merge", what retention policy applies, whether autonomous deletion is permitted.
That judgment must be grounded in the **agent's own values and rules**, not
generic defaults. Reading `SOUL.md` and `RULES.md` at Step 1 provides that grounding.

## SOUL.md — Values Hierarchy and Memory Policy

### What to extract at Step 1

Read two sections from `SOUL.md`:

1. **Values hierarchy** — Determines priority when compaction goals conflict
   (e.g., efficiency says prune; safety says preserve). Apply the hierarchy when
   deciding close calls.

2. **Memory policy** — Specifies what the agent considers worth keeping long-term
   vs. what may be discarded. Drives merge and prune judgments.

### Default values hierarchy (when SOUL.md lacks an explicit one)

If `SOUL.md` does not contain a values hierarchy, apply this default and flag it
in the compaction report:

```
1. Safety    — never harm, never leak, never lose data without consent
2. Honesty   — accuracy over convenience; flag uncertainty
3. Solutions — solve problems, preserve actionable knowledge
4. Efficiency — respect context window; prune noise
5. Quality   — 8.5/10 minimum; don't merge into something worse than the source
6. Growth    — preserve lessons and patterns; they compound over time
```

### Typical memory policy structure

| Category | What it tells the compaction skill |
|----------|-----------------------------------|
| **Always remember** | Decisions + reasoning, corrections, preferences, environment facts, recurring patterns → treat as high-retention; never prune without explicit RULES.md authorization |
| **Remember temporarily** | Code snippets, meeting context, debugging details → eligible for prune once past retention date |
| **Forget deliberately** | PII after purpose served, specific financial amounts after period, one-off queries → prune if past retention date AND RULES.md permits |

## RULES.md — Hard Constraints on Compaction

### What to extract at Step 1

Look for rules in these categories:

| Category | What it controls in compaction |
|----------|-------------------------------|
| **Approval Gates** | Which actions require human sign-off before execution (e.g., "ASK BEFORE deleting any memory record") |
| **Data Handling** | PII retention rules, cross-session confidentiality, which categories require explicit expiry before pruning |
| **Security Boundaries** | What must never be automatically deleted or modified |

### The ALWAYS / ASK BEFORE / NEVER framework

RULES.md uses this three-tier vocabulary:

| Tier | Keyword | Enforcement |
|------|---------|-------------|
| 1 | `NEVER` | Absolute prohibition — no exceptions, no user override |
| 2 | `ASK BEFORE` | Conditional — stop, state intent, wait for explicit human approval |
| 3 | `ALWAYS` | Mandatory — must happen every time without fail |

Apply this framework literally: if RULES.md says `ASK BEFORE deleting memory
records`, halt before any prune and present the list.

### When RULES.md requires human approval for deletion

1. Collect all entries eligible for pruning.
2. Present them in a table (file path, retention date, reason for prune eligibility).
3. Wait for explicit user confirmation before writing any delete.
4. Log the outcome (approved / declined per entry) in the compaction report.

If RULES.md explicitly permits autonomous pruning for a category (e.g.,
"expired code snippets may be deleted without approval"), proceed without asking.

## Orchestrator vs. Direct Invocation

| Invocation mode | Identity context handling |
|-----------------|--------------------------|
| Called by `compact-memories` orchestrator | `SOUL.md` and `RULES.md` are already in conversation context. **Do not re-read from disk** at Step 1 — use the in-context versions. |
| Called directly (standalone) | Read both files from the agent's root directory at Step 1. |

## When SOUL.md or RULES.md Is Missing

- **SOUL.md missing:** Apply the default values hierarchy. Flag in report: "Default values hierarchy used — SOUL.md not found."
- **RULES.md missing:** Apply conservative defaults: treat all pruning as requiring human approval. Flag in report: "RULES.md not found — assuming human approval required for all deletions."
- Do not halt in either case unless the spec specifically requires it for this skill.

> **Hard halt trigger:** If both `SOUL.md` **and** `RULES.md` are missing, halt and
> warn the user — compaction without any identity context risks unsafe data loss.
