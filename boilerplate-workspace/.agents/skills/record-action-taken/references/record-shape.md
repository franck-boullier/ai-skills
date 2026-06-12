# Reference — Resolved action record shape

This is the on-disk shape of an action record after the `record-action-taken` skill has finished. The fields above the `---`-separated frontmatter mirror the contract established by `record-action-needed` (the companion creator skill); the resolution fields are added or updated by this skill.

## Frontmatter (full)

```yaml
---
# Original fields (from record-action-needed) — preserved exactly.
id: A-<UUIDv7>
status: <outcome>            # was "open"; now: done | skipped | obsolete | cancelled
owner: <owner>
due-date: <YYYY-MM-DD or "none">
priority: <low|medium|high>
source: <session reference or human-readable origin>
created-at: <UTC ISO-8601>

# Latest resolution metadata — overwritten on every re-resolution.
resolved-at: <UTC ISO-8601>
resolved-by: <agent name or "user">
resolution-status: <outcome>
resolution-note: <note or "No note provided.">

# Append-only audit trail of every resolution event.
resolution-history:
  - resolved-at: <UTC ISO-8601>
    resolved-by: <actor>
    status: <outcome>
    note: <note or null>
---
```

The flat `resolved-*` and `resolution-*` fields are duplicates of the latest entry in `resolution-history`. They exist so callers can read the current state without walking the history array. The history is the canonical record; the flat fields are the convenience cache.

## Body

```markdown
# Action — <description (truncated to ~80 chars)>

## Description
<original description, unchanged>

## Context
<original context, unchanged>

## Resolution
**Resolved as:** <outcome>
**At:** <UTC ISO-8601>
**By:** <actor>

<resolution note, or "No note provided.">
```

On a re-resolution, the body **appends** an additional section without altering the existing one:

```markdown
## Resolution Event 2
**Resolved as:** <new-outcome>
**At:** <UTC ISO-8601>
**By:** <actor>

<note>
```

The number after "Resolution Event" matches the 1-based index of the entry in `resolution-history`. The first event is rendered as the bare `## Resolution` heading; the second and beyond use `## Resolution Event N`.

## Why this shape

The append-only history makes the record **event-sourced**: every state transition is preserved on disk, and the latest state is always recoverable by replaying the events. This matters for re-resolution (an action skipped in one session and then completed in another) and for auditing decisions made by automated agents.

The flat `resolved-*` fields exist as a convenience for index generation and for callers who only need the latest state — walking `resolution-history` to find the most recent entry is fine but tedious in templated reports.

## Invariants

- `id` is **immutable** across the entire lifecycle. The skill must never alter it.
- `created-at`, `description`, `owner`, `due-date`, `priority`, `source` are **immutable** in this skill — they belong to `record-action-needed` and changing them here would corrupt the audit trail.
- `resolution-history` is **append-only**. Old entries are never edited or removed; only new entries are appended.
- The flat `resolved-*` / `resolution-*` fields always reflect the **last entry** of `resolution-history`.
