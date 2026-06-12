---
title: Memory Architecture — Write Reference
description: >-
  Distilled reference for save-agent-memories. Covers the three-tier memory
  model, all Tier 2 store types and their directory layout, the sub-folder
  pattern, the MAGI frontmatter requirement for all Tier 2 files, and the
  MEMORY.md index structure relevant to Step 7 updates.
purpose: reference
tags:
  - memory-architecture
  - tier-2-stores
  - MEMORY.md
  - progressive-disclosure
  - magi
audience: ai-agent
---

# Memory Architecture — Write Reference

## Three-Tier Model

| Tier | Location | Role | Loaded when |
|------|----------|------|-------------|
| Tier 1 — Index | `MEMORY.md` (agent root) | Compact index of stable facts and pointers. **Must stay under 4 KB.** | Every session start |
| Tier 2 — Topical stores | `memory/` sub-tree | Detailed, domain-grouped records. | On demand, when relevant |
| Tier 3 — Session | Conversation context | Ephemeral; vanishes at session end unless explicitly written to a store. | In-flight only |

`save-agent-memories` writes to **Tier 2** and conditionally updates **Tier 1**. It never creates Tier 3 entries — those are the raw conversation.

---

## Tier 2 Store Types

| Category | Target path | What it holds |
|----------|-------------|---------------|
| `decisions/` | `memory/decisions/` | Key choices with date, reasoning, alternatives considered, and trade-offs. One sub-folder per decision. |
| `lessons/` | `memory/lessons/` | Mistakes, surprising outcomes, and learnings. One file per lesson. |
| `preferences/` | `memory/preferences/` | Communication style, formatting, working-rhythm, or domain preferences. |
| `people/` | `memory/people/` | Contacts, collaborators, advisors. One file per person. |
| `projects/` | `memory/projects/` | Named initiatives spanning multiple sessions. One sub-folder per project. |
| `activities/` | `memory/activities/` | Ongoing activities tracked across multiple sessions. One sub-folder per activity. |
| `analysis/` | `memory/analysis/` | Analysis not tied to a single project or activity. Standalone or cross-cutting. |
| `daily/` | `memory/daily/` | Session journal: `YYYY-MM-DD.md`. One file per day. Never pointers in MEMORY.md. |
| Environment facts | `MEMORY.md` index directly | Stable contextual facts: domain, team, constraints, key dates. Written to Tier 1, not Tier 2. |
| Patterns | `MEMORY.md` index or `memory/analysis/` | Recurring themes across sessions. Short patterns go in the index; detailed patterns go in `analysis/`. |

**Corrections** do not create a new file — they update an existing Tier 2 entry in place.

---

## Sub-Folder Pattern

Most Tier 2 stores use a sub-folder model for entries with non-trivial detail:

```text
memory/
└── decisions/
    ├── README.md                    ← store entry point
    └── decision-auth-provider/
        ├── README.md                ← sub-folder entry point (required)
        └── analysis-alternatives.md ← supporting detail (optional)
```

**Rules:**

- Every sub-folder **must** contain a `README.md` as its entry point.
- If the sub-folder does not exist, create it.
- If the parent store directory does not exist (e.g. `memory/decisions/`), create it with a `README.md`.
- For categories with flat files (lessons, preferences, people), there is no sub-folder — just the file itself and the store's `README.md`.

---

## Daily Store Special Handling

Daily session logs live at `memory/daily/YYYY-MM-DD.md`. After writing:

1. Append a one-line entry to `memory/daily/README.md`:

   ```markdown
   - [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence summary of the session focus>
   ```

2. If `memory/daily/README.md` does not exist, create it with a header and the first entry.
3. **Do not touch `MEMORY.md`.** The bootstrap pointer `[Daily log index](memory/daily/README.md)` is established once at agent setup — this skill never adds, modifies, or removes it.

---

## MAGI Frontmatter Requirement

Every Tier 2 file written by this skill **must** include MAGI-compatible YAML frontmatter. Minimum required fields:

```yaml
---
doc-id: <UUID v7>
title: <descriptive title>
description: <one-sentence summary for progressive discovery>
category: <memory category>
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - <tag-1>
  - <tag-2>
---
```

Optional fields:

- `classification-confidence: low` — add when the category choice was ambiguous.
- `retention: <duration>` — add when the agent's memory policy defines an expiration for this category.
- `origin: correction` — add when the file was created via a user correction rather than an initial write.

---

## MEMORY.md Index Structure

A well-formed `MEMORY.md` index follows this shape. Use it as the target when evaluating and applying Step 7 updates:

```markdown
# Memory

## Environment
- <domain context, team, tech stack, key dates>

## Active Projects
- [project-name](memory/projects/project-name/README.md)

## Recent Decisions
- YYYY-MM-DD: <decision summary> ([reasoning](memory/decisions/<entry>/README.md))

## User Preferences
- <preference 1>
- <preference 2>

## Lessons
- See [lessons/](memory/lessons/) for detailed learnings
- Key: "<most critical lesson>"

## Daily Logs
- [Daily log index](memory/daily/README.md)
```

When updating at Step 7, add new pointers, update facts, or correct stale entries. **Do not expand the index with detail.** Keep it as an index — detail belongs in Tier 2 stores. Verify the file stays under 4 KB before writing.
