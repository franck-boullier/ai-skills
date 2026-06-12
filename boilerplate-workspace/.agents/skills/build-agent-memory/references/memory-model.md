# Memory Model Reference

## Dedicated vs Shared Memory

**Dedicated memory** is this agent's own `memories/` tree (Tier 2 under its confirmed storage root). **Shared memory** is a separate org-wide store used by multiple agents. Definitions, non-negotiable rules, and a quick decision guide: [dedicated-vs-shared-memory.md](dedicated-vs-shared-memory.md). The three-tier model below applies to **each** store's layout; only the pointer to the shared index belongs in this agent's `MEMORY.md` for shared content.

## The Three-Tier Model

Memory is tiered, following progressive disclosure: the index loads at every session start, topical stores load on demand, and session context is ephemeral.

| Tier | Name | Content | When Loaded | Size Limit |
| --- | --- | --- | --- | --- |
| 1 | Memory Index (`MEMORY.md`) | Stable facts, environment, pointers to Tier 2 stores | Every session start | Under 4 KB |
| 2 | Topical Stores (`memories/*/`) | Detailed decisions, lessons, projects, daily logs | On demand via tools | No hard limit per file |
| 3 | Session Context | Current conversation, raw tool outputs | Ephemeral — lives in the context window | Truncated when window fills |

`MEMORY.md` is an **index**, not a database. Every entry in it is either a stable fact or a pointer to a Tier 2 file. If the index exceeds 4 KB, move the longest entries to topical stores and replace them with a summary line and link.

## `root_prefix` Convention (DRY link targets)

To avoid repeating long absolute paths in every README pointer, `MEMORY.md` may (and in this skill: should) declare a YAML frontmatter key `root_prefix`, containing a fully qualified path prefix.

- **Recommended value:** set `root_prefix` to the fully qualified path of the memory root directory (the same directory you would otherwise call `[AGENT-MEMORY-ROOT]`).
- **Link rule:** write link targets in `MEMORY.md` relative to `root_prefix`.
- **Resolution rule:** the agent resolves full paths as: `{root_prefix}{link_target}`.

This improves index readability and helps keep the index under the 4 KB limit, while still keeping the Storage backend location fully qualified and unambiguous.

## Canonical Topical Store Structure

```text
memories/
├── activities/        # Multi-session activities worth tracking across sessions
├── analysis/          # Analysis not tied to a single project
├── daily/             # Daily logs: YYYY-MM-DD.md
├── projects/          # One sub-folder per active project
├── decisions/         # Key decisions with reasoning
├── preferences/       # How the user likes things done
├── people/            # Key contacts and relationships
├── lessons/           # Mistakes and learnings
└── test/              # Connectivity test entries — always created during setup
```

Domain-specific categories may be added (e.g., `contracts/` for a legal agent, `incidents/` for an ops agent). Categories the agent will never use may be omitted — except `test/`, which is always created.

All markdown files in `memories/` must carry MAGI-compatible frontmatter to support progressive discovery.

## What to Remember

**Always remember:**

- Decisions and the reasoning behind them — the highest-value memory category; prevents re-litigating settled choices.
- Corrections — when the user corrects the agent, store it to prevent repeating the mistake.
- Preferences — communication style, formatting, working patterns.
- Environment facts — tech stack, team members, project names, key dates.
- Patterns — recurring themes, repeated requests, observed trends.

**Remember temporarily:**

- Specific code snippets — useful for days, stale after a week.
- Meeting context — relevant for follow-ups, irrelevant after actions complete.
- Error details — important during debugging, forgettable after resolution.

**Forget deliberately:**

- PII that is no longer needed for the current task.
- Specific financial amounts after the relevant period (trends matter more than transactions).
- Health details after they are no longer medically relevant (unless the agent is a health agent).
- One-off queries that have no bearing on future interactions.
