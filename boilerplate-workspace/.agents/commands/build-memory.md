---
name: build-memory
description: Design and create the complete memory architecture for this workspace — MEMORY.md index, tiered topical store, the decision-records subsystem (decisions.config.md + destination folders for record-decision-needed / record-decision-made), update triggers, retention policies, connectivity test, and setup report. Usage: /build-memory
---

# /build-memory

Build the workspace memory: the `MEMORY.md` index, the `memories/` folder
structure, and the decision-records subsystem that turn this workspace into an
AI agent with persistent context instead of one that starts from zero every
session.

## Usage

```bash
/build-memory
```

## Behaviour

Use the skill `build-agent-memory` to help me build the memories files and
folder structure for this workspace now.

Act as a thought partner.
DO NOT GUESS!
Ask questions if you have ANY doubt!

The skill will ask for the candidate workspace root, detect any inherited
`MEMORY.md` + `memories/` tree, and select the correct mode (`workspace`,
`agent`, or `workspace-confirm-and-update`) before creating or merging anything.

## Decision-records subsystem (required)

After `build-agent-memory` finishes, **ensure the files and folders the
`record-decision-needed` and `record-decision-made` skills depend on exist**,
because greenfield `workspace` mode does not scaffold them. This step is
**additive — never overwrite or modify a file that already exists**; only
create what is missing, then confirm the result with me.

1. **`decisions.config.md` at the workspace root.** If it is missing, create it
   from the canonical template at
   `.agents/skills/build-agent-memory/references/decisions-config-template.md`
   (path relative to the workspace root), replacing `[PROJECT-NAME]` with the
   confirmed workspace name and `YYYY-MM-DD` with today's date. This is the file
   both decision skills read first (lookup order: workspace root → `.agents/` →
   per-project). Then call `format-md-for-progressive-disclosure` on it.

2. **The destination folders**, created eagerly with a seeded `_index.md` in
   each (the canonical paths declared in that same template):
   - `memories/decision-records/list-decision-needed/` — pending decisions
   - `memories/decision-records/list-decision-taken/final/` — closed, no scheduled re-evaluation
   - `memories/decision-records/list-decision-taken/temporary/` — closed, revisit at a trigger
   - `memories/decision-records/list-decision-action-plans/active/`
   - `memories/decision-records/list-decision-action-plans/paused/`
   - `memories/decision-records/list-decision-action-plans/completed/`
   - `memories/decision-records/list-decision-action-plans/abandoned/`
   - plus the parent cross-folder indexes `list-decision-taken/_index.md` and
     `list-decision-action-plans/_index.md`

3. **Seed each `_index.md` empty but valid** — MAGI-compliant frontmatter, the
   correct table header, and a Quick Status block with zero counts. The exact
   per-index column schemas differ (pending vs final vs temporary vs the four
   action-plan statuses); use the index shapes documented in the
   `record-decision-needed` and `record-decision-made` skills (the latter's
   Step 5 and the action-plan template's "First-time folder setup" section) as
   the source of truth. Run `format-md-for-progressive-disclosure` on each
   `_index.md` after writing it.

Resolve every path under the workspace root (no absolute paths, no `..`
segments). Report which decision-records artefacts were created versus already
present.

## Output Structure

- `MEMORY.md` index at the workspace root (under 4 KB, MAGI-compliant frontmatter)
- Tiered topical store under `memories/` with a `README.md` entry point per category
- `decisions.config.md` at the workspace root + the full decision-records subtree with seeded `_index.md` files
- Memory update triggers (topical + daily log) and retention policies documented in `MEMORY.md`
- Connectivity test entry confirming the storage backend is writable
- `memory-setup-report-YYYY-MM-DD-HH-MM.md` documenting the full configuration

## Skill Reference

- `build-agent-memory`
- `format-md-for-progressive-disclosure`
- `save-agent-memories`
- `record-decision-needed`
- `record-decision-made`
