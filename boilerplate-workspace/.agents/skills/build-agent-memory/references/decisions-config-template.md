---
title: decisions.config.md canonical template
description: The minimal but complete `decisions.config.md` template the `workspace-confirm-and-update` mode writes when V.4 detects the file is missing at workspace root. Declares the canonical ID series, the standard folder paths for decision records and action plans, and the placeholder header all derived projects fill during bootstrap.
audience: ai-agent
purpose: reference
last-updated: "2026-05-28"
---

# `decisions.config.md` — canonical template

Read this file when Step 1's V.4 check fires MISSING and the user accepts the additive-merge write. The output is written verbatim to `[MEMORY-ROOT]/decisions.config.md`, replacing the `[PROJECT-NAME]` placeholder with the workspace name confirmed at Step 0.

The template below is the smallest file that satisfies V.4:

- File exists at workspace root.
- Parseable as markdown with YAML frontmatter.
- Declares at least one domain (the `## ID series` section's bullet list).

Projects extend it during bootstrap by adding domain-specific ID series and folder paths. The validator never inspects those extensions — V.5 keeps the validator structural-only.

## Template

```markdown
---
title: Decisions configuration — [PROJECT-NAME]
description: Workspace configuration for the decision-records subsystem. Declares the ID series the workspace uses (A, B, flag — and any domain extensions) and the canonical folder paths for pending decisions, closed decisions (final + temporary), and paired action plans. Read by `record-decision-needed` and `record-decision-made` before every write.
purpose: configuration
audience: humans-and-ai
last-updated: "YYYY-MM-DD"
---

# Decisions configuration — [PROJECT-NAME]

## ID series

Each decision record carries an identifier of the form `<series>.<index>`. The series declared below are universal across the workspace; add new domain-specific series (`P` for product, `O` for organisational, `V` for vendor, `C` for compliance, etc.) here AND to the ID-series table in `memories/decision-records/list-decision-taken/_index.md` before the first record of that domain is written.

- A: Planning items — design decisions about product scope, phasing, milestones.
- B: Fundamentals closed early — bedrock architectural decisions taken at workspace setup that are not expected to change.
- flag: Reversals of prior design — decisions that explicitly supersede an earlier closed decision.

## Folder paths

- `memories/decision-records/list-decision-needed/` — pending decisions (awaiting closure).
- `memories/decision-records/list-decision-taken/final/` — closed decisions with no scheduled re-evaluation.
- `memories/decision-records/list-decision-taken/temporary/` — closed decisions made for the current phase, expected to be revisited at a known trigger (phase, date, threshold, or external event).
- `memories/decision-records/list-decision-action-plans/active/` — paired action plans actively being executed.
- `memories/decision-records/list-decision-action-plans/paused/` — paused action plans.
- `memories/decision-records/list-decision-action-plans/completed/` — completed action plans.
- `memories/decision-records/list-decision-action-plans/abandoned/` — abandoned action plans.

## Action-plan statuses

- **Active** — currently being executed.
- **Paused** — paused intentionally (e.g. blocked on an external dependency).
- **Complete** — every task is Done.
- **Abandoned** — decision was reversed or scope changed; the plan no longer applies.

## Naming conventions

- Decision records: `YYYY-MM-DD-<series>.<index>-<short-slug>.md` (e.g. `2026-05-19-A5-build-agent-memory-confirm-and-update-mode.md`).
- Paired action plans: `YYYY-MM-DD-<series>.<index>-action-plan.md`.

## Revisit-trigger schema (temporary closed decisions only)

When a decision is closed with `decision-type: temporary`, the frontmatter must include a `revisit-trigger` field whose value declares when the decision is to be re-evaluated:

- `phase: <name>` — revisit when the workspace exits a named phase.
- `date: YYYY-MM-DD` — revisit on a specific date.
- `threshold: <metric and value>` — revisit when a measurable threshold is crossed.
- `external-event: <description>` — revisit when an external event occurs.

## Path-safety rules

- Skills must resolve every link target via the `root_prefix` declared in `MEMORY.md` frontmatter — never hand-construct absolute paths.
- The folder paths above are workspace-root-relative; concatenate them with the workspace root, not with `root_prefix`.
```

## After writing

After this file is written, `format-md-for-progressive-disclosure` is called on it to refresh the MAGI frontmatter (see SKILL.md Sub-skills section). The placeholder values inside the template body (`[PROJECT-NAME]`, `YYYY-MM-DD`) are left for the user to fill at Step 8's review — the skill never invents project content.
