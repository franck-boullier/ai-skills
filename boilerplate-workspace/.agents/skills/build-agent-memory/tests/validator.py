"""Regression harness mirror of references/structural-validator.md.

This module is NOT shipped to consumers of build-agent-memory. It is a
regression harness used by tests/ to verify the validator algorithm
described in references/structural-validator.md is implementable and
unambiguous, and that the three A.5 Task 2 cases (matching /
missing-section / conflict-staged) produce the documented outcomes.

SKILL.md and references/structural-validator.md are the canonical spec;
this module is an executable mirror. If they drift, SKILL.md wins —
update this module to track, never the other way around.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# V.1 canonical H2 sections (exact heading wording — case-sensitive)
# ---------------------------------------------------------------------------
V1_CANONICAL_SECTIONS = (
    "## Memory Architecture",
    "## Source of truth boundaries",
    "## Configuration files",
    "## Decision records",
    "## Action records",
    "## Compacted working layer",
    "## Restart guides",
    "## Daily Logs",
    "## Notes on writing",
)

# ---------------------------------------------------------------------------
# V.2 required MEMORY.md frontmatter keys
# ---------------------------------------------------------------------------
V2_REQUIRED_FRONTMATTER_KEYS = (
    "doc-id",
    "title",
    "description",
    "root_prefix",
    "tags",
    "key_concepts",
    "last-updated",
)

# ---------------------------------------------------------------------------
# V.3 canonical memories/ subdirectories (always required)
# ---------------------------------------------------------------------------
V3_ALWAYS_REQUIRED_SUBDIRS = (
    "decisions",
    "decision-records",
    "lessons",
    "preferences",
    "restart-guides",
    "daily",
    "test",
)
# V.3 conditional: only when shared_actions_root is declared in MEMORY.md frontmatter
V3_CONDITIONAL_ACTIONS = "actions"

# ---------------------------------------------------------------------------
# V.6 boilerplate's expected root_prefix (per A.5 conflict example)
# ---------------------------------------------------------------------------
BOILERPLATE_EXPECTED_ROOT_PREFIX = "memories/"


# ---------------------------------------------------------------------------
# Result objects
# ---------------------------------------------------------------------------
@dataclass
class MissingEntry:
    """An item the validator marked as MISSING — to be additively merged."""
    artefact: str  # e.g. "frontmatter key 'doc-id'" or "section '## Memory Architecture'" or "subdir 'decisions/'"
    template: str  # e.g. "Template B" or "per-store template"
    write_at_step: int  # the SKILL.md step that owns the write (3, 6, or 7)


@dataclass
class Conflict:
    """An item the validator marked as MISMATCHED — surfaces and stops."""
    artefact: str  # e.g. "root_prefix" or "section '## Memory Architecture' body"
    existing: str
    skill_shipped: str
    description: str  # human-readable explanation


@dataclass
class ValidationResult:
    additive_merge_log: list[MissingEntry] = field(default_factory=list)
    conflict_log: list[Conflict] = field(default_factory=list)
    extras_noted: list[str] = field(default_factory=list)  # extra subdirs beyond V.3 (silent pass)
    stop_reason: Optional[str] = None  # set when a stop condition is hit

    @property
    def passes_silently(self) -> bool:
        return (
            not self.additive_merge_log
            and not self.conflict_log
            and self.stop_reason is None
        )


# ---------------------------------------------------------------------------
# Lightweight YAML frontmatter + heading extractor
# ---------------------------------------------------------------------------
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _extract_frontmatter(text: str) -> Optional[dict]:
    """Return a dict of top-level keys present in the YAML frontmatter.

    Lightweight — we only need key presence, not full value parsing.
    Lists and scalars both map to the literal string after the colon.
    Returns None if the file has no frontmatter or it is unparseable.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm_text = m.group(1)
    out: dict[str, str] = {}
    current_key: Optional[str] = None
    for line in fm_text.splitlines():
        # Top-level key on this line (no leading whitespace, has colon)
        if line and not line.startswith((" ", "\t", "#", "-")) and ":" in line:
            key, _, rest = line.partition(":")
            key = key.strip()
            out[key] = rest.strip()
            current_key = key
        # Continuation under a key (indented line) — ignored for presence check
    return out


def _extract_h2_headings(text: str) -> list[str]:
    """Return all H2 headings in the order they appear, with exact wording."""
    return [line.rstrip() for line in text.splitlines() if line.startswith("## ") and not line.startswith("### ")]


def _close_match(canonical: str, observed_headings: list[str]) -> Optional[str]:
    """Heading drift detection: same words, different casing or whitespace."""
    canonical_norm = canonical.lower().replace(" ", "")
    for h in observed_headings:
        h_norm = h.lower().replace(" ", "")
        if h_norm == canonical_norm and h != canonical:
            return h
    return None


# ---------------------------------------------------------------------------
# The validator pass (Step 1 of workspace-confirm-and-update mode)
# ---------------------------------------------------------------------------
def validate(memory_root: Path) -> ValidationResult:
    """Run the Step-1 validator algorithm against a memory_root.

    Mirrors references/structural-validator.md Section "Algorithm —
    workspace-confirm-and-update validation pass". Stop conditions
    (unparseable files, surfaced conflicts) populate ValidationResult.stop_reason
    or .conflict_log respectively; caller is responsible for invoking
    Conflict-Surfacing Semantics for each conflict.
    """
    result = ValidationResult()
    memory_md = memory_root / "MEMORY.md"
    memory_store = memory_root / "memories"
    decisions_config = memory_root / "decisions.config.md"

    # ----- Step 1: Read MEMORY.md -----
    if not memory_md.exists():
        result.stop_reason = "MEMORY.md not found at memory root"
        return result

    text = memory_md.read_text(encoding="utf-8")
    frontmatter = _extract_frontmatter(text)
    if frontmatter is None:
        result.stop_reason = "MEMORY.md has no parseable YAML frontmatter"
        return result

    # ----- Step 2: V.2 frontmatter keys -----
    for key in V2_REQUIRED_FRONTMATTER_KEYS:
        if key not in frontmatter:
            result.additive_merge_log.append(
                MissingEntry(
                    artefact=f"frontmatter key '{key}'",
                    template="Template B placeholder",
                    write_at_step=6,
                )
            )

    shared_actions_root_declared = "shared_actions_root" in frontmatter

    # ----- Step 3: V.1 H2 sections -----
    observed_h2 = _extract_h2_headings(text)
    for canonical in V1_CANONICAL_SECTIONS:
        if canonical in observed_h2:
            continue
        # Heading-drift check before declaring MISSING
        drifted = _close_match(canonical, observed_h2)
        if drifted is not None:
            result.conflict_log.append(
                Conflict(
                    artefact=f"section heading wording for '{canonical}'",
                    existing=drifted,
                    skill_shipped=canonical,
                    description=(
                        f"MEMORY.md contains '{drifted}' but the canonical "
                        f"wording is '{canonical}'. Exact-match is part of V.1."
                    ),
                )
            )
            return result  # stop on first conflict
        result.additive_merge_log.append(
            MissingEntry(
                artefact=f"section '{canonical}'",
                template="Template B",
                write_at_step=6,
            )
        )

    # ----- Step 4: V.3 subdirectories -----
    required_subdirs = list(V3_ALWAYS_REQUIRED_SUBDIRS)
    if shared_actions_root_declared:
        required_subdirs.append(V3_CONDITIONAL_ACTIONS)

    existing_subdirs: set[str] = set()
    if memory_store.exists() and memory_store.is_dir():
        existing_subdirs = {p.name for p in memory_store.iterdir() if p.is_dir()}

    for subdir in required_subdirs:
        subdir_path = memory_store / subdir
        index_exists = (subdir_path / "README.md").exists() or (subdir_path / "_index.md").exists()
        if subdir_path.exists() and index_exists:
            continue  # silent pass
        if subdir_path.exists() and not index_exists:
            result.additive_merge_log.append(
                MissingEntry(
                    artefact=f"index file for '{subdir}/' (neither README.md nor _index.md present)",
                    template="per-store template",
                    write_at_step=7,
                )
            )
            continue
        # Directory missing entirely
        result.additive_merge_log.append(
            MissingEntry(
                artefact=f"subdir '{subdir}/' + its index file",
                template="per-store template",
                write_at_step=7,
            )
        )

    # Extras beyond V.3 — silent pass with setup-report note
    for subdir in existing_subdirs - set(required_subdirs):
        result.extras_noted.append(f"extra subdir '{subdir}/' (project-specific; not flagged)")

    # ----- Step 5: V.4 decisions.config.md -----
    if not decisions_config.exists():
        result.additive_merge_log.append(
            MissingEntry(
                artefact="decisions.config.md at workspace root",
                template="canonical empty template",
                write_at_step=6,  # treat as MEMORY.md-adjacent; written before Step 7
            )
        )
    else:
        config_text = decisions_config.read_text(encoding="utf-8")
        # V.4 "declares at least one domain" — accept any of:
        #   - `id_series:` mention (YAML or top-level key form)
        #   - markdown bullet `- <ID>: <description>` (workspace convention)
        #   - top-level key `<ID>: <description>` (alternative form)
        domain_patterns = (
            r"id_series\s*:",
            r"^-\s+[A-Za-z]\w*\s*:\s+\S+",  # bullet form: `- A: Planning items`
            r"^[A-Za-z]\w*\s*:\s+\S+",       # top-level key form
        )
        if not any(re.search(p, config_text, re.MULTILINE) for p in domain_patterns):
            result.conflict_log.append(
                Conflict(
                    artefact="decisions.config.md domain declaration",
                    existing="(no domain declared)",
                    skill_shipped="(at least one domain declared, e.g. 'A: Planning items')",
                    description=(
                        "decisions.config.md is present and parseable but does not "
                        "declare at least one domain. V.4 requires ≥1 domain."
                    ),
                )
            )
            return result

    # ----- Step 6: body-content invariants (V.6 in the spec language) -----
    # root_prefix value check
    root_prefix_value = frontmatter.get("root_prefix")
    if root_prefix_value is not None:
        # Strip surrounding quotes if present
        normalised = root_prefix_value.strip().strip('"').strip("'")
        if normalised != BOILERPLATE_EXPECTED_ROOT_PREFIX:
            result.conflict_log.append(
                Conflict(
                    artefact="root_prefix",
                    existing=normalised,
                    skill_shipped=BOILERPLATE_EXPECTED_ROOT_PREFIX,
                    description=(
                        f"MEMORY.md frontmatter declares root_prefix='{normalised}' "
                        f"but the boilerplate expects '{BOILERPLATE_EXPECTED_ROOT_PREFIX}'."
                    ),
                )
            )
            return result

    return result
