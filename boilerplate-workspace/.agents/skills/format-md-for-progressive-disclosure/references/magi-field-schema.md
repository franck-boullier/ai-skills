---
name: magi-field-schema
description: MAGI front matter field definitions, types, requirements, and validation rules for progressive discovery metadata.
last-updated: 2026-04-01
---

# MAGI Front Matter Field Schema

This reference defines the complete field schema for MAGI-compliant YAML front
matter blocks. The skill's SKILL.md references this file when field-level detail
is needed during generation or update.

## Table of Contents

- [Mandatory Fields](#mandatory-fields)
- [Recommended Fields](#recommended-fields)
- [Optional Fields](#optional-fields)
- [Field Validation Rules](#field-validation-rules)
- [TODO Placeholder Format](#todo-placeholder-format)

---

## Mandatory Fields

These fields must appear in every front matter block. If a value cannot be
confidently determined, use a `# TODO` placeholder rather than guessing.

| Field          | Type   | Description                                                      | Generation Rule                                                        |
| -------------- | ------ | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `doc-id`       | string | A UUID v7 uniquely identifying the document.                     | Generate fresh if absent. Never modify an existing value.              |
| `title`        | string | The primary name of the document.                                | Infer from the first H1 heading, filename, or content summary.        |
| `description`  | string | A concise abstract (1-3 sentences) used during discovery.        | Summarise the document's core subject and utility in discovery terms.  |
| `purpose`      | string | The document's objective category.                               | Choose from: `tutorial`, `reference`, `constraint`, `guide`, `specification`, `report`, `overview`, or a similarly descriptive term. |
| `tags`         | list   | Keywords for classification and faceted filtering.               | Extract 3-8 keywords covering the main topics, technologies, and domains. |
| `last-updated` | string | ISO 8601 date (YYYY-MM-DD) of the most recent update.           | Always set to today's date on every run.                               |

### Field details

**doc-id** — The stable anchor for relational references between documents. Use
UUID v7 format (e.g., `550e8400-e29b-41d4-a716-446655440000`). Once assigned,
this value is immutable across all future updates.

**title** — Should reflect what the document *is about*, not its filename. If the
file has no H1 heading and the filename is cryptic (e.g., `notes-2.md`), infer
a descriptive title from the content or use a `# TODO` placeholder.

**description** — This is the single most important field for progressive
discovery. Agents read descriptions to decide whether to load the full document.
Write it as if answering: "Why would an agent or human need this file?" Avoid
vague phrases like "contains information about" — be specific about what the
document enables.

**purpose** — Categorises the document's role in a knowledge system. Common
values and when to use them:

| Value           | Use when the document...                                       |
| --------------- | -------------------------------------------------------------- |
| `tutorial`      | teaches through step-by-step instructions                      |
| `reference`     | provides lookup information (API specs, schemas, tables)       |
| `constraint`    | defines rules, policies, or guardrails                         |
| `guide`         | explains best practices or recommended approaches              |
| `specification` | formally defines a system, format, or protocol                 |
| `report`        | presents findings, analysis, or metrics                        |
| `overview`      | introduces a topic at a high level                             |

If none of the common values fit, use a short descriptive term that an agent
could filter on.

**tags** — Think of these as search facets. Include the primary domain (e.g.,
`context-engineering`), key technologies (e.g., `yaml`, `markdown`), and
functional descriptors (e.g., `metadata`, `front-matter`). Avoid tags that are
too broad (`software`) or too narrow (`line-42-fix`).

---

## Recommended Fields

Include these when the content provides enough signal to fill them confidently.

| Field          | Type   | Description                                                      | Generation Rule                                                        |
| -------------- | ------ | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `key_concepts` | list   | High-level entities or ideas discussed in the document.          | Extract 3-6 core concepts that summarise the document's intellectual territory. |
| `audience`     | string | The intended consumer of the document.                           | Infer from tone, vocabulary, and assumed prerequisite knowledge.       |

### Field details

**key_concepts** — These are the "nouns" of the document. For a document about
progressive discovery, concepts might include `progressive-disclosure`,
`context-window-economy`, `MAGI-front-matter`, `agentic-RAG`. Use lowercase
hyphenated form for consistency.

**audience** — Common values: `ai-agent`, `developer`, `senior-developer`,
`junior-developer`, `data-engineer`, `technical-writer`, `non-technical`. When
the document addresses multiple audiences, pick the primary one.

---

## Optional Fields

Include these only when they add genuine discovery value.

| Field      | Type | Description                                                          | Generation Rule                                                        |
| ---------- | ---- | -------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `entities` | list | Named entities (people, tools, systems, frameworks) in the document. | Extract proper nouns that an agent might search for — tool names, framework names, protocol names. |

### Field details

**entities** — These help agents find documents that mention specific
technologies or systems. For example: `Neo4j`, `Claude`, `MCP`,
`LangGraph`. Only include entities that are meaningfully discussed, not just
mentioned in passing.

---

## Field Validation Rules

| Rule                                         | Applies to     |
| -------------------------------------------- | -------------- |
| Never empty — use `# TODO` if unknown        | All fields     |
| UUID v7 format                               | `doc-id`       |
| ISO 8601 date (YYYY-MM-DD)                   | `last-updated` |
| 1-3 sentences, no filler phrases             | `description`  |
| 3-8 items, lowercase hyphenated              | `tags`         |
| 3-6 items, lowercase hyphenated              | `key_concepts` |
| Single value from controlled vocabulary      | `purpose`      |
| Proper noun casing preserved                 | `entities`     |

---

## TODO Placeholder Format

When a field value cannot be confidently inferred:

```yaml
field_name: # TODO: add [field-name]
```

Examples:

```yaml
audience: # TODO: add audience
entities: # TODO: add entities
```

A placeholder is always preferable to a hallucinated value. The user can fill
these in later, and automated tools can scan for `# TODO` markers to identify
incomplete metadata.
