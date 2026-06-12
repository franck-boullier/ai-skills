# Decision Made — File Template

Two shapes exist. Pick the one that matches the decision's weight. Both shapes can be used for any decision domain — architecture, product, engineering, legal, operational, vendor — as long as the ID series is declared in the workspace configuration.

## YAML frontmatter — required on every closed decision

In addition to the standard MAGI fields (`doc-id`, `title`, `description`, `purpose`, `audience`, `tags`, `key_concepts`, `last-updated`), every closed-decision file MUST carry:

```yaml
decision-type: final | temporary
```

When `decision-type: temporary`, the file MUST also carry:

```yaml
revisit-trigger:
  match: any-of                # any-of (default — first trigger to fire opens revisit) | all-of
  triggers:
    - type: phase | date | threshold | external
      value: "<concrete description>"
      # For type: threshold, additionally:
      metric: "<metric name>"
      operator: ">" | ">=" | "<" | "<=" | "=="
revisit-notes: |               # Optional free-text — context that doesn't fit the structured fields.
  Why these triggers, who watches for them, what to look at on revisit.
```

When `decision-type: final`, neither `revisit-trigger` nor `revisit-notes` may appear. A final decision with a revisit-trigger block is a contradiction — if the answer has a stated re-evaluation criterion, the decision is `temporary`, not `final`.

When a `temporary` decision is later confirmed as final via the `record-decision-made` confirm-as-final path, its frontmatter gains:

```yaml
confirmed-as-final-on: YYYY-MM-DD
```

The original `revisit-trigger` block is preserved as historical context. The file is moved from `temporary/` to `final/`, and a one-line confirmation note is added under the H2 heading.

---

## Short form

Used for focused decisions without schema DDL, detailed policy text, or significant design detail. Typical for single-issue decisions that can be stated and justified in one or two paragraphs.

Match the heading shape to the ID series declared in `decisions.config.md`. Some series print the dotted ID (`A.{N}`) in the heading; others omit the ID from the heading and keep it only in the filename.

````markdown
## {YYYY-MM-DD} — {Heading per series convention — either `{ID-dotted} {Title}` or just `{Title}`}

**Decision:** {One clear statement of what was decided. If it takes two sentences, split into two decisions.}

**Owner:** {Role or name. One person. If two, the first is accountable and the second supports.}
**Deadline:** {YYYY-MM-DD}
**Review:** {YYYY-MM-DD — strictly later than Deadline. Default: Deadline + 14 days.}

**Rationale:** {Why this over alternatives. One to two sentences in the short form — longer rationales belong in the long form. Explains the *why*, not the *what*.}

**User Override:**
{Leave blank if the accountable party approved the recommendation as offered. Fill in honestly if they changed something: "Owner rejected [recommendation] because [reason]. Actual decision: [what was chosen instead]."}

**Rejected:**
- {Proposal text} — {reason for rejection} [DO_NOT_RESURFACE]
- {Proposal text} — {reason for rejection} [DO_NOT_RESURFACE]

**Action Items:**
- [ ] {Specific action} — Owner: {role or name} — Due: {YYYY-MM-DD} — Review: {YYYY-MM-DD}
- [ ] {Specific action} — Owner: {role or name} — Due: {YYYY-MM-DD} — Review: {YYYY-MM-DD}

**Supersedes:** {Date + short ref of any prior decision this overrides. Dash (`—`) if none.}
**Superseded by:** —

**Source:** {Origin — conversation date, document version, file section, or named artefact.}
````

---

## Long form

Used when the decision carries concrete deliverables — schema DDL, policy text, contract terms, a multi-step implementation flow, or a detailed correctness / compliance argument. Include whichever of the design-detail blocks apply; omit the rest.

````markdown
## {YYYY-MM-DD} — {Heading per series convention}

**Status:** Closed
**Owner:** {Role or name}
**Deadline:** {YYYY-MM-DD}
**Review:** {YYYY-MM-DD}

---

### Decision

{One or two paragraphs stating what was decided. May include numbered design points when the decision has multiple linked parts (e.g. "1. Replace X with Y. 2. Move Z into W.").}

{Optionally: a sentence noting that this decision also closes another item — for example, "This decision also closes A.10 …".}

---

### Design detail

{Optional — include the blocks that apply to this domain. Omit entirely if the short form would have sufficed.}

#### Schema / DDL changes

```sql
CREATE TABLE schema.table (
    id UUID PRIMARY KEY DEFAULT gen_uuidv7(),
    ...
);
```

#### Policy / contract text

{The exact policy language, clause wording, or contract terms that land as part of this decision.}

#### Runtime / operator flow

{A numbered walkthrough so a future reader understands the design without reconstructing it from code.}

---

**Rationale:** {Why this over alternatives. Longer is fine here — include the correctness, compliance, or cost argument that carried the decision.}

**User Override:**
{As in short form.}

**Rejected:**
- **Option A — {name}:** {reason for rejection}. [DO_NOT_RESURFACE]
- **Option B — {name}:** {reason for rejection}. [DO_NOT_RESURFACE]
- **Option C — {name}:** {reason for rejection}. [DO_NOT_RESURFACE]

**Action Items:**
- [ ] {Specific action} — Owner: {role or name} — Due: {YYYY-MM-DD} — Review: {YYYY-MM-DD}
- [ ] {Specific action} — Owner: {role or name} — Due: {YYYY-MM-DD} — Review: {YYYY-MM-DD}

**Supersedes:** {Date + short ref, or `—`.}
**Superseded by:** —

**Source:** {Origin of the decision.}
````

### Optional body section — Revisit trigger (temporary decisions only)

When `decision-type: temporary`, the body MUST include a `### Revisit trigger` section (between the design detail and the Rationale) that mirrors, in human-readable prose, the structured `revisit-trigger:` block in the frontmatter. The two MUST NOT contradict — the `record-decision-made` skill's quality checklist enforces this.

````markdown
### Revisit trigger

Reopen this decision (as a `flag`-series reversal of {ID}) when {one or more of the trigger conditions described in the frontmatter}. The relevant frontmatter block is:

```yaml
revisit-trigger:
  match: any-of
  triggers:
    - type: external
      value: "<short description>"
```
````

---

## Title and heading conventions

The exact heading shape is declared per ID series in `decisions.config.md`. Three shapes are common; match the one that applies to the series you are writing for — do not invent a new shape.

A dotted-ID heading prints the ID as part of the heading text (`## {YYYY-MM-DD} — A.2 {Title}`). The dotted form appears in the heading only; the filename uses the undotted form (`{date}-A2-{slug}.md`).

An omitted-ID heading leaves the ID out of the heading entirely (`## {YYYY-MM-DD} — {Title}`). The ID lives only in the filename. Common for series that restate the decision verbatim in the title — the ID would be redundant in the heading.

An undotted-ID heading prints the ID exactly as it appears in the filename (`## {YYYY-MM-DD} — A2 {Title}`). Less common; declared per series when the workspace prefers consistency between heading and filename.

General title rules: start with the subject, not "Decision to…". `Property address is operational data, not PII` is a title; `Decision to classify property address as operational data` is not. For short-form decisions, keep the title to roughly twelve words or fewer — longer is fine when the series convention restates the decision verbatim. Put detail into the Decision body, not the title.

## Field ordering

Keep fields in the order shown above. Index scripts and downstream tooling rely on this order. Do not insert new top-level fields without also updating this template and the skill's Quality Checklist.
