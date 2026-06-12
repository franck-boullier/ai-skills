---
title: Compaction Rules — Per-Store Operations and Templates
description: >-
  Distilled reference for compact-topical-memories. Defines type-specific merge,
  archive, and prune conditions for all seven Tier 2 stores; sub-folder handling
  for decisions/, projects/, and activities/; archive naming conventions; and
  the analysis entry template for lesson-pattern promotions.
purpose: reference
tags:
  - compaction-rules
  - merge
  - archive
  - prune
  - analysis-template
  - sub-folder
audience: ai-agent
last-updated: 2026-04-05
---

# Compaction Rules — Per-Store Operations and Templates

## Type-Specific Compaction Rules

Apply these conditions during Step 2 (audit) to build each store's work list.

| Store | Merge condition | Archive condition | Prune condition | Special constraints |
|-------|----------------|-------------------|-----------------|---------------------|
| `decisions/` | Multiple entries amend the same decision (revision notes, implementation updates). | Entry explicitly marked `status: superseded` by a newer decision. | Past retention date AND explicitly permitted by RULES.md. | **Never discard reasoning.** Archive entire sub-folder to `decisions/archive/`. Successor decision must link to archived entry. |
| `projects/` | Multiple incremental update files for the same project. | `status: completed` or `status: abandoned`. | None — projects are archived, not pruned. | Archive entire sub-folder to `projects/archive/`. Update `projects/README.md`. |
| `activities/` | Multiple incremental update files for the same activity. | `status: completed`. | None — activities are archived, not pruned. | Archive entire sub-folder to `activities/archive/`. Update `activities/README.md`. |
| `lessons/` | 3+ lessons share the same root cause or theme; OR 2 near-identical lessons. Two lessons share a theme when: they share ≥ 2 tags, root-cause fields match, or semantic review identifies the same recurring mistake. | None (lessons are permanent unless explicitly expired). | Past retention date AND permitted by RULES.md. | When merging themed lessons, create a new `analysis/` entry documenting the pattern. See **Analysis Entry Template** below. Link the merged lesson to the new analysis. |
| `preferences/` | Duplicate entries stating the same preference. | Preference explicitly superseded by a newer entry. | Past retention date AND permitted by RULES.md. | Contradictions require human resolution before archiving the older entry. |
| `people/` | Duplicate contact entries for the same person. | `status: inactive` or `status: departed`. | Past retention date AND permitted by RULES.md — check PII policy first. | PII sensitivity: always check the `retention` frontmatter field. Never delete without an explicit retention policy. Missing `retention` → treat as permanent. |
| `analysis/` | Related analyses on the same topic or time period. | Explicitly superseded by a newer analysis. | Past retention date AND permitted by RULES.md. | Never discard key findings. When summarizing a verbose analysis, preserve the conclusions section verbatim. |

## Sub-folder Handling (decisions/, projects/, activities/)

These stores use a sub-folder structure. Apply the following conventions:

### Archive operation

Move the **entire sub-folder** to `[store]/archive/<name>/`. Do not move only the `README.md`.

```text
# Example: archiving a completed project
BEFORE: memory/projects/dashboard-redesign/
AFTER:  memory/projects/archive/dashboard-redesign/
```

### Merge operation

Consolidate incremental detail files into the sub-folder's `README.md`. Delete
the source detail files from the sub-folder after merging. Invoke
`format-md-for-progressive-disclosure` on the updated `README.md`.

### README update

Update the store's root `README.md` after every archive or merge to reflect
the structural change. Active entries link to active sub-folders; archived
entries link to `archive/<name>/README.md`.

## Archive Naming Conventions

- Retain the source name unchanged — do not add date prefixes.
- The `last-updated` front matter field provides the date.
- If a name conflict exists in `archive/`, append a numeric suffix: `-02`, `-03`, etc.
- Log conflicts in the compaction report.

## Compaction Operations — Step-by-Step

### Merge related entries

1. Read all entries to be merged.
2. Write a consolidated entry that preserves the complete narrative.
   - Retain the **oldest `doc-id`** and **oldest `created` date** from source entries.
   - Do not lose any decision reasoning, lesson content, or preference detail.
3. Delete or archive the source entries (follow RULES.md deletion policy).
4. Update the store's `README.md` to reflect the consolidated entry.
5. Invoke `format-md-for-progressive-disclosure` on the consolidated file.

### Archive lifecycle-complete entries

1. Move the file or sub-folder to `[store]/archive/`.
2. Create `[store]/archive/README.md` if it does not exist.
3. Update the store's root `README.md`: move the pointer from active to archived.
4. Invoke `format-md-for-progressive-disclosure` on the archived file's updated front matter.

### Prune expired entries

1. If RULES.md requires human approval: present the list of expired entries to the user.
   Wait for explicit confirmation before deleting anything.
2. If RULES.md permits autonomous pruning for this category: proceed without asking.
3. Log each deletion in the compaction report (file path, retention date, authorization source).

## Analysis Entry Template (Lesson-Pattern Promotions)

When 3+ lessons (or 2 near-identical lessons) share a theme, create a new
`analysis/` entry documenting the recurring pattern.

**Filename format:** `memory/analysis/YYYY-MM-<slug>.md`
(use today's date and a kebab-case slug describing the pattern)

**Required front matter fields** (populated by `format-md-for-progressive-disclosure`
after writing the body):

```yaml
doc-id: <uuid>
title: <pattern title>
description: <one-sentence summary of the recurring pattern>
status: active
category: pattern
tags:
  - <shared tag from source lessons>
  - <...>
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
```

**Required body sections:**

```markdown
## Pattern Identified

<1–3 sentences describing the recurring theme.>

## Root Cause

<The underlying cause, if identifiable. "Unknown" is acceptable if not clear.>

## Lessons Merged

- [lesson-file-01.md](../lessons/lesson-file-01.md)
- [lesson-file-02.md](../lessons/lesson-file-02.md)
- ...

## Recurrence Count

<N lessons matched this pattern.>

## Recommendations

<What to do differently going forward. Actionable, specific.>
```

After writing the body, invoke `format-md-for-progressive-disclosure` to generate
full MAGI-compliant front matter. Then link the merged lesson file to the new
analysis entry.
