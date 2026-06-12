---
title: Memory Architecture — Orchestrator Reference
description: >-
  Distilled reference for compact-agent-memories. Covers the three-tier memory
  model, all eight Tier 2 store types, MEMORY.md index constraints, the
  MEMORY.md example structure used at Step 6 (index rebuild), and the agent
  file layout relevant to pre-flight and audit.
purpose: reference
tags:
  - memory-architecture
  - tier-2-stores
  - MEMORY.md
  - progressive-disclosure
audience: ai-agent
---

# Memory Architecture — Orchestrator Reference

## Three-Tier Model

| Tier | File / Location | Role | When loaded |
|------|-----------------|------|-------------|
| Tier 1 — Index | `MEMORY.md` (agent root) | Compact index of stable facts + pointers to Tier 2 stores. **Must stay under 4 KB.** | Every session start |
| Tier 2 — Topical stores | `memory/` sub-tree | Detailed, domain-grouped records. Referenced on demand. | When the conversation makes them relevant |
| Tier 3 — Session | Conversation context | Ephemeral; vanishes at session end unless explicitly written to a store | N/A — in-flight only |

## The 4 KB Rule for MEMORY.md

`MEMORY.md` is loaded at **every** session start. If it grows beyond 4 KB, it consumes context window that should be available for actual work. The orchestrator is responsible for enforcing this limit at **Step 6** (index rebuild). If the index exceeds 4 KB after compaction, move the lowest-value entries to the appropriate topical stores and keep only pointers in the index — guided by the values hierarchy from `SOUL.md`.

## Tier 2 Store Types (all eight)

| Store | Path | What it holds |
|-------|------|---------------|
| `daily/` | `memory/daily/` | Session logs (`YYYY-MM-DD.md`). Reorganized by `compact-agent-daily-memories` into monthly/quarterly folders. |
| `activities/` | `memory/activities/` | Activities tracked across multiple sessions. One sub-folder per activity, anchored by `README.md`. |
| `analysis/` | `memory/analysis/` | Analysis not tied to a single activity or project (cross-cutting or standalone). |
| `projects/` | `memory/projects/` | Active and archived project records. One sub-folder per project, anchored by `README.md`. |
| `decisions/` | `memory/decisions/` | Key decisions with date, reasoning, alternatives considered, and affected parties. |
| `preferences/` | `memory/preferences/` | How the user likes things done — communication style, formatting, working patterns. |
| `people/` | `memory/people/` | Key contacts, their roles, relationship context. One file per person. |
| `lessons/` | `memory/lessons/` | Mistakes, learnings, and patterns extracted from mistakes. |

**Scope note:** The orchestrator audits all eight stores at Step 2. `compact-agent-daily-memories` handles `daily/`; `compact-agent-topical-memories` handles the other seven. The split is deliberate — each sub-skill is specialized.

## Agent File Layout (what the orchestrator reads)

```text
agents/<kebab-case-name>/
├── MEMORY.md       ← Tier 1 index; rebuilt by orchestrator at Step 6
├── SOUL.md         ← Identity file; read at Step 1; NEVER modified
├── RULES.md        ← Identity file; read at Step 1; NEVER modified
├── IDENTITY.md     ← Identity file; architectural context; NEVER modified
└── memory/
    ├── daily/
    ├── activities/
    ├── analysis/
    ├── projects/
    ├── decisions/
    ├── preferences/
    ├── people/
    └── lessons/
```

**Identity files (`SOUL.md`, `RULES.md`, `IDENTITY.md`)** define what the agent *is*. They are never modified by the memory system. If compaction reveals a contradiction with identity content, flag it for human review — do not auto-resolve.

## MEMORY.md Index Structure

A well-formed MEMORY.md index follows this shape (adapt to the agent's actual content):

```markdown
# Memory

## Environment
- Tech stack: <...>
- Team: <...>
- Current sprint / active context: <...>

## Active Projects
- [project-name](memory/projects/project-name/README.md)

## Recent Decisions
- YYYY-MM-DD: <decision summary> ([reasoning](memory/decisions/<file>.md))

## User Preferences
- <preference 1>
- <preference 2>

## Lessons
- See [lessons/](memory/lessons/) for detailed learnings
- Key: "<most critical lesson>"

## Daily Logs
- [Daily log index](memory/daily/README.md)
```

The orchestrator uses this structure as the target shape when rebuilding at Step 6. It removes stale pointers, adds new ones, and updates stable facts — it does NOT expand the index with detail. Detail belongs in the stores.

## Weekly Maintenance Cadence

| Trigger | Signal |
|---------|--------|
| Scheduled (weekly) | Run every 7 days or as configured in the agent's `MEMORY.md`. |
| Threshold | `MEMORY.md` index approaches 4 KB AND both daily and topical stores need attention. |
| Explicit request | User names this agent and says "compact", "maintenance", "clean up memory". |
| Upstream warning | `save-agent-memory` warns that compaction is needed before a new index update can proceed. |

## MAGI Front Matter Requirement

Every `README.md` created or substantially updated during maintenance must receive MAGI-compliant YAML front matter. Both sub-skills invoke `format-md-for-progressive-disclosure` for this — the orchestrator does not call it directly, but the step is enforced within each sub-skill.

## Agent Framework Context (broader knowledge base)

This skill operates within a structured agent framework defined across several KB files. The ones directly relevant at runtime are `agent-memory.md` (memory architecture) and `agent-soul.md` / `agent-rules.md` (identity context). The ancillary files below provide architectural grounding for understanding why the orchestrator is structured as it is:

| KB file | Relevance to this skill |
|---------|------------------------|
| `agent-identity.md` | `IDENTITY.md` is the agent's entry point — the first file an orchestrator agent or human reads. It is one of the three identity files this skill never modifies (alongside `SOUL.md` and `RULES.md`). |
| `agent-skills.md` | Defines skills as the procedural knowledge layer. This skill is itself a skill; understanding how skills are invoked explains the delegation model used in Steps 4–5. |
| `agent-tools.md` | Defines tool access as the execution layer. MCP storage backends (see `mcp-backend-routing.md`) are tools in this sense — the skill selects the highest-priority available one at Step 0. |
| `agent-workflows.md` | Defines repeatable processes. The 7-step sequential workflow in this skill is a formalized workflow; the strict sequencing (Steps 0–3 always run, Steps 4–5 conditional, Steps 6–7 always run) reflects the workflow design principle of separating mandatory from conditional stages. |

These files are not read at runtime — they are builder context. Reference them when modifying or extending this skill.
