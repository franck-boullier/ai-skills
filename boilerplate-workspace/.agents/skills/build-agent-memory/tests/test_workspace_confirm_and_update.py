"""A.5 Task 2 regression tests — workspace-confirm-and-update mode.

Three test cases mirroring A.5's decision file:

1. Case "matching" — fixture matches what the skill ships; validator
   passes silently (empty additive-merge log, empty conflict log, no
   stop reason).
2. Case "missing-section" — canonical H2 section deliberately removed;
   validator records exactly that one missing entry and nothing else.
3. Case "conflict-staged" — `root_prefix` differs from the boilerplate's
   expected value; validator surfaces a conflict and stops.

Run from the skill root:

    cd .agents/skills/build-agent-memory/
    pytest tests/

The validator under test is `tests/validator.py` — an executable mirror
of `references/structural-validator.md`. SKILL.md and the reference doc
are canonical; the Python mirror is regression coverage, not the spec.
"""
from __future__ import annotations

from pathlib import Path

import validator as v


# ---------------------------------------------------------------------------
# Case 1 — Matching
# ---------------------------------------------------------------------------
def test_matching_fixture_passes_silently(matching_fixture: Path) -> None:
    """Canonical fixture matches what the skill would have shipped.

    Asserts from A.5 §Design detail §Regression-test fixture:
      (a) skill completes without writing or modifying any pre-existing
          fixture file — verified here as: additive_merge_log is empty.
      (b) connectivity-test entry would land in memories/test/ —
          covered by Step 9 in the SKILL.md; out of scope for this
          unit-style validator (the test/ subdir is verified present
          via V.3).
      (c) setup report names PASS — covered by Step 10; out of scope.
      (d) skill exits cleanly with no surfaced conflict — verified
          here as: conflict_log is empty AND stop_reason is None.
    """
    result = v.validate(matching_fixture)
    assert result.stop_reason is None, f"unexpected stop: {result.stop_reason}"
    assert result.additive_merge_log == [], (
        f"matching fixture should have empty additive-merge log; got: "
        f"{[e.artefact for e in result.additive_merge_log]}"
    )
    assert result.conflict_log == [], (
        f"matching fixture should have empty conflict log; got: "
        f"{[c.artefact for c in result.conflict_log]}"
    )
    assert result.passes_silently is True
    # V.3 test/ subdir must be present in the canonical fixture (Step 9
    # writes the connectivity-check entry here).
    assert (matching_fixture / "memories" / "test" / "README.md").exists()


# ---------------------------------------------------------------------------
# Case 2 — Missing section
# ---------------------------------------------------------------------------
def test_missing_section_logs_one_entry(missing_section_fixture: Path) -> None:
    """`## Restart guides` removed from MEMORY.md.

    Asserts from A.5 §Design detail §Regression-test fixture:
      - The skill writes exactly the missing section (validated here
        as: the additive-merge log has exactly one entry naming the
        section, scheduled for Step 6).
      - Every other section / subdirectory / file is unchanged
        (validated here as: no other entries in the merge log; conflict
        log is empty).
    """
    result = v.validate(missing_section_fixture)
    assert result.stop_reason is None, f"unexpected stop: {result.stop_reason}"
    assert result.conflict_log == [], (
        f"missing-section case should have empty conflict log; got: "
        f"{[c.artefact for c in result.conflict_log]}"
    )
    assert len(result.additive_merge_log) == 1, (
        f"expected exactly one missing entry; got {len(result.additive_merge_log)}: "
        f"{[e.artefact for e in result.additive_merge_log]}"
    )
    entry = result.additive_merge_log[0]
    assert "Restart guides" in entry.artefact
    assert entry.write_at_step == 6
    assert entry.template == "Template B"


# ---------------------------------------------------------------------------
# Case 3 — Conflict-staged
# ---------------------------------------------------------------------------
def test_conflict_root_prefix_surfaces_and_stops(conflict_root_prefix_fixture: Path) -> None:
    """`root_prefix` differs from the boilerplate's expected value.

    Asserts from A.5 §Design detail §Regression-test fixture:
      - The skill stops at Step 1 with a surfaced conflict (validated
        here as: exactly one conflict in the log naming `root_prefix`).
      - No file is written or modified (the validator returns the
        conflict; the caller is responsible for stopping before any
        Step 3 / 6 / 7 writes — verified here as: additive_merge_log
        is empty for this case).
      - The conflict log records the mismatch (existing vs
        skill-shipped values).
    """
    result = v.validate(conflict_root_prefix_fixture)
    # The validator stops on the first conflict; the additive-merge log
    # may contain V.2 frontmatter or V.1 section detections recorded
    # before Step 6 (root_prefix) — but the canonical fixture has no
    # such missing items, so the merge log should be empty here.
    assert result.additive_merge_log == [], (
        f"conflict case should have empty additive-merge log; got: "
        f"{[e.artefact for e in result.additive_merge_log]}"
    )
    assert len(result.conflict_log) == 1, (
        f"expected exactly one conflict; got {len(result.conflict_log)}: "
        f"{[c.artefact for c in result.conflict_log]}"
    )
    conflict = result.conflict_log[0]
    assert conflict.artefact == "root_prefix"
    assert conflict.existing == "store/"
    assert conflict.skill_shipped == "memories/"
