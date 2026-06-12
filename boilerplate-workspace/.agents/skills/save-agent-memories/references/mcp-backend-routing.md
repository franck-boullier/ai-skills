---
title: MCP Backend Routing — Tier 2 Write Operations
description: >-
  Distilled reference for save-agent-memories. Covers backend priority order,
  runtime introspection at Step 0, per-backend write operations for Tier 2
  topical memory files, and the retry-then-fallback strategy on write failure
  at Step 5.
purpose: reference
tags:
  - mcp
  - storage-backend
  - tier-2
  - write-operations
  - fallback
audience: ai-agent
---

# MCP Backend Routing — Tier 2 Write Operations

Backend selection is decided **once at Step 0** (during context load) and cached. Do not re-query mid-run.

---

## Priority Order

Select the **highest-priority backend that is currently active**. Classify by capability, not vendor name — the examples are illustrations, not an exhaustive list.

| Priority | Capability category | Example providers | When to choose |
|----------|--------------------|--------------------|----------------|
| 1 | **Version-controlled store** | GitHub, GitLab, Bitbucket | Preferred. Provides full audit trail, diff history, and single-command rollback. Memory integrity benefits most from this. |
| 2 | **Cloud object storage** | AWS S3, GCP GCS, Azure Blob, Cloudflare R2 | Enterprise-grade persistence and durability. No built-in diff; rollback requires manual file restoration. |
| 3 | **Document store** | GCP Firestore, MongoDB, Supabase, DynamoDB | Use when structured querying across memory fragments is needed. |
| 4 | **Local filesystem** | Built-in file tools | Always available. Baseline fallback. |

If no explicit primary backend is configured in the agent's environment, use the **local filesystem**.

If multiple backends are active and the agent's configuration designates one as primary, use that one. Otherwise, take the highest-priority active one.

---

## Runtime Introspection at Step 0

Discover which backends are available **once**, during Step 0 context load:

1. List all available MCP tools.
2. Match tool names and descriptions against the four capability categories above.
3. Cache the selected backend for use at Step 5 (Tier 2 write) and, if triggered, at Step 7 (MEMORY.md index update).

Do not repeat this query later in the run.

---

## Per-Backend Write Operations for Tier 2 Files

Tier 2 files live inside the `memory/` sub-tree (e.g. `memory/decisions/decision-auth-provider/README.md`). The operation type and MCP tool name vary by provider.

| Backend category | Operation type | Notes |
|-----------------|----------------|-------|
| Local filesystem | Write or overwrite file at the resolved path | Tool names vary: `write_file`, `edit_file`, or equivalent. Use the resolved absolute path. |
| Cloud object storage | Upload object with the relative path as key | Use the same relative path as within the agent directory. Example key: `memory/decisions/decision-auth-provider/README.md`. |
| Version-controlled store | Commit file change with a descriptive message | Example commit message: `"memory(decisions): record auth-provider decision YYYY-MM-DD"`. Use a concise, conventional-commit-style message. |
| Document store | Create or update document | Use the file's relative path as the document key. Vary by provider (Firestore `add_document`; Supabase `upsert`; MongoDB `replaceOne`, etc.). |

**For corrections** (updating an existing file rather than creating a new one): use the same operation type but target the existing file path. Add a date-stamped amendment note at the bottom of the file rather than overwriting the original content.

---

## Retry and Fallback on Write Failure at Step 5

If the selected backend fails on write:

1. **Retry once** with the same backend.
2. If the retry fails, **fall back to the next-priority backend** in the list.
3. If all backends fail, **hold the entry in session context** and warn the user:
   > "Memory entry could not be persisted — all backends failed. The entry is held in session context. Please resolve the storage issue and re-run this skill to commit it."

Do not silently discard a failed write. The user must know the entry was not persisted.

**For Step 7 (MEMORY.md update) failures:** apply the same retry-then-fallback strategy. If the MEMORY.md update fails after all retries, do not leave the index in a partially updated state. Warn the user and, if possible, write the pending update to `MEMORY.md.pending` so content is not lost.
