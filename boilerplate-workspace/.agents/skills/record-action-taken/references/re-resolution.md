# Reference — Re-resolution semantics

Re-resolution is the case where the skill is asked to resolve an action that has **already been resolved** (its current `status` is one of `done | skipped | obsolete | cancelled`, not `open`). This is fully supported and is the mechanism by which the skill survives the messy reality of changing minds, cancelled features being un-cancelled, and skipped work that turned out to matter after all.

The on-disk record is **event-sourced**: the `resolution-history` array grows by one entry per resolution; the body grows by one `## Resolution Event N` section. Nothing is overwritten or deleted.

## Two sub-cases

### Outcome unchanged

The new outcome equals the current outcome (e.g. an action already in `done/` is re-resolved as `done`, perhaps to add a clarifying note).

- The record stays in its current per-outcome subfolder.
- The frontmatter `resolution-history` gains a new entry; the flat `resolved-*` fields update to the latest event.
- The body gains a new `## Resolution Event N` section.
- **Indexes are not touched.** The row already exists in the right per-outcome `INDEX.md`; no row needs to move.

This is the cheap case — useful when the caller wants to attach an additional note or correct the timestamp without changing the substantive outcome.

### Outcome changed

The new outcome differs from the current outcome (e.g. `skipped` → `done`, or `done` → `cancelled`).

- The file is **moved** atomically from `<old-outcome>/A-<id>.md` to `<new-outcome>/A-<id>.md`.
- The frontmatter `status` flips to the new outcome; `resolution-history` gains a new entry; the flat `resolved-*` fields update to the latest event.
- The body gains a new `## Resolution Event N` section.
- The row is **removed** from the old per-outcome `INDEX.md` and **appended** to the new per-outcome `INDEX.md`. (The new index is created from the bundled template if it does not yet exist.)
- The open `INDEX.md` is **not** touched in this case — the action was never open at the time of this re-resolution.

## What does NOT happen

- The original `id` never changes.
- The original `description`, `owner`, `due-date`, `priority`, `source`, `created-at` never change.
- The first `## Resolution` section in the body is never edited or removed; new events append below it.
- Old `resolution-history` entries are never edited or removed.

## Worked example

Starting state — action skipped on day 1:

```yaml
status: skipped
resolved-at: '2026-05-06T12:00:00Z'
resolution-status: skipped
resolution-note: "Decided we don't need this for the current sprint."
resolution-history:
  - resolved-at: '2026-05-06T12:00:00Z'
    status: skipped
    resolved-by: user
    note: "Decided we don't need this for the current sprint."
```

Re-resolved as `done` on day 2:

```yaml
status: done
resolved-at: '2026-05-07T06:25:27Z'
resolution-status: done
resolution-note: "Actually needed for prod release after all."
resolution-history:
  - resolved-at: '2026-05-06T12:00:00Z'
    status: skipped
    resolved-by: user
    note: "Decided we don't need this for the current sprint."
  - resolved-at: '2026-05-07T06:25:27Z'
    status: done
    resolved-by: user
    note: "Actually needed for prod release after all."
```

The body now has a `## Resolution` section (the day-1 event) and a `## Resolution Event 2` section (the day-2 event). The file lives at `<root>/done/A-<id>.md`. The row moved from `skipped/INDEX.md` to `done/INDEX.md`.

## Implementation note

`scripts/resolve_action.py` handles both sub-cases. The agent does not need to detect which one applies — it passes the same arguments either way and the script computes the right move and index updates from the existing record's `status` field.
