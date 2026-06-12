---
name: format-md-for-progressive-disclosure
description: Adds or updates MAGI-compliant YAML front matter in markdown files so AI agents and indexing tools can discover, classify, and retrieve documents without reading the full body. Use this skill whenever the user wants to add front matter to a markdown file, make a markdown file discoverable by AI agents, tag or describe a file for agentic retrieval, prepare documents for progressive discovery, or update existing front matter metadata. Also trigger when the user mentions "front matter", "MAGI", "progressive discovery metadata", or asks to enrich a .md file with structured metadata — even if they don't use those exact terms.
---

# Formatting Markdown Documents for Progressive Discovery

Add a MAGI-compliant YAML front matter block to a markdown file so that AI
agents and indexing tools can discover and classify the document at Layer 1
(metadata scan) without loading the full body. If front matter already exists,
review and update it — never replace it wholesale. The document body is never
modified.

## Before you start

Read the field schema reference to understand the exact fields, types, and
validation rules you'll be working with:

- **Field definitions and types:** [references/magi-field-schema.md](references/magi-field-schema.md) — read this before generating any front matter.
- **Writing guidance and pitfall avoidance:** [references/front-matter-engineering-guide.md](references/front-matter-engineering-guide.md) — read this before inferring any field values to ensure accurate descriptions, correct tag coverage, and pitfall avoidance.

---

## Input requirements

**Required:** A markdown file the user explicitly referenced (by path, filename,
or `@mention`). Do not assume the currently open file unless the user says so.

**Optional:** Context hints from the user (e.g., "this is for junior developers",
"treat this as a reference document"). When provided, these hints override any
values inferred from the file content.

If the user does not provide a file reference, ask for one before proceeding.

---

## Execution flow

Follow these seven steps in order. Do not skip or reorder steps.

### Step 1 — Read the target file

Load the full content of the markdown file the user referenced. If the file does
not exist at the specified path, report the error and stop — do not create a new
file.

### Step 2 — Check for existing front matter

Look for a YAML block between opening and closing `---` delimiters at the top of
the file. If present, parse it and note which fields already exist and their
current values. If absent, treat front matter as empty.

### Step 3 — Read the field schema

Read [references/magi-field-schema.md](references/magi-field-schema.md) to load
the complete field definitions, types, and validation rules. This ensures you
generate fields that conform to the MAGI specification.

### Step 4 — Analyse the document body

Read [references/front-matter-engineering-guide.md](references/front-matter-engineering-guide.md)
for description writing guidance, tag selection strategy, and the common pitfalls table before
inferring any values below.

Read the content below the front matter (or the entire file if no front matter
exists) and infer:

- **Subject matter** — what is this document about?
- **Purpose** — is it a tutorial, reference, guide, specification, constraint, report, or overview?
- **Audience** — who is the intended reader? (only if confidently inferable from tone and vocabulary)
- **Key concepts** — what are the 3-6 core ideas or entities discussed?
- **Named entities** — what tools, frameworks, systems, or people are meaningfully discussed?
- **Tags** — what 3-8 keywords would help an agent find this document via faceted search?

For each of these, assess your confidence. If you cannot confidently infer a
value, mark it for a `# TODO` placeholder — a placeholder is always preferable
to a guess.

### Step 5 — Apply user hints

If the user provided context hints, override the corresponding inferred values.
User hints always take priority over content analysis.

### Step 6 — Generate or update the front matter block

Produce the YAML front matter according to these rules:

**For new front matter:**

- Generate a fresh UUID v7 for `doc-id`
- Set `last-updated` to today's date
- Include all mandatory fields (`doc-id`, `title`, `description`, `purpose`, `tags`, `last-updated`)
- Include recommended fields (`key_concepts`, `audience`) when confidently inferred
- Include optional fields (`entities`) only when they add genuine discovery value
- Use `# TODO: add [field-name]` for any field you cannot fill confidently

**For existing front matter:**

- Preserve the existing `doc-id` exactly — never generate a new one
- Preserve existing field values unless a user hint explicitly overrides them
- Add any mandatory or recommended fields that are missing
- Update `last-updated` to today's date
- Merge new and existing fields — the result should be the union, not a replacement

### Step 7 — Write the file and report

Write the enriched file back to the same path:

- Prepend the front matter block (new) or replace only the existing front matter
  block (update)
- Leave the document body completely unchanged — not a single character modified

Then display the generated or updated front matter block inline so the user can
review what was added or changed.

---

## Constraints

These rules protect document integrity and metadata quality:

- **Body is read-only.** Only the YAML front matter block (between the opening
  and closing `---` delimiters) may be changed. Everything below the closing
  `---` must remain byte-for-byte identical.
- **`doc-id` is immutable.** If a `doc-id` already exists, preserve it exactly.
  Only generate a new UUID when no `doc-id` is present.
- **Placeholders over guesses.** If a field value cannot be confidently inferred,
  use `# TODO: add [field-name]`. Agents trust metadata — wrong values actively
  mislead retrieval and classification.
- **`last-updated` is always today.** Set it to the current date (YYYY-MM-DD) on
  every run, whether creating or updating.
- **Same file, no copies.** Write the output back to the input file path. Do not
  create a new file or a copy.

---

## Edge cases

| Situation | What to do |
| --- | --- |
| File already has front matter | Parse existing fields, add missing ones, update `last-updated`, merge. Do not discard existing values unless a user hint overrides them. |
| Field cannot be confidently inferred | Insert `# TODO: add [field-name]` and continue. |
| File does not exist | Report the error to the user and stop. Do not create a new file. |
| User hint conflicts with existing value | User hint takes priority. Use the hint value. |
| File has no headings or minimal content | Infer what you can from the content available. Use `# TODO` for anything uncertain. A short file may still have a clear subject. |
| Front matter contains non-MAGI fields | Preserve them. The skill adds MAGI fields alongside any existing custom fields. |

---

## Example

**Input file** (`notes/deployment-guide.md`):

```markdown
# Deploying to AWS ECS

This guide walks through deploying a containerised Python app...
```

**User prompt:** "Add front matter to notes/deployment-guide.md — this is intended for senior DevOps engineers"

**Output front matter:**

```yaml
---
doc-id: 550e8400-e29b-41d4-a716-446655440000
title: Deploying to AWS ECS
description: Step-by-step guide to deploying containerised Python applications on AWS ECS, covering task definitions, service configuration, and CI/CD integration.
purpose: guide
tags:
  - aws-ecs
  - docker
  - deployment
  - python
  - ci-cd
key_concepts:
  - container-orchestration
  - task-definitions
  - service-configuration
  - fargate
audience: senior-devops-engineer
entities:
  - AWS ECS
  - Docker
  - Python
  - Fargate
last-updated: 2026-04-01
---
```

The document body below the closing `---` remains unchanged.
