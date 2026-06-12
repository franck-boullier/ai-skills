---
name: compact-agent-daily-memories
description: >-
  Reorganizes an agent's memory/daily/ folder into a progressively nested hierarchy
  of monthly (YYYY-MM/) and quarterly (YYYY-QN/) sub-folders, each anchored by a
  synthesized summary README.md. Keeps the memory/daily/README.md entry point
  small and navigable regardless of how many session logs have accumulated.
  Trigger when: flat daily files for a completed calendar month are still at
  memory/daily/ root; monthly folders for a completed quarter are not yet folded
  into a YYYY-QN/ folder; the user says "reorganize daily logs", "archive last
  month's logs", "compact this agent's daily memory", or "reorganize daily logs
  for [agent-name]". Scoped to exactly one agent per run — always ask which
  agent if ambiguous. Hard dependency on format-md-for-progressive-disclosure.
  Does not touch MEMORY.md, topical stores, or any other agent's files.
compatibility: >-
  Requires file-system access, MCP tool support, and the
  format-md-for-progressive-disclosure sub-skill (see Step 0).
  Git recommended for rollback.
metadata:
  author: fbo
  version: "0.1-draft"
  status: draft
  skill-target: compact-agent-daily-memories
---

# Compact Agent Daily Memory

Reorganize `memory/daily/` into a progressively nested hierarchy of monthly and
quarterly sub-folders. Each sub-folder is anchored by a synthesized `README.md`
that distills the period's signal, so the `memory/daily/README.md` entry point
stays small regardless of how many sessions have accumulated.

This skill handles **daily logs only**. It never touches `MEMORY.md`, topical
stores (`decisions/`, `projects/`, `lessons/`, etc.), or any other agent's files.

See `references/daily-log-architecture.md` for folder structure and README templates.
See `references/constraint-vocabulary.md` for the ALWAYS / NEVER framework.

---

## Step 0 — Pre-flight: verify required sub-skill

Before any other action, complete both checks below:

**Check A — required sub-skill:**

| Sub-skill | Expected path |
|-----------|---------------|
| `format-md-for-progressive-disclosure` | `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/SKILL.md` |

**Check B — MCP backend discovery:** Query the MCP tool listing and cache the result. This cached list is used at Step 5 to select the highest-priority available backend. See `references/mcp-backend-routing.md` for the priority order and introspection method. Do not repeat this query later in the run — use the cached result.

**If sub-skill is present and backend discovery succeeded:** proceed to Step 1.

**If missing:** halt immediately and display:

> **`compact-agent-daily-memories` cannot run — required sub-skill missing.**
>
> - **`format-md-for-progressive-disclosure`**
>   Expected: `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/SKILL.md`
>
> **Why required:** Monthly and quarterly README files are the navigation nodes of
> the daily log hierarchy. Without MAGI-compliant front matter, agents cannot
> discover or traverse those nodes — the progressive disclosure chain breaks silently.
>
> **To install:** copy the skill folder from
> `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/`
> and place `SKILL.md` at the path shown above. Then re-run `compact-agent-daily-memories`.

---

## Step 1 — Load synthesis context

Read `SOUL.md` from the agent's root directory to establish the **memory policy**
that guides what counts as signal in synthesized summaries.

**Exception:** when invoked by the `compact-memories` orchestrator, `SOUL.md` is
already in the active conversation context. Use it from there — do not re-read
from disk.

If `SOUL.md` is missing or unreadable: warn the user, then proceed with
best-effort synthesis (bias toward decisions, lessons, and environment changes).

See `references/soul-memory-policy.md` for how to apply memory-policy content
when writing summaries.

---

## Step 2 — Audit memory/daily/

1. List all flat `YYYY-MM-DD.md` files in `memory/daily/`.
2. List all existing `YYYY-MM/` and `YYYY-QN/` sub-folders.
3. Identify which reorganizations are due:
   - **Monthly:** flat daily files whose month is earlier than the current calendar month.
   - **Quarterly:** monthly sub-folders whose quarter is earlier than the current calendar quarter.
4. If nothing is due, skip Steps 3–5 and go directly to Step 6 (report).

---

## Step 3 — Monthly reorganization (run when due)

For each completed calendar month M whose daily files are still flat in `memory/daily/`:

1. Identify all `YYYY-MM-DD.md` files belonging to month M.
2. Create `memory/daily/YYYY-MM/` sub-folder.
3. Move all identified daily files into `memory/daily/YYYY-MM/`.
4. Write `memory/daily/YYYY-MM/README.md` **body only** (no front matter yet):
   - **Synthesized summary** — key decisions, lessons, preference changes, notable
     patterns, and environment changes during the month. Guided by `SOUL.md`
     memory policy. Do not reproduce daily entries verbatim; capture the signal.
     Note any gaps (missing or unreadable daily files) explicitly in the summary.
   - **Daily index** — links to each moved daily file, most-recent first:

     ```markdown
     ## Daily Entries

     - [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>
     ```

5. Invoke `format-md-for-progressive-disclosure` on the new `README.md` with
   context hint: `"Monthly memory summary for period YYYY-MM. Category: daily-log-monthly. Audience: ai-agent."`
6. Update `memory/daily/README.md`: replace the individual daily links for
   month M with a single line:

   ```markdown
   - [YYYY-MM](YYYY-MM/README.md) — <one-sentence month description>
   ```

---

## Step 4 — Quarterly reorganization (run when due)

For each completed calendar quarter Q whose monthly sub-folders are still directly
inside `memory/daily/`:

1. Identify all `YYYY-MM/` sub-folders belonging to quarter Q.
2. Create `memory/daily/YYYY-QN/` folder (e.g. `2026-Q1/`).
3. Move all identified monthly sub-folders into `memory/daily/YYYY-QN/`.
4. Write `memory/daily/YYYY-QN/README.md` **body only** (no front matter yet):
   - **Synthesized summary** — major decisions of the quarter, dominant lessons,
     significant preference or environment shifts, cross-month patterns.
     **Derive from monthly `README.md` summaries only** — do not re-read individual
     daily files.
   - **Monthly index** — links to each monthly sub-folder:

     ```markdown
     ## Monthly Summaries

     - [YYYY-MM](YYYY-MM/README.md) — <one-sentence month description>
     - [YYYY-MM](YYYY-MM/README.md) — <one-sentence month description>
     - [YYYY-MM](YYYY-MM/README.md) — <one-sentence month description>
     ```

5. Invoke `format-md-for-progressive-disclosure` on the new `README.md` with
   context hint: `"Quarterly memory summary for period YYYY-QN. Category: daily-log-quarterly. Audience: ai-agent."`
6. Update `memory/daily/README.md`: replace the monthly folder links for
   quarter Q with a single line:

   ```markdown
   - [YYYY-QN](YYYY-QN/README.md) — <one-sentence quarter description>
   ```

---

## Step 5 — Write all changes

Using the highest-priority available MCP backend (see `references/mcp-backend-routing.md`):

1. Write all new and modified files produced in Steps 3–4.
2. Write the updated `memory/daily/README.md`.

**On write failure:** roll back the current batch so `memory/daily/` is not left
partially reorganized. See `references/mcp-backend-routing.md` for the git-based
and no-git rollback procedures. Log all failed paths in the Step 6 report.

---

## Step 6 — Report

Provide a plain-text reorganization report. Always include:

- Monthly folders created and periods covered (or "none created").
- Quarterly folders created and periods covered (or "none created").
- Any gaps (missing daily files within a reorganized month).
- Paths that failed during write (if any), with rollback outcome.
- When nothing was due: `"Daily memory is up to date — no reorganization needed."`

---

## Non-Negotiable Constraints

See `references/constraint-vocabulary.md` for the full ALWAYS / NEVER / ASK BEFORE
framework. Key constraints:

- **NEVER delete a daily log file.** Move into `YYYY-MM/` — never destroy.
- **NEVER fabricate summary content.** If a daily file is missing, acknowledge the gap.
- **NEVER re-read individual daily files at quarterly synthesis.** Use monthly READMEs only.
- **NEVER modify `MEMORY.md`.** The bootstrap pointer is immutable from this skill's scope.
- **NEVER touch topical stores** (`decisions/`, `projects/`, `lessons/`, etc.).
- **NEVER reorganize multiple agents** without explicit per-agent user confirmation.
- **ALWAYS invoke `format-md-for-progressive-disclosure`** after writing any README body.
- **ALWAYS log every move, folder creation, and write** in the Step 6 report.
- **ASK BEFORE proceeding** when the target agent is ambiguous.

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Sub-skill missing at Step 0 | Halt immediately; display install instructions. |
| No reorganization due | Steps 0–2 and Step 6 run; Steps 3–5 skipped. Report "up to date". |
| Daily file missing within a month being reorganized | Create the folder, proceed, note the gap in the monthly summary. |
| `SOUL.md` missing or unreadable | Warn the user; proceed with best-effort synthesis. |
| Write fails during reorganization | Roll back the batch (git or halt-and-list); log failed paths in report. |
| More than one agent could apply | Ask which agent before Step 0; do not guess. |

---

## Sub-skills

| Sub-skill | Status | Expected path | When invoked |
|-----------|--------|---------------|--------------|
| `format-md-for-progressive-disclosure` | **Required** | `skills/skills-libraries/fbo-skills/utility-skills/format-md-for-progressive-disclosure/SKILL.md` | Step 3.5 (monthly README) and Step 4.5 (quarterly README). |

---

## Reference files

- `references/daily-log-architecture.md` — Folder hierarchy, MEMORY.md constraints, README state templates, MAGI requirement. Read at Steps 2–4.
- `references/soul-memory-policy.md` — How to use SOUL.md memory-policy to guide synthesis; orchestrator vs. direct invocation; fallback behavior. Read at Step 1.
- `references/mcp-backend-routing.md` — Backend priority order, introspection method, per-backend write operations, rollback strategy. Read at Step 5.
- `references/constraint-vocabulary.md` — ALWAYS / NEVER / ASK BEFORE framework and skill-specific constraints. Read before any execution.

---

## See also

- `skill-compact-memories` — Orchestrator that invokes this skill as part of full memory maintenance.
- `skill-compact-topical-memories` — Companion skill that compacts decisions, projects, lessons, and other topical stores.
- `skill-save-agent-memory` — Writes daily log files and updates `memory/daily/README.md` during a session.
