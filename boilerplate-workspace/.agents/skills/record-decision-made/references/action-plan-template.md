# Action Plan — File Template

The action plan is the execution tracker for a closed decision. The decision file records *what was decided and why*; the action plan records *how the team is going to make it real and how it will be clear the work is done*.

Paired with: the closed decision file at `{closed-folder}/{closed-subfolder}/{date}-{id}-{slug}.md`.
Lives in: a lifecycle subfolder of the action-plans folder declared in `decisions.config.md`. When `folders.action_plans_subfolders` is set (typical: `active`, `paused`, `completed`, `abandoned`), new plans are written into the `active` subfolder. The plan's physical subfolder must always match its `status:` frontmatter.
Filename: `{date}-{id}-action-plan.md`.

## Path-depth rule

When the plan lives in a lifecycle subfolder (e.g. `{action-plans-folder}/active/{file}.md`), every relative path the plan writes towards a sibling folder of the action-plans parent must use **two** `..` segments. Concretely:

- `decision_file` frontmatter → `../../{closed-folder}/{closed-subfolder}/{date}-{id}-{slug}.md`
- Body `**Decision:** see [...]` link → same as above.
- In-body completion-evidence links into the closed-decisions folder → same `../../...` depth.

When `action_plans_subfolders` is **not** declared (legacy single-folder layout), use a single `..`. Get the depth wrong and every link in the plan breaks.

## Status vocabulary and subfolders

The plan-level `status:` frontmatter uses the vocabulary in `decisions.config.md` (`action_plan_statuses`, typically `Active | Paused | Complete | Abandoned`). Each value maps 1:1 to a subfolder under the action-plans parent (`active/`, `paused/`, `completed/`, `abandoned/`). A plan changes physical subfolder when its `status:` changes — see the parent-folder `README.md` for the move procedure.

Note: the per-task `Status` field inside `## Tasks` uses a different vocabulary (`Not started | In progress | Blocked | Done`) and is independent of the plan-level `status:`.

---

## File template

````markdown
---
title: "Action Plan — {ID} {Short decision title}"
# When the plan lives in a lifecycle subfolder (e.g. active/), use TWO ../ segments.
# When no action_plans_subfolders are declared, use ONE ../ instead.
decision_file: "../../{closed-folder}/{closed-subfolder}/{YYYY-MM-DD}-{ID}-{slug}.md"
status: "Active"        # Active | Paused | Complete | Abandoned — value MUST match the subfolder
owner: "{Role or name}"
created: "{YYYY-MM-DD}"
last_updated: "{YYYY-MM-DD}"
---

# Action Plan — {ID} {Short decision title}

**Decision:** see [`{YYYY-MM-DD}-{ID}-{slug}.md`](../../{closed-folder}/{closed-subfolder}/{YYYY-MM-DD}-{ID}-{slug}.md)
**Owner:** {Role or name}
**Deadline:** {YYYY-MM-DD}        *(from decision file)*
**Review:** {YYYY-MM-DD}           *(from decision file)*

---

## Summary

{One or two sentences restating the decision in execution terms — what will change in the codebase, schema, docs, contracts, or operations when every task here is Done.}

---

## Tasks

### Task 1 — {Short imperative task title}

- **Status:** Not started
- **Owner:** {role or name}
- **Due:** {YYYY-MM-DD}
- **Review:** {YYYY-MM-DD}
- **Description:** {One or two sentences. What exactly gets changed, where.}
- **Dependencies:** {Other task IDs in this plan, decision files, or external specs this waits on. `—` if none.}
- **Blockers:** {Anything currently stopping progress. `—` if none.}
- **Completion evidence:** {Empty while Not started. When Done, link the PR, commit hash, migration filename, doc section, signed document, or other artefact that proves the task landed, plus a one-sentence outcome.}

### Task 2 — {Short imperative task title}

- **Status:** Not started
- **Owner:** {role or name}
- **Due:** {YYYY-MM-DD}
- **Review:** {YYYY-MM-DD}
- **Description:** …
- **Dependencies:** …
- **Blockers:** —
- **Completion evidence:** —

{Repeat for every Action Item from the decision.}

---

## Completed

{Move tasks here when Status becomes Done. Preserve the task block with final status line, completion evidence, and the date completed — the history is the record.}

- [x] **Task N — {title}** — Completed {YYYY-MM-DD} — Evidence: {link} — Result: {one-sentence outcome}

---

## Change log

- {YYYY-MM-DD} — Plan created from decision `{YYYY-MM-DD}-{ID}-{slug}.md`. Tasks 1–N seeded from Action Items.
- {YYYY-MM-DD} — {What changed, by whom.}
````

---

## Status values

Use exactly these strings. The grep-ability of the plan depends on this vocabulary — do not invent new values.

`Not started` — no work begun.
`In progress` — actively being worked.
`Blocked` — cannot advance until a dependency is resolved. Always fill the `Blockers` field when setting this status.
`Done` — completed, evidence linked, moved to the `## Completed` section.

## When to update the plan

Update the plan — and bump `last_updated` in the front matter — whenever a task status changes, a blocker is discovered, resolved, or reassigned, a new task emerges that was not in the original Action Items (add it to `## Tasks` and note it in the Change log), or a task is retired as no-longer-relevant (move to `## Completed` with Status `Abandoned` and an explanation).

## First-time folder setup

If the action-plans folder declared in `decisions.config.md` does not yet exist, create it alongside the first action plan. Two layouts are supported.

### Layout A — `action_plans_subfolders` declared (recommended)

Create the parent folder, every declared lifecycle subfolder (`active/`, `paused/`, `completed/`, `abandoned/`), the parent `_index.md`, a parent `README.md`, and an `_index.md` inside every lifecycle subfolder. The first plan goes into the `active` subfolder; the other three sub-indexes start empty.

The parent `_index.md` is a cross-folder log:

````markdown
---
title: "{Domain label} — Action Plans: Index"
last_updated: "{YYYY-MM-DD}"
owner: "{Role — taken from the domain's default_owner_role in decisions.config.md}"
related:
  - "./active/_index.md"
  - "./paused/_index.md"
  - "./completed/_index.md"
  - "./abandoned/_index.md"
  - "../{closed-folder}/_index.md"
  - "../{pending-folder}/_index.md"
---

# {Domain label} — Action Plans: Index

Each closed decision in [`../{closed-folder}/`](../{closed-folder}/) has a paired action plan here. Plans are partitioned by lifecycle status into [`active/`](./active/), [`paused/`](./paused/), [`completed/`](./completed/), and [`abandoned/`](./abandoned/).

## Quick status

- **Total plans:** 1
- **Active:** 1
- **Paused:** 0
- **Completed:** 0
- **Abandoned:** 0

## Cross-folder log

| File | Decision | Owner | Status | Subfolder |
|---|---|---|---|---|
| [active/{YYYY-MM-DD}-{ID}-action-plan.md](./active/{YYYY-MM-DD}-{ID}-action-plan.md) | {ID} {Short title} | {Owner} | Active | `active/` |

## Sub-indexes

- [`active/_index.md`](./active/_index.md)
- [`paused/_index.md`](./paused/_index.md)
- [`completed/_index.md`](./completed/_index.md)
- [`abandoned/_index.md`](./abandoned/_index.md)
````

The active sub-index is a per-status table; the paused/completed/abandoned sub-indexes start empty with placeholder text.

### Layout B — legacy single-folder (no `action_plans_subfolders`)

Create the action-plans folder with a single `_index.md`. New plans land at the parent path and use a single `..` to reach the closed-decisions folder.

````markdown
---
title: "{Domain label} — Action Plans: Index"
last_updated: "{YYYY-MM-DD}"
owner: "{Role — taken from the domain's default_owner_role in decisions.config.md}"
related:
  - "../{closed-folder}/_index.md"
  - "../{pending-folder}/_index.md"
---

# {Domain label} — Action Plans: Index

Each closed decision in [`{closed-folder}/`](../{closed-folder}/) has a paired action plan here that tracks implementation progress.

---

## Active plans

| File | Decision | Owner | Status |
|---|---|---|---|
| [{YYYY-MM-DD}-{ID}-action-plan.md](./{YYYY-MM-DD}-{ID}-action-plan.md) | {ID} {Short title} | {Owner} | Active |

## Completed plans

| File | Decision | Completed | Notes |
|---|---|---|---|

## Quick status

- Active: **1**
- Complete: **0**
- Paused/Abandoned: **0**
````

When a new action plan is created later, append a row to the relevant table and refresh the Quick status block.

## Paired-file invariants

Every file in the closed-decisions folder should have exactly one paired file in the action-plans folder, except historical decisions closed before the skill was introduced. The action plan's front-matter `decision_file` must resolve to an existing file. An action plan can be marked `Complete` only when every task is in the `## Completed` section.

**Subfolder invariant (when `action_plans_subfolders` is declared):** the plan file's physical subfolder must always match its `status:` frontmatter — `Active` ↔ `active/`, `Paused` ↔ `paused/`, `Complete` ↔ `completed/`, `Abandoned` ↔ `abandoned/`. A plan in `active/` with `status: Complete` (or any other mismatch) is a bug and must be reconciled by either correcting the status or moving the file. Cross-checks: the per-folder `_index.md` row count must equal the actual file count in that subfolder, and the parent `_index.md`'s cross-folder log must list every plan exactly once with the correct `Subfolder` column.
