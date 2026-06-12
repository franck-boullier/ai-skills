<!-- REFERENCE ONLY — not read at runtime.

scripts/resolve_action.py generates per-outcome INDEX.md files INLINE (it holds
the per-outcome titles, quick-status labels, and descriptions), matching the
live actions-store convention shown below. The live actions indexes carry NO
MAGI frontmatter — they begin at the H1 — so neither does what the script
generates. This file documents the shape; editing it does not change the
script's output.

Per-outcome substitutions used by the script:
  outcome    title word   quick-status label   description suffix
  done       Completed    completed            (none)
  skipped    Skipped      skipped              (conscious decision not to act)
  obsolete   Obsolete     obsolete             (became irrelevant before being acted on)
  cancelled  Cancelled    cancelled            (withdrawn by the creator)

The open index (INDEX.md, written by record-action-needed) uses a different,
6-column schema: | ID | Description | Owner | Due | Priority | Created |
-->

# {Completed|Skipped|Obsolete|Cancelled} Actions — Index

Actions resolved with outcome `{done|skipped|obsolete|cancelled}` ({description suffix}).

**Quick status:** 0 {completed|skipped|obsolete|cancelled} actions

---

| ID | Description | Owner | Resolved | Note |
| --- | --- | --- | --- | --- |

_No {done|skipped|obsolete|cancelled} actions._

<!-- Example of a populated row (ID is a markdown link; Resolved is a date):
| [A-019e…](./A-019e….md) | Replace inline style with Tailwind class in error.tsx | Franck Boullier | 2026-06-01 | Done — verified build. |
-->
