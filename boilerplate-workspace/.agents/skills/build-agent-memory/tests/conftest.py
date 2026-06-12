"""Pytest fixtures for the workspace-confirm-and-update regression suite.

Provides a parameterised fixture builder that copies the canonical
`fixtures/boilerplate-derived/` tree into a tmpdir, optionally applies a
mutation (remove a section / change a frontmatter value), and returns the
tmpdir path for the test to validate.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Callable, Optional

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CANONICAL_FIXTURE = FIXTURES_DIR / "boilerplate-derived"


def _copy_fixture(target: Path) -> Path:
    """Copy the canonical fixture tree into target/ and return target."""
    shutil.copytree(CANONICAL_FIXTURE, target)
    return target


@pytest.fixture
def matching_fixture(tmp_path: Path) -> Path:
    """Canonical fixture — should pass validation silently."""
    return _copy_fixture(tmp_path / "workspace")


@pytest.fixture
def missing_section_fixture(tmp_path: Path) -> Path:
    """Canonical fixture with `## Restart guides` removed from MEMORY.md."""
    root = _copy_fixture(tmp_path / "workspace")
    memory_md = root / "MEMORY.md"
    text = memory_md.read_text(encoding="utf-8")
    # Remove the entire `## Restart guides` section (heading through next H2 or EOF)
    new_text = re.sub(
        r"(^## Restart guides\n)(?:.*?)(?=^## |\Z)",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert new_text != text, "fixture mutation failed: '## Restart guides' not found"
    memory_md.write_text(new_text, encoding="utf-8")
    return root


@pytest.fixture
def conflict_root_prefix_fixture(tmp_path: Path) -> Path:
    """Canonical fixture with `root_prefix` changed to a non-canonical value."""
    root = _copy_fixture(tmp_path / "workspace")
    memory_md = root / "MEMORY.md"
    text = memory_md.read_text(encoding="utf-8")
    new_text = re.sub(
        r"^root_prefix:.*$",
        "root_prefix: store/",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    assert new_text != text, "fixture mutation failed: 'root_prefix:' not found"
    memory_md.write_text(new_text, encoding="utf-8")
    return root
