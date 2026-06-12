---
name: record-action-taken
description: >-
  Resolves a previously-recorded pending action by marking it done, skipped,
  obsolete, or cancelled, capturing resolution metadata, moving the record into
  a per-outcome archive folder, and updating the open and per-outcome INDEX.md
  files. Use this skill any time a user or agent declares an action is
  finished, no longer needed, or being abandoned — including phrasings like
  "mark this done", "we already did X", "skip the follow-up on Y", "Z is
  obsolete now", "close action <ID>", or any slash-command of the shape
  /record-action-taken, /resolve-action, /action-done. Also use it
  programmatically when a session-end agent (e.g. chat-session-scribe)
  detects that an open action has been completed during the session. Always
  use this skill — never edit the action file by hand — because the resolution
  must be recorded with timestamp, actor, outcome, and history, and because
  the file must move atomically between folders alongside two INDEX.md
  updates. The skill requires a caller-supplied MEMORY.md path; without it the
  skill stops before doing anything.
metadata:
  author: fbo
  version: "0.3-draft"
  status: draft
  spec-doc-id: 8385713f-37ed-4e72-bd36-3441a6c6796f
  companion-skill: record-action-needed
compatibility:
  python: ">=3.9"
  pip:
    - pyyaml
---

# Skill — Record Action Taken

This skill resolves an action item that was previously captured by `record-action-needed`. It is the **resolution end** of the pending-action lifecycle. The action's record is updated in place with resolution metadata, then moved into a per-outcome archive folder so the working list of open actions stays clean while the audit trail is preserved on disk.

This is a **low-freedom** skill: the steps below run in order, and skipping or reordering them breaks the audit trail or leaves the filesystem in a partial state. Most of the deterministic work (atomic moves, frontmatter merge, index updates, rollback on failure) is delegated to `scripts/resolve_action.py` so the agent does not have to perform brittle multi-file mutations by hand.

## When to use this skill

Trigger on any of these intents:

1. **Slash-commands** — `/record-action-taken`, `/resolve-action`, `/action-done`, or any equivalent the host exposes.
2. **Natural-language imperatives** — "mark this action as done", "resolve action `<ID>`", "close this action", "this action is complete".
3. **Action-completion phrasing** — "we did X", "X is done", "completed: X", "skipping action X", "X is obsolete now". Trigger when the user is declaring resolution even without an imperative verb.
4. **Agent-detected at session-end** — when an agent (e.g. `chat-session-scribe`) is wrapping up a session and identifies actions that were completed during the session, it calls the skill programmatically for each one.

## Prerequisite: MEMORY.md (hard gate)

**Do nothing on disk until the caller has supplied a path to a `MEMORY.md` file and you have read it.** This is a hard gate, not a soft warning.

If the caller has not supplied a `MEMORY.md` path, stop and prompt verbatim:

> *"This skill requires a `MEMORY.md` file to determine where to store the resolved action record. Please provide the path to your `MEMORY.md` file."*

`MEMORY.md` is a markdown file written for an LLM to read. It tells you where this caller's memories live. There is no rigid schema — read it, understand it, and extract two paths:

- **shared-actions-root** — the workspace-level actions folder (typically something like `<workspace>/memories/actions/`). This is the source of truth.
- **local-actions-root** *(optional)* — the caller-agent's local actions folder, if the caller is an FBO-framework agent with its own `memories/`.

If `MEMORY.md` is genuinely ambiguous about either path, ASK BACK to the caller with a concrete guess and confirm before proceeding. Never invent a default; never hardcode `<workspace>/memories/actions/`.

## Inputs

| Field | Provided by | If missing |
| --- | --- | --- |
| `MEMORY.md` path | Caller (**mandatory**) | STOP, prompt as above. |
| `id` | Caller (required, UUIDv7 of the form `A-<uuidv7>`) | Stop and error: *"id must be a valid UUIDv7"*. No file is touched. |
| `outcome` | Caller (optional) | ASK BACK: *"Was this done, skipped, obsolete, or cancelled?"* No silent default. |
| `note` | Caller (optional) | Default to `"No note provided."`. Do **not** ASK BACK — the note is genuinely optional. |
| `description-search` | Caller (rare, fallback only) | Used only when ID lookup fails and the caller agrees to a fuzzy fallback (Step 4a). |
| `resolved-at` | Auto-generated | UTC ISO-8601 timestamp at write time. **Never** accepted from the caller. |
| `resolved-by` | Auto-generated | The caller's identity — agent name when invoked by an agent, `"user"` when invoked by a human via slash-command or NL imperative. **Never** accepted from the caller. |

**Outcome controlled vocabulary**: `done`, `skipped`, `obsolete`, `cancelled`. Nothing else. Synonyms ("complete", "won't do", "scrapped"…) are not accepted — re-prompt instead. See `references/outcomes.md` for the meaning of each.

## Execution flow

Run these steps in order. Each depends on the previous one succeeding.

1. **Read `MEMORY.md`**. Extract `shared-actions-root` and, if applicable, `local-actions-root`. ASK BACK if ambiguous.

2. **Receive input** — at minimum an `id`; optionally `outcome` and `note`.

3. **Validate `id`** — confirm it parses as `A-<uuidv7>`. If malformed, stop and error: *"id must be a valid UUIDv7"*. The helper script (`scripts/resolve_action.py`) also validates, but checking early avoids wasted work.

4. **Locate the record.** Look it up by ID in this order:
   - `<shared-actions-root>/A-<id>.md` (the open path)
   - `<shared-actions-root>/done/A-<id>.md`
   - `<shared-actions-root>/skipped/A-<id>.md`
   - `<shared-actions-root>/obsolete/A-<id>.md`
   - `<shared-actions-root>/cancelled/A-<id>.md`

   If found anywhere, note whether the record is at the open path or in a per-outcome subfolder — this determines whether the resolution is first-time or a re-resolution. If found in a per-outcome subfolder, this is a **re-resolution** case — continue normally; the script handles both cases given only `--shared-root` and `--id`.

   - **4a. Not found anywhere** — ASK BACK: *"No record found for that ID. Should I search by description, or cancel?"*
     - On `cancel` → stop, no writes.
     - On `search` → ASK for the description, then fuzzy-match against open actions (descriptions in `<shared-actions-root>/INDEX.md`, plus bodies of `A-*.md` files in the open folder). Present the top 3 candidates with their IDs and one-line summaries; ask the caller to pick one or cancel.
     - On `no match` → error: *"No open action matches that description"*. No writes.

5. **Read the record's frontmatter `status`.** If it is malformed or missing, stop and error. If it is `open`, this is a first-time resolution. If it is one of `done | skipped | obsolete | cancelled`, this is a re-resolution case — the body's resolution-history will be appended (see `references/re-resolution.md`).

6. **Resolve the outcome.** If the caller provided one, validate it is in the controlled vocabulary. If not provided, ASK BACK: *"Was this done, skipped, obsolete, or cancelled?"* Wait for one of those four exact values. If the caller cancels the prompt, stop with no writes.

7. **Note remains optional.** If not provided, set the note to `"No note provided."` Do not ASK BACK.

8. **Privacy ASK BEFORE.** If the note appears to contain secrets, credentials, API keys, tokens, or personal information, prompt: *"This appears to contain sensitive content. Confirm before I write it to disk?"* On decline, cancel the entire resolution. (When in doubt, ask. Better an extra prompt than a leaked secret.)

9. **Auto-derive metadata.** `resolved-at = UTC now (ISO-8601)`. `resolved-by = caller identity` — your agent name if you are an agent calling this skill, or `"user"` when triggered by a human via slash-command or NL imperative.

10. **Call the helper script** to perform the atomic update:

    ```bash
    python scripts/resolve_action.py \
      --shared-root <shared-actions-root> \
      [--local-root <local-actions-root>] \
      --id <A-uuidv7> \
      --outcome <done|skipped|obsolete|cancelled> \
      --note "<note text>" \
      --resolved-by "<actor>" \
      [--resolved-at <iso8601>]
    ```

    The script:
    - validates the UUIDv7,
    - locates the record (open or per-outcome),
    - merges frontmatter (preserving every original field; updating `status`, `resolved-at`, `resolved-by`, `resolution-status`, `resolution-note`; appending to `resolution-history`),
    - appends a `## Resolution` (or `## Resolution Event N`) block to the body,
    - moves the file atomically to the new outcome folder (or leaves it in place when the outcome did not change),
    - removes the row from the open `INDEX.md` and recomputes its `**Quick status:**` count,
    - appends a row to the per-outcome `INDEX.md` in the live shape (markdown-link ID; `ID · Description · Owner · Resolved · Note`, Description/Owner carried over from the source row), recomputes its count, and generates the index inline (H1 + description + `**Quick status:**` line + table header — no frontmatter) if it does not yet exist,
    - mirrors all of the above into `local-actions-root` if supplied,
    - rolls back every partial change if any step fails,
    - prints a JSON confirmation: `{"id":..., "outcome":..., "new-path":..., "resolved-at":..., "was-re-resolution":...}`.

    See `references/script-contract.md` for full argument and exit-code documentation.

11. **Read the script's JSON output and report back** to the caller — typically by quoting the new path and outcome so the user can audit the change. If the script exits non-zero, surface the error verbatim and do not retry.

12. **Return the confirmation object** `{id, outcome, new-path, resolved-at}` to the caller for chaining (e.g. into a session-end summary).

## Output shape (after a resolution)

The action record's frontmatter is extended with resolution fields; original fields from `record-action-needed` are preserved exactly. The body gains a `## Resolution` section (or, on re-resolution, a `## Resolution Event N` section). See `references/record-shape.md` for the full template, and `references/re-resolution.md` for re-resolution semantics.

The file moves from `<shared-actions-root>/A-<id>.md` to `<shared-actions-root>/<outcome>/A-<id>.md`. The corresponding row leaves the open `INDEX.md` and joins the per-outcome `INDEX.md`. If the caller is an agent with a local copy, the same move and index updates mirror in the local tree.

## Non-negotiable constraints

These exist because the audit trail and on-disk consistency are the whole point of the skill. Violating them defeats its purpose.

- **`MEMORY.md` is a hard prerequisite.** Nothing reads, writes, or moves on disk until a valid path has been supplied and the file has been read.
- **Outcome must be one of the four controlled values.** No synonyms, no free-form text, no silent defaulting.
- **The outcome must be declared explicitly** — at invocation or via ASK BACK. Resolution without an explicit outcome is forbidden.
- **The action's `id` must appear in `resolution-history`** for every resolution event. Nothing is silently overwritten.
- **Original fields from the `record-action-needed` write are preserved exactly.** Resolution adds metadata; it never alters `description`, `owner`, `due-date`, `priority`, `source`, `created-at`, or `id`.
- **Apparent sensitive content in the note triggers ASK BEFORE.** Mirrors the privacy rule applied at action creation.
- **Dual-write atomicity.** If any of {shared move, local move, shared INDEX update, local INDEX update} fails after another has succeeded, roll back to the pre-resolution state. The helper script enforces this; do not call shell `mv`/`sed` by hand to bypass it.
- **The skill never deletes a record.** "Cancelled" is a status with its own folder, not a deletion. Every state change is preserved on disk via `resolution-history`.
- **The skill never alters an `id`.** UUIDv7 IDs are immutable across the entire lifecycle.

## Sub-skills

- **`format-md-for-progressive-disclosure`** — relevant when initialising a new per-outcome `INDEX.md` (e.g. the first action ever resolved as `cancelled` triggers creation of `cancelled/INDEX.md`). The helper script generates the per-outcome `INDEX.md` **inline**, matching the live actions-store convention (an H1 title, a one-line description, a `**Quick status:** N … actions` count line, and the `| ID | Description | Owner | Resolved | Note |` table — **no** MAGI frontmatter, because the live actions indexes carry none). It does not invoke the sub-skill directly; `references/index-template.md` documents that shape for reference but is not read at runtime.

## Bundled resources

- `scripts/resolve_action.py` — the atomic update + move + reindex helper. Always use this rather than performing the file mutations by hand.
- `references/examples.md` — four worked walkthroughs covering the main trigger paths (slash-command happy path, ID-not-found fuzzy fallback, re-resolution, agent-detected with missing outcome). Read this when uncertain which code path applies.
- `references/record-shape.md` — full frontmatter and body template for the resolved record.
- `references/index-template.md` — reference example of a per-outcome `INDEX.md` in the live shape (H1 + description + `**Quick status:**` line + the `ID · Description · Owner · Resolved · Note` table). Documentation only — the script generates this inline.
- `references/outcomes.md` — semantics of `done` / `skipped` / `obsolete` / `cancelled`, and how to disambiguate them when the caller is uncertain.
- `references/re-resolution.md` — what happens when an already-closed action is resolved again (outcome unchanged vs. outcome changed).
- `references/script-contract.md` — full argument, output, and exit-code contract for `resolve_action.py`.

Read a reference only when its content is needed — they are intentionally short and scoped.

## Edge cases

| Situation | Behaviour |
| --- | --- |
| `MEMORY.md` not supplied | STOP before Step 1. Prompt verbatim. No reads, no writes. |
| `id` missing, malformed, or not a UUIDv7 | Stop, error: *"id must be a valid UUIDv7"*. No writes. |
| `id` not found at the open path | ASK BACK on whether to fuzzy-search by description (Step 4a). |
| `id` not found at any path (open or per-outcome) | After fuzzy search exhausts the open set, error: *"No record found"*. Do not create orphan resolution records. |
| Caller supplies an `outcome` outside the controlled vocabulary | Stop, error, then re-ask if interactive. |
| Caller cancels the ASK BACK on outcome | Cancel the entire resolution. No partial writes. |
| Caller declines the privacy ASK BEFORE | Cancel the entire resolution. Inform the caller. |
| Re-resolution, outcome unchanged | Allowed. Body's `resolution-history` grows by one event; a new `## Resolution Event N` section appends; file does **not** move; indexes are **not** touched. |
| Re-resolution, outcome changed | File moves between per-outcome subfolders; both indexes update; history accumulates. |
| Per-outcome `INDEX.md` does not yet exist | Helper script generates it inline in the live shape (H1 + description + `**Quick status:**` line + `ID · Description · Owner · Resolved · Note` header), appends the row, and recounts. No MAGI frontmatter; the script never invokes `format-md-for-progressive-disclosure` directly. |
| Caller is not an FBO agent and has no `memories/` folder | Skip all local-copy operations silently. Source-of-truth shared writes are unaffected. |
| `resolution-history` array does not yet exist on the record | Create it as an empty array, then append the new event. (Records written by earlier versions of `record-action-needed` may not have it yet.) |
| Filesystem move fails partway | Helper script rolls back any other partial writes and surfaces the error. No partial state on disk. |

## See also

- **`record-action-needed`** — companion skill that creates the records this one resolves. Shares the same ID schema and frontmatter contract.
- **`record-decision-needed`** / **`record-decision-made`** — sibling universal skills covering the *decision* axis of the same memory matrix.
- **`format-md-for-progressive-disclosure`** — used when initialising new per-outcome `INDEX.md` files.
- **`chat-session-scribe`** — primary agent consumer of the skill via the agent-detected trigger path.
