# Session-start path — discover and offer active guides

This reference covers the session-start invocation only. The goal is to discover any in-flight restart guides under `memories/restart-guides/active/`, offer the user a chooser, and load the chosen guide's context end-to-end before any task work begins. **No file is written on session start.**

If you are wrapping a session up and need to write or update a guide, read `session-end-writer.md` instead.

---

## Why this path exists

A typical session-start without a chooser costs the agent and the user 20–60 minutes of re-discovery: reading the workspace map, scanning recent commits, re-reading decision records, guessing at where work stopped. A restart guide compresses that cost to about five minutes — but only if the agent reliably finds and reads the guide at the top of the session. This path makes the find-and-read step deterministic.

---

## Inputs the agent needs

- **Path to `memories/restart-guides/`**, relative to the workspace root. Confirm the folder exists before doing anything else. If it doesn't, inform the user — "No restart-guide folder in this workspace yet; nothing to resume" — and exit this path cleanly.
- **Today's date** in `YYYY-MM-DD` form (used for the stale-guide flag).

That is the full input contract for this path. There are no required inputs from the user beyond their session-start utterance.

---

## Step-by-step

### Step 1 — Confirm the folder exists, then read `_index.md`

The `_index.md` at the root of `memories/restart-guides/` is the primary discovery surface. Its **Active** table lists every guide currently in flight.

- Read the file.
- If `_index.md` does not exist or has no rows under **Active**, skip the chooser entirely. Inform the user: "No active restart guides found — starting fresh." Then exit this path. Do not create or write anything; the index is created on the session-end path the first time a guide is written.
- If one or more rows exist under **Active**, continue to Step 2.

### Step 2 — Parse the Active table

The Active table looks like this in the live workspace and the knowledge-base mirror:

```markdown
## Active

Guides for in-flight work, eligible for resume.

| Guide | Topic | Last updated |
|---|---|---|
| [active/2026-05-12-knowledge-base-sync-decisions-and-playbook.md](./active/2026-05-12-knowledge-base-sync-decisions-and-playbook.md) | Knowledge-base 2-way sync: close A.14, A.15, A.16, B.9, B.10, then resume the implementation-playbook rewrite | 2026-05-12 |
```

For each row, extract:

- the relative path to the guide (the link target in the first cell);
- the topic string (second cell);
- the `Last updated` date (third cell).

### Step 3 — Flag stale guides

For each row, compare `Last updated` to today's date. If the difference is **more than 90 days**, flag the guide as stale in the chooser. Do not auto-move stale guides — surface the decision to the user and let them choose whether to resume, mark as abandoned, or leave for later.

A stale guide's row in the chooser should look like:

```
[stale — last updated YYYY-MM-DD, over 90 days ago] Topic — path/to/guide.md
```

### Step 4 — Present the chooser via `AskUserQuestion`

Use the `AskUserQuestion` tool with one question and one option per active guide, plus a "start fresh" option, plus an optional "different — explain" escape. Phrasing template:

> Question: "I found {N} active restart guide(s) for this workspace. Which would you like to resume?"
>
> Options:
>
> 1. "Resume: {topic of guide 1}" — short description noting last-updated date, and "(stale)" suffix if applicable.
> 2. "Resume: {topic of guide 2}" — same pattern.
> 3. … one option per active guide …
> 4. "Start fresh" — no guide loaded; proceed with the session as a new task.
> 5. (optional) "Different — explain" — only include if you have a specific alternative path in mind.

If there is only one active guide, you may still present the chooser to make the choice explicit. The cost of one extra tap is small; the cost of silently loading a guide the user did not want is high.

### Step 5 — Load the chosen guide end-to-end

If the user picks a guide:

1. **Read the entire guide file**. The opening callout will instruct you to do exactly this; honour it.
2. **Internalise the TL;DR, What landed, What is NOT done, Critical sequencing, How to start the next session, Things NOT to redo, and Things to be careful about sections.** These are the seven sections that contain the operational context. The Session log and Pointers sections are useful background but not strictly required to do the work.
3. **Record the guide's filename** so that — when the session ends — the session-end path can update this guide rather than creating a new one. The simplest mechanism is a single in-memory note: `active_restart_guide = "memories/restart-guides/active/<filename>.md"`. Pass this forward to any session-end invocation.
4. **Follow the guide's "How to start the next session" section** before doing any new work. Those steps were written precisely to avoid wasted motion.

If the user picks "Start fresh":

1. Do not load any guide.
2. Proceed with the session as a new task.
3. Record nothing — at session end, the writer path will create a new guide if the task warrants one.

If the user picks "Different — explain" (when offered) or types a custom answer:

1. Accept the user's framing.
2. If they describe a path that maps to a different guide (e.g. "actually, let's look at the superseded one from last week"), read that guide for context but treat it as historical record, not a live resume target.
3. If their framing is genuinely new work, treat it as "Start fresh".

---

## Edge cases

| Situation | What to do |
|---|---|
| `memories/restart-guides/` folder does not exist | Inform the user. Exit this path. The session-end writer will create the folder if a guide ever needs to be written. |
| `_index.md` exists but the Active table is empty | Inform the user: "No active restart guides found." Exit cleanly. |
| Active table row points to a file that no longer exists on disk | This indicates index drift. Surface to the user: "The index references `<path>` but the file is missing — likely an incomplete move." Offer to either remove the row or treat the file as found-elsewhere (search the other lifecycle subfolders). Do not silently delete the row. |
| Active table row has a `Last updated` cell that is malformed (not `YYYY-MM-DD`) | Treat the row as present but skip the stale check. Surface the format issue at the end of the chooser for the user to clean up later. |
| Multiple active guides for what is clearly the same underlying task | Present them all. Surface the duplication to the user — usually one is the live target and the others should be marked `superseded`. The user decides; the session-end writer applies the lifecycle move if asked. |
| User says "ignore the guides, do X instead" without picking an option | Accept as "Start fresh". Do not block on a chooser selection. |
| Guide file's `status:` is `active` but the file lives in a different lifecycle subfolder | Status / subfolder mismatch is a non-negotiable violation per `SKILL.md`. Flag it to the user as a workspace-integrity issue before loading the guide. Offer to run `lifecycle_move.py` to reconcile (you may need to ask which is correct: the status or the location). |

---

## What this path does NOT do

- **Does not write any file.** Including `_index.md`. Including creating the folder structure. If the folder doesn't exist, this path exits — folder creation belongs to the session-end writer's "first-write bootstrap" step.
- **Does not modify any guide.** Even if a stale guide is encountered, this path does not auto-mark it abandoned. That's a user decision, executed by the session-end writer or directly by `lifecycle_move.py`.
- **Does not load anything from `superseded/`, `completed/`, or `abandoned/` by default.** Those are historical record. Only `active/` guides are resume candidates. If the user explicitly asks to read a non-active guide, you may load it as context, but treat it as read-only.

---

## Done criteria

You have finished the session-start path when one of:

- You informed the user that no active guides were found and proceeded with the session as a fresh task.
- The user picked an active guide, you read it end-to-end, you internalised its operational sections, you recorded its filename for the session-end path, and you began following its "How to start the next session" steps.
- The user picked "Start fresh" and you proceeded with the session as a new task.

If none of those is true and you are about to start task work, you have not finished this path. Go back to Step 1.
