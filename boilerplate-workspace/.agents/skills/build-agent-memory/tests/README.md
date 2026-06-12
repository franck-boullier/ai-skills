---
title: Regression tests — workspace-confirm-and-update mode (A.5 Task 2)
description: How to run the three regression test cases (matching / missing-section / conflict-staged) that exercise the structural validator of build-agent-memory's third Step-0 mode. The Python harness is an executable mirror of references/structural-validator.md; SKILL.md is canonical, the mirror is regression coverage.
audience: humans-and-ai
purpose: reference
last-updated: "2026-05-28"
---

# Regression tests — `workspace-confirm-and-update` mode

These tests cover the structural validator + additive-merge + conflict-surfacing algorithm of `build-agent-memory`'s third Step-0 mode. They are the load-bearing piece of A.5 Task 2 — see `memories/decision-records/list-decision-action-plans/active/2026-05-19-A5-action-plan.md` for the originating task.

## What these tests cover (and do not cover)

The harness implements the validator's algorithm in Python (`tests/validator.py`) and runs it against three fixture scenarios. It tests **structural validation only** — the three SKILL.md steps that own writes (Step 3 subdirectories, Step 6 `MEMORY.md`, Step 7 per-store READMEs) and the connectivity test (Step 9) are out of scope; their behaviour is verified indirectly by checking the validator's output logs (additive-merge log + conflict log).

For end-to-end agent-behavioural coverage (does the SKILL.md actually trigger correctly on the right prompts? does the agent produce the expected outputs?), see `../evals/evals.json` — that suite is run by `skill-eval-runner` per the building-a-new-skill playbook's Session 7.

## Canonical vs mirror

**Canonical sources of truth:**

- `../SKILL.md` — the skill specification (Step 0–10 logic, Non-Negotiable Constraints, Edge Cases).
- `../references/structural-validator.md` — the V.1–V.5 lists and the validate + additive-merge + conflict-surface algorithm.

**Executable mirror (this folder):**

- `validator.py` — Python implementation of the algorithm declared in `references/structural-validator.md`. If `validator.py` and the reference doc disagree, update `validator.py` to match the doc, never the other way around.
- `test_workspace_confirm_and_update.py` — three pytest cases.
- `conftest.py` — pytest fixture loaders (copy canonical fixture to tmpdir, optionally mutate).
- `fixtures/boilerplate-derived/` — the canonical fixture tree (one `MEMORY.md`, one `decisions.config.md`, eight per-store `README.md` files).

## Test cases (A.5 §Design detail §Regression-test fixture)

| Case | Setup | Asserts |
| --- | --- | --- |
| **matching** | Canonical fixture unchanged | additive-merge log is empty; conflict log is empty; `stop_reason is None`; the V.3 `test/` subdirectory exists (Step 9 writes its connectivity-check entry here). |
| **missing-section** | `## Restart guides` removed from `MEMORY.md` | additive-merge log has exactly one entry naming that section, scheduled for Step 6 from Template B; conflict log is empty. |
| **conflict-staged** | `root_prefix` changed to a non-canonical value (`store/`) | exactly one conflict in the log naming `root_prefix`, with existing=`store/` and skill-shipped=`memories/`; additive-merge log is empty (validator stopped before recording it). |

## How to run

From the skill root:

```sh
cd .agents/skills/build-agent-memory/      # or 00-temp/.../draft-skill/ during development
pip install --user pytest                  # if not already installed
python3 -m pytest tests/ -v
```

Expected output:

```text
tests/test_workspace_confirm_and_update.py::test_matching_fixture_passes_silently PASSED
tests/test_workspace_confirm_and_update.py::test_missing_section_logs_one_entry PASSED
tests/test_workspace_confirm_and_update.py::test_conflict_root_prefix_surfaces_and_stops PASSED
3 passed in 0.03s
```

## When to update these tests

Update only when:

1. **`references/structural-validator.md` changes** (V.1–V.5 lists, algorithm). The mirror in `validator.py` must track the doc; the doc is canonical.
2. **The boilerplate's expected canonical shape changes** (e.g. a new H2 section is added to `MEMORY.md`'s canonical form). Update both the reference doc and the validator + the fixture.
3. **A new conflict case is added by a follow-up decision** (a `flag`-series reversal of A.5 or a Type 2+ extension). The new case gets its own test (do not weaken the existing three).

Never update the validator to "make the tests pass" without first updating `references/structural-validator.md` to reflect the desired behaviour — that path silently drifts the executable mirror from the spec.

## Open extensions (future work)

- **Step 9 / Step 10 integration** — invoke `skill-save-agent-memories` in a sandbox to verify the connectivity-check entry actually writes to `memories/test/` and the setup report records PASS. Out of scope for the current iteration because it requires a working `skill-save-agent-memories` mock or a real storage backend in CI.
- **Conflict-surfacing UX** — verify the side-by-side `EXISTING:` / `SKILL-SHIPPED:` format renders correctly. Currently the `Conflict` dataclass carries both fields but the harness doesn't assert on display.
- **More fixture variants** — additional V.3 missing-subdirectory cases, V.2 missing-frontmatter-key cases, V.4 unparseable `decisions.config.md` cases.
