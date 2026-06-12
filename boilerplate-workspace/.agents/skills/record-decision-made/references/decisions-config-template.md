# decisions.config.md — Workspace Configuration Template

This file tells the `record-decision-made` and `record-decision-needed` skills where to write decision artefacts in this workspace and which naming conventions to follow. It is read at the start of every invocation of either skill; if it does not exist the skills fall back to defaults and prompt for essentials on first use.

A single `decisions.config.md` can declare multiple decision domains (e.g. `db-architecture`, `product`, `legal`). Each domain has its own folders, ID series, and heading conventions. The skills pick the correct domain from context in the conversation — or ask if ambiguous.

## Where to put this file

Check these locations, in order. The first one found wins:

1. Workspace root: `decisions.config.md`.
2. Hidden agents folder: `.agents/decisions.config.md`.
3. Per-project: `{project-folder}/decisions.config.md` when the conversation clearly scopes the decision to a sub-project.

## File shape

The file is a YAML document wrapped in a markdown code fence so it remains human-readable. The skills parse the YAML between the `---` fences.

```markdown
# Decisions configuration

This workspace uses the `record-decision-made` and `record-decision-needed` skills. The configuration below tells those skills where decisions live, how they are named, and how to distinguish final from temporary decisions.

---
# Default domain when the conversation does not disambiguate.
default_domain: db-architecture

domains:
  db-architecture:
    label: "Database Architecture"
    folders:
      # Parent closed-decisions folder. With closed_subfolders set, the skills
      # never write decision files directly here — the parent only holds
      # _index.md and README.md.
      closed: "strymin-portal/db-architecture-decisions"
      closed_subfolders:                  # Optional. Omit for legacy single-folder layouts.
        final: "final"                    # Closed decisions with no scheduled re-evaluation.
        temporary: "temporary"            # Closed decisions with a stated revisit-trigger.
      pending: "strymin-portal/db-architecture-decision-needed"
      # Parent action-plans folder. With action_plans_subfolders set, the
      # skills never write plan files directly here — only the parent _index.md
      # and README.md live at this path.
      action_plans: "strymin-portal/db-architecture-decision-action-plans"
      action_plans_subfolders:                # Optional. Omit for legacy single-folder layouts.
        active: "active"                      # status: Active — new plans land here on creation.
        paused: "paused"                      # status: Paused — work temporarily on hold.
        completed: "completed"                # status: Complete — every task is in `## Completed`.
        abandoned: "abandoned"                # status: Abandoned — plan dropped before completion.
    index_files:
      closed: "_index.md"                 # Parent index (cross-folder summary).
      closed_final: "final/_index.md"     # Sub-index inside final/ (used when closed_subfolders is set).
      closed_temporary: "temporary/_index.md"  # Sub-index inside temporary/ (used when closed_subfolders is set).
      pending: "_index.md"
      action_plans: "_index.md"           # Parent action-plans index (cross-folder log).
      # Per-status sub-indexes inside the action-plans folder (used when action_plans_subfolders is set).
      action_plans_active: "active/_index.md"
      action_plans_paused: "paused/_index.md"
      action_plans_completed: "completed/_index.md"
      action_plans_abandoned: "abandoned/_index.md"
    default_owner_role: "Database Architecture Owner"

    # Action-plan status vocabulary. Each value MUST have a matching entry in
    # folders.action_plans_subfolders when subfolders are declared.
    action_plan_statuses: [Active, Paused, Complete, Abandoned]

    # ----- Final-vs-temporary distinction -----
    decision_types:
      - final       # No scheduled re-evaluation; reversal requires a flag-series decision.
      - temporary   # Made deliberately for current phase; revisit at a known trigger.

    # The schema for the `revisit-trigger` field, REQUIRED on every closed
    # decision whose decision-type is `temporary` and FORBIDDEN on `final`.
    revisit_trigger_schema:
      match_default: any-of
      match_values: [any-of, all-of]
      types:
        phase:
          description: "Phase or milestone transition (e.g., 'Phase 2 kickoff'). Use when the trigger is the project's own roadmap."
          required_fields: [type, value]
        date:
          description: "Calendar date (YYYY-MM-DD). Use when the trigger is time-boxed independent of project state."
          required_fields: [type, value]
        threshold:
          description: "Quantitative threshold on a measurable metric. Use when the trigger fires once a measurable condition is breached."
          required_fields: [type, metric, operator, value]
          operator_values: [">", ">=", "<", "<=", "=="]
        external:
          description: "External event outside the team's control (vendor change, regulatory action, customer ask, near-miss incident)."
          required_fields: [type, value]
      optional_field: revisit-notes

    id_series:
      - prefix: "A"
        label: "Planning item"
        case: upper
        heading_form: dotted        # e.g. A.2 — used in the heading of the closed file
        filename_form: undotted     # e.g. A2 — used in the filename
        filename_pattern_closed: "{date}-{id}-{slug}.md"
        filename_pattern_pending: "{id}-{slug}.md"
        heading_pattern_closed: "## {date} — {id-dotted} {title}"
        heading_pattern_pending: "## ⚠️ {date} — {id-dotted} {title} — PENDING DECISION"
      - prefix: "B"
        label: "Fundamental closed early"
        case: upper
        heading_form: omit          # ID does not appear in the heading
        filename_form: undotted
        filename_pattern_closed: "{date}-{id}-{slug}.md"
        filename_pattern_pending: "{id}-{slug}.md"
        heading_pattern_closed: "## {date} — {title}"
        heading_pattern_pending: "## ⚠️ {date} — {title} — PENDING DECISION"
      - prefix: "flag"
        label: "Reversal of prior design"
        case: lower
        heading_form: omit
        filename_form: undotted
        filename_pattern_closed: "{date}-{id}-{slug}.md"
        filename_pattern_pending: "{id}-{slug}.md"
        heading_pattern_closed: "## {date} — {title}"
        heading_pattern_pending: "## ⚠️ {date} — {title} — PENDING DECISION"

  product:
    label: "Product"
    folders:
      closed: "product/decisions"
      closed_subfolders:
        final: "final"
        temporary: "temporary"
      pending: "product/decisions-pending"
      action_plans: "product/decision-action-plans"
      action_plans_subfolders:
        active: "active"
        paused: "paused"
        completed: "completed"
        abandoned: "abandoned"
    index_files:
      closed: "_index.md"
      closed_final: "final/_index.md"
      closed_temporary: "temporary/_index.md"
      pending: "_index.md"
      action_plans: "_index.md"
      action_plans_active: "active/_index.md"
      action_plans_paused: "paused/_index.md"
      action_plans_completed: "completed/_index.md"
      action_plans_abandoned: "abandoned/_index.md"
    default_owner_role: "Product Owner"
    decision_types: [final, temporary]
    action_plan_statuses: [Active, Paused, Complete, Abandoned]
    revisit_trigger_schema:
      match_default: any-of
      match_values: [any-of, all-of]
      types:
        phase: { description: "Phase boundary", required_fields: [type, value] }
        date: { description: "Calendar date", required_fields: [type, value] }
        threshold: { description: "Metric threshold", required_fields: [type, metric, operator, value], operator_values: [">", ">=", "<", "<=", "=="] }
        external: { description: "External event", required_fields: [type, value] }
      optional_field: revisit-notes
    id_series:
      - prefix: "P"
        label: "Product decision"
        case: upper
        heading_form: dotted
        filename_form: undotted
        filename_pattern_closed: "{date}-{id}-{slug}.md"
        filename_pattern_pending: "{id}-{slug}.md"
        heading_pattern_closed: "## {date} — {id-dotted} {title}"
        heading_pattern_pending: "## ⚠️ {date} — {id-dotted} {title} — PENDING DECISION"
---
```

## Field reference

`default_domain` — the domain used when the conversation does not make the domain explicit. If unset, the skills must ask which domain applies on every run where more than one is declared.

`domains.{key}.label` — human-readable name for the domain; used in index headings and when asking the user to disambiguate.

`domains.{key}.folders.closed` — path (relative to the workspace root) of the folder holding closed decision files. When `closed_subfolders` is also declared, this path holds only the parent `_index.md` and `README.md`; actual decision files live in the subfolders.

`domains.{key}.folders.closed_subfolders` — optional. Maps each value in `decision_types` to a relative subfolder under `closed`. Typical shape: `{ final: "final", temporary: "temporary" }`. Omit for legacy single-folder layouts (in which case all closed decisions land directly in `closed`, regardless of `decision-type`).

`domains.{key}.folders.pending` — path of the folder holding open-question files. Omit if this domain does not maintain a pending backlog.

`domains.{key}.folders.action_plans` — path of the folder holding per-decision action plans. When `action_plans_subfolders` is also declared, this path holds only the parent `_index.md` and `README.md`; actual plan files live in the lifecycle subfolders.

`domains.{key}.folders.action_plans_subfolders` — optional. Maps each value in `action_plan_statuses` to a relative subfolder under `action_plans`. Typical shape: `{ active: "active", paused: "paused", completed: "completed", abandoned: "abandoned" }`. Omit for legacy single-folder layouts (in which case all plans co-exist in the parent folder regardless of `status:`). When this block is set, the `record-decision-made` skill writes new plans into the `active` subfolder; status-change moves between subfolders are documented in the action-plans `README.md`.

`domains.{key}.index_files.closed` — filename of the parent closed index. Almost always `_index.md`.

`domains.{key}.index_files.closed_final` / `closed_temporary` — relative paths (from `closed`) to the per-subfolder indexes when `closed_subfolders` is declared. Typical: `final/_index.md`, `temporary/_index.md`.

`domains.{key}.index_files.pending` / `action_plans` — filename of the index in each respective folder. Almost always `_index.md`. When `action_plans_subfolders` is declared, the `action_plans` index file is the **parent** cross-folder index; per-status sub-indexes live at the paths declared in `action_plans_active` / `action_plans_paused` / `action_plans_completed` / `action_plans_abandoned`.

`domains.{key}.index_files.action_plans_active` / `action_plans_paused` / `action_plans_completed` / `action_plans_abandoned` — relative paths (from `action_plans`) to the per-status sub-indexes when `action_plans_subfolders` is declared. Typical: `active/_index.md`, `paused/_index.md`, `completed/_index.md`, `abandoned/_index.md`.

`domains.{key}.action_plan_statuses` — the vocabulary of `status:` values that the skills accept on action-plan files. Typically `[Active, Paused, Complete, Abandoned]`. Each value must have a matching entry in `action_plans_subfolders` when subfolders are declared.

`domains.{key}.decision_types` — the vocabulary of `decision-type` values that the skills accept on closed decision files. Typically `[final, temporary]`. Each value must have a matching entry in `closed_subfolders` if `closed_subfolders` is declared.

`domains.{key}.revisit_trigger_schema` — the schema for the `revisit-trigger` frontmatter block on `temporary` decisions. The skills validate every temporary file's frontmatter against this schema. The schema declares: the `match_default` (composition rule when multiple triggers exist), the allowed `match_values`, the allowed `types` (each with its `description` and `required_fields`), and the name of the optional free-text field (typically `revisit-notes`).

`domains.{key}.default_owner_role` — role name to suggest as the owner when the conversation does not name one. Use a role, not a person — people change, roles do not.

`domains.{key}.id_series[]` — list of ID series this domain uses. Each series declares:

`prefix` — the letter or word that precedes the integer (e.g. `A`, `B`, `flag`, `P`).

`label` — what this series is for. Helps the skill explain choices to the user.

`case` — `upper` or `lower`. Governs how the prefix is written in filenames and headings. Do n