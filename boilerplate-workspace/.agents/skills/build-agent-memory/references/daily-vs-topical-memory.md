# Daily vs Topical Memory — Reference

This document is the canonical definition of the two types of Tier 2 memory for
the `build-agent-memory` skill. All daily log rules, triggers, and
`memories/daily/README.md` specifications live here. Steps 4 and 7 of the skill
point here rather than re-stating these rules inline.

---

## The Two Types of Tier 2 Memory

Tier 2 memory is not homogeneous. There are two fundamentally different types,
and conflating them produces bloated, unreliable memory architectures.

### Type A — Topical Memory Stores (curated, stable, low volume)

Stores for **curated signal**: `decisions/`, `lessons/`, `preferences/`,
`people/`, `projects/`, `activities/`, `analysis/`.

- Written **selectively** — only when a significant event occurs.
- Each entry is a refined, structured record.
- These stores conditionally update `MEMORY.md` when a stable fact changes or a
  new pointer is needed.

### Type B — Daily Log (`memories/daily/`) — raw journal, high volume

The daily log is a **raw session journal** written at the end of every session.
It captures what happened: key events, decisions made, corrections received,
people introduced, open items.

- Written at the end of **every** session — regardless of whether any topical
  event occurred.
- Deliberately **unfiltered** — the value is the complete audit trail, not
  curation.
- The daily log is **raw material, not curated memory.** The compaction process
  (`compact-agent-daily-memories`) distils signal from daily logs into topical
  stores. Do not treat `memories/daily/` as a substitute for `memories/decisions/`
  or `memories/lessons/` — they serve different purposes.

---

## Three Rules That Govern the Daily Log

These rules differ from every other Tier 2 store. They apply without exception.

## Path Resolution Convention (when `root_prefix` is used)

`MEMORY.md` may declare a YAML frontmatter key `root_prefix` (per the skill spec).
When this convention is used:

- All markdown link targets in `MEMORY.md` are written **relative to `root_prefix`**.
- The agent resolves full paths as: `{root_prefix}{link_target}`.

**Canonical recommendation:** set `root_prefix` to the fully qualified path of the memory root directory (the same location you would otherwise use as `[AGENT-MEMORY-ROOT]`).

**Examples:**

- If `root_prefix` points to the memory root (recommended): use `daily/README.md`
- If `root_prefix` points to a parent directory above the memory root: use `memories/daily/README.md` (or `memories/daily/README.md`, depending on your store directory name)

This reference uses the canonical `memories/` directory name for examples. Adapt the directory name (`memories/` vs `memories/`) to your actual store.

### Rule 1 — Never updates `MEMORY.md`

The only `MEMORY.md` entry for all daily logs is a single bootstrap pointer
established once during setup (Step 6):

```markdown
## Daily Logs

- [Daily log index](memories/daily/README.md)
```

**Using `root_prefix`:** If `MEMORY.md` declares `root_prefix` and you set it to the memory root directory (recommended), the bootstrap pointer is written as:

```markdown
## Daily Logs

- [Daily log index](daily/README.md)
```

If `root_prefix` points to a parent directory above the memory root, keep the link target as `memories/daily/README.md` (or your store’s equivalent path).

No individual daily file (`YYYY-MM-DD.md`), and no update to
`memories/daily/README.md`, ever modifies `MEMORY.md`. The bootstrap pointer is
immutable after setup — it is established once and never extended or replaced.

### Rule 2 — Navigation flows through `memories/daily/README.md`

After each session, exactly one line is appended to `memories/daily/README.md`
(most-recent first):

```markdown
- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>
```

This README is the entry point for all daily log navigation. `MEMORY.md`
contains only the bootstrap pointer to this README — not individual session
links.

### Rule 3 — Progressive disclosure hierarchy inside `daily/`

As daily files accumulate, they are reorganized into a nested structure to keep
`memories/daily/README.md` navigable. This reorganization is handled by
`compact-agent-daily-memories`, not by the save skill:

```text
memories/daily/
├── README.md                  ← sole navigation entry point; lists current month flat
├── 2026-04-09.md              ← current month: flat, most-recent first
├── 2026-04-08.md
├── 2026-Q1/                   ← created by compact-agent-daily-memories when Q1 ends
│   ├── README.md              ← quarterly synthesized summary + monthly links
│   ├── 2026-01/               ← created when January ends
│   │   ├── README.md          ← monthly synthesized summary + daily links
│   │   └── 2026-01-31.md … 2026-01-01.md
│   ├── 2026-02/
│   └── 2026-03/
```

The current month's flat files live directly under `memories/daily/`. When a
month completes, `compact-agent-daily-memories` creates a `YYYY-MM/` sub-folder,
moves the daily files into it, and writes a synthesized monthly `README.md`.
When a quarter completes, the three monthly sub-folders are folded into a
`YYYY-QN/` sub-folder with a quarterly `README.md`.

---

## Daily Log Trigger (for use in Step 4)

Document the daily log trigger as a **separate category** below the topical
trigger table. Never merge it with topical triggers — they have different
destinations and different `MEMORY.md` update rules.

| Event | Memory destination |
| --- | --- |
| Session ends | Write `memories/daily/YYYY-MM-DD.md`; append one line to `memories/daily/README.md`; **do NOT touch `MEMORY.md`** |

This trigger fires at the end of **every** session without exception —
regardless of whether any topical event occurred. It is handled by the
`skill-save-agent-memories` workflow when invoked for the daily log. The two
operations (daily log write and topical memory write) use the same skill but
must never be conflated — they write to different destinations and follow
different `MEMORY.md` update rules.

---

## `memories/daily/README.md` — Initial Content Specification (for use in Step 7)

The `daily/` README is **not** a static description file like every other
topical store README. It is the sole navigation entry point for all daily logs
and has fundamentally different behavior.

### Purpose

This file is the navigation index for all daily session logs. It is appended to
after every session and reorganized by `compact-agent-daily-memories` as the
archive grows.

### Initial content skeleton

When first created (Step 7), the file starts with no daily entries yet. Write
the following body and then invoke `format-md-for-progressive-disclosure` to
add MAGI-compliant frontmatter:

```markdown
# Daily Log Index

One line is appended here at the end of each session by `skill-save-agent-memories`.
Format: `- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>`

As logs accumulate, `compact-agent-daily-memories` reorganizes this index into
monthly (YYYY-MM/) and quarterly (YYYY-QN/) sub-folders, each with a synthesized
summary README.

---

<!-- entries appear here, most-recent first -->
```

### Append format (per session)

Each session appends exactly one line, prepended at the top of the entries
block (most-recent first):

```markdown
- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>
```

### Context hint for `format-md-for-progressive-disclosure`

Pass: `"Daily log navigation index. Category: daily-log-index. Audience: ai-agent."`

---

## Bootstrap Pointer Rule — Summary

| Rule | Detail |
| --- | --- |
| Establish once | The `## Daily Logs` section in `MEMORY.md` is written during Step 6 and never modified after setup. |
| Sole reference | The `Daily log index` bootstrap pointer is the only daily-log entry that ever appears in `MEMORY.md`. Use exactly one of these targets, depending on `root_prefix`: If `root_prefix` points to the memory root: `- [Daily log index](daily/README.md)`. If `root_prefix` points to a parent directory above the memory root (or no `root_prefix` convention is used): `- [Daily log index](memories/daily/README.md)` (or your store's equivalent, e.g. `memories/daily/README.md`) |
| Never individual links | No `YYYY-MM-DD.md` file, and no update to the daily log index README (`daily/README.md` when `root_prefix` points to the memory root; otherwise `memories/daily/README.md` or equivalent), ever adds a pointer to `MEMORY.md`. |
| Navigation direction | Daily log navigation flows **downward** from the bootstrap pointer: `MEMORY.md` → daily log index README (`daily/README.md` when `root_prefix` points to the memory root; otherwise `memories/daily/README.md` or equivalent) → daily files. Never upward. |

---

## See Also

- `memory-policies.md` — full trigger table (topical + daily) and DON'Ts
- `memory-model.md` — Tier 1 / Tier 2 / Tier 3 model; canonical topical store layout
- `compact-agent-daily-memories` skill — handles the Step 7 progressive disclosure reorganization at monthly/quarterly boundaries
