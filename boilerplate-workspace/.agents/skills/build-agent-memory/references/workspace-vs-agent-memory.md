# Workspace Memory vs Agent Memory

This document is the **canonical definition** of the two memory modes supported by
the `build-agent-memory` skill. Read it during Step 0 (mode selection) and Steps 1–6.

---

## The Two Modes

| Dimension | Workspace Memory | Agent Memory |
| --- | --- | --- |
| **`MEMORY.md` location** | Repository root (`./MEMORY.md`) | Agent's own directory (`[agent-root]/MEMORY.md`) |
| **Memory store root** | `memories/` at repo root (by convention) | `memories/` inside the agent's directory (by convention) |
| **Who uses it** | All agents in this workspace — shared | Only this one agent — dedicated |
| **Prerequisites** | **None** — no IDENTITY.md / SOUL.md / RULES.md required | IDENTITY.md, SOUL.md, and RULES.md must exist first |
| **Typical content** | Workspace decisions, projects, team, environment facts, shared conventions | Agent-specific decisions, preferences, lessons, people |
| **Shared memory section in MEMORY.md** | Not applicable — this file IS the shared layer | Applicable when a workspace MEMORY.md exists; include pointer here |
| **Template to use** | Workspace-mode template in `memory-index-template.md` | Agent-mode template in `memory-index-template.md` |
| **Setup report "name" field** | Workspace name (repo name or confirmed label) | Agent name from `IDENTITY.md` |

---

## When to Use Each Mode

**Workspace memory** — Use when:

- You are setting up a repository and want a single shared memory layer any future
  agent can read and write from the start.
- Multiple agents will co-exist in the same repo and need to share environment facts,
  workspace decisions, and project context without duplicating them.
- No specific agent has been created yet — workspace memory can precede any agent.
- The user explicitly places `MEMORY.md` at the repository root and points the memory
  store at a folder named `memories/` (or another confirmed name).

**Agent memory** — Use when:

- A specific agent is fully specified: `IDENTITY.md`, `SOUL.md`, and `RULES.md` are
  all in place.
- The agent has domain-specific memory needs distinct from workspace-wide facts.
- You are adding a second or third agent to a workspace that already has workspace
  memory — this agent's `MEMORY.md` will carry a pointer to the workspace store.

---

## Directory Structure Comparison

**Workspace memory:**

    [workspace-root]/
    ├── MEMORY.md                         ← workspace memory index (this skill's output)
    ├── memories/                         ← Tier 2 memory store root ([MEMORY-STORE-ROOT])
    │   ├── activities/
    │   ├── analysis/
    │   ├── daily/
    │   ├── decisions/
    │   ├── lessons/
    │   ├── people/
    │   ├── preferences/
    │   ├── projects/
    │   └── test/
    └── memory-setup-report-YYYY-MM-DD-HH-MM.md

**Agent memory:**

    [workspace-root]/
    └── agents/
        └── my-agent/
            ├── IDENTITY.md               ← pre-existing (required)
            ├── SOUL.md                   ← pre-existing (required)
            ├── RULES.md                  ← pre-existing (required)
            ├── MEMORY.md                 ← this skill's output
            ├── memories/                   ← Tier 2 memory store root ([MEMORY-STORE-ROOT])
            │   ├── activities/
            │   ├── analysis/
            │   ├── daily/
            │   ├── decisions/
            │   ├── lessons/
            │   ├── people/
            │   ├── preferences/
            │   ├── projects/
            │   └── test/
            └── memory-setup-report-YYYY-MM-DD-HH-MM.md

---

## Relationship Between the Two

When a workspace has BOTH a workspace `MEMORY.md` and one or more agent `MEMORY.md`
files:

- The workspace `MEMORY.md` holds org-wide context (team, architecture, shared
  decisions, workspace conventions).
- Each agent's `MEMORY.md` holds agent-specific context **and** a pointer to the
  workspace `MEMORY.md` in its **Shared memory** section.
- An agent must **NEVER** duplicate workspace memory in its own dedicated store —
  only a pointer. See `dedicated-vs-shared-memory.md`.

---

## Memory Store Root Name Convention

By convention:

- **Workspace memory** uses `memories/` (plural) as the Tier 2 root — signalling
  shared, workspace-wide scope.
- **Agent memory** uses `memories/` (singular) as the Tier 2 root — signalling
  single-agent ownership.

Whatever name is confirmed during Step 1 is recorded as `[MEMORY-STORE-ROOT]` and
used throughout all subsequent steps and file paths. Do not change it after setup
without running a new connectivity test.

---

## Triggers and Daily Logs in Workspace Mode

Workspace memory follows the same trigger and retention model as agent memory
(see `memory-policies.md`), with one addition: the "session ends" daily log trigger
can be fired by **any agent** or session working in the workspace, not just one
specific agent. Daily log entries in workspace memory should identify the authoring
agent or session in the entry body so the audit trail is clear.

---

## See Also

- `dedicated-vs-shared-memory.md` — rules against duplicating shared content in
  agent-specific stores
- `memory-model.md` — three-tier model; applies to both workspace and agent stores
- `agent-creation-context.md` — creation order for agent documents; workspace
  exception documented there
