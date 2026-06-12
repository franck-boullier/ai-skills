---
name: record-action-needed
description: >-
  Captures pending action items into uniform, ID-addressable, durable records —
  one markdown file per action plus a shared INDEX.md — so they survive past the
  originating session and remain queryable across agents and humans. Use when the
  user types /record-action or /action-needed; says "record this action", "add
  this to the action list", "track this as a todo", "capture this as an action
  item", "we need to", "someone should", "action item:", "TODO:", or
  "follow-up:"; or when an agent such as chat-session-scribe invokes it
  programmatically at session-end. A MEMORY.md path is a hard prerequisite —
  the skill stops and asks for it if not provided. Performs ASK-BACK for missing
  owner and due-date. Auto-generates a UUIDv7 ID (time-sortable). Dual-writes to
  shared workspace memories (source of truth) and, when the caller is an
  FBO-framework agent, a local copy in the agent's own memories. Companion skill:
  record-action-taken resolves actions by ID.
metadata:
  author: fbo
  version: "0.3-draft"
---

# Record Action Needed

The entry point of the **pending-action lifecycle** in the FBO framework. Captures
any action item a downstream party needs to execute into a durable, ID-addressable
record that survives past the originating session. The companion skill
`record-action-taken` uses the IDs assigned here when an action is completed.

This is a **universal** skill — every agent's `SKILL-INDEX.md` is expected to list it.

---

## Triggers

Activate on any of the following intents:

1. **Slash-command** — `/record-action`, `/action-needed`, or any equivalent
   slash-prefixed command the host tool exposes for action capture.
2. **Natural-language imperative** — "record this action", "add this to the
   action list", "track this as a todo", "capture this as an action item".
3. **Action-item phrasing** — "we need to ___", "someone should ___",
   "action item: ___", "TODO: ___", "follow-up: ___". Trigger when the agent
   recognises the user is declaring an action, even without an explicit imperative.
4. **Agent-detected at session-end** — when an agent (e.g. `chat-session-scribe`)
   wraps up a session and identifies pending actions in the transcript, it invokes
   this skill programmatically for each. No user-facing trigger phrase required.

---

## Input

| Field | Provided by | If missing |
| --- | --- | --- |
| `MEMORY.md` (file path) | Caller — **mandatory** | **STOP at Step 1.** Output **exactly and only** the phrase: *"To run this skill I need a `MEMORY.md` file that specifies where action records will be stored. Please provide the path to your `MEMORY.md`."* The backtick formatting on `MEMORY.md` is required. No preamble, no explanation, no additional questions. No file is written, no ID is generated, no other input is processed. No default fallback. |
| `description` | Caller (required, non-empty string) | **Stop and error**: *"description is required and cannot be empty"*. No file is written. |
| `owner` | Caller (optional) | **ASK-BACK**: *"Who owns this action?"* Wait for a reply before continuing. |
| `due-date` | Caller (optional) | **ASK-BACK**: *"When is this due?"* Wait for a reply before continuing. |
| `source` | Caller (optional) | Auto-derived from session metadata exposed by the host tool. Caller may override. |
| `priority` | Caller (optional) | Defaults to `medium`. Allowed values: `low`, `medium`, `high`. |
| `id` | Auto-generated | UUIDv7 (time-sortable). Never accepted from the caller. |
| `created-at` | Auto-generated | UTC ISO-8601 timestamp at the moment of writing. Never accepted from the caller. |

**ASK-BACK behaviour**: the skill pauses, prompts the caller, and resumes once
the answer is provided. If the caller declines, the skill cancels the entire
record — no partial writes.

---

## Output

All storage paths are read from the caller-provided `MEMORY.md`. The paths below
are illustrative defaults only; actual paths are always those declared in `MEMORY.md`.

### Per-action record

Written to the shared-workspace actions folder declared in `MEMORY.md`
(default: `<workspace>/memories/actions/A-<uuid>.md`).

When the caller is an FBO-framework agent, an additional copy is written to the
caller-agent local actions folder declared in `MEMORY.md`
(default: `<caller-agent>/memories/actions/A-<uuid>.md`).

File structure:

```markdown
---
id: A-<UUIDv7>
status: open
owner: <owner>
due-date: <YYYY-MM-DD or "none">
priority: <low|medium|high>
source: <session reference or human-readable origin>
created-at: <UTC ISO-8601>
---

# Action — <description truncated to ~80 chars>

## Description

<full description as provided by the caller>

## Context

<source-derived context, if any>
```

**Body content contract — non-negotiable:**

- The frontmatter MUST contain exactly the seven fields above, in that order, with no additions or omissions.
- The `## Description` section MUST contain the caller-provided `description` verbatim and in full — no truncation, no paraphrasing.
- The `## Context` section MUST always be present. If no source-derived context is available, leave the section body empty rather than omitting the section.
- No additional sections (e.g. `## Notes`, `## Tags`) may be added.

### INDEX.md

Maintained at the shared-workspace actions folder (and at the caller-agent local
folder when applicable). Updated on every successful write.

Schema — append a new row for each action; do not rewrite earlier rows:

| ID | Description (truncated) | Owner | Due | Priority | Created | Status |
| --- | --- | --- | --- | --- | --- | --- |

**INDEX.md row contract — non-negotiable:**

- The `ID` column MUST contain the exact UUIDv7 string generated in Step 5 (format: `A-<UUIDv7>`). No abbreviated, date-sequential, or reformatted IDs.
- The row MUST be appended; existing rows MUST NOT be modified or rewritten.

### Return value

The skill returns the action `id` (UUIDv7) to the caller so the action can be
referenced later — in particular, by `record-action-taken` at resolution.

The returned `id` MUST be byte-for-byte identical to:

- the `id` field in the YAML frontmatter of the written action file, and
- the `ID` cell in the INDEX.md row appended in Step 10.

Any mismatch between these three values is a fatal implementation error.

---

## Execution Steps

This is a **low-freedom** skill. Steps run in the exact order below. No
reordering, merging, or skipping. Each step depends on the success of the previous one.

1. **Locate and validate `MEMORY.md`** — hard gate. If no path was provided,
   **STOP** and output **exactly and only** the phrase:
   *"To run this skill I need a `MEMORY.md` file that specifies where action records
   will be stored. Please provide the path to your `MEMORY.md`."*
   The backtick formatting on `MEMORY.md` is required. Output nothing else — no
   preamble, no explanation, no other questions. Do not proceed, do not generate an
   ID, do not touch any file. Once the path is supplied, read the file and extract
   the configured storage paths: shared workspace actions folder and, if specified,
   caller-agent local actions folder. If the file does not exist or cannot be read,
   stop and report the error — do not create a `MEMORY.md`; that is the caller's
   responsibility.

2. **Receive input** from the caller — at minimum a `description`; optionally
   `owner`, `due-date`, `source`, `priority`.

3. **Validate description** — if empty, missing, or whitespace-only, **stop and
   error**: *"description is required and cannot be empty"*. No file is written.

4. **ASK-BACK for missing required fields** — if `owner` is missing, ask
   *"Who owns this action?"*; if `due-date` is missing, ask *"When is this due?"*.
   Wait for a reply for each before continuing. If the caller declines to answer,
   **cancel the record** (no partial writes) and exit.

5. **Auto-derive remaining fields** — set `id := UUIDv7()`, `created-at := UTC now`,
   `source := caller-provided OR session-metadata-derived`,
   `priority := caller-provided OR "medium"`.

6. **Privacy check** — if `description` or `source` contains apparent secrets,
   credentials, API keys, tokens, or personal information, prompt the caller before
   continuing: *"This appears to contain sensitive content. Confirm before I write it
   to disk?"* If declined, cancel the record.

7. **Render the markdown record** using the file structure in the Output section.
   Frontmatter and body must conform exactly to the schema.

8. **Write to the shared workspace memories** folder read from `MEMORY.md`. If
   the directory does not exist, create it.

9. **Write a local copy** to the caller-agent's memories folder read from
   `MEMORY.md` — only when the caller is an FBO-framework agent that owns a
   `memories/` folder. Skip this step silently if the caller is a human or a
   non-agent process.

10. **Update `INDEX.md`** in both locations (shared and local, if applicable).
    Append a new row to the index table. If `INDEX.md` does not yet exist at a
    target location, create it with MAGI-compliant frontmatter (via
    `format-md-for-progressive-disclosure`) and the empty table header, then append
    the new row. Do not rewrite earlier rows — actions remain in the index until
    resolved by `record-action-taken`. This step is part of the write transaction:
    the action record is not considered successfully persisted until the correct
    ID row exists in every required `INDEX.md`. If any required index update fails,
    restore affected `INDEX.md` files to their previous contents, delete any action
    files written by this invocation, and return an error.

11. **Return the action `id`** to the caller. The returned value MUST be the
    same UUIDv7 string written to the file frontmatter (`id:` field) and to the
    INDEX.md row (`ID` column). No transformation, abbreviation, or reformatting.

---

## Non-Negotiable Constraints

- **`MEMORY.md` is a hard prerequisite.** Do not write any file, generate any ID,
  or advance past Step 1 until the caller has explicitly provided a path and the
  skill has successfully read it. No default fallback, no silent substitution. Ask
  every single time it is missing.
- **Every action record must carry a UUIDv7 ID generated by this skill.** Caller-
  supplied IDs are rejected. UUIDv7 ensures global uniqueness and time-sortability.
- **Required fields must be collected before any file is written.** ASK-BACK for
  `owner` and `due-date` is mandatory. Silent defaulting is forbidden — the user
  must explicitly opt in to "unassigned" or "none".
- **Existing action files must never be overwritten.** If a UUIDv7 collision is
  detected, regenerate the ID. Surface a warning if collision occurs more than once
  in a single invocation (indicates a clock or generator issue).
- **Apparent sensitive content must trigger an ASK-BEFORE prompt.** The user is
  the final authority on what gets persisted.
- **Output schema is uniform across every invocation.** No per-call variation in
  frontmatter fields, body sections, or index columns. Downstream tools rely on
  this contract.
- **Dual-write atomicity:** if the shared write succeeds but the local-copy write
  fails, roll back the shared write (delete the file just written) before returning
  an error. Partial state on disk is forbidden.
- **Index atomicity:** a written action file without its matching `INDEX.md` row is
  incomplete and MUST NOT be left on disk. If any required `INDEX.md` row cannot be
  created or appended, roll back all action files and any index changes made by
  this invocation before returning an error.
- **Step 1 response is exactly one phrase.** When the skill stops at Step 1 due to
  a missing `MEMORY.md`, the entire output MUST be the specified ask-back phrase —
  nothing before it, nothing after it. Adding preamble (e.g. "Sure, I can help…")
  or appending follow-on questions (e.g. asking for owner simultaneously) is a
  violation.
- **ID consistency is a hard invariant.** The UUIDv7 ID generated in Step 5 MUST
  appear unchanged in three places: the file frontmatter `id:` field, the INDEX.md
  `ID` column, and the value returned to the caller. Any mismatch is a fatal error.
- **Body schema is fixed.** Action record files MUST contain exactly the seven
  frontmatter fields (no more, no less), a `## Description` section with the
  verbatim caller-provided description, and a `## Context` section (empty body is
  allowed; omitting the section is not).

---

## Sub-skills

- **`format-md-for-progressive-disclosure`** (at `sub-skills/format-md-for-progressive-disclosure/SKILL.md`
  relative to the parent `record-action-needed` skill folder) — invoke when
  initialising a new `INDEX.md` in either location to generate MAGI-compliant
  frontmatter. Per-action record files use the inline frontmatter schema defined
  above and do not require this sub-skill.

---

## Edge Cases

| Situation | Behaviour |
| --- | --- |
| `MEMORY.md` path not provided | **STOP at Step 1.** Ask for it. No file written, no ID generated. |
| `MEMORY.md` path provided but file not found or unreadable | **STOP at Step 1.** Report the error. Do not create `MEMORY.md`. |
| `description` is empty, missing, or whitespace-only | Stop. Error: *"description is required and cannot be empty"*. No file written. |
| Caller declines ASK-BACK for `owner` or `due-date` | Cancel entire record. No partial writes. Inform the caller. |
| Caller declines the privacy ASK-BEFORE | Cancel entire record. Inform the caller. |
| Shared-memories write fails | Stop, surface the error. No local copy written. |
| Local-copy write fails after shared write succeeded | Roll back the shared write. Surface the error. No partial state. |
| Shared `INDEX.md` update fails after action file write | Restore the shared index to its previous contents, delete the shared action file, surface the error. No unindexed action file remains. |
| Local `INDEX.md` update fails after shared/local action files were written | Restore any changed index files to their previous contents, delete all action files written by this invocation, surface the error. No partial state. |
| `INDEX.md` does not yet exist at a target location | Create it with MAGI frontmatter (via `format-md-for-progressive-disclosure`) and empty table header, then append the new row. |
| Duplicate `description` from same caller in same session | Warn but still record — UUIDv7 ensures unique IDs; the duplicate may be intentional (e.g. recurring tasks). |
| UUIDv7 collision detected on write | Regenerate ID and retry. Warn if collision occurs more than once. |
| Caller has no `memories/` folder or is not an FBO-framework agent | Skip Step 9 (local copy) silently. Shared write is unaffected. |
| Source metadata not available from session | Set `source = "unknown-session"`. Non-blocking — do not stop for this. |

---

## Foundation

Consult these references when implementing or extending this skill:

- **RFC 9562** — UUIDv7 specification. This skill MUST use a v7 generator (time-sortable) rather than v4 (random-only).
- **`record-action-taken` specification** — companion skill that resolves actions recorded here. The two skills MUST share the same ID schema and frontmatter contract; co-author the specs to avoid drift.
- **`<workspace>/AGENTS.md`** — resolution rules for session metadata, caller-agent identity, and the `memories/` directory layout.
- **`<workspace>/chat-session-scribe/spec-chat-session-scribe.md`** — primary first consumer of this skill at session-end; documents the agent-detected trigger path in detail.

---

## Examples

Two worked examples (slash-command invocation and agent-detected session-end invocation) are in
[`references/examples.md`](references/examples.md).

---

## See Also

- **`record-action-taken`** — companion skill that resolves actions recorded here. MUST share the same ID schema and frontmatter contract.
- **`record-decision-needed`** / **`record-decision-made`** — sibling universal skills covering the *decision* axis of the same memory matrix.
- **`save-agent-memories`** — universal memory persistence skill operating at a different layer (whole-session memories rather than discrete actions).
- **`chat-session-scribe`** specification — primary first consumer of this skill via the agent-detected trigger.
