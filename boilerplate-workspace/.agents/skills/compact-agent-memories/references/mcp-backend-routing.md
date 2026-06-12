---
title: MCP Backend Routing — MEMORY.md Index Write
description: >-
  Distilled reference for compact-agent-memories. Covers backend priority order,
  runtime introspection, per-backend write operations for the MEMORY.md root
  index, and rollback strategy on write failure at Step 6.
purpose: reference
tags:
  - mcp
  - storage-backend
  - MEMORY.md
  - rollback
audience: ai-agent
---

# MCP Backend Routing — MEMORY.md Index Write

This reference applies to **Step 6** (rebuild and write `MEMORY.md`) and, transitively, to all file writes performed by the sub-skills during their execution. Backend selection is decided once at **Step 0 (pre-flight)** and cached — do not re-query mid-run.

## Priority Order

Select the **highest-priority backend that is currently active**.

| Priority | Category | Examples | When to choose |
|----------|----------|----------|---------------|
| 1 | Version-controlled store | GitHub, GitLab, Bitbucket MCP | Preferred — provides a full audit trail and single-command rollback. The memory system benefits most from this. |
| 2 | Cloud object storage | AWS S3, GCP GCS, Azure Blob, Cloudflare R2 | Enterprise-grade persistence. Rollback requires manual file restoration. |
| 3 | Document store | GCP Firestore, MongoDB, Supabase, DynamoDB | Use when structured querying of memory fragments is needed. |
| 4 | Local filesystem | Built-in file tools | Always available as the baseline fallback. |

If no explicit primary backend is configured, use the **local filesystem**.

## How to Introspect Available Backends at Runtime

Introspection happens once at **Step 0**, as part of backend discovery. Cache the result and use it throughout the run.

1. List all available MCP tools.
2. Match tools against the four capability categories above.
3. Cache the selected backend — use it for all writes in this run (sub-skill writes AND the orchestrator's Step 6 `MEMORY.md` write).

Do not repeat this query later in the run.

## Per-Backend Write Operations for MEMORY.md

`MEMORY.md` lives at the agent's **root directory** (not inside `memory/`). The write target is a single file.

| Backend category | Operation type | Notes |
|-----------------|----------------|-------|
| Local filesystem | Write or overwrite file at agent root | `write_file` / `edit_file` — tool names vary |
| Cloud object storage | Upload object with the agent-root path as key | Use the same relative path as the agent directory |
| Version-controlled store | Commit file change with a descriptive message | Example commit message: `"chore(memory): rebuild MEMORY.md index after weekly maintenance YYYY-MM-DD"` |
| Document store | Create or update document with agent-root path as key | Vary by provider — use tool listing from Step 0 |

## Rollback Strategy on Write Failure at Step 6

`MEMORY.md` is the most critical file in the agent's memory system — it is loaded at every session start. If the Step 6 write fails, do **not** leave a partial or corrupted index.

**If the agent's root is git-tracked:**
1. Restore the previous `MEMORY.md`: `git checkout HEAD -- MEMORY.md`
2. Report the failure. Sub-skill changes remain in place — only the index update is missing.
3. Inform the user: the stores are compacted but the index was not updated. They should re-run the orchestrator once the write issue is resolved.

**If git is unavailable:**
1. Do not overwrite the existing `MEMORY.md`.
2. Write the new index to a temporary file (e.g. `MEMORY.md.pending`) so the content is not lost.
3. Report the failure, list all attempted backends, and confirm that sub-skill changes remain in place.
4. Ask the user to manually rename the `.pending` file after verifying its contents.

**If all backends fail:**
Report the failure, list every attempted backend, confirm sub-skill changes are intact, and halt. Do not leave the session without informing the user of the exact state: "Stores compacted; index not updated."
