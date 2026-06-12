# Worked Examples

Three representative scenarios showing the complete set of artefacts this skill produces. All examples use invented content — they are illustrative, not authoritative decisions. They cover three domains so readers can see how the skill generalises: database architecture, a fresh product decision, and a vendor-selection reversal.

All path references below use the shapes declared in `decisions.config.md`. The examples show a workspace where the `db-architecture`, `product`, and `vendor` domains have each been configured.

---

## Example 1 — Promotion of a pending item (database architecture, A.5 Insurance Model)

### Input

The accountable party says: *"Let's close A.5 with Option C — external broker only. Owner is Finance, deadline mid-May. Reason: MAS licensing for an internal pool is too heavy for Phase 3."*

A pending file exists at the path declared by the `db-architecture` domain: `strymin-portal/db-architecture-decision-needed/A5-insurance-model.md`.

### Actions

Read the pending file first to carry over Context, Sources in conflict, and Options into the closed decision. Create the closed file at `strymin-portal/db-architecture-decisions/2026-04-20-A5-insurance-external-broker.md` using the long form — the decision carries DDL implications (provider catalogue, `provider_id NOT NULL`). Create the paired action plan at `strymin-portal/db-architecture-decision-action-plans/2026-04-20-A5-action-plan.md` with one task per Action Item from the decision.

Append a row to `strymin-portal/db-architecture-decisions/_index.md`:
`| [2026-04-20-A5-insurance-external-broker.md](./2026-04-20-A5-insurance-external-broker.md) | 2026-04-20 | Insurance — external broker only (MAS complexity) | ✅ Closed |`

Before deleting the pending file, verify on disk that the closed decision file and the action plan file both exist and contain their expected headings (Step 6 invariant check). Once confirmed, delete `strymin-portal/db-architecture-decision-needed/A5-insurance-model.md` and update the pending index: remove the `A5-insurance-model.md` row, add `> **A5 closed 2026-04-20** — moved to db-architecture-decisions/` (or append to an existing same-day line), update Quick status counts, and bump `last_updated` to `2026-04-20`.

Key fields in the resulting closed file: the `Rejected` section lists Options A and B from the pending file, each with a reason and the `[DO_NOT_RESURFACE]` tag. The `Source` line cites the pending file's original source plus today's conversation. `Supersedes` is `—` because A.5 had no prior resolution.

---

## Example 2 — Fresh product decision with no pending file

### Input

The accountable party says: *"We're shipping the new onboarding flow with no email verification at sign-up — mobile verification only. Owner: Product, due end of month."*

No matching pending file exists.

### Actions

Skip the pending-file lookup — there is nothing to promote. Pick a new ID in the `product` domain. Scanning the closed and pending indexes, the highest existing `P`-series integer is `P4`, so the next ID is `P5`. Create `product/decisions/2026-04-20-P5-mobile-verification-only-onboarding.md` using the short form — the decision does not carry DDL or contract text, and one paragraph of rationale is sufficient. Create `product/decision-action-plans/2026-04-20-P5-action-plan.md`. Append a row to `product/decisions/_index.md`. Do not touch `product/decisions-pending/` — no pending file existed.

Traps to avoid on fresh decisions: the `Rejected` field cannot be empty. If no alternatives were discussed, record the implicit default that was rejected — for example, "Require both email and mobile verification — rejected because onboarding drop-off at the email step is currently 23 %, and mobile already satisfies the regulatory requirement. [DO_NOT_RESURFACE]". The `Rationale` cannot be "leadership decided it" — capture the reason leadership decided it, even if one clarifying question is needed. "Because mobile verification alone meets KYC for Phase 2 markets and removes a friction point responsible for 23 % drop-off" is a rationale; "Product owner chose it" is not. The `Deadline` must be concrete — "end of month" resolves to a specific date; write the date.

---

## Example 3 — Vendor reversal that supersedes a prior decision

### Input

The accountable party says: *"We're switching the email provider from SendHawk back to RelayMail. Their deliverability in APAC is 14 points higher in the last three months of data, and they've matched SendHawk's price. Close the reversal. Owner: Platform."*

A prior closed decision exists at `vendor/decisions/2025-11-03-V2-sendhawk-email-provider.md` naming SendHawk as the chosen provider.

### Actions

Scan both vendor indexes for the next free ID. The highest existing `V`-series integer is `V7`, so the next ID is `V8`. Because this is a reversal of a specific prior design, the workspace convention for reversals uses a `flag`-style ID — but the `vendor` domain in this example does not declare a flag series, so the decision uses the regular `V` series and explicitly calls out the `Supersedes` relationship.

Create `vendor/decisions/2026-04-20-V8-relaymail-email-provider.md` using the long form — the decision carries contract terms (the RelayMail agreement) and a multi-step migration flow. Create `vendor/decision-action-plans/2026-04-20-V8-action-plan.md`. Append a row to `vendor/decisions/_index.md`.

Crucially, edit the prior decision at `vendor/decisions/2025-11-03-V2-sendhawk-email-provider.md` to set `Superseded by: 2026-04-20 — V8` — the forward-pointer is what makes the supersede chain discoverable. The new file's `Supersedes` field points back: `2025-11-03 — V2 (SendHawk)`.

The `Rejected` field in the new decision must include "Stay with SendHawk — rejected because deliverability in APAC has trailed the benchmark by 14 points for three consecutive months and the original cost advantage has disappeared. [DO_NOT_RESURFACE]". Without that entry, a future reviewer cannot see that the status quo was considered and dropped deliberately.

---

## Counter-example — when *not* to use this skill

The accountable party says: *"I'm not sure whether we should use UUID v7 for primary keys. Let's think about it."*

This is an open question. Do not produce a decision file. Use the `record-decision-needed` skill instead to capture the options and the conflicting sources, and file it in the pending-decisions folder for the relevant domain.
