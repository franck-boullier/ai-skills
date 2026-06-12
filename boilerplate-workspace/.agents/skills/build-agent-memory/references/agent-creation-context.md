# Agent Creation Context — Memory

## Creation Order

This order applies to **agent memory** (a `MEMORY.md` created for a specific named agent).
`MEMORY.md` is Phase 4 — it depends on `IDENTITY.md`, `SOUL.md`, and `RULES.md` being
in place first.

```text
1. IDENTITY.md  ← Entry point: what this agent is, what it does
2. SOUL.md      ← Who the agent is: personality, values, style, memory policy
3. RULES.md     ← Hard constraints: what the agent must and must never do, data handling
4. MEMORY.md    ← What the agent remembers and how  ← this skill
5. SKILL-INDEX.md ← What expertise the agent draws on
6. TOOLS.md     ← What the agent can execute (optional)
7. WORKFLOWS.md ← Repeatable processes (optional)
```

The memory architecture must be designed **after** `SOUL.md` and `RULES.md` because:

- The `SOUL.md` Memory Policy section defines what the agent's values say about what to remember, what to forget, and for how long. The memory architecture must honour this policy.
- The `RULES.md` Data Handling section defines hard constraints on what can be stored and for how long. These override any preference set in the Soul.

If `IDENTITY.md`, `SOUL.md`, or `RULES.md` do not yet exist, stop and ask the user to complete the missing document(s) before proceeding.

## Workspace Memory Exception

**This creation order applies only to agent memory.** When building a **workspace-level
`MEMORY.md`** (placed at the repository root, shared by all agents), the three prerequisite
documents are **not required** and must not be treated as blockers.

Workspace memory captures context that is shared across all agents in the repository —
environment facts, workspace decisions, team, active projects, conventions. No single
agent "owns" it, so no agent-specific identity documents govern it.

When `[MEMORY-MODE]` = `workspace` (set during Step 0 of `build-agent-memory`):

- Do **not** look for or require `IDENTITY.md`, `SOUL.md`, or `RULES.md`.
- `MEMORY.md` is placed at the repository root; the Tier 2 store goes in `memories/`
  (or a user-confirmed name) at the same root.
- Retention policies and triggers are based on the workspace's domain and the categories
  confirmed during Step 3 — not on a Soul or Rules document.
- The setup report uses the repository/workspace name in place of an agent name.

For the full comparison of workspace vs agent mode, see `workspace-vs-agent-memory.md`.

## Memory vs. Knowledge Base

These two are frequently confused. They serve entirely different purposes.

| Dimension | `MEMORY.md` | `knowledge-base/` |
| --- | --- | --- |
| **Answers** | "What has this agent learned from experience?" | "What reference material does this agent have?" |
| **Content type** | Dynamic — decisions, lessons, preferences, corrections | Static — domain guides, specifications, templates |
| **Update frequency** | High — updated after significant interactions | Low — updated when the domain knowledge changes |
| **Who writes it** | The agent itself (with human oversight) | The human builder |
| **Example content** | "On 2026-03-28 we chose Supabase over Firebase — see decisions/2026-03-28-auth-provider.md" | "The authentication specification for this system" |

Memory is what the agent **accumulates through use**. The knowledge base is what the builder **provides upfront**. Do not store knowledge base content in memory and do not put learned experience in the knowledge base.

## The Memory Dump Anti-Pattern

**What happens:** The memory file grows unbounded, storing every interaction verbatim.

**Why it fails:** The memory file consumes the entire context window, leaving no room for actual work. The agent becomes slow and confused.

**Correct approach:** `MEMORY.md` is an index, not a dump. Keep it under 4 KB. Detailed records go in subdirectories. Decisions live in `memories/decisions/`; the index contains only a summary line and a link.

## Output Location by Mode

All output files created by `build-agent-memory` are placed within the confirmed memory
root, not in the skill's own folder.

**Agent memory — output under the agent's directory:**

```text
    agents/
    └── my-agent-name/
        ├── IDENTITY.md          # Required — created before this skill runs
        ├── SOUL.md              # Required — created before this skill runs
        ├── RULES.md             # Required — created before this skill runs
        ├── MEMORY.md            # Created by this skill
        ├── memories/              # Created by this skill ([MEMORY-STORE-ROOT])
        │   ├── activities/
        │   ├── decisions/
        │   ├── lessons/
        │   ├── preferences/
        │   ├── test/
        │   └── ...
        └── memory-setup-report-YYYY-MM-DD-HH-MM.md
```

**Workspace memory — output at the repository root:**

```text
    [workspace-root]/
    ├── MEMORY.md            # Created by this skill
    ├── memories/            # Created by this skill ([MEMORY-STORE-ROOT])
    │   ├── activities/
    │   ├── decisions/
    │   ├── lessons/
    │   ├── preferences/
    │   ├── projects/
    │   ├── people/
    │   ├── analysis/
    │   ├── daily/
    │   └── test/
    └── memory-setup-report-YYYY-MM-DD-HH-MM.md
```
