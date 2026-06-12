---
title: Identity Context — How to Read and Apply SOUL.md and RULES.md
description: >-
  Distilled reference for compact-agent-memories. Explains what to extract from
  SOUL.md and RULES.md at Step 1, how to apply the values hierarchy and memory
  policy throughout execution, the default hierarchy to use when SOUL.md is
  absent, and the absolute prohibition on modifying identity files.
purpose: reference
tags:
  - soul
  - rules
  - values-hierarchy
  - memory-policy
  - identity
audience: ai-agent
---

# Identity Context — How to Read and Apply SOUL.md and RULES.md

## Why Identity Is Loaded Once

`SOUL.md` and `RULES.md` define *who the agent is*, not what it has learned. Loading them once at Step 1 and sharing that context with sub-skills:

1. **Avoids duplicate reads.** Both files can be several KB. Re-reading them in each sub-skill wastes context window.
2. **Ensures consistency.** All compaction decisions — what to keep, prune, or archive — use the same values hierarchy and memory policy throughout the run.
3. **Preserves the identity/memory boundary.** The memory system learns from experience; identity defines what the agent is. This boundary must never blur.

## What to Extract from SOUL.md

The orchestrator needs two things from `SOUL.md`:

### 1. Values Hierarchy

A ranked list of what matters most when values conflict. Used at **Step 6** when the MEMORY.md index exceeds 4 KB and you must decide which entries to demote to topical stores.

Typical structure:

```
1. Safety — never harm, never leak, never deceive
2. Honesty — truth over comfort, delivered with care
3. Solutions — solve problems, bias toward action
4. Efficiency — respect time
5. Quality — 8.5/10 minimum
6. Growth — learn from every interaction
```

**Higher = keep in the index.** When pruning, demote entries that serve the lowest-ranking values first. An entry that supports Safety stays in the index; a minor efficiency preference gets moved to `preferences/`.

### 2. Memory Policy

Specifies what the agent considers signal worth preserving vs. noise to omit. Three categories:

| Category | Examples |
|----------|---------|
| **Always remember** | Decisions and their reasoning, corrections received, stated preferences, environment facts, recurring patterns |
| **Remember temporarily** | Code snippets (days), meeting context (until actions close), error details (until resolved) |
| **Forget deliberately** | PII after its purpose is served, specific financial amounts after the period, one-off queries irrelevant to future sessions |

The memory policy guides sub-skills during synthesis (README summaries) and helps the orchestrator at Step 3 (contradiction detection) when deciding which entries are candidates for pruning.

## What to Extract from RULES.md

`RULES.md` contains the agent's hard constraints, organized into five categories:

| Category | How it affects compaction |
|----------|--------------------------|
| **Security Boundaries** | Defines what may NEVER be stored or surfaced. If compaction would expose this content, halt and flag. |
| **Approval Gates** | Actions requiring user sign-off. Relevant if compaction would delete or archive content the user hasn't approved removing. |
| **Data Handling** | Retention policies — which categories expire, what must be forgotten. Drives pruning decisions at `compact-agent-topical-memories`. |
| **Escalation Protocols** | When to stop and ask a human. Use when contradictions or ambiguous deletions arise. |
| **Output Constraints** | Format requirements for the maintenance report. |

The Rules constrain what the sub-skills *may* do during compaction. A data-handling rule that says "health information must be forgotten after the session" means those entries are eligible for pruning; a security boundary that says "PII must never appear in group channels" means related entries must be handled with special care.

## Default Values Hierarchy (when SOUL.md is absent)

If `SOUL.md` is missing or does not contain a values hierarchy, use this default (highest to lowest):

1. **Safety** — Never harm, never leak, never deceive
2. **Honesty** — Truth over comfort
3. **Solutions** — Solve problems, bias toward action
4. **Efficiency** — Respect time
5. **Quality** — Good enough isn't
6. **Growth** — Learn from every interaction

**Always flag this substitution in the maintenance report** so the user knows a default was used instead of the agent's actual hierarchy.

## Identity Files Are Immutable

`SOUL.md`, `RULES.md`, and `IDENTITY.md` are **never modified** by any compaction skill. If compaction reveals content that contradicts these files:

1. Surface the contradiction in the Step 3 table.
2. Wait for human resolution before proceeding to Step 6 (index rebuild).
3. Record the contradiction and its resolution (or pending status) in the maintenance report.

Do not auto-resolve contradictions with identity files. The human decides.

## Orchestrator vs. Sub-skill Handling

| File | Orchestrator (Step 1) | Sub-skill |
|------|-----------------------|-----------|
| `SOUL.md` | Read from disk once; keep in context | Use from context — do NOT re-read |
| `RULES.md` | Read from disk once; keep in context | Use from context — do NOT re-read |

Both sub-skills (`compact-agent-daily-memories` and `compact-agent-topical-memories`) honor this contract — their specifications say "skip the identity-load step when invoked by the orchestrator."

## What to Do If SOUL.md or RULES.md Is Missing

| Situation | Action |
|-----------|--------|
| `SOUL.md` missing | **Halt at Step 1.** Warn the user. Do not proceed without identity context — compaction decisions without a values hierarchy may incorrectly prune high-value entries. |
| `RULES.md` missing | **Halt at Step 1.** Warn the user. Without hard constraints, the orchestrator cannot guarantee data-handling compliance during compaction. |
| Both missing | **Halt at Step 1.** Report both missing files and their expected paths. |
