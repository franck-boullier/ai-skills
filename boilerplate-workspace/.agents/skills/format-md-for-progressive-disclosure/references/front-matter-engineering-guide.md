---
name: front-matter-engineering-guide
description: Best practices for writing and updating YAML front matter for progressive discovery, drawn from context engineering and agentic RAG research.
last-updated: 2026-04-01
---

# Front Matter Engineering Guide

Practical guidance for generating high-quality front matter that maximises
document discoverability by AI agents and indexing systems.

## Table of Contents

- [Why Front Matter Matters](#why-front-matter-matters)
- [Writing Effective Descriptions](#writing-effective-descriptions)
- [Tag Selection Strategy](#tag-selection-strategy)
- [Handling Existing Front Matter](#handling-existing-front-matter)
- [Common Pitfalls](#common-pitfalls)

---

## Why Front Matter Matters

Front matter is the "spine" of a document in a progressive discovery system.
Agents and indexing tools read it to determine relevance without parsing the full
body. In the three-layer discovery architecture:

1. **Layer 1 (Discovery)** — Agents scan metadata (title, description, tags) at
   startup. This costs ~50-100 tokens per document.
2. **Layer 2 (Activation)** — When a document matches, the agent loads its full
   content into the context window (~5,000 tokens).
3. **Layer 3 (Deep Dive)** — The agent reads linked reference files only when
   needed (unlimited tokens, loaded on demand).

Well-engineered front matter ensures that Layer 1 filtering is accurate — the
right documents surface for the right tasks, and irrelevant documents stay out
of the context window.

---

## Writing Effective Descriptions

The `description` field is the single highest-impact field for discovery. An
agent deciding whether to load a 3,000-token document will base that decision
almost entirely on the description.

**Do:**
- Answer "what does this document help someone do?"
- Include the primary subject and the document's functional role
- Use concrete, specific language

**Don't:**
- Start with "This document..." (the context already implies it)
- Use vague phrases: "contains information about", "discusses various aspects of"
- Repeat the title verbatim as the description

**Examples:**

Weak:
> Contains information about deploying applications to the cloud.

Strong:
> Step-by-step guide to deploying containerised Python applications on AWS ECS
> using Fargate, including IAM role configuration and CI/CD pipeline setup.

---

## Tag Selection Strategy

Tags serve as faceted search filters. Think of them as the dimensions by which
someone (human or agent) might search for this document.

**Selection heuristic:** For each candidate tag, ask: "Would an agent searching
for this term expect to find this document?" If yes, include it.

**Coverage targets:**
- 1-2 tags for the primary domain (e.g., `devops`, `context-engineering`)
- 1-2 tags for key technologies (e.g., `docker`, `yaml`)
- 1-2 tags for functional role (e.g., `tutorial`, `troubleshooting`)
- 0-2 tags for audience or level (e.g., `beginner`, `enterprise`)

**Format:** Lowercase, hyphenated. Prefer established terms over invented ones.

---

## Handling Existing Front Matter

When a document already has a YAML front matter block:

1. **Parse the existing block** — extract all current fields and their values.
2. **Preserve `doc-id`** — never modify an existing UUID.
3. **Preserve existing values** — do not overwrite fields that already have
   valid, non-placeholder content unless a user hint explicitly overrides them.
4. **Add missing fields** — check the schema and add any mandatory or
   recommended fields that are absent.
5. **Update `last-updated`** — always set to today's date.
6. **Merge, don't replace** — the output should be the union of existing and
   new fields, not a wholesale replacement.

**Conflict resolution:** If an existing field value contradicts what the content
analysis suggests, keep the existing value. The assumption is that a human
previously set it intentionally. Only override when the user explicitly provides
a hint that conflicts with the existing value — in that case, the user hint wins.

---

## Common Pitfalls

| Pitfall                                  | Why it's harmful                                            | Fix                                                        |
| ---------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------- |
| Guessing values for uncertain fields     | Agents trust metadata — wrong values mislead retrieval      | Use `# TODO` placeholders instead                          |
| Overly broad tags (`software`, `tech`)   | Everything matches, nothing is useful                       | Be specific: `python-asyncio`, `kubernetes-networking`     |
| Copying the H1 heading as the title      | Often the H1 is a decorative label, not a discovery title   | Write a descriptive title that conveys subject and scope   |
| Omitting `description` or making it tiny | Agents can't distinguish this doc from others in Layer 1    | Write 1-3 sentences that explain the document's utility    |
| Including formatting in field values     | YAML renders Markdown literally — bold/italic won't render  | Use plain text in all front matter values                  |
| Modifying the document body              | The skill's contract is front-matter-only changes           | Treat everything below the closing `---` as read-only      |
