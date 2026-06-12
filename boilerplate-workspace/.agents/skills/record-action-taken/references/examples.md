# Reference — Examples

Four worked examples covering the main trigger paths. Read this file when you are uncertain which code path applies to the current invocation.

---

## Example 1 — Slash-command, first resolution

**Trigger:** User issues a slash-command with ID, outcome, and note all supplied.

**Invocation:**
```
/record-action-taken A-019e011c-829f-7f3b-ae23-f9a500c77a51 done "Pushed v0.4 to staging at 14:48 UTC, smoke tests green."
MEMORY.md is at ./MEMORY.md
```

**What the skill does:**

1. Reads `./MEMORY.md`. Extracts `shared-actions-root = ./memories/actions`. No `local-actions-root`.
2. Receives `id = A-019e011c-829f-7f3b-ae23-f9a500c77a51`, `outcome = done`, `note = "Pushed v0.4 …"`. All three supplied — no ASK BACK needed.
3. Validates the ID: parses as `A-<uuidv7>`, version nibble = `7`, variant bits = `10xx`. Valid.
4. Locates the record at `./memories/actions/A-019e011c-829f-7f3b-ae23-f9a500c77a51.md` (open path). Status = `open` → first-time resolution.
5. Outcome `done` is in the controlled vocabulary. Note supplied. No privacy concern in the note.
6. Derives `resolved-at = 2026-05-07T14:52:00Z`, `resolved-by = "user"`.
7. Calls `scripts/resolve_action.py --shared-root ./memories/actions --id A-019e011c-829f-7f3b-ae23-f9a500c77a51 --outcome done --note "Pushed v0.4 to staging at 14:48 UTC, smoke tests green." --resolved-by user`.
8. Script moves the file to `./memories/actions/done/A-019e011c-829f-7f3b-ae23-f9a500c77a51.md`, removes its row from `./memories/actions/INDEX.md`, creates `./memories/actions/done/INDEX.md` (did not exist), and appends the row.
9. Script prints: `{"id": "A-019e011c-829f-7f3b-ae23-f9a500c77a51", "outcome": "done", "new-path": "memories/actions/done/A-019e011c-829f-7f3b-ae23-f9a500c77a51.md", "resolved-at": "2026-05-07T14:52:00Z", "was-re-resolution": false}`.
10. Skill reports the new path and outcome to the user, returns the confirmation object.

**Key point:** Because all three inputs were supplied at invocation, the skill runs straight through with no interruptions.

---

## Example 2 — ID not found, fuzzy description fallback

**Trigger:** User asks to resolve an action by ID, but the ID does not exist in any folder.

**Invocation:**
```
Please resolve action A-019e0123-0000-7000-8000-000000000099 as done.
MEMORY.md is at ./MEMORY.md
```

**What the skill does:**

1. Reads `./MEMORY.md`. Extracts `shared-actions-root = ./memories/actions`.
2. Validates the ID: syntactically valid UUIDv7.
3. Searches `./memories/actions/A-019e0123-0000-7000-8000-000000000099.md`, then `done/`, `skipped/`, `obsolete/`, `cancelled/`. Not found anywhere.
4. ASK BACK: *"No record found for ID `A-019e0123-0000-7000-8000-000000000099`. Should I search by description instead, or cancel?"*

**User replies:** `search`

5. ASK: *"What description should I search for?"*

**User replies:** `Update the API documentation for the new auth flow`

6. Fuzzy-matches the description against open-action descriptions in `./memories/actions/INDEX.md` and record bodies. Finds a strong match: `A-019295b1-0000-7000-a000-000000000001` — "Update the API docs for the new auth flow" (owner: Franck).
7. Presents the top candidates: *"I found these open actions — please pick one or cancel: (1) A-019295b1-… — Update the API docs for the new auth flow (Franck) …"*

**User replies:** `1`

8. Continues with `id = A-019295b1-0000-7000-a000-000000000001`, outcome already supplied as `done`. No further ASK BACK needed for outcome or note.
9. Proceeds from Step 5 (read status) onward and resolves normally.

**Key point:** The skill never writes anything to disk before a valid record is confirmed. The fuzzy search is read-only.

---

## Example 3 — Re-resolution, outcome changed (skipped → done)

**Trigger:** User resolves an action that was previously closed as `skipped`. The new outcome differs.

**Invocation:**
```
/record-action-taken A-019e011c-d37a-7fab-a004-91064da644bf done "Actually needed for prod release after all."
MEMORY.md is at ./MEMORY.md
```

**What the skill does:**

1. Reads `./MEMORY.md`. Extracts `shared-actions-root = ./memories/actions`.
2. Validates the ID: valid UUIDv7.
3. Checks the open path — not found. Checks `done/` — not found. Checks `skipped/A-019e011c-d37a-7fab-a004-91064da644bf.md` — found. Status = `skipped` → re-resolution case.
4. Outcome `done` is in the controlled vocabulary. Note supplied. No privacy concern.
5. Derives `resolved-at`, `resolved-by = "user"`.
6. Calls `scripts/resolve_action.py --shared-root ./memories/actions --id A-019e011c-d37a-7fab-a004-91064da644bf --outcome done --note "Actually needed for prod release after all." --resolved-by user`.
7. Script appends a `## Resolution Event 2` block to the body, grows `resolution-history` to two entries, moves the file from `skipped/` to `done/`, removes its row from `skipped/INDEX.md`, creates `done/INDEX.md` (if absent), and appends the row. The open `INDEX.md` is not touched (this action was never open after the prior resolution).
8. Script prints the confirmation object with `"was-re-resolution": true`.
9. Skill reports the move and the re-resolution flag to the user.

**Key point:** The skill searches all per-outcome subfolders, not just the open path. The script handles the re-resolution atomically — the caller does not need to know where the file currently lives.

---

## Example 4 — Agent-detected at session-end, outcome missing

**Trigger:** A `chat-session-scribe` agent wrapping up a session detects a completed action but does not supply an outcome.

**Invocation:**
```
I am the chat-session-scribe agent, wrapping up a session. During this session the user said "we shipped the auth audit logs to staging this morning". The matching open action is A-019e0200-0000-7002-8002-000000000042 ("Add audit logs to the deployment runbook"). MEMORY.md is at ./scribe/MEMORY.md. Please resolve that action with note "Confirmed completion in chat at 09:14 UTC."
```

**What the skill does:**

1. Reads `./scribe/MEMORY.md`. Extracts `shared-actions-root = ./memories/actions`, `local-actions-root = ./scribe/memories/actions`.
2. Validates the ID: valid UUIDv7.
3. Locates the record at the open path in the shared root. Also finds a local copy at `./scribe/memories/actions/A-019e0200-0000-7002-8002-000000000042.md`. Both have INDEX rows.
4. **No outcome supplied.** ASK BACK: *"Was this done, skipped, obsolete, or cancelled?"* — does not default silently.

**Agent replies:** `done`

5. Outcome `done` confirmed. Note already supplied ("Confirmed completion in chat at 09:14 UTC."). No privacy concern.
6. Derives `resolved-at`, `resolved-by = "chat-session-scribe"` (caller is an agent, not a human).
7. Calls `scripts/resolve_action.py --shared-root ./memories/actions --local-root ./scribe/memories/actions --id A-019e0200-0000-7002-8002-000000000042 --outcome done --note "Confirmed completion in chat at 09:14 UTC." --resolved-by chat-session-scribe`.
8. Script performs dual-write atomically: shared file moves to `./memories/actions/done/`, local file moves to `./scribe/memories/actions/done/`, both INDEX files update. If any step fails, all changes are rolled back.
9. Skill returns the confirmation object with `resolved-by = "chat-session-scribe"` to the scribe agent for inclusion in the session summary.

**Key point:** `resolved-by` is derived from the caller's identity — `"chat-session-scribe"`, not `"user"`. The skill never writes before an explicit outcome is confirmed, even when called programmatically.
