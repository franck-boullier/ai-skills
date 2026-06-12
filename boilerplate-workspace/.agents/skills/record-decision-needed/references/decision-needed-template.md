# Decision Needed — File Template

Produces a pending-decision file suitable for the pending folder declared in `decisions.config.md` (e.g. `{domain}/decisions-pending/`). Works for any decision domain — architecture, product, engineering, legal, operational, vendor.

Filename: `{ID}-{kebab-slug}.md` — no date prefix. The date is added when the item is promoted to the closed-decisions folder via `record-decision-made`. The filename uses the undotted form of the ID; the heading uses whatever form the ID series declares.

## decision-type and revisit-trigger are NOT pre-filled

Pending files do NOT carry `decision-type` or `revisit-trigger` in their frontmatter. Both are decided at closure time, not at intake. Even when the question's framing strongly hints at the eventual classification (e.g. the question is itself "what should we do for v0.1?"), `record-decision-needed` does not pre-fill these fields. The decision-maker captures them when they close the decision via `record-decision-made`.

That said, when the open question is itself the reopening of a previously closed temporary decision, the new pending file's `**Supersedes:**` field is pre-seeded with the temporary decision's ID. See the `supersedes-temporary` input documented in this skill's SKILL.md.

---

In the heading below, `{ID-dotted}` is the form declared in the series configuration — `A.11`, `P.3`, `flag6`, etc. — and may be dotted, undotted, or omitted depending on the series. The surrounding filename uses the undotted form (`A11-…md`, `P3-…md`, `flag6-…md`).

````markdown
## ⚠️ {YYYY-MM-DD} — {ID per series convention} {Question title} — PENDING DECISION

**Status:** Pending
**Owner:** {Role or name — who must make the call}
**Deadline:** _____________________________________________
**Review:** _____________________________________________

---

### Context

{One to two short paragraphs. What is the question? Where does it live in the project — which component, column, process, contract, or policy? Why is it open now rather than closed weeks ago?}

### Sources in conflict

- **Source A — {short label}:** {citation — file path, section, and the specific sentence or example that encodes this position}.
- **Source B — {short label}:** {citation — same structure}.
- {Add Source C, D, … as needed. Three sources is common; more than four is usually a sign to split the question.}

### Why this matters

{The concrete downstream impact of the ambiguity. Be specific and quantified where possible — financial exposure, migration cost, compliance risk, user-visible behaviour. "This could cause bugs" is too vague; "A 3× discrepancy in the seed value will corrupt every payout report" is right.}

{If the impact is multi-dimensional, a short numbered list is fine:}

1. **{Dimension}** — {impact}.
2. **{Dimension}** — {impact}.

### Current placeholder

{What is in the project right now while this remains unresolved. "Nothing — the column is deliberately empty and blocks go-live until filled" is a valid placeholder. Name the object explicitly — table, column, contract clause, policy section — so the placeholder can be grep'd.}

### Options

**Option A — {short label}**
{One paragraph. What this option is, what it enables, what it costs, what it forecloses. Name the trade-off in plain terms.}

**Option B — {short label}**
{Same structure.}

**Option C — {short label}**
{Same structure. Include a "no-op / defer" option if that is a genuinely live path, so the decision-maker can see it as a conscious choice rather than an implicit default.}

---

**Decision:** _____________________________________________

**Rationale:** _____________________________________________

**User Override:**
<!-- Leave blank if the accountable party approved the recommendation. Fill in if they changed something. -->

**Rejected:**
<!-- Fill in every proposal explicitly rejected after the decision is made. -->

**Action Items:**
<!-- Pre-seed the tasks that will fire when the decision is made. Dates stay blank. -->
- [ ] {First action — the change specific to this decision} — Owner: {role} — Due: ___ — Review: ___
- [ ] {Second action — docs, spec, or cross-check} — Owner: {role} — Due: ___ — Review: ___
- [ ] Move this file to the closed-decisions folder — Owner: {domain owner from decisions.config.md} — Due: ___ — Review: ___

**Supersedes:** {Date + short ref of any prior decision this re-opens, or `—`.}
**Superseded by:** —

**Source:** {Origin — conversation date, document version, which upstream doc raised the question.}
````

---

## Conventions

### Title line

Start with `## ⚠️` exactly — the warning emoji is how the file is visually flagged in the pending folder and how downstream tooling identifies unresolved items. Use the form `## ⚠️ {YYYY-MM-DD} — {ID per series convention} {Question title} — PENDING DECISION`.

The trailing `— PENDING DECISION` marker is required. It keeps the file obviously unresolved when someone opens it later and lets greps distinguish open items from closed files even when they are moved between folders.

The filename always uses the undotted form. Dotted filenames confuse some filesystems and tooling; keep dots in the heading only, and only when the series declares `heading_form: dotted`.

### Options

A minimum of two options. A one-option pending file is an announcement masquerading as a decision. A maximum of four options in the main body — if more exist, move the unusual ones to a "Rejected at triage" note at the bottom with a one-line reason each. Always include an honest default / no-op option if one exists — forcing a binary choice when a "defer" is live is misleading.

### Action Items pre-seeding

Even though the decision is not made, pre-seed the likely tasks. This signals to the decision-maker what effort the decision will trigger, makes promotion to the closed-decisions folder cheaper because the tasks carry over, and always ends with the "Move this file to the closed-decisions folder" item because that is the final step of closure. The owner on that last item is the default domain owner declared in `decisions.config.md`.

### Status, Deadline, Review

Leave Deadline and Review as underscored blanks. They get filled when the decision is closed — not before. An empty Deadline on a pending file is a feature, not a bug.

### Source

At minimum, name the conversation date and the upstream document that raised the question with a version or section reference — for example, "Schema review conversation 2026-04-20 — `database-schema.md` v0.2 §X.Y" or "Product triage 2026-04-20 — `roadmap-q2.md` v3 §2.1". If a specific review or audit doc raised the question, name it. Vague sources are a red flag — they usually mean the question has drifted away from whatever originally surfaced it.
