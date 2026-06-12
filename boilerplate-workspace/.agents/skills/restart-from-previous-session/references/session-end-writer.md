# Session-end path — write or update the restart guide

This reference covers the session-end invocation only. The goal is to capture the in-flight state of the just-finished session in a restart guide so a future agent can resume in minutes. Either a **new guide** is written to `memories/restart-guides/active/`, or the **existing guide** loaded at session start is updated. In both cases, `_index.md` is brought back into agreement.

If you are at session start, read `session-start-chooser.md` instead.

If you are about to write the **body** of a new or updated guide, read `restart-guide-body-template.md` after Step 4 below — it gives the exact 12-section structure the body must follow.

---

## Why this path exists

A session ends with information in the agent's head that nobody else can see: what files moved, what decisions opened, what trap to avoid next time, what numbered step to take first when work resumes. The session-end path moves that information from memory to disk in a form the next session can pick up cheaply.

---

## Inputs the agent needs

**Required at every invocation:**

- **Today's date** in `YYYY-MM-DD` form. Used in the filename (for new guides), the `last-updated` field, and the session-log entry.
- **Path to `memories/restart-guides/`**, relative to the workspace root. The session-end path is responsible for creating this folder structure if it does not yet exist (see Step 0 below).
- **Session context** — what landed this session. Gathered by the agent over the course of the work and confirmed with the user in Step 1.

**Required when updating an existing guide:**

- **`active_restart_guide`** — the filename recorded by the session-start path when the user picked a guide from the chooser. If session-start was not run or no guide was picked, this is empty.

**Required when creating a new guide:**

- **Task slug** — a short kebab-case identifier for the task being handed off (e.g. `playbook-rewrite`). Ask the user if not already known.

**Optional:**

- **User-supplied notes** — additional context or summary text the user wants folded into the guide body.

---

## Step-by-step

### Step 0 — Bootstrap the folder structure if missing

If `memories/restart-guides/` does not yet exist:

1. Create the folder.
2. Create the four lifecycle subfolders: `active/`, `superseded/`, `completed/`, `abandoned/`.
3. Create a stub `README.md` mirroring the convention documented in the deployed workspace (or in `knowledge-base/memories/restart-guides/README.md` during skill development).
4. Create an empty `_index.md` with the four section headings and an empty Quick Status block. Format:

```markdown
# Restart guides — index

Cross-folder index of every restart guide in the workspace.

## Quick status

- **Active:** 0
- **Superseded:** 0
- **Completed:** 0
- **Abandoned:** 0
- **Total:** 0

## Active

| Guide | Topic | Last updated |
|---|---|---|

## Superseded

| Guide | Superseded by | Superseded on | Reason |
|---|---|---|---|

## Completed

| Guide | Closed on | Reason |
|---|---|---|

## Abandoned

| Guide | Closed on | Reason |
|---|---|---|
```

If `memories/restart-guides/` already exists, skip this step.

### Step 1 — Gather and confirm session context

Walk the user through what you captured during the session. Use `AskUserQuestion` or a short prose summary, depending on how much context there is. Cover:

- **Files created, modified, or moved.** Be exhaustive — every file is worth a line in the guide.
- **Decisions opened or closed.** Reference each by ID (e.g. `A.14`, `B.10`) and link to the decision-record file.
- **Action items created, closed, or still in flight.**
- **Known traps.** Anything that cost time this session and should not be repeated next session.
- **Open questions.** Surfaced but not yet answered.

Ask: "Here is what I captured this session — anything to add or correct before I write the guide?" Do not skip the confirmation. The user may know something you don't, and the cost of a stale guide section is paid by the next agent, not this one.

### Step 2 — Confirm or determine the task slug

If an existing guide is being updated, its slug is already fixed (in its filename) — use it.

If a new guide is being created and the slug isn't already known, ask the user: "What short kebab-case label should I use for this guide's filename? (e.g. `playbook-rewrite`, `decision-A14-notion-access`)". Validate that the result is:

- lowercase;
- hyphen-separated;
- 3–60 characters;
- not already used by an existing guide in any of the four subfolders.

If there's a conflict, surface it and ask the user to pick a different slug, or to confirm that the existing guide should be updated rather than creating a duplicate.

### Step 3 — Decide: create new or update existing

| Condition | Decision |
|---|---|
| `active_restart_guide` is empty (no guide loaded at session start) | **Create new.** |
| `active_restart_guide` is set and the session's work matches the same task | **Update existing.** |
| `active_restart_guide` is set but the session addressed a different task | **Ask the user.** Options: "update the existing guide", "create a new guide and mark the old one superseded", "create a new guide and leave the old one untouched". |
| The user explicitly asks to mark the old guide superseded by a new one | **Create new + mark old as superseded.** See Step 5d below. |
| The work is single-session (closed in this turn, no follow-up needed) | **Refuse to create a guide.** Explain why; offer to record a decision or action plan instead. |

### Step 4 — Detect any status transition

Before writing, check whether the session's outcome changes the guide's status:

| Outcome | New status | Required closure fields |
|---|---|---|
| All action items the guide tracks are now closed | `completed` | `closed-on`, `closed-reason` |
| The work has been dropped before completion (scope change, blocker, plan replaced) | `abandoned` | `closed-on`, `closed-reason` |
| A newer guide now covers the same task | `superseded` | `superseded-by`, `superseded-on`, `superseded-reason` |
| Work is still in flight | `active` (no change) | none |

If a status transition is happening, you will need both an **update** to the guide's body and a **lifecycle move** out of `active/`. Steps 5 and 6 below cover both.

Now read [`restart-guide-body-template.md`](restart-guide-body-template.md) for the body structure before continuing.

### Step 5 — Write or update the file

This is the only step that branches by path. Pick the sub-step that matches Step 3's decision.

#### Step 5a — Create new guide

1. **Generate a fresh `doc-id`** by calling `python scripts/generate_uuid_v7.py`. Capture stdout.
2. **Compose the front matter.** Restart-guide-specific fields first:

   ```yaml
   status: active
   ```

   (No closure fields on a fresh active guide.)

3. **Compose the body** following the 12-section template in `restart-guide-body-template.md`. Every section is mandatory except "Critical sequencing", which is included only when there are dependencies between remaining tasks. The session log section contains exactly one line — today's entry.
4. **Write to a temp path** (e.g. `memories/restart-guides/active/.draft-{slug}.md`). Do not write to the final path yet — front-matter base fields are added next.
5. **Invoke the `format-md-for-progressive-disclosure` sub-skill** on the temp file. It will add the MAGI base fields (`doc-id` placeholder, `title`, `description`, `purpose`, `audience`, `tags`, `key_concepts`, `last-updated`). Replace the placeholder `doc-id` with the UUID captured in step 1.

   **If the sub-skill is unavailable** (not listed in `available_skills`, or the invocation fails for any reason), do NOT silently skip the MAGI base fields. Fall back to constructing them inline using the schema documented at `sub-skills/format-md-for-progressive-disclosure/references/magi-field-schema.md`. Surface to the user that the inline fallback was used so the missing sub-skill can be deployed if needed.
6. **Rename the temp file** to its final path: `memories/restart-guides/active/YYYY-MM-DD-{slug}.md`.
7. **Verify the temp file is gone.** A successful rename on a POSIX filesystem removes the source, but in sandboxed or networked filesystems the rename may fall back to copy-then-delete and the delete step may fail silently. Check whether `.draft-{slug}.md` still exists in `active/`:
   - If absent: proceed.
   - If present: attempt one explicit delete. If the delete also fails, do NOT abort — the final guide is already in place — but tell the user verbatim: "Heads-up: the draft staging file `memories/restart-guides/active/.draft-{slug}.md` was left behind by the rename and could not be auto-deleted. Please remove it manually so a future session-start glob doesn't pick it up as an orphaned guide."
8. **Update `_index.md`** by calling:

   ```bash
   python scripts/update_index.py \
     --index memories/restart-guides/_index.md \
     --action add \
     --table active \
     --row-path "active/YYYY-MM-DD-{slug}.md" \
     --topic "<one-line topic summary>" \
     --last-updated YYYY-MM-DD
   ```

   The script refreshes the Quick Status counts as part of the same call.

#### Step 5b — Update existing guide (no status change)

1. **Open the existing guide** at `active_restart_guide`.
2. **Append to "What landed this session"** a new dated subsection (e.g. `### 2026-05-12 session`) listing files modified, decisions touched, conventions added in this session.
3. **Append exactly one line to "Session log"**, most-recent first:

   ```markdown
   - **YYYY-MM-DD (this session)** — one-sentence summary of what landed.
   ```

4. **Update front-matter `last-updated`** to today.
5. **Optionally** update "Things NOT to redo", "Open questions", or "Pointers" if this session added items there.
6. **Update `_index.md`** by calling:

   ```bash
   python scripts/update_index.py \
     --index memories/restart-guides/_index.md \
     --action update \
     --table active \
     --row-path "active/YYYY-MM-DD-{slug}.md" \
     --last-updated YYYY-MM-DD
   ```

   The script finds the row by path and refreshes its `last-updated` cell. Quick Status counts are unchanged.

#### Step 5c — Update existing guide AND lifecycle-move (status changes to completed or abandoned)

1. Do everything in Step 5b for the body update (append to landed, append to log, update last-updated).
2. **Set the new status field** in front matter (`status: completed` or `status: abandoned`).
3. **Fill the required closure fields:**

   ```yaml
   closed-on: YYYY-MM-DD
   closed-reason: "one-sentence reason — what was the terminal state?"
   ```

4. **Invoke `lifecycle_move.py`** to do the physical move and the index migration in one atomic call:

   ```bash
   python scripts/lifecycle_move.py \
     --root memories/restart-guides/ \
     --from active/YYYY-MM-DD-{slug}.md \
     --to completed/   # or abandoned/
   ```

   The script:
   - validates that `status:` and the destination subfolder agree;
   - validates that the required closure fields are present and non-empty;
   - moves the file;
   - calls `update_index.py` internally to remove the row from `Active` and add a row to the destination table;
   - refreshes the Quick Status counts.

#### Step 5d — Create new guide AND mark old as superseded

This is the "create-plus-supersede" pattern, used when this session has reshaped the work enough that a fresh guide is clearer than appending to the old one.

1. **Do everything in Step 5a** for the new guide. Add one extra front-matter field on the new guide:

   ```yaml
   supersedes: "memories/restart-guides/superseded/YYYY-MM-DD-{old-slug}.md"
   ```

   (Forward pointer — optional but useful. The reciprocal `superseded-by` field on the old guide is required.)

2. **Open the old guide** at `active_restart_guide`.
3. **Set its `status:` to `superseded`** and add the required closure fields:

   ```yaml
   superseded-by: "memories/restart-guides/active/YYYY-MM-DD-{new-slug}.md"
   superseded-on: YYYY-MM-DD
   superseded-reason: "one-sentence reason for the supersession."
   ```

4. **Invoke `lifecycle_move.py`** to move the old guide:

   ```bash
   python scripts/lifecycle_move.py \
     --root memories/restart-guides/ \
     --from active/YYYY-MM-DD-{old-slug}.md \
     --to superseded/
   ```

### Step 6 — Verify

After Step 5, the on-disk state should look like:

- The guide(s) you wrote/updated are at their correct paths.
- Each guide's `status:` field matches the lifecycle subfolder it lives in.
- `_index.md` lists each guide in exactly one table, with the correct columns filled.
- Quick Status counts equal the row counts.

Run a quick sanity pass:

1. Read `_index.md` end-to-end. Confirm row counts match the Quick Status block.
2. For each row, confirm the linked file exists at the referenced path and that its front-matter `status:` matches the table it appears in.
3. If anything disagrees, fix by re-running `update_index.py` or `lifecycle_move.py` rather than hand-editing.

Tell the user a one-paragraph summary of what was written and where, plus a link to the active guide (if any) so they can review it.

---

## Edge cases

| Situation | What to do |
|---|---|
| User asks for a guide but the session was clearly single-session | Refuse. Explain: "A restart guide is for work that will resume in a future session — for this, a decision record or action plan is the right tool." Offer to create that instead. |
| Two sessions happen back-to-back without a session-start chooser between them | The `active_restart_guide` variable from the prior session may or may not still be in memory. Treat as "no guide loaded" if you cannot verify the variable, and surface to the user: "I don't see a loaded guide from this turn. Should I update `<filename>` (the most recent active guide on disk) or create a new one?" |
| Slug conflicts with an existing guide in any subfolder | Ask the user to pick a different slug, or to confirm the existing guide is the right target for an update. |
| Required closure fields missing when attempting a lifecycle move | `lifecycle_move.py` refuses the move and prints which fields are missing. Add them to the front matter and retry. |
| `_index.md` got out of sync (Quick Status counts don't match table row counts) | Don't hand-edit. Re-run `update_index.py` with `--action recount` to refresh the Quick Status block from the table contents. |
| `format-md-for-progressive-disclosure` sub-skill is not available in `available_skills` (or invocation fails) | Do NOT silently skip the MAGI base fields. Construct them inline using the schema at `sub-skills/format-md-for-progressive-disclosure/references/magi-field-schema.md` as the authoritative reference. Tell the user the inline fallback was used so the missing sub-skill can be deployed if needed. (See Step 5a → step 5 for the procedure.) |
| Front-matter sub-skill produces base fields that conflict with the restart-guide-specific fields | The sub-skill only adds missing fields and preserves existing ones, so this should not happen. If it does, the bug is in the sub-skill, not here — preserve the restart-guide-specific fields and report the conflict. |
| Temp staging file (`.draft-{slug}.md`) survives the rename in Step 5a step 6 | A network or sandboxed filesystem may copy-and-not-delete on rename. Attempt one explicit delete. If it still fails, the final guide is in place — leave it, and tell the user the orphaned draft must be removed manually so a future session-start glob doesn't pick it up. (See Step 5a → step 7 for the procedure.) |
| User wants to record a session that touched multiple distinct tasks | Ask whether to create one combined guide or one guide per task. The cost of two guides is small; the cost of conflating two tasks in one guide is paid every future session. |

---

## What this path does NOT do

- **Does not delete any guide.** Even if the user asks. Move to `abandoned/` instead and fill `closed-reason` with an honest explanation.
- **Does not modify guides in `superseded/`, `completed/`, or `abandoned/`.** Those are historical record. The only legitimate edit to a non-active guide is the supersession-pointer write in Step 5d (which happens just before the move, while the guide is still technically in `active/`).
- **Does not edit the deployed `memories/restart-guides/README.md`.** That is convention documentation, not working memory.

---

## Done criteria

You have finished the session-end path when all four are true:

1. A guide is written or updated to reflect this session's work, with all 12 body sections filled and front matter complete.
2. Any status transition is reflected both in `status:` and in the file's lifecycle subfolder location.
3. `_index.md` lists the guide in exactly one table, the row's columns are correct, and the Quick Status counts match the on-disk reality.
4. The user has been told, in one paragraph, what was written and where.
