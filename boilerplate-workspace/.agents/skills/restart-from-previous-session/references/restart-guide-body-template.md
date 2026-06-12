# Restart-guide body template — the 12 mandatory sections

This reference describes the exact body structure every restart guide must follow. The structure was distilled from two worked examples in the knowledge base: the active guide `2026-05-12-knowledge-base-sync-decisions-and-playbook.md` and the superseded guide `2026-05-10-implementation-playbook-review.md`. Both followed every section below; both are excellent body-content references if you want to see the structure with real content.

The structure is in this order on purpose. The resuming agent reads top-down. Reordering breaks the cost model.

Eleven sections are mandatory. One — Critical sequencing — is conditional (include when dependencies exist between remaining tasks). The total is 12 named sections.

---

## Section 1 — Opening callout (MANDATORY)

A prominent blockquote at the very top of the body, before any heading, telling the resuming agent to read the file end-to-end before doing any task work.

**Template:**

```markdown
> **Read this file end-to-end before doing any task work when resuming.** Run the standard `AGENTS.md` startup workflow first (read `MEMORY.md`, list `.agents/skills/` and read each `SKILL.md` front matter), then come back here. The whole point of this guide is to skip 20–60 minutes of re-discovery — invest five minutes reading instead.
```

The "20–60 minutes" framing is intentional. It tells the resuming agent the size of the cost they are saving, which makes the five-minute read feel like the bargain it is.

---

## Section 2 — TL;DR for the resuming agent (MANDATORY)

3–5 numbered bullets capturing the most important facts about where the work stands. Written for someone with zero prior context on this task — assume the reader has not seen the workspace before, the prior session, or the decisions you opened.

**Each bullet should land one of:**

1. What was already true coming in (and is still true now).
2. What changed in this session.
3. What is blocked on what.
4. The plan from here, in one sentence.
5. Any lurking gotcha the next agent must know.

**Example (excerpted from the KB):**

```markdown
## TL;DR for the resuming agent

1. **The original 2026-05-10 review (tasks 1–9) is still done.** Workspace map refreshed, B.7 (folder rename `00-raw/` → `00-sources/`) closed, B.8 (agent/skill placement) closed, A.13 opened. None of that needs redoing.
2. **The 2026-05-12 session added five pending decisions.** A.14 (Notion-access layer), A.15 (sync runtime substrate), A.16 (HITL by trust tier), B.9 (External ID strategy), B.10 (document-lifecycle property alignment). All five are upstream of the playbook rewrite that was paused on 2026-05-10.
3. **The playbook rewrite is now blocked on more than just A.13.** A.13 may even be superseded depending on how A.14 closes.
4. **The plan is one decision per session, in sequence.** Five short sessions for the five decisions, then one substantial session for the playbook rewrite.
5. **There is also lingering path drift.** Pick up `company-os/` references and the `knowldege-base` typo as part of the final playbook-rewrite session.
```

Aim for 1–3 sentences per bullet. Bold the lede phrase; keep the supporting prose tight.

---

## Section 3 — What this task is, in one paragraph (MANDATORY)

A concise summary of the work and why it matters, understandable without reading any other file. This is the section a brand-new agent reads first if they are deciding whether to take the task.

Cover, in roughly this order:

- the artifact under change (what file or system is being modified);
- the originating reason (what triggered the work);
- the current state (what's in flight);
- the destination state (what "done" looks like).

Keep it to one paragraph — three to five sentences. If you find yourself wanting two paragraphs, you are restating the TL;DR.

---

## Section 4 — What landed this session (MANDATORY)

Concrete record of what changed in this session. Used by the next agent both to avoid redoing work and to verify state.

Use subsections (`###`) to group:

- **Files created, modified, or moved** — list every one. A `text` code block listing paths is the lowest-friction format. Annotate each with `(NEW)`, `(modified)`, or `(moved from …)`.
- **Decisions opened or closed** — a small table with ID, link, and a one-line summary.
- **Conventions established or revised** — short prose for each.

**Example file-list format:**

```markdown
### Files modified this session

```text
memories/restart-guides/                                                                 (NEW folder)
memories/restart-guides/README.md                                                        (NEW)
memories/restart-guides/_index.md                                                        (NEW)
memories/restart-guides/active/2026-05-12-knowledge-base-sync-decisions-and-playbook.md  (NEW — this file)
AGENTS.md                                                                                 (updated — startup workflow now includes restart-guide check)
```
```

For an update (Step 5b in the writer reference), add a new subsection dated by session — do not overwrite the prior session's subsection. The result over time is a layered record of what each session contributed.

---

## Section 5 — What is NOT done (MANDATORY)

The remaining plan. For multi-session tasks, **partition by session**, with clear inputs and expected outputs for each.

For each remaining session:

- A short heading naming the session (e.g. `### Session 3 — Close A.15 (Sync runtime substrate)`).
- **Inputs** — exactly which files the agent must read first.
- **What the session should produce** — the deliverables. Be specific. "Close A.14" is too vague; "Closed `2026-MM-DD-A14-notion-access-layer.md` in `list-decision-made/{final|temporary}/` with `decision-type` filled, paired action plan, updated MEMORY.md counts, session-log entry" is specific.
- **Notable cross-effects** — what this session's outcome forces elsewhere. Helps the next agent recognise downstream impact without reading the whole index.

If the task is single-track (no multi-session partition needed), write the remaining work as a checklist of tasks rather than a session list. The shape is flexible; the discipline of "I will spell out exactly what done looks like" is not.

---

## Section 6 — Critical sequencing (CONDITIONAL — include when dependencies exist)

A text diagram or numbered dependency list showing which items block which. Helps the next agent pick the right next move without re-deriving the graph.

**Text-diagram template (recommended for clarity):**

```markdown
## Critical sequencing

```text
A.14 ── must close first; affects A.13 supersession, A.2 options, A.15 host choice
   ▼
A.15 ── depends on A.14; affects A.16 viability
   ▼
A.16 ── depends on A.15
   ▼
B.10 ── independent of the A-series above; gates chapter 06 trigger logic
   ▼
B.9 ── depends on B.10's Notion-side property additions being practical
   ▼
Playbook rewrite ── all five answers now bake in
```
```

If there are no dependencies between remaining tasks, omit this section. Don't include an empty one.

---

## Section 7 — How to start the next session (MANDATORY)

Exact, numbered steps for the resuming agent. Specific enough to execute without re-deriving context from the rest of the guide.

**Template:**

```markdown
## How to start the next session — exact steps

1. Run the standard `AGENTS.md` startup workflow (read `MEMORY.md`, list `.agents/skills/`, read each `SKILL.md` front matter).
2. AGENTS.md will direct the agent to check `memories/restart-guides/active/`. If this file is still there (it should be), read it end-to-end before any task work.
3. Look at the **Session log** section below to see which sessions have been completed and which is next.
4. Confirm the next session's scope with the user via `AskUserQuestion`. Always offer at least:
   - "Take session N (closing decision X — recommended path)"
   - "Different session — explain"
5. Read the inputs named in the chosen session's **Inputs** sub-section.
6. Invoke the relevant skill (e.g. `record-decision-made`) to do the actual work.
7. After the work: update `MEMORY.md`, update the relevant index, append a one-line entry in the **Session log** below, add a `memories/daily/{YYYY-MM-DD}.md` entry.
```

The numbered structure is non-negotiable. Prose doesn't give the next agent a checkbox-able experience; numbered steps do.

---

## Section 8 — Session log (MANDATORY, APPEND-ONLY)

One line per completed session, **most-recent first** within this section. Append only; never overwrite prior entries.

**Template:**

```markdown
## Session log

Append one line per completed session. Most-recent first within this section.

- **YYYY-MM-DD (this session)** — Brief summary of what landed.
- **YYYY-MM-DD** — Brief summary of what landed in the prior session.
- **YYYY-MM-DD** — …
```

On a fresh guide (Step 5a in the writer reference), the section contains exactly one line — today's entry. On an update (Step 5b or 5c), prepend the new line above existing lines so the newest is on top.

Why most-recent first: the resuming agent reads top-down and needs to know the latest state, not the original state, to act. The Session log is a hot path; the rest of the guide is the cold path.

---

## Section 9 — Things NOT to redo (MANDATORY)

A list with ❌ markers identifying work already complete that a resuming agent might mistakenly repeat. This section saves the next session's time more reliably than any other.

**Template:**

```markdown
## Things NOT to redo

These were done in earlier sessions. The action plans and decision files already document the closure.

- ❌ Do **not** reopen B.7 (`00-sources/` folder rename) — closed and acted on.
- ❌ Do **not** rewrite the spec corpus under `specifications/knowldege-base/`. Those are reports; their text is historical.
- ❌ Do **not** rerun the `document-workspace-structure` skill end-to-end — `WORKSPACE-STRUCTURE.md` is current.
```

Each entry should:

- Start with the ❌ marker.
- Use "Do **not** {verb}" framing — imperative, with `not` bolded for skimmability.
- Add a short reason, even if obvious.

If you have no items here, you're probably under-documenting. Most sessions touch at least one thing that the next agent would otherwise re-investigate. Look harder before leaving the section empty.

---

## Section 10 — Things to be careful about (MANDATORY)

Gotchas, caveats, and cross-effects the resuming agent should know before touching any files. Different from "Things NOT to redo" — that section is about completed work; this section is about live hazards.

**Example entries:**

- **A.14 supersedes A.13 conditionally, not unconditionally.** If A.14 closes as Option B (Complementary) or C (Orthogonal), A.13 is still a live question.
- **B.10 depends on a Notion-side capability that is currently PENDING VERIFICATION.** Don't close B.10 as Option A or B unless you also flag the dependency in the action plan.

Each entry should:

- Be bold-leded with the trap statement.
- Be followed by one or two sentences explaining the consequence.

If you have no items here, double-check. Multi-session work almost always has at least one cross-effect that bit someone this session and could bite again.

---

## Section 11 — Open questions (MANDATORY)

Questions surfaced but not yet answered. Not necessarily blocking the next session, but worth tracking.

**Template:**

```markdown
## Open questions still on the table

These are not blocking the next session but should be tracked:

1. **The `knowldege-base` typo rename.** Worth a decision, or live with it? Both options are real.
2. **Hub-default agents.** Should `workspace-librarian` and `workspace-scribe` be subtree-pulled into every spoke or workspace-only?
```

Numbered list. Bold lede phrase. One or two sentences of context per entry.

If the open question becomes a recorded decision in a future session, link to the decision record from this section in that session's update — but leave the original question text intact for the audit trail.

---

## Section 12 — Pointers (MANDATORY)

Links to the most important files and conventions the next agent should know about. Different from the cross-references scattered through the rest of the guide — this section is a curated short-list.

**Example structure:**

```markdown
## Pointers

- **Sources of truth for this work.** `documentation/implementation-playbook/` (the operating manual being rewritten) and `memories/decision-records/`.
- **The conventions to enforce.** `decisions.config.md`, `AGENTS.md`, and the closed decisions (B.7, B.8, A.14 once closed) govern the folder layout and identity model.
- **Workspace-local skills.** `.agents/skills/record-decision-made/`, `.agents/skills/record-decision-needed/`, `.agents/skills/document-workspace-structure/`. Read each `SKILL.md` front matter on session start.
- **Key references.** Specific files the next agent will need to consult repeatedly.
```

Use bullet form. Bold the category lede; keep each entry's prose tight.

---

## Putting it all together — the section order at a glance

```text
1.  Opening callout                        (MANDATORY)
2.  TL;DR for the resuming agent           (MANDATORY)
3.  What this task is, in one paragraph    (MANDATORY)
4.  What landed this session               (MANDATORY)
5.  What is NOT done                       (MANDATORY)
6.  Critical sequencing                    (CONDITIONAL — include when there are dependencies)
7.  How to start the next session          (MANDATORY)
8.  Session log                            (MANDATORY, APPEND-ONLY, MOST-RECENT FIRST)
9.  Things NOT to redo                     (MANDATORY)
10. Things to be careful about             (MANDATORY)
11. Open questions                         (MANDATORY)
12. Pointers                               (MANDATORY)
```

---

## Worked-example reference

For a full guide that follows this template end-to-end with real content, read the most recent guide in `memories/restart-guides/active/`. If `active/` is empty, read the most recent guide in `memories/restart-guides/superseded/` (the supersession pattern itself is also worth seeing, since it's the second-most-likely lifecycle transition).

If the workspace has no guides yet at all (a fresh deployment), the skill's own development tree ships a `knowledge-base/` mirror with two worked examples — one active guide demonstrating the standard 12-section body, one superseded guide demonstrating the supersession frontmatter pattern. Look there only when the deployed `memories/restart-guides/` is empty; once the workspace has its own guides, those become the canonical reference.
