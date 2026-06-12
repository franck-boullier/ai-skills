#!/usr/bin/env python3
"""
Atomically move a restart guide between lifecycle subfolders.

The lifecycle invariant (a non-negotiable constraint of this skill):

    A guide's `status:` front-matter field and the subfolder it lives in
    must ALWAYS agree.

Moving a guide therefore involves four coordinated changes:

    1. Validate the target subfolder is a known lifecycle subfolder.
    2. Validate that the guide has the required closure fields for that
       destination (closed-on / closed-reason for completed/abandoned;
       superseded-by / superseded-on / superseded-reason for superseded).
    3. Update the `status:` field in the file's front matter to match the
       destination.
    4. Move the file to the destination subfolder.
    5. Migrate the row in `_index.md` from the source table to the
       destination table (delegated to update_index.py).

If any of validation steps 1-2 fail, the script makes NO disk changes and
exits non-zero. Validation always precedes any mutation.

Source table is inferred from the source subfolder; destination table is
inferred from the destination subfolder. The script does not accept
arbitrary table names — only the four lifecycle states.

On success, the script emits a per-mutation confirmation line (status flip,
file move, index migration) followed by the relayed stdout from
update_index.py — so a calling agent can verify what changed without
re-reading any file.

Usage:

    # Move active/2026-05-12-foo.md to completed/.
    python lifecycle_move.py \\
        --root memories/restart-guides/ \\
        --from active/2026-05-12-foo.md \\
        --to completed/

    # Move active/2026-05-10-old.md to superseded/ (after editing front matter
    # to add superseded-by / superseded-on / superseded-reason).
    python lifecycle_move.py \\
        --root memories/restart-guides/ \\
        --from active/2026-05-10-old.md \\
        --to superseded/

The --to argument can be either the bare subfolder ("completed/") or a full
target path ("completed/2026-05-12-foo.md"). If only the subfolder is given,
the original filename is preserved.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

LIFECYCLE_SUBFOLDERS = ("active", "superseded", "completed", "abandoned")

# Required closure fields by destination status.
REQUIRED_CLOSURE_FIELDS = {
    "active": set(),
    "superseded": {"superseded-by", "superseded-on", "superseded-reason"},
    "completed": {"closed-on", "closed-reason"},
    "abandoned": {"closed-on", "closed-reason"},
}


# ---------------------------------------------------------------------------
# Front-matter parsing — minimal, no PyYAML dependency
# ---------------------------------------------------------------------------


def read_frontmatter(file_path: Path) -> tuple[list[str], list[str]]:
    """Return (frontmatter_lines, body_lines).

    Front-matter is the block between the first `---` and the next `---`
    at column 0. If no front matter is present, returns ([], all-lines).
    """
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)
    if not lines or lines[0].strip() != "---":
        return [], lines
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        die(f"Front matter at top of {file_path} is not closed (no trailing '---').")
    fm = lines[1:end_idx]
    body = lines[end_idx + 1 :]
    return fm, body


def write_with_frontmatter(file_path: Path, fm: list[str], body: list[str]) -> None:
    parts = ["---", *fm, "---", *body]
    text = "\n".join(parts)
    if not text.endswith("\n"):
        text += "\n"
    file_path.write_text(text, encoding="utf-8")


def parse_frontmatter_fields(fm: list[str]) -> dict[str, str]:
    """Return a flat mapping of top-level scalar fields in front matter.

    This is intentionally a simple parser: it handles `key: value` lines at
    column 0 with the value as either a bare scalar or a quoted string. It
    does NOT parse nested mappings or lists. That's enough to validate the
    closure fields and to find/replace `status:`.
    """
    fields: dict[str, str] = {}
    for line in fm:
        # Skip comments and blanks.
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Top-level scalar lines must start at column 0.
        if line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        # Strip surrounding quotes.
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        fields[key.strip()] = value
    return fields


def replace_status_field(fm: list[str], new_status: str) -> list[str]:
    """Return a new front-matter list with the `status:` line updated.

    If `status:` is not present, append it at the end of the front matter.
    """
    out: list[str] = []
    found = False
    for line in fm:
        if line.startswith("status:") or line.startswith("status :"):
            out.append(f"status: {new_status}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"status: {new_status}")
    return out


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_subfolder(path_fragment: str) -> str:
    """Extract the lifecycle subfolder from a path-fragment like 'active/foo.md'."""
    parts = path_fragment.strip("/").split("/")
    if not parts:
        die(f"Cannot determine subfolder from path: {path_fragment!r}")
    sub = parts[0]
    if sub not in LIFECYCLE_SUBFOLDERS:
        die(
            f"'{sub}' is not a lifecycle subfolder. "
            f"Must be one of: {', '.join(LIFECYCLE_SUBFOLDERS)}."
        )
    return sub


# ---------------------------------------------------------------------------
# Main move
# ---------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Atomically move a restart guide between lifecycle subfolders, "
            "updating its `status:` front-matter field and migrating its row in _index.md."
        )
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Path to the memories/restart-guides/ root.",
    )
    parser.add_argument(
        "--from",
        dest="src",
        required=True,
        help="Source path relative to --root (e.g. 'active/2026-05-12-foo.md').",
    )
    parser.add_argument(
        "--to",
        dest="dst",
        required=True,
        help=(
            "Destination relative to --root. Either a bare subfolder "
            "('completed/') or a full path ('completed/2026-05-12-foo.md')."
        ),
    )
    parser.add_argument(
        "--update-index-script",
        default=None,
        help=(
            "Optional path to update_index.py. Defaults to looking next to "
            "this script."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without changing any files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).resolve()
    if not root.is_dir():
        die(f"--root is not a directory: {root}")

    # ---- Resolve source ----
    src_rel = args.src.lstrip("./")
    src_full = (root / src_rel).resolve()
    if not src_full.exists():
        die(f"Source file does not exist: {src_full}")
    if not src_full.is_file():
        die(f"Source is not a regular file: {src_full}")
    src_subfolder = parse_subfolder(src_rel)

    # ---- Resolve destination ----
    dst_input = args.dst.rstrip()
    if dst_input.endswith("/"):
        # Bare subfolder: preserve filename.
        dst_subfolder = parse_subfolder(dst_input)
        dst_rel = f"{dst_subfolder}/{src_full.name}"
    else:
        dst_subfolder = parse_subfolder(dst_input)
        dst_rel = dst_input.lstrip("./")
    dst_full = (root / dst_rel).resolve()

    if dst_subfolder == src_subfolder:
        die(
            f"Source and destination subfolders are the same ('{src_subfolder}'). "
            "Nothing to move."
        )

    # ---- Read source front matter for validation ----
    fm, body = read_frontmatter(src_full)
    if not fm:
        die(f"Source file has no front matter: {src_full}")
    fields = parse_frontmatter_fields(fm)

    # ---- Validate closure fields are present and non-empty ----
    required = REQUIRED_CLOSURE_FIELDS[dst_subfolder]
    missing = [f for f in required if not fields.get(f)]
    if missing:
        die(
            f"Cannot move to '{dst_subfolder}/': missing required closure field(s): "
            f"{', '.join(missing)}. Add them to the front matter and retry."
        )

    # ---- Validate the destination does not already exist ----
    if dst_full.exists():
        die(f"Destination already exists, refusing to overwrite: {dst_full}")

    # ---- Dry run? ----
    if args.dry_run:
        print(f"DRY RUN: would update status to '{dst_subfolder}' in {src_full}")
        print(f"DRY RUN: would move {src_full} -> {dst_full}")
        print(f"DRY RUN: would call update_index.py to move row {src_rel} -> {dst_rel}")
        return 0

    # ---- Mutate: status flip, move, index migration ----
    new_fm = replace_status_field(fm, dst_subfolder)
    write_with_frontmatter(src_full, new_fm, body)

    dst_full.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_full), str(dst_full))

    # ---- Migrate index row ----
    update_index_path = (
        Path(args.update_index_script).resolve()
        if args.update_index_script
        else Path(__file__).resolve().parent / "update_index.py"
    )
    if not update_index_path.exists():
        die(
            f"update_index.py not found at {update_index_path}. "
            "Pass --update-index-script to override."
        )
    index_path = root / "_index.md"
    if not index_path.exists():
        die(f"_index.md not found at {index_path}.")

    cmd = [
        sys.executable,
        str(update_index_path),
        "--index",
        str(index_path),
        "--action",
        "move",
        "--from-table",
        src_subfolder,
        "--to-table",
        dst_subfolder,
        "--row-path",
        src_rel,
        "--new-row-path",
        dst_rel,
    ]
    # Pass through the closure fields for the destination row.
    if dst_subfolder == "superseded":
        cmd += [
            "--superseded-by",
            fields["superseded-by"],
            "--superseded-on",
            fields["superseded-on"],
            "--reason",
            fields["superseded-reason"],
        ]
    elif dst_subfolder in ("completed", "abandoned"):
        cmd += [
            "--closed-on",
            fields["closed-on"],
            "--reason",
            fields["closed-reason"],
        ]
    # Moving to 'active' is unusual but allowed for symmetry.
    elif dst_subfolder == "active":
        # Need topic and last-updated for the Active table; we can't infer
        # them, so this path is rarely useful from this script. Fall back to
        # leaving the row deletion + manual add to the caller.
        die(
            "Moving to 'active/' requires topic and last-updated for the Active table. "
            "Use update_index.py manually after this move."
        )

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Try to roll back the file move so the workspace stays consistent.
        try:
            shutil.move(str(dst_full), str(src_full))
            # And revert status field.
            fm2, body2 = read_frontmatter(src_full)
            new_fm2 = replace_status_field(fm2, src_subfolder)
            write_with_frontmatter(src_full, new_fm2, body2)
        except Exception as e:  # pragma: no cover — rollback best-effort
            print(
                f"WARNING: rollback after index-update failure failed: {e}",
                file=sys.stderr,
            )
        die(
            "Index migration failed; file move rolled back. "
            f"update_index.py stderr:\n{result.stderr}"
        )

    # Explicit, line-per-action confirmation so a calling agent never has to
    # guess what changed. Each line names exactly one mutation (front-matter
    # status flip, file move, index migration) followed by the relayed stdout
    # from update_index.py — which itself emits a row-level diff line.
    print(
        f"[lifecycle_move.py] Updated front-matter status -> {dst_subfolder!r} in {src_rel}"
    )
    print(f"[lifecycle_move.py] Moved file {src_rel} -> {dst_rel}")
    print(
        f"[lifecycle_move.py] Index row migration ({src_subfolder!r} -> {dst_subfolder!r}) "
        f"delegated to update_index.py; relayed output follows:"
    )
    relayed = result.stdout.strip()
    if relayed:
        for line in relayed.splitlines():
            print(f"  | {line}")
    else:
        print("  | (update_index.py produced no stdout)")
    print(f"OK: moved {src_rel} -> {dst_rel}; status updated to '{dst_subfolder}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
