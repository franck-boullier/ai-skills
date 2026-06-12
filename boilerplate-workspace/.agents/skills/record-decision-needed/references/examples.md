# Worked Examples

Three representative scenarios covering three different decision domains — database architecture, product prioritisation, and vendor selection. All examples use invented content — they are illustrative, not authoritative pending decisions. All path references use the shapes declared in `decisions.config.md`; the examples show workspaces where each domain has been configured with its own folders and ID series.

---

## Example 1 — Database-architecture ambiguity (audit log retention)

### Input

During a schema review the user says: *"We still haven't decided how long we keep `audit_ops.event_log` rows. The compliance doc says 7 years, the cost estimate assumes 2 years of hot storage. Add it to the decision-needed list."*

### Actions

Pick the next free `A`-series ID by scanning the "Open items" table in `strymin-portal/db-architecture-decision-needed/_index.md` and the "Decisions log" in `strymin-portal/db-architecture-decisions/_index.md`. Suppose the highest existing integer is 10 — the next free ID is `A11` (filename) / `A.11` (heading, because the `A` series declares `heading_form: dotted`). Create `strymin-portal/db-architecture-decision-needed/A11-audit-log-retention.md` using the decision-needed template. Append a row to the pending index and update Quick status counts.

### Resulting file

The filename carries the undotted `A11`; the heading below uses the dotted `A.11`, matching the series convention.

```markdown
## ⚠️ 2026-04-20 — A.11 Audit Log Retention Window — PENDING DECISION

**Status:** Pending
**Owner:** Database Architecture Owner / Compliance
**Deadline:** _____________________________________________
**Review:** _____________________________________________

---

### Context

`audit_ops.event_log` captures every state-changing action in the platform (investments, payouts, RLS denials, admin overrides). The retention policy for this table is unresolved: the compliance schema expects multi-year retention for PDPA audit defensibility, while the hot-storage cost estimate assumes a much shorter window with older rows archived to cold storage or deleted.

### Sources in conflict

- **Source A — 7 years retention:** `original-documents/compliance-plan.md` §3.2 states "all audit log entries must be retained for seven years to meet PDPA and anticipated MAS audit requirements."
- **Source B — 2 years hot storage:** `original-documents/infra-cost-model.md` §5.1 assumes `event_log` holds approximately 24 months of data at steady state, with no provision for cold-storage archival or deletion.
- **Source C — schema silent:** `database-schema-strymin-portal.md` v0.2 §4.9 defines `audit_ops.event_log` but specifies no retention policy.

### Why this matters

1. **Compliance exposure** — if the platform deletes rows before the required retention window, audit requests during a MAS or PDPA inquiry cannot be answered, exposing the platform to regulatory action.
2. **Storage cost** — retaining 7 years of hot storage on a heavily-written table is materially more expensive than the current cost model assumes. Without a decision, either the cost model is wrong or the compliance promise cannot be kept.
3. **Deletion mechanism** — whichever window is chosen, the schema needs either a partitioning strategy, a scheduled delete job, or an archival pipeline. None currently exist.

### Current placeholder

No retention policy; `audit_ops.event_log` grows unbounded. Nothing deletes or archives rows.

### Options

**Option A — 7 years, hot storage, accept the cost**
Keep every audit row in the primary Postgres instance for 7 years. Simplest mechanism — no archival pipeline — but blows through the current cost model's assumptions.

**Option B — 2 years hot + 5 years cold archive**
Partition `audit_ops.event_log` by month. After 24 months, move partitions to cold storage (e.g. S3 Glacier or a warehouse). Audit queries beyond 2 years go through a slower retrieval path. Cost-efficient but requires building the archival pipeline and retrieval SLA.

**Option C — Per-event-type retention**
Classify events: high-value (financial, RLS denials) retained 7 years; low-value (read events, admin UI clicks) retained 90 days. Cheapest option that still meets compliance for the events that matter, but requires an explicit classification on every event type.

---

**Decision:** _____________________________________________

**Rationale:** _____________________________________________

**User Override:**
<!-- Leave blank if the accountable party approved. Fill in if they changed something. -->

**Rejected:**
<!-- Fill in every proposal explicitly rejected after the decision is made. -->

**Action Items:**
- [ ] Update `audit_ops.event_log` in `database-schema-strymin-portal.md` §4.9 with the chosen retention policy and partitioning strategy — Owner: Engineering — Due: ___ — Review: ___
- [ ] If archival/deletion is required: design and schedule the pipeline — Owner: Engineering — Due: ___ — Review: ___
- [ ] Reconcile `infra-cost-model.md` §5.1 with the chosen retention window — Owner: Finance — Due: ___ — Review: ___
- [ ] Move this file to `db-architecture-decisions/` — Owner: Database Architecture Owner — Due: ___ — Review: ___

**Supersedes:** —
**Superseded by:** —

**Source:** Schema review conversation 2026-04-20 — `database-schema-strymin-portal.md` v0.2 §4.9; `compliance-plan.md` §3.2; `infra-cost-model.md` §5.1.
```

### Index update

In `strymin-portal/db-architecture-decision-needed/_index.md`: append to the open-items table `| [A11-audit-log-retention.md](./A11-audit-log-retention.md) | Audit log retention window — 7 years vs 2 years vs per-event | ⚠️ Pending |`. Update Quick status so the item count and the parenthesised ID list both include `A11`. Bump `last_updated` to `2026-04-20`.

---

## Example 2 — Product prioritisation question (Q3 roadmap slot)

### Input

During roadmap planning the user says: *"We have one slot left in Q3 — either the multi-currency payout feature or the in-app support chat. We haven't decided. Log it so we can come back to it after the investor meeting."*

### Actions

Pick the next free `P`-series ID for the `product` domain. Scanning both product indexes, the highest existing `P` integer is 6, so the next free ID is `P7`. Create `product/decisions-pending/P7-q3-roadmap-slot.md`. Append a row to `product/decisions-pending/_index.md` and update Quick status counts.

### Resulting file (excerpt)

```markdown
## ⚠️ 2026-04-20 — P.7 Q3 Roadmap Slot — Multi-Currency Payouts vs In-App Support Chat — PENDING DECISION

**Status:** Pending
**Owner:** Product Owner
**Deadline:** _____________________________________________
**Review:** _____________________________________________

---

### Context

One slot remains in the Q3 delivery plan. Two candidate features are contending for it — multi-currency payouts (expansion into two new markets) and in-app support chat (response to rising NPS criticism about time-to-resolution). The decision is parked until after the investor meeting on 2026-04-29 because investor priorities may shift the answer.

### Sources in conflict

- **Source A — multi-currency payouts:** `roadmap-q2-review.md` §4 notes that every market-expansion KPI requires multi-currency to land by end of Q3; the partnership team has two signed LOIs that are contingent on this feature.
- **Source B — in-app support chat:** `nps-analysis-2026-q1.md` §2.3 shows a 9-point NPS drop driven by support response times; customer research suggests in-app chat would recover ~5 points within a quarter.
- **Source C — capacity estimate:** `engineering-capacity-q3.md` v2 confirms that only one of the two can ship in Q3 with current headcount; both would require one additional hire or scope cuts elsewhere.

### Why this matters

1. **Revenue timing** — the two LOIs contingent on multi-currency represent approximately 18 % of Q4 forecast revenue. Slipping to Q4 delays that revenue by at least one quarter.
2. **Retention risk** — the NPS drop is accelerating. Every additional quarter without in-app support widens the gap with the nearest competitor, who shipped equivalent chat in 2025-12.
3. **Team morale** — engineering has been asked to re-scope Q3 twice already. A third reshuffle without a clear priority will damage velocity.

### Current placeholder

Q3 plan has a `TBD — one of: payouts | chat` slot in `roadmap-q3.md` §1.2. No work started on either feature.

### Options

**Option A — Multi-currency payouts**
Unlocks signed-LOI revenue and keeps the market-expansion timeline intact. Does nothing for NPS; the support-response gap continues to widen for a quarter.

**Option B — In-app support chat**
Reverses the NPS slide and catches up to a capability the nearest competitor already ships. Delays multi-currency to Q4, with the LOIs at risk of lapsing.

**Option C — Defer the decision until the investor meeting on 2026-04-29**
A live no-op. The investor priorities set at that meeting may resolve the trade-off cleanly (e.g. if growth signals are prioritised over retention, payouts wins). Costs one week of engineering idle-time on this slot.

---

**Decision:** _____________________________________________

**Rationale:** _____________________________________________

**User Override:**
<!-- Leave blank if the accountable party approved. -->

**Rejected:**
<!-- Fill in after the decision is made. -->

**Action Items:**
- [ ] Update `roadmap-q3.md` §1.2 with the chosen feature and remove the TBD slot — Owner: Product — Due: ___ — Review: ___
- [ ] Notify the partnership team (if chat wins) or the customer-success team (if payouts wins) of the deferral — Owner: Product — Due: ___ — Review: ___
- [ ] Re-run the capacity estimate to confirm the chosen feature fits — Owner: Engineering — Due: ___ — Review: ___
- [ ] Move this file to `product/decisions/` — Owner: Product Owner — Due: ___ — Review: ___

**Supersedes:** —
**Superseded by:** —

**Source:** Roadmap planning conversation 2026-04-20 — `roadmap-q2-review.md` §4; `nps-analysis-2026-q1.md` §2.3; `engineering-capacity-q3.md` v2.
```

---

## Example 3 — Vendor selection trade-off (payments provider)

### Input

During a vendor review the user says: *"We need to pick between StripeClone and PayForge for card payments. The finance team is split. Put it on the list — we'll revisit when the security audit is back."*

### Actions

Pick the next free `V`-series ID for the `vendor` domain. Scanning both vendor indexes, the highest existing `V` integer is 4, so the next free ID is `V5`. Create `vendor/decisions-pending/V5-card-payments-provider.md`. Append a row to the pending index and update Quick status counts.

### Resulting file (excerpt)

```markdown
## ⚠️ 2026-04-20 — V.5 Card Payments Provider — StripeClone vs PayForge — PENDING DECISION

**Status:** Pending
**Owner:** Platform / Finance
**Deadline:** _____________________________________________
**Review:** _____________________________________________

---

### Context

The platform currently has no card-payment provider integrated. Two vendors have completed commercial discovery — StripeClone (market leader, higher fees) and PayForge (challenger, lower fees but smaller network). A final choice is blocked on the outcome of the security audit scheduled for 2026-04-28.

### Sources in conflict

- **Source A — commercial comparison:** `vendor-eval/card-payments-matrix.md` v1.3 shows PayForge is 0.25 percentage points cheaper per transaction but StripeClone has 2.3× the chargeback-dispute tools.
- **Source B — engineering assessment:** `vendor-eval/integration-assessment-stripeclone.md` and `integration-assessment-payforge.md` both conclude that StripeClone's SDK is materially easier to integrate — estimated two weeks versus six weeks for PayForge.
- **Source C — finance memo:** `finance/payments-provider-memo-2026-04.md` argues that the fee difference compounds to roughly £180k/year at projected Q4 volume and recommends PayForge; the CFO has signed off on that memo.

### Why this matters

1. **Annual cost** — the fee gap is £180k/year at steady state, which is material for the current burn rate.
2. **Integration timeline** — a four-week difference in integration effort delays the end-to-end payments launch by a full release train.
3. **Dispute exposure** — the weaker chargeback tooling on PayForge is estimated to cost £40–60k/year in unrecovered disputes at projected volume; the commercial matrix does not net this against the fee savings.

### Current placeholder

`vendor-register.md` §2 lists card-payments provider as `TBD — StripeClone | PayForge`. Neither vendor has been contracted; no integration work has started.

### Options

**Option A — StripeClone**
Faster integration, stronger dispute tooling, higher fees. Best fit if time-to-market and operational maturity outweigh cost.

**Option B — PayForge**
Lower fees, longer integration, weaker dispute tooling. Best fit if the fee saving net of extra dispute losses is the dominant consideration and the launch timeline can absorb four extra weeks.

**Option C — Defer until the security audit on 2026-04-28**
A live no-op. If the audit surfaces a material security gap at either vendor, the decision may be forced.

---

**Decision:** _____________________________________________

**Rationale:** _____________________________________________

**User Override:**
<!-- Leave blank if the accountable party approved. -->

**Rejected:**
<!-- Fill in after the decision is made. -->

**Action Items:**
- [ ] Update `vendor-register.md` §2 with the chosen vendor and remove the TBD marker — Owner: Platform — Due: ___ — Review: ___
- [ ] Kick off contract negotiation with the chosen vendor — Owner: Finance / Legal — Due: ___ — Review: ___
- [ ] Schedule integration work for the chosen vendor in the release plan — Owner: Engineering — Due: ___ — Review: ___
- [ ] Move this file to `vendor/decisions/` — Owner: Vendor Owner — Due: ___ — Review: ___

**Supersedes:** —
**Superseded by:** —

**Source:** Vendor review conversation 2026-04-20 — `vendor-eval/card-payments-matrix.md` v1.3; `integration-assessment-*.md`; `finance/payments-provider-memo-2026-04.md`.
```

---

## Counter-example — when *not* to use this skill

The user says: *"Should we use `snake_case` or `camelCase` for column names?"*

This is an editorial naming convention, not an architectural decision. In a workspace where the configuration declares a dedicated editorial series (e.g. a `C` series filed in a shared editorial-items document), add a short entry there instead of producing a standalone pending file. If no editorial series is declared, the right move is usually to add the convention to a style guide — not to create an `A12-snake-case.md` that will carry more weight than the question deserves.
