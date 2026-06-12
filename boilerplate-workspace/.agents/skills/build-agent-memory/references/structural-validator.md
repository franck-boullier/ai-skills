---
title: Structural validator — canonical lists and algorithm
description: Reference doc for the `workspace-confirm-and-update` mode (v1.2). Hosts the four canonical structural lists V.1–V.4 (MEMORY.md H2 sections, MEMORY.md frontmatter keys, memories/ subdirectories, decisions.config.md requirements) and the validate + additive-merge + conflict-surface algorithm. SKILL.md Step 1 reads this file when [MEMORY-MODE] = workspace-confirm-and-update. The validator is STRUCTURAL ONLY — never inspects placeholder values, key_concepts list contents, domain-specific topical-store categories beyond V.3, individual decision records or action plans, or any project-specific business content. Anchored by closed decision A.5 (2026-05-19, final).
audience: ai-agent
purpose: reference
last-updated: "2026-05-28"
---

# Structural validator — canonical lists and algorithm

Read this file at Step 1 when `[MEMORY-MODE] = workspace-confirm-and-update`. The validator's lists are the source of truth for what counts as "present", "missing", or "mismatched" — and explicitly enumerates what the validator must NEVER inspect.

## Load-bearing constraint (do not violate)

**The validator is structural only.** It checks presence and shape, not content. The boundary set in V.5 below bounds the skill-to-boilerplate coupling — every time the boilerplate's memory architecture evolves (Type 2+ adds new canonical sections), the lists in V.1–V.3 update in lockstep, but V.5's exclusion list does not move. Inspecting placeholder values, `key_concepts` list contents, or any project business content from here couples the skill to the project's content and re-introduces the failure mode the third mode exists to prevent.

## Scope — "boilerplate-canonical", not "skill-canonical"

V.1, V.2, V.3, V.4 are **the boilerplate's** canonical structural lists — the shape derived projects inherit from `boilerplate/.agents/` + the boilerplate's bootstrap playbooks. They are **NOT** the only valid workspace memory shape. The skill's two original Step-0 modes — `workspace` (greenfield) and `agent` — continue to use the broader, more open canonical set documented in `references/memory-model.md` (`activities/`, `analysis/`, `projects/`, `people/`, `decisions/`, `lessons/`, `preferences/`, `daily/`, `test/`) plus the simpler `MEMORY.md` Template B in `references/memory-index-template.md`. Those modes are deliberately flexible: greenfield workspaces and individual agents pick the categories that suit their domain.

V.1–V.4 only apply when `[MEMORY-MODE] = workspace-confirm-and-update`. That mode exists to validate the **specific** evolved tree the boilerplate ships — the H2 sections at V.1 and the subdirectories at V.3 are precisely the set the boilerplate's templates produce. If a derived project's tree differs from V.1/V.3, that is either a conflict (the project diverged structurally from the boilerplate) or a project-specific extension (extras beyond V.3 — silent pass).

The intentional inconsistency between V.1/V.3 and `memory-model.md` + Template B is therefore a **scope boundary**, not a defect: greenfield modes get the broader menu of choices; the third mode validates against the boilerplate's specific frozen shape. When the boilerplate evolves (a new H2 section becomes canonical, a new subdirectory becomes required), V.1/V.3 update in lockstep with the boilerplate's templates — `memory-model.md` and Template B may or may not move with it depending on whether the change is also relevant to greenfield projects.

## V.1 — `MEMORY.md` canonical H2 sections (workspace shape)

Each of the following H2 sections must be present in `MEMORY.md`'s body. The heading wording is part of the check — case-sensitive, exact match. Bodies are NOT inspected (per V.5).

| Order | Heading (exact match) |
| --- | --- |
| 1 | `## Memory Architecture` |
| 2 | `## Source of truth boundaries` |
| 3 | `## Configuration files` |
| 4 | `## Decision records` |
| 5 | `## Action records` |
| 6 | `## Compacted working layer` |
| 7 | `## Restart guides` |
| 8 | `## Daily Logs` |
| 9 | `## Notes on writing` |

**Detected outcomes:** PRESENT (silent), MISSING (additive merge), MISMATCHED (conflict — heading present but body materially differs per V.4-style criteria).

## V.2 — `MEMORY.md` required frontmatter keys

Each key must be present in the YAML frontmatter block. Values are NOT inspected (per V.5).

- `doc-id`
- `title`
- `description`
- `root_prefix`
- `tags` (list — may be empty; contents not inspected)
- `key_concepts` (list — contents not inspected per V.5)
- `last-updated`

**Optional but check-presence-only:** `shared_actions_root`. If present, V.3 includes `actions/` in the required subdirectory set. If absent, `actions/` is not required.

## V.3 — `memories/` canonical subdirectories

Each directory must exist under `[MEMORY-STORE-ROOT]` and contain either `README.md` or (where the workspace convention specifies) `_index.md`. The list:

| Subdirectory | Required index file | Required only when |
| --- | --- | --- |
| `decisions/` | `README.md` | always |
| `decision-records/` | `README.md` | always |
| `lessons/` | `README.md` | always |
| `preferences/` | `README.md` | always |
| `restart-guides/` | `README.md` | always |
| `daily/` | `README.md` (special — see SKILL.md Step 7 daily-README rules) | always |
| `test/` | `README.md` | always |
| `actions/` | `README.md` | only when `shared_actions_root` is declared in `MEMORY.md` frontmatter (per V.2) |

**Domain-specific subdirectories beyond this set are project-specific and outside the validator's scope** (silent pass; setup-report note that they were found but not validated).

## V.4 — `decisions.config.md` at workspace root

| Requirement | Check |
| --- | --- |
| File exists at `[MEMORY-ROOT]/decisions.config.md` | PRESENT / MISSING |
| File is parseable as markdown with optional YAML frontmatter | PARSEABLE / UNPARSEABLE |
| File declares at least one domain | DECLARES-DOMAIN / NO-DOMAIN |

**Detected outcomes:**

- All three pass → silent.
- Missing or unparseable → additive merge (write canonical empty template from `references/decisions-config-template.md` if shipped, or surface as a structural failure if no template ships).
- Parseable but no domain declared → conflict (the file exists but doesn't satisfy the contract; surface side-by-side EXISTING vs SKILL-SHIPPED and ask).

## V.5 — What the validator must NEVER inspect

The following are explicitly OUT OF SCOPE for the validator. Inspecting any of these couples the skill to project content and breaks A.5's load-bearing constraint:

- **Placeholder substitutions** like `[STORAGE-TYPE]`, `[STORAGE-PROVIDER]`, `[STORAGE-LOCATION]`, `[MEMORY-STORE-ROOT]`. Substitution is the responsibility of `replace-boilerplate-value-in-fbo-framework`, run earlier in the bootstrap sequence (boilerplate `TODO.md` step 27).
- **The contents of the `key_concepts` list** in `MEMORY.md` frontmatter. Project-specific concepts may have been added by hand; this is expected.
- **Domain-specific topical-store categories beyond V.3.** Extra subdirectories under `memories/` (e.g. `contracts/`, `incidents/`, `clients/`) are project-specific; report their presence in the setup report but do not flag them as conflicts.
- **Individual decision records, action plans, lessons, daily log entries, or any business content under `memories/`.** The validator never opens those files.
- **The bodies of canonical H2 sections.** V.1 checks heading presence and exact wording; the section body's prose is project-specific.
- **The bodies of per-store `README.md` files** beyond confirming a canonical-section heading shape (per the per-store template's required-section list — but only for the headings themselves, never their content).

## Algorithm — `workspace-confirm-and-update` validation pass

The Step-1 validator runs in this order. Each detection contributes to **one of two outputs**: the **additive-merge log** (artefacts to write later) or the **conflict log** (resolutions the user must make before merging continues).

```text
1. Read [MEMORY-ROOT]/MEMORY.md.
   - If file unreadable or YAML frontmatter unparseable → conflict (file is corrupt; surface and stop).

2. Check V.2 (frontmatter keys).
   For each required key:
     - PRESENT → silent.
     - MISSING → append `MISSING: frontmatter key '<name>' — will write from Template B placeholder` to additive-merge log.
   Note presence of `shared_actions_root` (drives V.3 actions/ requirement).

3. Check V.1 (H2 sections).
   For each section in canonical order:
     - PRESENT with exact heading wording → silent.
     - PRESENT with different wording (close match) → conflict (heading drift; surface and stop). This is rare and usually means the doc was hand-edited.
     - MISSING → append `MISSING: section '<heading>' — will write from Template B` to additive-merge log.

4. Check V.3 (subdirectories under [MEMORY-STORE-ROOT]).
   For each required subdirectory (per the V.2 shared_actions_root flag):
     - Directory PRESENT and index file PRESENT → silent.
     - Directory PRESENT but index file MISSING → append `MISSING: <subdir>/<index-file> — will write from per-store template` to additive-merge log.
     - Directory MISSING → append `MISSING: <subdir>/ + <subdir>/<index-file> — will create directory and write index from per-store template` to additive-merge log.
   For each EXTRA subdirectory (present but not in V.3) → silent pass, note in setup report.

5. Check V.4 ([MEMORY-ROOT]/decisions.config.md).
   - PRESENT, parseable, declares ≥1 domain → silent.
   - MISSING → append `MISSING: decisions.config.md — will write from references/decisions-config-template.md` to additive-merge log. The canonical empty template ships with this skill (added in v1.2.1).
   - PRESENT but UNPARSEABLE → conflict (file is corrupt; surface and stop).
   - PRESENT, parseable, but NO domain declared → conflict (file doesn't satisfy V.4; surface side-by-side EXISTING vs SKILL-SHIPPED-MINIMAL and ask).

6. Body-content checks (limited; per V.5 the validator does NOT inspect bodies in general, but a few key invariants are structural):
   - MEMORY.md root_prefix value vs boilerplate's expected value → conflict if differs (per A.5 conflict examples).
   - MEMORY.md Memory Architecture section's declared storage backend block — check presence of `Backend type:` / `Provider:` / `Location:` / `MCP tool:` lines; conflict if absent.

7. Build outputs:
   - Additive-merge log → carried to Steps 3, 6, 7 for the actual writes.
   - Conflict log → for every conflict, the user's resolution is collected at Step 1 via Conflict-Surfacing Semantics (one conflict at a time; stop and ask; default = keep).
```

### Stop conditions

- Any UNPARSEABLE file (MEMORY.md or decisions.config.md) → stop immediately. Cannot proceed; ask the user to fix the file and re-run.
- Any conflict → stop the validation pass; surface the one conflict; wait for user resolution; resume from where the validator paused.

### Resume from user resolution

When the user picks "keep existing" → the conflict is recorded as resolved-keep; the merge does NOT touch that artefact; continue validation.

When the user picks "replace with skill-shipped" → for `README.md` files with hand-edited prose, require a SECOND confirmation; on confirm, replace; record as resolved-replace; continue.

When the user picks "exit so I can merge by hand" → stop the entire skill cleanly. Do not run Steps 2–10. Print a one-line summary of the unresolved conflict to stdout. Exit code 0 (clean exit; the user knows what to fix).

## Outputs

After Step 1 completes (no stop conditions hit), the additive-merge log and conflict log are passed forward to:

- **Step 3** (Design topical store structure) — for each `MISSING: <subdir>/ + index` in the additive-merge log, the directory + index is created from the per-store template.
- **Step 6** (Draft MEMORY.md) — for each `MISSING: frontmatter key` or `MISSING: section`, the key/section is written from Template B (placeholders left for the user to fill at Step 8 review).
- **Step 7** (Create directory structure) — for each `MISSING: <subdir>/<index-file>` (directory present but index missing), the index file is written from the per-store template.
- **Step 10** (Generate setup report) — Report C includes Validator Findings, Additive Merge Log, and Conflict Log sections (one row per detected outcome, including the silent passes summarised).

## Edge cases (validator-specific)

| Situation | Behaviour |
| --- | --- |
| MEMORY.md present but `memories/` empty | Detected at Step 0a — third mode is NOT offered. Validator does not run; falls through to greenfield workspace mode. |
| `memories/` present but MEMORY.md absent | Detected at Step 0a — third mode is NOT offered. Falls through. |
| MEMORY.md present, `memories/` present and non-empty, but `decisions.config.md` absent | V.4 MISSING — append to additive-merge log; the canonical empty template is written. |
| MEMORY.md frontmatter declares `shared_actions_root` but `actions/` subdirectory absent | V.3 MISSING (conditional row triggers) — append to additive-merge log; directory + README written. |
| MEMORY.md frontmatter does NOT declare `shared_actions_root` but `actions/` subdirectory IS present | Treat as extra subdirectory (V.3 silent pass with note). Project may be in transition; no flagging. |
| `key_concepts` list in MEMORY.md frontmatter has been heavily edited | V.2 PRESENT (silent). Contents are out of scope per V.5. |
| A canonical heading exists but with different casing (e.g. `## memory architecture`) | V.1 MISMATCHED (conflict). The exact wording is part of the check. |
| A subdirectory exists with `_index.md` instead of expected `README.md` (or vice versa) | Treat as PRESENT (silent). The workspace uses both conventions interchangeably for store indexes — accept either name. |
