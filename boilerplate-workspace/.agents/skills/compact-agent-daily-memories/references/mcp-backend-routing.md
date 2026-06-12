---
title: MCP Backend Routing for Memory Writes
description: >-
  Distilled reference for compact-agent-daily-memories. Covers the priority order
  for selecting an MCP storage backend, how to introspect available tools at
  runtime, per-backend write operations, and rollback strategy on failure.
purpose: reference
tags:
  - mcp
  - storage-backend
  - file-write
  - rollback
audience: ai-agent
---

# MCP Backend Routing for Memory Writes

## Priority Order

Select the **highest-priority backend that is currently active**. Selection is by *capability category*, not vendor name — the examples are illustrative.

| Priority | Category | Examples | When to choose |
|----------|----------|----------|---------------|
| 1 | Version-controlled store | GitHub, GitLab, Bitbucket MCP | Preferred — provides full audit trail and rollback. Choose when memory integrity and change history matter. |
| 2 | Cloud object storage | AWS S3, GCP GCS, Azure Blob, Cloudflare R2 | Enterprise-grade persistence and durability. |
| 3 | Document store | GCP Firestore, MongoDB, Supabase, DynamoDB | Structured queries or filtering needed across memory fragments. |
| 4 | Local filesystem | Built-in file tools | Always available as the baseline fallback. |

If no explicit primary backend is configured, use the **local filesystem**.

## How to Introspect Available Backends at Runtime

Backend introspection happens once at **Step 0 (pre-flight)**, as part of Check B. Cache the result and use it throughout the skill run. Do not re-query at Step 5.

1. List available MCP tools.
2. Match tools against the four capability categories above.
3. Cache the result — use it for all writes in this skill run (Steps 3–4 and Step 5).

## Per-Backend Write Operations

| Backend category | Operation type | Common MCP tool examples |
|-----------------|----------------|--------------------------|
| Local filesystem | Write or edit file | `write_file` / `edit_file` (actual names vary by implementation) |
| Cloud object storage | Upload object with path key | `s3_put_object`, `gcs_put_object`, or equivalent |
| Version-controlled store | Commit file change | git-commit MCP tool (varies by provider) |
| Document store | Create or update document | `add_document` / `update_document` (varies by provider) |

Actual tool names and parameter names vary by provider. Use the tool listing obtained at Step 0 to determine exact names.

## Rollback Strategy on Write Failure

If a write fails at any point during a reorganization batch, the entire batch must be rolled back — partial reorganization leaves `memory/daily/` in an inconsistent state.

**If `memory/daily/` is git-tracked:**

1. Restore each modified or moved path: `git checkout HEAD -- <path>` (per file or directory as needed).
2. Delete any **newly created** files or folders that are still untracked (they have no prior committed state to restore to).
3. Do **not** run `git clean` on the whole repo — scope the cleanup to only paths touched in this batch.

**If git is unavailable or paths are not restorable via git:**

1. Halt immediately — do not write any further files.
2. List every path created or modified during the failed batch.
3. Ask the user to restore those paths manually.

In all cases, log the failed paths in the Step 6 report.
