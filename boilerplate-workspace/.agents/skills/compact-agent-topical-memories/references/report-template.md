---
title: Compaction Report Template
description: >-
  Distilled reference for compact-agent-topical-memories. Defines the Markdown
  table structure for the Step 6 compaction report and the Step 3 contradiction
  table, with annotated column definitions and one example row each.
purpose: reference
tags:
  - report-template
  - compaction-report
  - contradiction-table
  - output-format
audience: ai-agent
last-updated: 2026-04-05
---

# Compaction Report Template

Two structured outputs are produced by this skill: the **compaction report**
(Step 6) and the **contradiction table** (Step 3). Use the templates below
exactly — do not invent new columns or reorder them.

---

## Compaction Report (Step 6)

One report covering all target stores. Render as a Markdown table.

### Column definitions

| Column | Content |
|--------|---------|
| **Store** | Store name, e.g. `decisions/`, `lessons/`, `analysis/` |
| **Action** | One of: `Merged`, `Archived`, `Pruned`, `Created`, `Skipped`, `No action` |
| **Entry** | Relative path of the entry acted on (e.g. `decisions/decision-auth-provider/`) or a range (`lessons/lesson-01.md … lesson-03.md`) for batch merges |
| **Result** | What now exists after the action: path of the consolidated file, `→ archive/`, `deleted`, or `no change` |
| **Notes** | Flags, conflicts, human-review items, or reason for skipping. Leave blank if none. |

### Template

```markdown
## Compaction Report — <agent-name> — <YYYY-MM-DD>

| Store | Action | Entry | Result | Notes |
|-------|--------|-------|--------|-------|
| `decisions/` | Archived | `decisions/decision-auth-provider/` | `→ decisions/archive/decision-auth-provider/` | Superseded by `decision-supabase-auth/` |
| `lessons/` | Merged | `lessons/lesson-staging-01.md`, `lessons/lesson-staging-02.md`, `lessons/lesson-staging-03.md` | `lessons/lesson-staging-deploy.md` | Pattern promoted to `analysis/2026-04-05-staging-failures.md` |
| `preferences/` | No action | — | — | 3 entries reviewed; no merge or prune criteria met |
| `people/` | Skipped | — | — | `people/` not found or empty |
| `analysis/` | Created | — | `analysis/2026-04-05-staging-failures.md` | Promoted from 3 merged `lessons/` entries |
| `projects/` | Archived | `projects/dashboard-redesign/` | `→ projects/archive/dashboard-redesign/` | `status: completed` |
| `activities/` | No action | — | — | All entries `status: active` |
```

### Summary footer

After the table, always append a one-line summary in this format:

```markdown
**Summary:** <N> actions taken across <M> stores
(<merges> merged, <archives> archived, <prunes> pruned, <creates> created).
<P> items require human review. <Q> contradictions pending resolution.
```

Example:

```markdown
**Summary:** 4 actions taken across 7 stores
(2 merged, 2 archived, 0 pruned, 1 created).
0 items require human review. 0 contradictions pending resolution.
```

---

## Contradiction Table (Step 3)

Produced before any write action when contradictions are detected. Render as
a Markdown table. Present this table and wait for user confirmation before
writing anything to the affected stores.

### Column definitions

| Column | Content |
|--------|---------|
| **Entry A** | Relative path of the first conflicting file |
| **Entry B** | Relative path of the second conflicting file (or `RULES.md` / `SOUL.md` if the conflict is with an identity file) |
| **Store** | Store that owns the conflict |
| **Nature of contradiction** | One sentence describing the specific conflict |
| **Recommended resolution** | Which entry should prevail and why (or "Defer to user" if unclear) |

### Template

```markdown
## Contradiction Table — <agent-name> — <YYYY-MM-DD>

Contradictions found. No write actions have been taken yet. Please resolve
each row before confirming that compaction should proceed.

| Entry A | Entry B | Store | Nature of contradiction | Recommended resolution |
|---------|---------|-------|------------------------|------------------------|
| `decisions/decision-auth-provider/README.md` | `decisions/decision-supabase-switch/README.md` | `decisions/` | Both record conflicting choices for the authentication provider on the same date | Keep `decision-supabase-switch/` (newer); archive `decision-auth-provider/` as superseded |

**Action required:** Confirm resolution for each row above before compaction proceeds.
```

---

## Diagnostic Mode Output (Steps 0–3 only)

When the skill is triggered in diagnostic mode, produce the **compaction work
list** (not the full report) and the contradiction table. Use this structure:

```markdown
## Diagnostic Report — <agent-name> — <YYYY-MM-DD>

> Diagnostic mode: no files have been written. Confirm to proceed with compaction.

### Compaction Work List

| Store | Candidate action | Entry | Reason |
|-------|-----------------|-------|--------|
| `decisions/` | Archive | `decisions/decision-auth-provider/` | `status: superseded` |
| `lessons/` | Merge | `lessons/lesson-staging-01.md`, `lessons/lesson-staging-02.md`, `lessons/lesson-staging-03.md` | 3 entries share theme `staging-deploy` (shared tags + matching root-cause) |

### Contradictions Found

<contradiction table or "None detected.">
```
