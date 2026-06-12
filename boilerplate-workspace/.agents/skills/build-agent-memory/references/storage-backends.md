# Storage Backends Reference

## Capability-First Backend Selection

Select the storage backend by **capability category**, not by hard-coding a single vendor. The MCP host discovers which tools exist at runtime; the skill maps "what operation is needed" to the available tool names for that deployment.

Apply priority from highest to lowest, skipping a tier if no MCP tools implement it:

| Priority | Capability | When to prefer it | Typical providers |
| --- | --- | --- | --- |
| 1 | **Version-controlled store** | Audit trail, reviewable diffs, rollback | GitHub, GitLab, Bitbucket, Gitea, local git |
| 2 | **Cloud object storage** | Durable shared blobs across sessions or devices | AWS S3, GCP GCS, Azure Blob, Cloudflare R2 |
| 3 | **Document store** | Structured queries across many small memory records | Firestore, MongoDB, Supabase, DynamoDB |
| 4 | **Local filesystem** | Lowest latency; universal fallback | Filesystem MCP servers |

## Backend Comparison

| Backend | Latency | Accessibility | Key advantage | Key limitation |
| --- | --- | --- | --- | --- |
| Local filesystem | Ultra-low | Single device | No setup; instant reads/writes | No audit trail; no shared access |
| Cloud object storage | Moderate | Global, multi-device | Durable; scales to any size | Requires MCP setup; IAM configuration |
| Version-controlled store | Higher (commit cycle) | Team-wide; full diff history | Every change is reviewable and reversible | Slower write cycle |
| Document store | Low–moderate | Global; queryable | Filter by metadata; good for many small entries | Most complex to set up |

## MCP Tool Patterns by Backend

The exact tool names depend on the MCP server installed. The patterns below map the required memory operations to what each category of server provides.

### Local Filesystem

| Operation | Typical tool name | Parameters |
| --- | --- | --- |
| Read memory file | `read_file` / `read_text_file` | `path` |
| Write new memory entry | `write_file` | `path`, `content` |
| Update MEMORY.md index | `edit_file` | `path`, `edits` |
| Search across stores | `search_files` | `path`, `pattern` |

### Version-Controlled Store (Git Hosts)

The pattern is: read current file → perform reasoning task → commit updated Markdown under `memories/`. Tool names vary by MCP server (e.g., `bb_post` / `bb_clone` for Bitbucket-oriented servers; other servers may use generic `git_commit` or `create_or_update_file`).

Required operations: read file, write/commit file, optionally list changed files.

### Cloud Object Storage

Key tools follow a get/put pattern: `s3_get_object` / `s3_put_object` for S3-compatible servers, or equivalent for GCS. The key prefix for memory files (e.g., `agents/my-agent/memories/`) must be confirmed during the probing sequence.

### Document Store (NoSQL)

Key operations: `add_document` / `upsert_document` (write), `get_document` (read), `query_collection` (search). Each memory entry becomes a document whose fields carry MAGI-style metadata plus Markdown body text. Individual document size limits apply (e.g., 1 MiB for Firestore) — entries that grow large must be split or summarized.

## Required Configuration by Backend Type

Use this table during Probe 2 of the storage destination sequence to collect all required configuration details before proceeding.

| Backend type | Required configuration |
| --- | --- |
| Version-controlled store | Provider (GitHub / GitLab / Bitbucket / other), repository name or URL, branch where memory files will be committed |
| Cloud object storage | Provider (AWS S3 / GCP GCS / Azure Blob / Cloudflare R2 / other), bucket name, region or project ID, key prefix for memory files |
| Document store | Provider (Firestore / MongoDB / Supabase / DynamoDB / other), database name, collection or table name |
| Local filesystem | Absolute path to the directory where memory files will be stored |

## Shared Memory Considerations

When the agent operates in a multi-agent environment, some categories belong in a **shared** store (org-wide facts) rather than in this agent’s **dedicated** `memories/` tree. Duplication across stores is forbidden.

**Canonical definitions, rules, and examples:** [dedicated-vs-shared-memory.md](dedicated-vs-shared-memory.md).

**Summary:** The agent’s `MEMORY.md` includes only a **pointer** to the shared store’s index — not a copy of shared content. The agent reads shared context from that path at session start. If this agent may maintain shared categories, it writes to the shared path for those categories and to its own `memories/` for everything else.
