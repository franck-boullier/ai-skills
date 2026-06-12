---
title: MCP Backend Routing for Topical Store Writes
description: >-
  Distilled reference for compact-topical-memories. Covers backend priority order
  for selecting an MCP storage backend, how to introspect available tools at
  runtime (Step 0), per-backend write operations, and rollback strategy on
  write failure.
purpose: reference
tags:
  - mcp
  - storage-backend
  - file-write
  - rollback
audience: ai-agent
last-updated: 2026-04-05
---

# MCP Backend Routing for Topical Store Writes

## Priority Order

Select the **highest-priority backend that is currently active**. Selection is by
capability category, not vendor name.

| Priority | Category | Examples | When to choose |
|----------|----------|----------|----------------|
| 1 | Version-controlled store | GitHub, GitLab, Bitbucket MCP | Preferred — full audit trail and rollback. Choose when memory integrity matters. |
| 2 | Cloud object storage | AWS S3, GCP GCS, Azure Blob, Cloudflare R2 | Enterprise durability; no built-in diff. |
| 3 | Document store | GCP Firestore, MongoDB, Supabase, DynamoDB | Structured queries across memory fragments. Note Firestore 1 MiB document limit — split large merges. |
| 4 | Local filesystem | Built-in file tools | Always available as baseline fallback. |

If no primary backend is configured, use the **local filesystem**.

## Introspection at Step 0 (Pre-flight)

Backend introspection happens once at **Step 0, Check B**. Cache the result; use
it for all writes in this run. Do not re-query later.

1. List available MCP tools.
2. Match against the four categories above.
3. Cache the highest-priority active backend for use at Step 5.

## Per-Backend Write Operations

| Backend category | Operation | Notes |
|-----------------|-----------|-------|
| Local filesystem | `write_file` / `edit_file` | Actual tool names vary by implementation |
| Cloud object storage | Upload with path key | `s3_put_object`, `gcs_put_object`, or equivalent |
| Version-controlled store | Commit file change | Git MCP tool names vary by provider |
| Document store | Create or update document | `add_document` / `update_document`; watch the 1 MiB Firestore limit |

Use the tool listing from Step 0 to determine exact tool names and parameters.

## Rollback Strategy on Write Failure

If a write fails during a compaction batch, **roll back the entire batch** for the
affected store — partial compaction leaves a store in an inconsistent state.

**If the store is git-tracked:**

1. Restore each modified or moved file: `git checkout HEAD -- <path>`
2. Delete any newly created files that are still untracked (no prior committed state).
3. Scope cleanup to only paths touched in this batch — do not run `git clean` on the repo.

**If git is unavailable or paths cannot be restored via git:**

1. Halt immediately — do not write any further files.
2. List every path created or modified before the failure.
3. Present the list to the user and request manual restoration.

In both cases, log all failed paths in the Step 6 compaction report.

## Firestore Document Size Limit

Firestore enforces a **1 MiB per-document limit**. If a merge would produce a
file exceeding this size, split it into numbered files:

```
decision-auth-provider-01.md
decision-auth-provider-02.md
```

Update the store's `README.md` to link both files. Log the split in the compaction report.
