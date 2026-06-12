---
title: Soul Memory Policy — Synthesis Guidance
description: >-
  Distilled reference for compact-agent-daily-memories. Explains how to read
  SOUL.md's memory-policy section and use it to guide monthly and quarterly
  summary synthesis: what counts as signal, what to omit, and fallback behavior
  when SOUL.md is unavailable.
purpose: reference
tags:
  - soul
  - memory-policy
  - synthesis-guidance
audience: ai-agent
---

# Soul Memory Policy — Synthesis Guidance

## What SOUL.md Is (as it relates to this skill)

`SOUL.md` is the agent's behavioral constitution. For the purpose of this skill, only the **memory-policy section** matters. That section answers: *"What does this agent consider signal worth preserving vs. noise to omit?"*

## The Memory-Policy Section

Typical memory-policy content specifies:

- **Always remember:** decisions and their reasoning, corrections received, preferences stated, environment facts, recurring patterns.
- **Remember temporarily:** code snippets (days), meeting context (until actions done), error details (until resolved).
- **Forget deliberately:** PII after its purpose is served, specific financial amounts after the period, one-off queries with no future relevance.

## How to Use SOUL.md When Synthesizing Summaries

Read the memory-policy section **once at Step 1** (or use it from context if the orchestrator already loaded it). Apply it as a filter when writing monthly and quarterly README summaries:

| Signal worth capturing | What to omit |
|------------------------|--------------|
| Decisions made and why | Routine task completions with no learning |
| Corrections received from the user | Specific code snippets unless marked important |
| New preferences or updated ones | Full conversation transcripts |
| Environment changes (stack, team, key dates) | Temporary debugging context |
| Lessons from mistakes or unexpected outcomes | One-off queries irrelevant to future sessions |
| Cross-session patterns | Ephemeral meeting notes once actions are closed |

**The synthesis goal:** capture the *what changed and why* — not a replay of events. A monthly summary should compress 20–31 daily files into a single-page narrative that tells the agent what mattered during that month.

## Fallback — When SOUL.md Is Missing or Unreadable

If `SOUL.md` cannot be read:

1. Proceed with synthesis using best-effort judgment (bias toward decisions, lessons, and environment changes).
2. Warn the user: "SOUL.md could not be loaded — synthesis guidance unavailable; used best-effort defaults."
3. Do **not** halt the reorganization. The file-structuring work (folder creation, moves, README index) must still complete.

## Orchestrator vs. Direct Invocation

| Invocation mode | SOUL.md handling |
|-----------------|-----------------|
| Called from `compact-memories` orchestrator | SOUL.md content is already in conversation context from the orchestrator's Step 1. **Do not re-read from disk.** Use the in-context version. |
| Called directly (standalone) | Read `SOUL.md` from the agent's root directory at Step 1. |

## What NOT to Do

- Do not reproduce daily entries verbatim in summaries — summarize the signal.
- Do not let a missing SOUL.md block folder reorganization — warn and continue.
- Do not apply one agent's SOUL.md to another agent's `memory/daily/` tree — the memory policy is agent-specific.
