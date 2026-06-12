#!/usr/bin/env python3
"""
Add, remove, update, move, or recount rows in `_index.md` for restart guides.

The index has four tables — Active, Superseded, Completed, Abandoned — and
a Quick Status block. Every guide must appear in exactly one of the four
tables; the Quick Status counts must match the row counts. This script
keeps both in agreement.

Why a script (and not have the model edit the file): the index is multi-row,
multi-table markdown with a Quick Status block. Hand-editing across three
spots (remove from source table, add to destination table, refresh counts)
is error-prone. The skill calls this script atomically.

Operations:

    add      Add a row to one of the four tables.
    update   Update an existing row's `last-updated` cell (Active table only).
    remove   Remove a row by path from any table.
    move     Equivalent to remove + add — used by lifecycle_move.py.
    recount  Refresh the Quick Status block from the current table contents.

Table-specific columns:

    Active     | Guide | Topic | Last updated |
    Superseded | Guide | Superseded by | Superseded on | Reason |
    Completed  | Guide | Closed on | Reason |
    Abandoned  | Guide | Closed on | Reason |

Examples:

    # Add a brand-new guide to Active.
    python update_index.py \\
        --index memories/restart-guides/_index.md \\
        --action add \\
        --table active \\
        --row-path active/2026-05-12-playbook-rewrite.md \\
        --topic "Resume the implementation-playbook rewrite" \\
        --last-updated 2026-05-12

    # Update the last-updated cell on an existing Active row.
    python update_index.py \\
        --index memories/restart-guides/_index.md \\
        --action update \\
        --table active \\
        --row-path active/2026-05-12-playbook-rewrite.md \\
        --last-updated 2026-05-15

    # Move a row from Active to Superseded (typically called by lifecycle_move.py).
    python update_index.py \\
        --index memories/restart-guides/_index.md \\
        --action move \\
        --from-table active \\
        --to-table superseded \\
        --row-path active/2026-05-10-old-guide.md \\
        --new-row-path superseded/2026-05-10-old-guide.md \\
        --superseded-by active/2026-05-12-new-guide.md \\
        --superseded-on 2026-05-12 \\
        --reason "Replaced by multi-session plan."

    # Recount the Quick Status block from the table row counts.
    python update_index.py \\
        --index memories/restart-guides/_index.md \\
        --action recount

The script is idempotent on `add` (re-running with the same row-path is a
no-op + a non-zero exit code so the caller notices), idempotent on `recount`,
and on `remove` quietly succeeds if the row was already absent.

Every action prints a row-level diff line on success (in addition to the
generic `OK:` line), so a calling agent can confirm exactly what changed
from stdout alone — no need to re-read the file. The move action in
particular used to print only the generic line, which made silent
success indistinguishable from no-op; the per-action confirmation block
in `main()` fixes that.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

TABLES = ("active", "superseded", "completed", "abandoned")

# Heading text expected for each table.
TABLE_HEADINGS = {
    "active": "## Active",
    "superseded": "## Superseded",
    "completed": "## Completed",
    "abandoned": "## Abandoned",
}

# Header row + separator row that each empty table starts with.
TABLE_TEMPLATES = {
    "active": ("| Guide | Topic | Last updated |", "|---|---|---|"),
    "superseded": (
        "| Guide | Superseded by | Superseded on | Reason |",
        "|---|---|---|---|",
    ),
    "completed": ("| Guide | Closed on | Reason |", "|---|---|---|"),
    "abandoned": ("| Guide | Closed on | Reason |", "|---|---|---|"),
}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def read_index(index_path: Path) -> list[str]:
    if not index_path.exists():
        die(f"Index file does not exist: {index_path}")
    return index_path.read_text(encoding="utf-8").splitlines()


def write_index(index_path: Path, lines: list[str]) -> None:
    # Preserve final-newline convention: index files always end with one.
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    index_path.write_text(text, encoding="utf-8")


def find_section_range(lines: list[str], heading: str) -> tuple[int, int]:
    """Return (start_idx, end_idx) of the section under `heading`.

    The range covers from the line immediately after the heading
    through the line immediately before the next H2 heading or EOF.
    """
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    if start is None:
        die(f"Section heading not found: {heading}")
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return start, end


def find_table_rows(lines: list[str], table: str) -> list[tuple[int, str]]:
    """Return (line_index, line_text) for every data row in the given table.

    A data row is a line in the section under `## <Table>` that starts with `|`
    and is not the header row or the separator row.
    """
    heading = TABLE_HEADINGS[table]
    start, end = find_section_range(lines, heading)
    header_line, sep_line = TABLE_TEMPLATES[table]

    rows: list[tuple[int, str]] = []
    for i in range(start, end):
        line = lines[i]
        if not line.startswith("|"):
            continue
        if line.strip() == header_line.strip():
            continue
        if line.strip() == sep_line.strip():
            continue
        rows.append((i, line))
    return rows


def find_row_by_path(
    lines: list[str], table: str, row_path: str
) -> Optional[tuple[int, str]]:
    for idx, line in find_table_rows(lines, table):
        # Match the link target inside `| [text](./<row_path>) | …` (with or without `./`).
        if f"({row_path})" in line or f"(./{row_path})" in line:
            return (idx, line)
    return None


def header_and_separator_indices(lines: list[str], table: str) -> tuple[int, int]:
    """Return (header_idx, separator_idx) for the given table.

    If the table has no header (corrupt index), die.
    """
    heading = TABLE_HEADINGS[table]
    start, end = find_section_range(lines, heading)
    header_line, sep_line = TABLE_TEMPLATES[table]
    header_idx = None
    sep_idx = None
    for i in range(start, end):
        if lines[i].strip() == header_line.strip():
            header_idx = i
        elif lines[i].strip() == sep_line.strip():
            sep_idx = i
        if header_idx is not None and sep_idx is not None:
            break
    if header_idx is None or sep_idx is None:
        die(
            f"Could not find header row and separator row under '{heading}'. "
            f"Expected: {header_line!r} and {sep_line!r}."
        )
    return header_idx, sep_idx


# ---------------------------------------------------------------------------
# Row construction
# ---------------------------------------------------------------------------


def slug_from_path(row_path: str) -> str:
    """Derive a bare filename slug from `active/2026-05-12-foo.md` -> `2026-05-12-foo.md`.

    Retained as a helper for callers that want the bare filename. NOT used for
    the index link text — see `make_link` below.
    """
    return row_path.rsplit("/", 1)[-1]


def make_link(row_path: str) -> str:
    """Render a markdown link for a guide row.

    Convention: the link text includes the subfolder prefix (e.g.
    `active/2026-05-12-foo.md`) so a reader scanning the raw `_index.md` can
    tell each guide's lifecycle status at a glance without following the link.
    This matches the format established in the knowledge-base reference
    `_index.md` shipped with this skill.
    """
    return f"[{row_path}](./{row_path})"


def build_row(
    table: str,
    row_path: str,
    topic: Optional[str] = None,
    last_updated: Optional[str] = None,
    superseded_by: Optional[str] = None,
    superseded_on: Optional[str] = None,
    closed_on: Optional[str] = None,
    reason: Optional[str] = None,
) -> str:
    link = make_link(row_path)
    if table == "active":
        require(topic, "--topic")
        require(last_updated, "--last-updated")
        return f"| {link} | {topic} | {last_updated} |"
    if table == "superseded":
        require(superseded_by, "--superseded-by")
        require(superseded_on, "--superseded-on")
        require(reason, "--reason")
        sb_link = make_link(superseded_by) if superseded_by else ""
        return f"| {link} | {sb_link} | {superseded_on} | {reason} |"
    if table in ("completed", "abandoned"):
        require(closed_on, "--closed-on")
        require(reason, "--reason")
        return f"| {link} | {closed_on} | {reason} |"
    die(f"Unknown table: {table}")
    return ""  # unreachable


def require(value: Optional[str], flag: str) -> None:
    if value is None or value == "":
        die(f"Missing required argument for this action: {flag}")


# ---------------------------------------------------------------------------
# Quick Status recount
# ---------------------------------------------------------------------------


QUICK_STATUS_KEYS = (
    ("Active", "active"),
    ("Superseded", "superseded"),
    ("Completed", "completed"),
    ("Abandoned", "abandoned"),
)


def recount_quick_status(lines: list[str]) -> list[str]:
    counts = {t: len(find_table_rows(lines, t)) for t in TABLES}
    total = sum(counts.values())

    # Find the "## Quick status" section.
    start, end = find_section_range(lines, "## Quick status")

    # Locate and replace the count lines. We match `- **<Name>:** <number>`.
    pattern = re.compile(
        r"^- \*\*(Active|Superseded|Completed|Abandoned|Total):\*\* \d+\s*$"
    )

    new_section: list[str] = []
    for i in range(start, end):
        line = lines[i]
        if pattern.match(line):
            # Skip — we will re-emit the whole block in canonical order below.
            continue
        new_section.append(line)

    # Insert canonical counts immediately after the heading-blank-line pair, if present.
    # Strategy: build the canonical block, then prepend it to `new_section` after any
    # leading blank line.
    canonical_block = [
        f"- **Active:** {counts['active']}",
        f"- **Superseded:** {counts['superseded']}",
        f"- **Completed:** {counts['completed']}",
        f"- **Abandoned:** {counts['abandoned']}",
        f"- **Total:** {total}",
    ]

    # Strip leading and trailing blank lines from `new_section` so we control spacing.
    while new_section and new_section[0].strip() == "":
        new_section.pop(0)
    while new_section and new_section[-1].strip() == "":
        new_section.pop()

    # If `new_section` is empty (the original block was only the count lines),
    # the section body becomes just the canonical block.
    if new_section:
        rebuilt = ["", *canonical_block, "", *new_section, ""]
    else:
        rebuilt = ["", *canonical_block, ""]

    return lines[:start] + rebuilt + lines[end:]


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def op_add(args: argparse.Namespace, lines: list[str]) -> list[str]:
    existing = find_row_by_path(lines, args.table, args.row_path)
    if existing is not None:
        die(
            f"Row for path '{args.row_path}' already exists in table '{args.table}'. "
            "Use --action update or --action move instead."
        )
    row = build_row(
        table=args.table,
        row_path=args.row_path,
        topic=args.topic,
        last_updated=args.last_updated,
        superseded_by=args.superseded_by,
        superseded_on=args.superseded_on,
        closed_on=args.closed_on,
        reason=args.reason,
    )
    _, sep_idx = header_and_separator_indices(lines, args.table)
    return lines[: sep_idx + 1] + [row] + lines[sep_idx + 1 :]


def op_update(args: argparse.Namespace, lines: list[str]) -> list[str]:
    if args.table != "active":
        die("--action update is only meaningful for the Active table (refreshes last-updated).")
    found = find_row_by_path(lines, args.table, args.row_path)
    if found is None:
        die(f"No row found for path '{args.row_path}' in table '{args.table}'.")
    idx, _ = found
    require(args.last_updated, "--last-updated")
    # Reconstruct the row preserving the link (slug) and topic, replacing last-updated.
    line = lines[idx]
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 3:
        die(f"Malformed Active row at line {idx + 1}: {line!r}")
    cells[2] = args.last_updated
    lines[idx] = "| " + " | ".join(cells) + " |"
    return lines


def op_remove(args: argparse.Namespace, lines: list[str]) -> list[str]:
    table = args.from_table or args.table
    if table is None:
        die("--action remove requires --table or --from-table.")
    found = find_row_by_path(lines, table, args.row_path)
    if found is None:
        # Idempotent: removing a missing row is a no-op.
        return lines
    idx, _ = found
    return lines[:idx] + lines[idx + 1 :]


def op_move(args: argparse.Namespace, lines: list[str]) -> list[str]:
    require(args.from_table, "--from-table")
    require(args.to_table, "--to-table")
    if args.from_table == args.to_table:
        die("--from-table and --to-table must differ for a move.")

    # Build the destination row first so that input validation happens before we mutate state.
    new_path = args.new_row_path or args.row_path
    row = build_row(
        table=args.to_table,
        row_path=new_path,
        topic=args.topic,
        last_updated=args.last_updated,
        superseded_by=args.superseded_by,
        superseded_on=args.superseded_on,
        closed_on=args.closed_on,
        reason=args.reason,
    )

    # Remove from source.
    found = find_row_by_path(lines, args.from_table, args.row_path)
    if found is None:
        die(
            f"No row found for path '{args.row_path}' in source table '{args.from_table}'."
        )
    src_idx, _ = found
    lines = lines[:src_idx] + lines[src_idx + 1 :]

    # Add to destination.
    _, sep_idx = header_and_separator_indices(lines, args.to_table)
    return lines[: sep_idx + 1] + [row] + lines[sep_idx + 1 :]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Maintain a restart-guides _index.md (add/update/remove/move/recount).",
    )
    parser.add_argument("--index", required=True, help="Path to _index.md.")
    parser.add_argument(
        "--action",
        required=True,
        choices=("add", "update", "remove", "move", "recount"),
    )
    parser.add_argument("--table", choices=TABLES, help="Target table for add/update.")
    parser.add_argument("--from-table", choices=TABLES, help="Source table for move.")
    parser.add_argument("--to-table", choices=TABLES, help="Destination table for move.")
    parser.add_argument(
        "--row-path",
        help="Relative path to the guide (e.g. 'active/2026-05-12-foo.md').",
    )
    parser.add_argument(
        "--new-row-path",
        help="New row path (used by move when the file is being placed in a new subfolder).",
    )
    parser.add_argument("--topic", help="Topic cell (Active table only).")
    parser.add_argument("--last-updated", help="Date (YYYY-MM-DD).")
    parser.add_argument("--superseded-by", help="Path to the superseding guide.")
    parser.add_argument("--superseded-on", help="Date the supersession happened.")
    parser.add_argument("--closed-on", help="Date the guide moved to completed/abandoned.")
    parser.add_argument("--reason", help="One-sentence reason (closure or supersession).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    index_path = Path(args.index)
    lines = read_index(index_path)

    if args.action == "add":
        require(args.table, "--table")
        require(args.row_path, "--row-path")
        lines = op_add(args, lines)
        lines = recount_quick_status(lines)
    elif args.action == "update":
        require(args.table, "--table")
        require(args.row_path, "--row-path")
        lines = op_update(args, lines)
        # No recount: row count is unchanged.
    elif args.action == "remove":
        require(args.row_path, "--row-path")
        lines = op_remove(args, lines)
        lines = recount_quick_status(lines)
    elif args.action == "move":
        require(args.row_path, "--row-path")
        lines = op_move(args, lines)
        lines = recount_quick_status(lines)
    elif args.action == "recount":
        lines = recount_quick_status(lines)
    else:
        die(f"Unknown action: {args.action}")

    write_index(index_path, lines)

    # Per-action confirmation BEFORE the generic OK line. The move action used
    # to print only the generic line, which made it impossible for a calling
    # agent to distinguish "row moved successfully" from "no-op". Each branch
    # below names exactly which row was touched and where it landed, so the
    # caller can verify behaviour from stdout alone.
    if args.action == "add":
        print(
            f"[update_index.py] Added row {args.row_path!r} to {args.table!r} table in {index_path}"
        )
    elif args.action == "update":
        print(
            f"[update_index.py] Updated row {args.row_path!r} in {args.table!r} table "
            f"(last-updated -> {args.last_updated!r}) in {index_path}"
        )
    elif args.action == "remove":
        table = args.from_table or args.table or "<auto>"
        print(
            f"[update_index.py] Removed row {args.row_path!r} from {table!r} table in {index_path}"
        )
    elif args.action == "move":
        new_path = args.new_row_path or args.row_path
        print(
            f"[update_index.py] Moved row {args.row_path!r} ({args.from_table!r} table) "
            f"-> {new_path!r} ({args.to_table!r} table) in {index_path}"
        )
    elif args.action == "recount":
        print(f"[update_index.py] Recounted Quick Status block in {index_path}")

    print(f"OK: {args.action} on {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
