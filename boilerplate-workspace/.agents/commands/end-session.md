---
name: end-session
description: Clean session shutdown. Runs the full end-of-session protocol — persists Tier-2 memories, closes or opens decisions and actions, creates/updates the restart guide for in-flight work, updates MEMORY.md if warranted, then verifies everything was written before reporting what is still open. Usage: /end-session
---

# /end-session

Run the structured end-of-session protocol so nothing meaningful is lost between sessions. This is the mirror of the session-start workflow in `AGENTS.md`: start loads context, `/end-session` persists it.

Run the protocol **autonomously end-to-end**, then report. Do not pause for confirmation at each step — gather session state, write everything, verify it, and present a single closing report. Only stop to ask if you hit a genuine ambiguity you cannot resolve from the session (a decision you cannot classify, a file you are unsure you may overwrite).

Act as a thought partner.
DO NOT GUESS!
Ask questions if you have ANY doubt about what to persist or where it belongs.

## Usage

```bash
/end-session
```

## Behaviour

Work through these steps in order. Skip a step only when it genuinely does not apply this session, and say so in the report.

1. **Reconstruct the session.** Review what happened since the session began: facts learned, preferences expressed, decisions reached, questions left open, actions promised, files changed. This is the raw material every later step draws from.

2. **Persist Tier-2 memories.** Use `save-agent-memories` to classify and write each durable fact to the correct topical store (preferences, projects, activities, decisions, lessons, people, environment, analysis, daily session log). One fact per entry. No duplication between the shared store and an agent's dedicated store.

3. **Close and open decisions.**
   - For every question the user (or responsible party) confirmed, approved, or finalised this session, use `record-decision-made` to close it — preserving the rationale and **every rejected alternative**, with a paired action plan. Link and update, never delete, any superseded record.
   - For every question that surfaced but **could not be resolved this session**, use `record-decision-needed` to capture it — the question, conflicting sources, live options with trade-offs, and any placeholder.

4. **Close and open actions.**
   - For every action item completed, skipped, or abandoned this session, use `record-action-taken` to resolve it and move it to the right per-outcome archive.
   - For every new follow-up the session produced, use `record-action-needed` to capture it into the action list.

5. **Create or update the restart guide.** Always invoke the `restart-from-previous-session` **session-end path** and let that skill decide the outcome: create a new guide if multi-session work is in flight, update the guide that was loaded at session start if it is the same task, or skip (and say so) if this was a single-session task that closed cleanly. Let the skill own the `_index.md` and lifecycle-folder bookkeeping via its bundled scripts — do not hand-edit those.

6. **Run `format-md-for-progressive-disclosure`** on every new or edited `.md` file in `knowledge-base/` or `memories/` so it carries MAGI front matter and is discoverable without a full read. (The decision, action, and restart skills already do this for their own outputs — apply it to anything they did not cover.)

7. **Update `MEMORY.md`** at the workspace root **only if** a section was added or removed this session. Keep it under 4 KB. Do not rewrite the index for routine entries — the topical stores already hold those.

8. **Verify, then report** (see below).

## Verification

Before declaring the session closed, run all four checks. Treat a failure as work that is not done — fix it, then re-verify.

- **Re-read what was written.** Re-open each file you created or updated and confirm it actually persisted, with correct front matter and the intended content. Do not trust that a write succeeded — look.
- **Index consistency.** Confirm `MEMORY.md`, the decision-records indexes, the action `INDEX.md` files, and the restart-guide `_index.md` all agree with on-disk reality — no orphaned rows, no missing rows, counts correct.
- **AGENTS.md conventions.** Confirm every new file follows the workspace rules: MAGI-compliant YAML front matter, the `YYYY-MM-DD-HH-MM-<slug>` filename pattern for dated artefacts, no hard-wrapped prose paragraphs, relative cross-links inside the workspace.
- **Open-items report.** Produce an explicit list the user can act on before the next session.

Double-check your work before marking it complete: this work will be reviewed, and we do not want to be caught missing something important.

## Output Structure

- Tier-2 memory entries written (preferences, projects, activities, decisions, lessons, daily log)
- Decisions closed this session (`list-decision-taken/`) and decisions newly opened (`list-decision-needed/`)
- Actions resolved and actions newly recorded
- Restart-guide outcome — created / updated / skipped, with the guide filename and status
- `MEMORY.md` index updated only if a section was added or removed
- Verification results — each of the four checks passed, or what was fixed to make it pass
- Open decisions, pending actions, and active restart guides the user should review before the next session

## Skill Reference

- `save-agent-memories`
- `record-decision-made`
- `record-decision-needed`
- `record-action-taken`
- `record-action-needed`
- `restart-from-previous-session`
- `format-md-for-progressive-disclosure`
