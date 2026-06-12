---
title: Topical Store Architecture
description: >-
  Distilled reference for compact-agent-topical-memories. Defines the seven
  Tier 2 topical memory stores — their purpose, directory layout, sub-folder
  patterns, MAGI front matter fields required for compaction, archive target
  conventions, and how to handle legacy flat-file layouts for stores that the
  current architecture defines as sub-folder stores.
purpose: reference
tags:
  - agent-memory
  - agent-memories
  - topical-memories
  - tier-2
  - magi
  - archive
  - legacy-flat-file
audience: ai-agent
last-updated: 2026-04-05
---

# Topical Store Architecture

## The Seven Tier 2 Stores

Tier 2 stores live under the agent's `memory/` tree. Each is a sub-directory with
a `README.md` entry point. They are loaded **on demand** — never at every session
start (that's Tier 1, the `MEMORY.md` index).

| Store | Content | File pattern | Compaction risk |
|-------|---------|--------------|-----------------|
| `decisions/` | Key choices + full reasoning | Sub-folder per decision | **High** — reasoning must never be lost |
| `projects/` | Active project records | Sub-folder per project | Medium |
| `activities/` | Multi-session activities | Sub-folder per activity | Medium |
| `lessons/` | Mistakes and learnings | One `.md` file per lesson | Medium |
| `preferences/` | User style and working patterns | One `.md` file per topic | Low–Medium |
| `people/` | Key contacts and relationships | One `.md` file per person | Low |
| `analysis/` | Cross-topic or cross-project analyses | One `.md` file per analysis | Medium |

## Directory Layouts

### Sub-folder stores (decisions/, projects/, activities/)

Each entry is a **sub-folder** containing a `README.md` and optional detail files.
The store root also has its own `README.md` index.

```text
memory/decisions/
├── README.md                        ← store-level index (links to all decisions)
├── decision-auth-provider/
│   ├── README.md                    ← entry point for this decision
│   ├── analysis-01.md               ← detail file (added when README grows too large)
│   └── ...
├── decision-mobile-defer/
│   └── README.md
└── archive/
    └── decision-superseded-01/      ← archived sub-folders land here
        └── README.md
```

Same layout applies to `projects/` and `activities/`.

### Flat-file stores (lessons/, preferences/, people/, analysis/)

Each entry is a single `.md` file. The store has a `README.md` index.

```text
memory/lessons/
├── README.md                        ← store-level index
├── lesson-staging-deploy.md
├── lesson-rate-limit-cache.md
└── archive/                         ← archived files land here (if needed)
```

## MAGI Front Matter Fields Used by This Skill

Every `.md` file in the topical stores carries MAGI-compliant front matter.
The compaction skill reads these fields during the audit (Step 2):

| Field | Purpose during compaction |
|-------|--------------------------|
| `doc-id` | Preserved unchanged across merges — the stable identity of a record |
| `created` | Retained in merged entries (use the oldest source date) |
| `last-updated` | Updated by `format-md-for-progressive-disclosure` after any modification |
| `status` | Drives archive triggers (`completed`, `abandoned`, `superseded`, `inactive`, `departed`) |
| `retention` | Governs prune eligibility — missing field means "keep indefinitely" |
| `category` | Classification used for grouping and promotion to `analysis/` |
| `tags` | Used for lesson theme detection (shared ≥ 2 tags → potential merge candidates) |

## Archive Conventions

- **Destination:** `[store]/archive/` sub-folder (e.g., `memory/decisions/archive/`).
- **Sub-folder stores:** move the **entire sub-folder** to `[store]/archive/<name>/`. Never move only the `README.md`.
- **Flat-file stores:** move the single `.md` file to `[store]/archive/<filename>`.
- **Naming:** retain the source name unchanged. Do not add date prefixes — the `last-updated` front matter provides the date.
- **Conflict:** if a file or folder with the same name already exists in `archive/`, append a numeric suffix (e.g., `-02`) and log the conflict in the compaction report.
- **archive/README.md:** create it if it does not already exist when the first entry is archived to that store.

## Legacy Flat-File Layouts for Sub-folder Stores

Older agents may use a **flat-file layout** for stores that the current
architecture defines as sub-folder stores (`decisions/`, `projects/`,
`activities/`). In a flat-file layout each entry is a single `.md` file
directly in the store root — for example `decisions/2026-03-28-auth-provider.md`
instead of `decisions/decision-auth-provider/README.md`.

When the skill encounters a flat-file layout in a store that should be
sub-folder based:

1. **Do not error or skip.** Treat each flat `.md` file as the primary entry
   for that record — equivalent to a sub-folder's `README.md`.
2. Apply all merge, archive, and prune logic using the flat file as the entry.
3. **Archive:** move the flat file to `[store]/archive/<filename>` (keep it
   flat — do not create a sub-folder on archive).
4. **Merge:** consolidate into a new flat file, retaining the oldest source
   filename.
5. **Do not convert** flat-file stores to sub-folder stores during compaction.
   Structural migration is out of scope. Log in the compaction report:
   "`[store]/` uses flat-file layout — sub-folder migration not performed."

> **Root cause note:** the worked memory-update example in `agent-memory.md`
> shows a flat-file decision path. That example predates the current sub-folder
> architecture. Both layouts are valid in the wild; the sub-folder layout is
> the current standard.

---

## The README.md Entry Point Pattern

Each store's root `README.md` is the **navigation hub** — it links to all active entries
and all archived entries. After any compaction action:

1. Remove links to merged, archived, or pruned entries.
2. Add links to new consolidated entries or archive folders.
3. Invoke `format-md-for-progressive-disclosure` on the updated `README.md`.

Keeping the `README.md` accurate is what makes the store navigable by agents
without loading every file.
