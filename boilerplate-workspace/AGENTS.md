# Workspace Agent Instructions

## Purpose of This Workspace

This workspace exists for one reason: **<explain the purpose of the workspace>**.  It is a knowledge base — not a codebase. Most files here are markdown, spreadsheets (CSV/XLSX), and exports from external tools (Notion, Google Drive).
If you are an AI agent loaded into this workspace, read this file end-to-end before doing anything else. It tells you (a) where to find the context you need, (b) where to record what you produce, and (c) which skills to use for each task.

## Session Startup Policy

On every new chat session, before doing anything else, follow this startup sequence: orient first (load workspace context), then arm (load skills).

### Required startup workflow

1. Read `MEMORY.md` at the workspace root to load workspace context, active projects, key decisions, and preferences.
2. List directories under `.agents/skills/`.
3. For each skill directory, read the front matter of the `SKILL.md` file immediately.
4. Do NOT read the entire `SKILL.md` file at this stage, only the front matter. The front matter contains metadata about the skill, such as its name, description, and tags, which are necessary for understanding what the skill does and when to use it. Reading the full `SKILL.md` should be reserved for when you are actually implementing a task that requires that skill.
5. If a skill also has key reference docs that affect execution rules, read those before continuing.
6. **Check for active restart guides.** Invoke the `restart-from-previous-session` skill (session-start path) — read its full `SKILL.md` at `.agents/skills/restart-from-previous-session/SKILL.md`, then follow the session-start path as described there. In short: list files in `memories/restart-guides/active/`; if any are present, surface them to the user via `AskUserQuestion` with options to (a) resume one of the listed guides, (b) start fresh on a different task, or (c) review a guide and decide. Read the chosen guide end-to-end before any further work. If no active restart guide exists, proceed without prompting. See [`memories/restart-guides/README.md`](memories/restart-guides/README.md) for the full convention and status definitions.
7. Glance at `memories/decisions/` and `memories/lessons/` (the compacted layer) so you do not contradict prior decisions or repeat past mistakes.
8. Only after this loading step, proceed with user requests.

### Blocking requirement

- Do not answer task requests, propose plans, or edit files until `MEMORY.md` has been read, all available skill `SKILL.md` files in `.agents/skills/` have been read, AND `memories/restart-guides/active/` has been checked.
- If any expected `SKILL.md` is missing, report it and continue loading the remaining skills.
- If an active restart guide exists and the user chooses to resume from it, read the guide end-to-end before producing any plan or edit.

## Top-Level Folder Map

```text

```

The single most important rule: **read before you write**. The `knowledge-base/` folder is the source of truth for the *restricted or confidential information about Strymin*. The `memories/` folder is the source of truth for *what we have decided and learned*. Never invent context that contradicts either.

## Agents in this Workspace

The agents below are personas defined in this workspace. Each one has its own complete configuration (IDENTITY, SOUL, RULES, MEMORY, SKILL-INDEX) and its own dedicated memory tree. Any agent loading into this workspace must locate its own persona folder before answering tasks.

| Agent | Persona entry-point | Role |
|---|---|---|

> Add a row when a new agent's `IDENTITY.md` is created. The role column should match the one-sentence description in the agent's IDENTITY.md.

## Where the Context Lives: `knowledge-base/`

Treat `knowledge-base/` as authoritative. When a user asks a question, search here first. Do not paraphrase from training data when a local source exists — quote the local source.

If you discover a fact that belongs in `knowledge-base/` but is missing, do **not** silently add it. Either (a) ask the user where it should live, or (b) record it as an open question in `memories/decision-records/list-decision-needed/` using the `record-decision-needed` skill.

When you create or edit any markdown file inside `knowledge-base/`, run the `format-md-for-progressive-disclosure` skill afterwards so it has MAGI front matter and can be discovered by future agents without a full read.

## The `memories/` Folder: Why It Matters

`memories/` is the **shared** memory store — organisational, cross-agent context that every agent in this workspace reads from a single source. The Tier-1 entry point for the shared store is `MEMORY.md` at the workspace root.

Each agent additionally maintains its own **dedicated** Tier-2 stores under `agents/<agent>/memory/` (daily logs, working preferences, projects, activities, connectivity tests). The agent's own `MEMORY.md` indexes that dedicated tree and points back at this shared store.

Cross-agent facts go in the shared store. Per-agent or per-session facts go in the dedicated store. **No duplication across the two.**

There are two layers:

1. **Raw decision records** under `memories/decision-records/` — the chronological, append-only log of every open question raised and every decision made. One file per item. High fidelity, low compression.
2. **Compacted memory** under `memories/decisions/` and `memories/lessons/` — the curated, deduplicated, indexed summary that future agents actually load first. Low size, high signal.

Always write to layer 1 first. Layer 2 is built *from* layer 1 by a periodic compaction pass — see "Compacting Memory" below.

### Recording an Open Question → `list-decision-needed/`

When a question surfaces that **cannot be resolved in the current conversation** — sources disagree, the accountable owner is absent, more investigation is required, or you simply do not have enough context — record it as a pending decision.

- **Skill to use:** `record-decision-needed`
- **Destination folder:** `memories/decision-records/list-decision-needed/`
- **Trigger phrases:** "we need to decide", "open question", "TBD", "parked for later", "sources conflict on …", "flag this for later".

A good pending-decision file makes it easy for the decision-maker to choose *without* re-reading the whole project. Capture: the question, the conflicting sources, the live options with their trade-offs, and any current placeholder.

### Recording a Decision Made → `list-decision-taken/`

When the user (or the responsible party) confirms, approves, finalises, or signs off on a question, close it.

- **Skill to use:** `record-decision-made`
- **Destination folder:** `memories/decision-records/list-decision-taken/`
- **Trigger phrases:** "we've decided X", "let's go with Y", "close item A.5", "lock it in", "approved", "supersede the previous decision".

A decision-made file must preserve the decision, the rationale, **every rejected alternative**, and a paired action plan so the path to execution is not lost. If the decision supersedes an earlier one, link both files and update the index — never delete the old record.

### Workspace configuration for the decision skills

Both skills read `decisions.config.md` at the workspace root for folder paths, ID series, and filename conventions. That file is checked in — extend it when you add a new decision domain (legal, engineering, etc.) rather than overriding paths inline.

## Compacting Memory: From Records to `decisions/` and `lessons/`

The `decision-records/list-decision-taken/` folder grows forever. Left alone, it becomes too large for any agent to load at the start of a session. The purpose of compaction is to fold finished decisions and recurring patterns into a small, indexed `memories/decisions/` and `memories/lessons/` that *can* be loaded up-front.

### What gets compacted where

| From                                              | To                       | What survives                                               |
|---------------------------------------------------|--------------------------|-------------------------------------------------------------|
| `decision-records/list-decision-taken/*.md`       | `memories/decisions/`    | Decision title, rationale summary, links back to the raw record, supersession links |
| Repeated mistakes, corrections, or "next time we should …" notes across decisions and sessions | `memories/lessons/`      | The lesson itself, the trigger that should remind us of it, links to the source records |

Raw records are **not deleted** by compaction — they are referenced. The raw log is the audit trail; compacted memory is the working set.

### How to run compaction

- **Full weekly maintenance** (rebuilds the index, audits all stores, detects contradictions): use `compact-agent-memories` (orchestrator).
- **Topical stores only** (`decisions/`, `lessons/`, etc., merge / archive / prune): use `compact-agent-topical-memories`.
- **Daily session logs only** (fold flat daily files into monthly / quarterly sub-folders): use `compact-agent-daily-memories`.
- **Saving a single new memory** between compactions: use `save-agent-memories`.

All four skills depend on `format-md-for-progressive-disclosure` so that every compacted file carries discoverable front matter. Run it on any new file in `memories/decisions/` or `memories/lessons/` if the compaction skill did not already do so.

### When to compact

- Any time `list-decision-taken/` has 10+ files that have not yet been folded into `memories/decisions/`.
- Whenever you notice the same lesson being re-derived in a new session — that is the signal it needs to be promoted to `memories/lessons/`.
- On a weekly cadence, regardless, via `compact-agent-memories`.

## Conventions

- **Filename for new dated artefacts:** `YYYY-MM-DD-HH-MM-<slug-or-uuid>.<ext>` (this matches the existing files in `knowledge-base/databases-and-lists/`).
- **Markdown:** every new `.md` file in `knowledge-base/` or `memories/` must carry MAGI-compliant YAML front matter. Use `format-md-for-progressive-disclosure` to add or update it.
- **Markdown line wrapping:** do **not** hard-wrap paragraph prose at a fixed column. Write each paragraph as one long line and let the editor wrap it. Hard-wrapped paragraphs make diffs noisy and edits painful. Headers, list items, and tables retain their own line structure as usual.
- **Cross-links:** prefer relative links inside the workspace (`../../knowledge-base/strymin-platform/...`) so they survive when the workspace is mounted at a different path.
- **No silent edits to source-of-truth files:** anything in `knowledge-base/` that you change should also be summarised in a decision record so the reasoning is preserved.

## Markdown Formatting Rules

Write all documents using clean, readable Markdown:

- Do not hard-wrap prose lines at a fixed column width. Let paragraphs flow naturally.
- Break lines only at meaningful semantic boundaries (e.g. end of a sentence) or let a paragraph be a single long line.
- Hard line breaks are appropriate inside code blocks, tables, and YAML — not in prose paragraphs or list items.

## Misc rules

- Do NOT GUESS, NEVER! Ask question if something is unclear.
- NEVER run `git` commands! If you need to run any `git` command, explain which command you want to run and why, then ask the user to run it for you.
