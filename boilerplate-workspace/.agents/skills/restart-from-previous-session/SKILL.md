---
name: restart-from-previous-session
version: 0.5
compatibility:
  python: ">=3.8"
description: Creates and maintains restart guides — session-handoff documents that capture the in-flight state of multi-session tasks so a future agent can resume in ~5 minutes instead of re-discovering context over 20–60 minutes. At session start, discovers active guides under `memories/restart-guides/active/` and offers a chooser. At session end, writes a new guide or updates the loaded one — capturing files modified, decisions opened/closed, action items in flight, traps, exact next-session steps — and maintains `_index.md` and the lifecycle subfolders. Use this skill whenever the user says "continue where we left off", "resume the previous session", "check if there's a restart guide", "prepare a restart guide", "write a handoff doc", "create a session handoff", invokes `/prepare-restart-guide`, or whenever the agent is starting or ending a session and a multi-session task is in flight — even if the user doesn't use those exact words.
---

# Restart from previous session

This skill manages **restart guides** — self-contained handoff documents that capture the in-flight state of a multi-session task so a future agent (or human) can resume work without reconstructing context from scratch. Guides live under `memories/restart-guides/` in four lifecycle subfolders (`active/`, `superseded/`, `completed/`, `abandoned/`), with a cross-folder `_index.md` as the primary discovery surface.

The skill has two invocation paths. Pick one in Step 0; never run both in the same turn.

---

## Step 0 — Determine invocation mode

Decide which path to follow before doing anything else:

- **Session-start** — the user is opening a session and wants to know whether to resume earlier work. Triggers: `AGENTS.md` startup workflow directs the agent to check `memories/restart-guides/active/`; the user says "continue where we left off", "resume the previous session", "check if there's a restart guide", "what were we working on?", or similar.
- **Session-end** — the user is wrapping up and wants the session's in-flight state captured. Triggers: the user says "prepare a restart guide", "write a handoff doc", "create a session handoff", `/prepare-restart-guide`; or the agent itself recognises that the task is being paused mid-execution and the next session would need workspace-state, decision, or open-question context not already captured elsewhere.

If both contexts seem present in the same turn (rare but possible — e.g. the user resumes a session, finishes some work, then asks to update the guide), run the session-start path first, then run the session-end path as a second invocation.

---

## When NOT to create a guide

A restart guide is for work that will resume in a future session. **Never create one for a single-session task.** If the work can be completed in the current session, close it normally with decision records and action plans — a guide would be noise, not signal. Surface this to the user explicitly if asked to create a guide for trivial or one-shot work.

---

## The two paths

### Session-start path

Goal: discover active guides, offer a chooser, load the chosen guide's context end-to-end. No files are written on session start.

**Read [`references/session-start-chooser.md`](references/session-start-chooser.md) for the full step-by-step**, including how to parse `_index.md`, how to present the chooser, how to flag stale (>90-day) guides, and how to record the loaded guide's filename so the matching session-end update can find it.

### Session-end path

Goal: write a new guide or update the loaded one; perform any lifecycle move triggered by status changes; keep `_index.md` consistent with the on-disk reality.

**Read [`references/session-end-writer.md`](references/session-end-writer.md) for the full step-by-step**, including how to gather session context, the create-vs-update decision, frontmatter construction, body assembly, and the four lifecycle transitions (active → superseded, → completed, → abandoned).

For the actual content shape of the guide — the 12 mandatory body sections — read [`references/restart-guide-body-template.md`](references/restart-guide-body-template.md). The writer reference points to it at the right moment.

---

## Front matter — division of labour with the sub-skill

Every restart guide carries MAGI base front matter (`doc-id`, `title`, `description`, `purpose`, `audience`, `tags`, `key_concepts`, `last-updated`) **plus** six restart-guide-specific fields (`status`, `superseded-by`, `superseded-on`, `superseded-reason`, `closed-on`, `closed-reason`).

To keep front-matter authorship in one place, you **MUST** delegate the MAGI base fields to the sibling sub-skill **`format-md-for-progressive-disclosure`** (located at `sub-skills/format-md-for-progressive-disclosure/` relative to this skill) rather than hand-author those fields inline from memory. The sub-skill is the single source of truth for the MAGI schema; if it evolves (new required field, changed controlled vocabulary), an agent that authors the fields inline will silently produce stale front matter — the delegation pattern exists precisely to prevent that schema drift. Invoke it after you have drafted the guide body but before final write:

1. Write the guide body and the restart-guide-specific fields (`status:` and any closure fields) to a temp path or staging buffer.
2. Invoke `format-md-for-progressive-disclosure` on that staged file. It will infer and add the MAGI base fields, leaving the body and existing front matter untouched.
3. Add the restart-guide-specific fields if not already in place; the sub-skill preserves existing fields and only adds missing ones, so the order is safe.

**Fallback when the sub-skill is unavailable.** If `format-md-for-progressive-disclosure` is not listed in `available_skills` (or its invocation fails for any reason), do NOT silently skip the MAGI base fields. Construct them inline using the schema documented at `sub-skills/format-md-for-progressive-disclosure/references/magi-field-schema.md` as the authoritative reference, and surface to the user that the inline fallback was used so the missing sub-skill can be deployed if needed. The full procedure (and the exact wording for the user-facing notice) lives in `references/session-end-writer.md` Step 5a → step 5.

This skill owns the **six restart-guide-specific fields** and their rules:

```yaml
status: active | superseded | completed | abandoned
# When status is `superseded`, the following are REQUIRED:
superseded-by: "memories/restart-guides/active/<filename>.md"
superseded-on: "YYYY-MM-DD"
superseded-reason: "one-sentence reason"
# When status is `completed` or `abandoned`, the following are REQUIRED:
closed-on: "YYYY-MM-DD"
closed-reason: "one-sentence reason — what was the terminal state?"
```

`status: active` carries none of the closure fields. As soon as a guide moves out of `active/`, the matching closure fields become required. The authoritative definitions of all four statuses live in `knowledge-base/memories/restart-guides/README.md` (or, in a workspace where the skill is deployed, the same `README.md` at the root of `memories/restart-guides/`). Read it before writing if you're unsure about a state.

---

## Filename convention

Every guide is named `YYYY-MM-DD-{kebab-slug}.md`, dated by the day the guide was **created** — not by the day the underlying work began. Date-prefixed filenames keep every subfolder sortable by recency and make grep-friendly cross-references unambiguous. The `kebab-slug` is short, lowercase, hyphen-separated, and describes the task being handed off (e.g. `playbook-rewrite`, `decision-A14-notion-access`).

---

## Non-negotiable constraints

These rules protect the guide-to-index integrity that makes restart guides useful at scale. Treat them as invariants — if you find yourself about to violate one, stop and re-think.

- **Always update `_index.md` when writing a new guide or moving an existing one between subfolders.** A guide and the index must never disagree. Use `scripts/update_index.py` (and, for moves, `scripts/lifecycle_move.py`) rather than hand-editing — these helpers do the multi-step work atomically.
- **Always fill closure fields before moving a guide out of `active/`.** `completed` and `abandoned` guides require `closed-on` and `closed-reason`. `superseded` guides require `superseded-by`, `superseded-on`, and `superseded-reason`. `scripts/lifecycle_move.py` validates this before letting the move proceed.
- **Never delete a guide.** Guides are historical record. Move them to `superseded/`, `completed/`, or `abandoned/` — never delete them. The audit trail is the whole point.
- **Never create a restart guide for a single-session task.** See "When NOT to create a guide" above.
- **Append to the session log; never overwrite prior entries.** Each completed session contributes exactly one line, most-recent first.
- **The `status:` field and the subfolder must always agree.** An `active` guide lives in `active/`; a `completed` guide lives in `completed/`; and so on. `lifecycle_move.py` flips both in lockstep.
- **Never reuse a `doc-id`.** Every guide's `doc-id` is a fresh UUID v7 (time-ordered, RFC 9562) — preferred over v4 because it sorts by creation time and aligns with the date-prefixed filename convention. Use `scripts/generate_uuid_v7.py`; do not copy a UUID from another guide.

---

## Bundled scripts

Three small helpers do the multi-file, error-prone work so the agent doesn't have to compose it by hand. All three are pure-Python, standard-library-only, idempotent where it makes sense, and print explicit per-action diff lines on success (so an agent can verify behaviour from stdout alone — no need to re-read the index after every call).

| Script | Purpose | When the agent calls it |
|---|---|---|
| `scripts/generate_uuid_v7.py` | Print one fresh UUID v7 to stdout. | Every time a new guide is created. |
| `scripts/update_index.py` | Add, update, remove, or move a row in `_index.md`'s four tables; refresh the Quick Status block. Idempotent on add. Each action prints a row-level confirmation line (e.g. `[update_index.py] Moved row 'active/foo.md' ('active' table) -> 'completed/foo.md' ('completed' table) in /path/_index.md`) before the generic `OK:` line. | Every guide create, every guide update with no status change, and as the second step of any lifecycle move. |
| `scripts/lifecycle_move.py` | Validate closure fields, flip `status:` in front matter, physically move the file between lifecycle subfolders, then invoke `update_index.py` to migrate the row. Prints a line per mutation (status flip, file move, index migration) and relays the `update_index.py` stdout, so the full chain is auditable from the call site. | Whenever a guide's status changes (`active` → any of the other three). |

Read each script's `--help` once before first use. The writer reference explains exactly when to invoke them inside the session-end path.

---

## Edge cases at a glance

The session-start and session-end reference files cover edge cases per path. A short cross-cutting table:

| Situation | Behaviour |
|---|---|
| `memories/restart-guides/` folder does not exist | Create it with the four lifecycle subfolders, a stub `README.md` mirroring `knowledge-base/memories/restart-guides/README.md`, and an empty `_index.md`. Then proceed. |
| Slug conflict — proposed filename already exists | Ask the user to choose a different slug, or confirm the existing guide should be updated rather than creating a duplicate. |
| User asks for a guide for a task you judge single-session | Push back. Explain why a restart guide would be noise. Offer to record a decision or action plan instead. |
| User asks to delete a guide | Refuse. Explain the audit-trail rationale. Offer to mark it `abandoned` with a clear `closed-reason` instead. |
| Both paths fire in one turn | Run session-start first, then session-end as a separate logical invocation. |
| `format-md-for-progressive-disclosure` sub-skill is not in `available_skills` (or invocation fails) | Apply the inline fallback documented above and in `references/session-end-writer.md` Step 5a → step 5. Surface the fallback to the user so the missing sub-skill can be deployed. |

---

## Foundation — what the agent reads on demand

Layered loading so the agent only pulls what the current invocation needs:

- **For session-start invocations** — read `references/session-start-chooser.md`.
- **For session-end invocations** — read `references/session-end-writer.md`, then `references/restart-guide-body-template.md` once the create-vs-update decision is made.
- **For status-meaning questions** — the single source of truth is the deployed `memories/restart-guides/README.md` (mirrored during skill development at `knowledge-base/memories/restart-guides/README.md`). Don't duplicate its definitions; point to it.
- **For the index format and Quick Status block** — the live `memories/restart-guides/_index.md` in the workspace; mirrored during skill development at `knowledge-base/memories/restart-guides/_index.md`.
- **For body-structure worked examples** — the most recent guide in `active/`; if none, the most recent in `superseded/`. These were the primary references the skill was distilled from.

---

## How to invoke the skill — quick decision tree

```
User opens a session
  └── Run session-start path
        ├── _index.md missing or Active table empty → inform user, no chooser
        └── 1+ active guides → present chooser → read selected end-to-end

User wraps up a session
  └── Decide: was this a single-session task?
        ├── YES → do NOT create a guide; close normally
        └── NO  → run session-end path
                  ├── No guide loaded at start → create new
                  ├── Guide loaded, same task → update existing
                  └── Guide loaded, different task → ask; usually create new
                                                    + mark old one superseded
```
