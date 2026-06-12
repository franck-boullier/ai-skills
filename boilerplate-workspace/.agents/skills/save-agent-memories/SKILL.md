---
name: save-agent-memories
description: >-
  Classifies and persists memory entries to the correct Tier 2 topical store
  and conditionally updates the Tier 1 MEMORY.md index via the
  highest-priority available MCP backend. Covers decisions, corrections,
  preferences, lessons, people, projects, activities, environment facts,
  analysis, patterns, and daily session logs. Activate proactively — without
  waiting to be asked — when the user says "remember this", "save this
  decision", or "note this preference"; or when a decision, correction, new
  person, or session end occurs. Companion to compact-agent-memories.
compatibility: >-
  Requires file-system access or an MCP storage backend. Local filesystem is
  the minimum; a git-backed store is strongly recommended for audit trail and
  rollback. The agent root must contain a valid MEMORY.md index.
metadata:
  author: fbo
  version: "0.2-draft"
  status: draft
  skill-target: save-agent-memories
---

# Save Agent Memories

Classifies and persists a single memory-worthy event to the agent's persistent memory store. Executes the full path: classify → resolve target path → select backend → format entry → write Tier 2 → evaluate and optionally update Tier 1 index → confirm.

This skill handles **creation and update** only. Memory compaction, reorganization, and index pruning belong to `compact-agent-memories`.

Read `references/constraint-vocabulary.md` before executing — especially the NEVER constraints on identity files, verbatim storage, and the 2 KB index limit.

---

## Triggers

Activate this skill **proactively** — without waiting for the user to ask — whenever any of the following occurs:

**Explicit triggers:** the user says "remember this", "save this decision", "log this lesson", "update my memory", "add this person", "note this preference".

**Implicit triggers:** a decision is made (with reasoning and alternatives); a correction is received from the user; a new project or activity is discussed for the first time; a new person is introduced; a lesson is learned from a mistake or unexpected outcome; a recurring pattern is noticed across sessions; an environment fact changes (domain context, key relationships, working constraints, key dates); a user preference is stated or updated; the session ends (write a daily log before closing).

---

## Step 0 — Load required context

Before classifying the event, load the context all subsequent steps depend on:

1. Read `MEMORY.md` from the agent's root directory. This is the Tier 1 index; it defines the active memory store structure and current stable facts.
2. From `MEMORY.md`, confirm the `memory/` directory structure (which stores exist, what naming conventions are in use). See `references/memory-architecture.md` for the canonical store inventory and sub-folder pattern.
3. Query the MCP tool listing to discover which storage backends are available. Cache this list for Step 3. See `references/mcp-backend-routing.md` for the priority order and how to classify backends by capability.
4. If the memory event's worth is genuinely unclear, read the `memory-policy` section of `SOUL.md` as a tiebreaker. Skip this read if the event clearly qualifies.

Do not proceed to Step 1 until all required context is loaded.

**If `MEMORY.md` is missing or unreadable:** halt and warn the user. The index is required to determine the correct store structure and to evaluate Step 6.

**If `MEMORY.md` is already over 2 KB when first read at Step 0:** note this immediately and apply the following rule at Step 7 — skip the MEMORY.md update entirely regardless of the event type. For high-value events (new decision, new project), warn the user that the index pointer was omitted and recommend running `compact-agent-memories` to free up space before re-running this skill. For lower-value events (preference, lesson), proceed silently and route discovery through the store's own README.md.

---

## Step 1 — Classify the memory event

Determine which category best describes the event:

| Category | Target store | Notes |
|----------|-------------|-------|
| Decision | `memory/decisions/` | Any choice worth preserving with its reasoning and alternatives — strategy, approach, method, process. |
| Correction | Relevant existing file | **User corrections are authoritative.** Accept the correction as the new truth without questioning existing data. Update the relevant file in place; do not create a new file. |
| Preference | `memory/preferences/` | Communication style, formatting, working rhythm, domain-specific preferences. |
| Lesson | `memory/lessons/` | Mistakes, surprising outcomes, things that worked well. |
| Person | `memory/people/` | Anyone worth remembering: collaborator, client, advisor, expert. |
| Project | `memory/projects/` | Named initiative spanning multiple sessions. |
| Activity | `memory/activities/` | Ongoing activity tracked across multiple sessions. |
| Environment fact | `MEMORY.md` index directly | Stable contextual facts: domain context, team, tech stack, key dates, constraints. Written to Tier 1, not Tier 2. |
| Pattern | `MEMORY.md` index or `memory/analysis/` | Recurring themes across sessions. Short patterns go in the index; detailed patterns with evidence go in `analysis/`. |
| Analysis | `memory/analysis/` | Standalone analysis not tied to a single project or activity — cross-cutting observations, root-cause investigations, comparative studies. |
| Daily session log | `memory/daily/YYYY-MM-DD.md` | Raw journal of today's session. **Never** adds a pointer to `MEMORY.md`. |

If the event does not fit clearly into one category, choose the closest match and note the ambiguity in the entry's frontmatter (`classification-confidence: low`).

---

## Step 2 — Determine the target path

Using the classification from Step 1, resolve the full path within the `memory/` tree:

- For sub-folder categories (decisions, projects, activities): determine a descriptive kebab-case slug. Check whether the sub-folder already exists. Create it if not, including a `README.md` entry point.
- For flat-file categories (lessons, preferences, people): target the store directory directly. Create the directory with a `README.md` if missing.
- For corrections: identify the existing file to update. If no file exists for the corrected fact, treat as a new entry with `origin: correction` in the frontmatter.

### Step 2a — Daily session log path

For the daily session log category only:

1. Target file: `memory/daily/YYYY-MM-DD.md` (today's date).
2. After writing, append a one-line entry to `memory/daily/README.md`:

   ```markdown
   - [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>
   ```

3. If `memory/daily/README.md` does not exist, create it with a header and the first entry.
4. Do not touch `MEMORY.md` — the daily log bootstrap pointer is established once at agent setup and this skill never modifies it.

---

## Step 3 — Select the storage backend

Use the cached MCP tool list from Step 0 to select the backend. Apply this priority order (highest to lowest):

1. Version-controlled store (GitHub, GitLab, Bitbucket, etc.)
2. Cloud object storage (S3, GCS, Azure Blob, Cloudflare R2, etc.)
3. Document store (Firestore, Supabase, MongoDB, DynamoDB, etc.)
4. Local filesystem (always available)

Select by **capability category**, not vendor name. If no explicit primary backend is configured, use the local filesystem.

Full priority table and per-backend write operations: `references/mcp-backend-routing.md`.

---

## Step 4 — Format the memory entry

Structure the entry as a Markdown document. Every file must begin with MAGI-compatible YAML frontmatter:

```yaml
---
doc-id: <UUID v7>
title: <descriptive title>
description: <one-sentence summary>
category: <category>
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - <tag>
---
```

Then add the body structured for the category. The body captures signal — what was decided, what was learned, what changed — not the raw conversation.

Full body templates for every category: `references/memory-entry-formats.md`.

Key category notes:

- **Decisions**: always include date, decision, reasoning, alternatives considered, trade-offs, affected areas.
- **Lessons**: always include date, context, what happened, what was learned, action taken.
- **Daily session log**: include session focus, key events (decisions, corrections, people, environment changes), and open items carried forward.
- **Corrections**: do not create a new file — append a date-stamped amendment note to the bottom of the relevant existing file and update `last-updated`.

---

## Step 5 — Write to the topical memory store

Using the backend selected at Step 3, write the formatted entry to the path resolved at Step 2. The MCP tool name and parameters vary by provider — use the tool listing obtained at Step 0 to determine the exact call.

| Backend category | Operation type |
|-----------------|----------------|
| Local filesystem | Write or overwrite file at path |
| Cloud object storage | Upload object with relative path as key |
| Version-controlled store | Commit file change with a descriptive message |
| Document store | Create or update document with path as key |

On failure: retry once with the same backend, then fall back to the next-priority backend. If all backends fail, hold the entry in session context and warn the user. Full retry and fallback details: `references/mcp-backend-routing.md`.

---

## Step 6 — Evaluate whether MEMORY.md needs updating

The Tier 1 index (`MEMORY.md`) should be updated **only** when:

- A new stable fact was established (environment change, new key date, new project started).
- A new pointer to a topical store entry is needed (new decision recorded, new person added).
- An existing index entry is now outdated and must be corrected.

**Daily session logs never trigger a MEMORY.md index update.** If none of the conditions above apply, skip Step 7 and proceed directly to Step 8.

---

## Step 7 — Update the MEMORY.md index

When the Step 6 conditions are met:

1. Read the current `MEMORY.md` (already in context from Step 0 — re-read only if the session is long and the cached version may be stale).
2. Calculate the current file size in bytes.
3. Draft the update: add the new pointer, update the fact, or correct the stale entry.
4. Measure the updated file. If it would exceed **2 KB**, do not write. Instead:
   > "MEMORY.md would exceed 2 KB with this update. Run `compact-agent-memories`
   > first to free up index space, then re-run this skill."
5. If under 2 KB, write the updated index using the same backend as Step 5.

Target index structure: `references/memory-architecture.md` (MEMORY.md Index Structure section).

---

## Step 8 — Confirm to the user

Always confirm, regardless of whether Step 7 executed:

> "Saved [category]: [brief description] → [destination path].
> MEMORY.md index [updated with pointer to X / unchanged]."

---

## Non-Negotiable Constraints

Read `references/constraint-vocabulary.md` for the full ALWAYS / NEVER / ASK BEFORE framework. Key constraints repeated here for visibility:

- **NEVER modify `SOUL.md`, `RULES.md`, or `IDENTITY.md`.** If a memory event contradicts an identity file, flag it for human review.
- **NEVER store external content verbatim.** Summarize emails, documents, and web content before persisting.
- **NEVER exceed the 2 KB limit on `MEMORY.md`.** Halt Step 7 and recommend compaction instead.
- **NEVER store PII without explicit user consent** and a defined retention policy in the frontmatter.
- **NEVER add individual daily log pointers to `MEMORY.md`.**
- **ALWAYS include MAGI-compatible YAML frontmatter** in every Tier 2 file.
- **ALWAYS summarize, never dump.** Capture the signal, not the transcript.

---

## Edge Cases & Error Handling

| Situation | Behavior |
|-----------|----------|
| No MCP storage backend available | Fall back to local filesystem. If also unavailable, hold in session context and warn the user. |
| `MEMORY.md` would exceed 2 KB after Step 7 | Do not write. Warn the user; recommend running `compact-agent-memories` first. |
| Contradictory memory detected (new fact conflicts with existing entry) | Flag the contradiction. Present both versions. Ask the user to resolve before writing. |
| Target topical store directory does not exist | Create it per the architecture in `references/memory-architecture.md`, including a `README.md` entry point. |
| `memory/daily/README.md` does not exist | Create it with a header and the first entry. Do not add a new pointer in `MEMORY.md`. |
| Event does not fit any category | Choose the closest category; set `classification-confidence: low` in frontmatter. |
| Same fact already recorded | Update the existing entry with a date-stamped amendment rather than creating a duplicate. |
| Correction received but no existing memory file covers it | Create an appropriate file using the closest category template; add `origin: correction` to frontmatter. |
| Backend write fails | Retry once, then fall back to the next-priority backend. If all fail, hold in session context and warn the user. |
| `MEMORY.md` is missing or unreadable at Step 0 | Halt. Warn the user. Do not proceed — the index is required to determine store structure and to evaluate Step 6. |

---

## Reference Files

- `references/memory-architecture.md` — Three-tier model, Tier 2 store types, directory layout, sub-folder pattern, MAGI frontmatter  requirements, MEMORY.md index structure. **Read before Steps 0 and 7.**
- `references/mcp-backend-routing.md` — Backend priority order, runtime introspection, per-backend write operations for Tier 2 files, retry and fallback strategy. **Read before Steps 3 and 5.**
- `references/memory-entry-formats.md` — MAGI frontmatter fields and Markdown body templates for every category. **Read at Step 4.**
- `references/constraint-vocabulary.md` — ALWAYS / NEVER / ASK BEFORE constraints specific to this skill. **Read before any execution.**

---

## See Also

- `compact-agent-memories` — The companion skill for periodic memory maintenance: reorganizes daily logs, compacts topical stores, resolves contradictions, and rebuilds the MEMORY.md index.
- `format-md-for-progressive-disclosure` — Adds or updates MAGI-compatible YAML frontmatter. Use it on any README you create or substantially update.
