---
name: add-front-matter
description: Add or update MAGI-compliant YAML front matter on a markdown file so AI agents can discover and classify it. Usage: /add-front-matter [file-path]
argument-hint: [file-path]
---

# /add-front-matter

Add or update MAGI-compliant YAML front matter on a markdown file so AI agents
and indexing tools can discover, classify, and retrieve it without reading the
full body. The document body is never modified.

## Usage

```bash
/add-front-matter knowledge-base/business-continuity-plan/README.md
/add-front-matter        # uses the file currently open in the editor
```

## Behaviour

Use the skill `format-md-for-progressive-disclosure` to add or update the front
matter on the file: $ARGUMENTS

If no file path is provided in the arguments, use the markdown file currently
open in the editor. If neither is available, ask the user which file to process.

## Skill Reference

- `format-md-for-progressive-disclosure`
