---
doc-id: 00000000-0000-7000-8000-000000000001
title: Fixture workspace MEMORY.md (boilerplate-derived canonical)
description: Test fixture mirroring the boilerplate's canonical workspace memory index. Used by tests/test_workspace_confirm_and_update.py to verify the structural validator's matching / missing-section / conflict-staged behaviour. Not a real workspace.
purpose: index
audience: humans-and-ai
root_prefix: memories/
shared_actions_root: memories/actions/
local_actions_root: null
tags:
  - memory
  - index
  - governance
  - fixture
key_concepts:
  - workspace-memory
  - memory-index
  - tiered-memory
  - record-decision-needed
  - record-decision-made
  - build-agent-memory
last-updated: "2026-05-28"
---

# Workspace Memory — fixture

## Memory Architecture

This file is the workspace memory index — shared by all agents in this fixture workspace. Storage backend: local filesystem (this fixture tree). Writing skills: `record-decision-needed`, `record-decision-made`, `record-action-needed`, `record-action-taken`, `save-agent-memories`. Compaction skills: `compact-agent-topical-memories`, `compact-agent-daily-memories`, `compact-agent-memories`. Setup skill: `build-agent-memory`.

## Source of truth boundaries

- Memory (what we decided / did / learned over time): `memories/`
- Codebase (the actual project under construction): `codebase/`
- Specifications: `specifications/`
- Documentation: `documentation/`

## Configuration files

- Decisions and action plans: `decisions.config.md` at workspace root.
- Actions: declared in this file's frontmatter (`shared_actions_root`).

## Decision records

- [decisions/README.md](decisions/README.md) — compacted decisions layer.
- [decision-records/README.md](decision-records/README.md) — raw audit trail (placeholder for the fixture).

## Action records

- [actions/README.md](actions/README.md) — pending and resolved actions.

## Compacted working layer

- [decisions/README.md](decisions/README.md) — compacted meta-decisions.
- [lessons/README.md](lessons/README.md) — reusable lessons.
- [preferences/README.md](preferences/README.md) — workspace behaviour preferences.

## Restart guides

- [restart-guides/README.md](restart-guides/README.md) — session handoff guides.

## Daily Logs

- [Daily log index](daily/README.md)

## Notes on writing

- Prefer creating new records over editing history (decisions).
- Summarise external content before storing it.
- Let the skills do the writes — don't hand-edit filenames or relocate files between subfolders.
