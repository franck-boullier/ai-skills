---
title: Daily Log Architecture
description: >-
  Distilled reference for compact-agent-daily-memories. Covers the progressive
  disclosure hierarchy for memory/daily/, folder naming conventions, MEMORY.md
  constraints, and the three-tier memory model as it applies to daily logs.
purpose: reference
tags:
  - daily-log
  - progressive-disclosure
  - memory-architecture
audience: ai-agent
---

# Daily Log Architecture

## Three-Tier Memory Model (daily-log perspective)

| Tier | File | Role |
|------|------|------|
| Tier 1 — Index | `MEMORY.md` | Loaded every session. Contains **one** bootstrap pointer to daily logs: `[Daily log index](memory/daily/README.md)`. **Never modified** by this skill. |
| Tier 2 — Topical stores | `memory/daily/` tree | On-demand. The progressive hierarchy managed by this skill. |
| Tier 3 — Session | Conversation context | Ephemeral; vanishes at session end. |

**Critical constraint:** `MEMORY.md` must stay **under 4 KB**. The skill never writes to it — the sole pointer is established once at agent setup and is immutable from this skill's perspective.

## Folder Hierarchy

```text
memory/
└── daily/
    ├── README.md              ← MEMORY.md points here; agents navigate from here
    ├── YYYY-MM-DD.md          ← current month's files, flat, most-recent first
    ├── YYYY-MM/               ← created when that calendar month is complete
    │   ├── README.md          ← monthly synthesized summary + daily index
    │   └── YYYY-MM-DD.md      ← daily files moved here
    └── YYYY-QN/               ← created when that calendar quarter is complete
        ├── README.md          ← quarterly synthesized summary + monthly index
        └── YYYY-MM/           ← monthly folders moved inside the quarter folder
            ├── README.md
            └── YYYY-MM-DD.md
```

**Key rule:** monthly folders live *inside* the quarter folder after quarterly fold — not beside it at `memory/daily/` root.

## When Reorganization Is Due

| Trigger | Condition |
|---------|-----------|
| Monthly | Flat `YYYY-MM-DD.md` files in `memory/daily/` whose month is earlier than the current calendar month. |
| Quarterly | `YYYY-MM/` sub-folders in `memory/daily/` whose quarter is earlier than the current calendar quarter. |
| Nothing due | All completed periods are already in sub-folders; only current-month flat files remain at root. |

## memory/daily/README.md — State Templates

The entry-point file must match the actual on-disk layout. Use these shapes:

**State A — current month only:**

```markdown
# Daily Memory Log

## Current month

- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>
```

**State B — one or more completed months folded (no full quarter yet):**

```markdown
# Daily Memory Log

## Current month

- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>

## Archived

- [YYYY-MM](YYYY-MM/README.md) — <one-sentence month description>
```

**State C — a full quarter folded:**

```markdown
# Daily Memory Log

## Current month

- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>

## Archived

- [YYYY-QN](YYYY-QN/README.md) — <one-sentence quarter description>
```

**State D — completed months at root, not yet folded into a quarter:**

```markdown
# Daily Memory Log

## Current month

- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>

## Archived

- [YYYY-03](YYYY-03/README.md) — <one-sentence month description>
- [YYYY-02](YYYY-02/README.md) — <one-sentence month description>
- [YYYY-01](YYYY-01/README.md) — <one-sentence month description>
```

## All Markdown Files Require MAGI Front Matter

Every `README.md` created by this skill (monthly or quarterly) must receive MAGI-compliant YAML front matter via the `format-md-for-progressive-disclosure` sub-skill. This enables agent discovery through progressive disclosure. Without it, the navigation chain breaks silently.

Context hints to pass:

- Monthly: `"Monthly memory summary for period YYYY-MM. Category: daily-log-monthly. Audience: ai-agent."`
- Quarterly: `"Quarterly memory summary for period YYYY-QN. Category: daily-log-quarterly. Audience: ai-agent."`
