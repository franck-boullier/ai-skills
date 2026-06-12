---
name: examples
description: Worked examples for the record-action-needed skill — slash-command invocation by a human user and agent-detected programmatic invocation at session-end.
---

# Examples — Record Action Needed

## Example 1 — Slash-command invocation by a human user

**Caller input:**

```text
/record-action Update the API documentation for the new auth flow
```

MEMORY.md path supplied alongside the command. MEMORY.md contains:

```text
actions_shared: <workspace>/memories/actions
actions_local: null
```

**Skill behaviour — step by step:**

1. Reads `MEMORY.md` at the supplied path. Extracts shared actions folder =
   `<workspace>/memories/actions/`. No local-agent folder — caller is human.
2. Receives input — `description = "Update the API documentation for the new auth flow"`.
   No other fields provided.
3. Validates description (non-empty — pass).
4. **ASK-BACK**: *"Who owns this action?"* → caller answers `"Franck"`.
   **ASK-BACK**: *"When is this due?"* → caller answers `"2026-05-15"`.
5. Auto-derives: `id = A-01928a3c-2f1e-7c2d-8b1a-...` (UUIDv7),
   `created-at = 2026-05-06T14:23:00Z`, `source = "chat:cowork-session-2026-05-06-14:20"`,
   `priority = "medium"`.
6. No apparent sensitive content — privacy check passes.
7. Renders markdown record.
8. Writes to `<workspace>/memories/actions/A-01928a3c-2f1e-7c2d-8b1a-....md`.
9. Caller is human — no local copy (Step 9 skipped silently).
10. Updates `<workspace>/memories/actions/INDEX.md`.
11. Returns `id` to caller.

**Resulting record file** (`A-01928a3c-....md`):

```markdown
---
id: A-01928a3c-2f1e-7c2d-8b1a-...
status: open
owner: Franck
due-date: 2026-05-15
priority: medium
source: chat:cowork-session-2026-05-06-14:20
created-at: 2026-05-06T14:23:00Z
---

# Action — Update the API documentation for the new auth flow

## Description

Update the API documentation for the new auth flow

## Context

chat:cowork-session-2026-05-06-14:20
```

---

## Example 2 — Agent-detected invocation at session-end

**Caller** (`chat-session-scribe` agent wrapping up a session):

```text
record-action-needed.invoke(
  memory_md="/workspace/MEMORY.md",
  description="Schedule a follow-up review of the migration plan with the database team"
)
```

MEMORY.md at `/workspace/MEMORY.md` contains:

```text
actions_shared: /workspace/memories/actions
actions_local: draft-agents/chat-session-scribe/memories/actions
```

**Skill behaviour — step by step:**

1. Reads `/workspace/MEMORY.md`. Extracts shared actions folder =
   `/workspace/memories/actions/` and local-agent folder =
   `draft-agents/chat-session-scribe/memories/actions/`.
2. Receives input — description only.
3. Validates description (non-empty — pass).
4. **ASK-BACK** (relayed to user by Scribe): *"Who owns this action?"* → user answers
   `"db-team"`. **ASK-BACK**: *"When is this due?"* → user answers `"2026-05-13"`.
5. Auto-derives all remaining fields (UUIDv7 id, created-at, priority = "medium",
   source from session metadata or `"unknown-session"`).
6. No sensitive content — privacy check passes.
7. Renders markdown record.
8. Writes shared record to `/workspace/memories/actions/A-<uuid>.md`.
9. Writes local copy to
   `draft-agents/chat-session-scribe/memories/actions/A-<uuid>.md`
   (caller is an FBO-framework agent).
10. Updates `INDEX.md` in both locations (creates either if it does not yet exist,
    initialising it with MAGI frontmatter via `format-md-for-progressive-disclosure`).
11. Returns the `id` to Scribe, which references it in the session summary.
