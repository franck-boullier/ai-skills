---
title: decisions store (fixture)
description: Per-store README for the decisions/ subdirectory in the boilerplate-derived test fixture. Used by tests/validator.py V.3 presence check.
purpose: index
audience: ai-agent
last-updated: "2026-05-28"
---

# decisions/

Test fixture per-store README. The store holds decisions-related memory entries.

## File naming

- Topical entries: `YYYY-MM-DD-topic.md` (when relevant).
- Index: this file.

## Retention

Indefinite (compacted by `compact-agent-topical-memories` per workspace policy).

## Example entry

```markdown
---
doc-id: <uuid>
title: <topic>
last-updated: "YYYY-MM-DD"
---

# <topic>

Body.
```
