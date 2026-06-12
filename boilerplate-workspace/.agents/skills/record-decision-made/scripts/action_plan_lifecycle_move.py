#!/usr/bin/env python3
"""
Atomically move a paired action plan between lifecycle subfolders.

This is the action-plan analogue of the restart-guide
`restart-from-previous-session/scripts/lifecycle_move.py`. Action plans live
under `memories/decision-records/list-decision-action-plans/{subfolder}/`,
where the subfolder must always agree with the plan's `status:` front-matter
field:

    active/    <-> status: Active
    paused/    <-> status: Paused
    completed/ <-> status: Complete      (NOTE: "Complete", not "Completed")
    abandoned/ <-> status: Abandoned

`decisions.config.md` previously noted "there is no automated mover — moves
happen by hand or via a future status-transition skill." This IS that mover.

A move is five coordinated edits (the exact list `record-decision-made`
documents under "Moving an action plan between lifecycle subfolders"):

    1. Flip the plan's `status:` front-matter to the destination's value.
    2. Physically relocate active|paused|.../<plan>.md to the destination.
    3. Source sub-index `{src}/_index.md`: remove the row, fix the count.
    4. Destination sub-index `{dst}/_index.md`: add the row, fix the count.
    5. Parent `_index.md`: per-subfolder bullet counts + Quick-status totals
       line + the plan's cross-folder-log row (File link, Status, Subfolder).

Validation always precedes any mutation. For a move to `completed/`, the
precondition "every task is done" is checked from the per-task `**Status:**`
lines in the body (override with --force if your plan uses a shape this can't
read). The status flip and file move roll back if an index edit fails.

The sub-indexes do NOT share a column schema — each has a distinct 4th
(and sometimes 3rd) column:

    active/    | File | Decision | Owner     | Progress |
    paused/    | File | Decision | Owner     | Blocker  |
    completed/ | File | Decision | Completed | Notes    |
    abandoned/ | File | Decision | Abandoned | Reason   |

The Decision cell (column 2) is carried over from the source row
automatically; the destination-specific cells are supplied via --owner,
--date, and --note (see each destination's requirements below).

Usage
-----
    # Close a finished plan (active -> completed). --date fills the
    # "Completed" column; --note fills the "Notes" column.
    python action_plan_lifecycle_move.py \\
        --root memories/decision-records/list-decision-action-plans \\
        --plan 2026-05-31-flag22-action-plan.md \\
        --to completed --date 2026-05-31 \\
        --note "All 5 tasks done; paired restart guide closed."

    # Pause a plan (active -> paused). --owner + --note (the Blocker cell).
    python action_plan_lifecycle_move.py --root <root> --plan <file> \\
        --to paused --owner "Franck Boullier" --note "Blocked on X."

    # Heal drifted counts across every index without moving anything.
    python action_plan_lifecycle_move.py --root <root> --recount

Destination cell requirements
-----------------------------
    completed : --date (Completed), --note (Notes)
    abandoned : --date (Abandoned), --note (Reason)
    paused    : --owner (Owner),    --note (Blocker)
    active    : --owner (Owner),    --note (Progress)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

SUBFOLDERS = ("active", "paused", "completed", "abandoned")

# subfolder -> canonical `status:` front-matter value
STATUS_VALUE = {
    "active": "Active",
    "paused": "Paused",
    "completed": "Complete",
    "abandoned": "Abandoned",
}

# subfolder -> (col3 header, col4 header). Columns 1-2 are always File, Decision.
SUBINDEX_COLS = {
    "active": ("Owner", "Progress"),
    "paused": ("Owner", "Blocker"),
    "completed": ("Completed", "Notes"),
    "abandoned": ("Abandoned", "Reason"),
}

# Per-task statuses that mean "not finished" — block a move to completed/.
UNFINISHED_TASK_STATUSES = {"not started", "in progress", "blocked", "paused"}


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Front-matter (minimal, no PyYAML — mirrors lifecycle_move.py)
# ---------------------------------------------------------------------------


def read_frontmatter(path: Path) -> tuple[list[str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        die(f"Front matter at top of {path} is not closed (no trailing '---').")
    return lines[1:end], lines[end + 1 :]


def write_frontmatter(path: Path, fm: list[str], body: list[str]) -> None:
    text = "\n".join(["---", *fm, "---", *body])
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def replace_status(fm: list[str], value: str) -> list[str]:
    out, found = [], False
    for line in fm:
        if re.match(r"\s*status\s*:", line):
            # Preserve original quoting style if present.
            out.append(f'status: "{value}"' if '"' in line else f"status: {value}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f'status: "{value}"')
    return out


# ---------------------------------------------------------------------------
# Markdown table helpers
# ---------------------------------------------------------------------------


def is_data_row(line: str) -> bool:
    """A table data row begins with '| [' (a markdown link in the File cell)."""
    return line.lstrip().startswith("| [")


def split_cells(row: str) -> list[str]:
    """Split a markdown table row into trimmed cell strings."""
    inner = row.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def plural(n: int) -> str:
    return "" if n == 1 else "s"


def count_data_rows(lines: list[str]) -> int:
    return sum(1 for ln in lines if is_data_row(ln))


def set_subindex_count(lines: list[str], sub: str) -> None:
    """Rewrite the '**Quick status:** N <sub> plan(s)' line from the row count."""
    n = count_data_rows(lines)
    target = f"**Quick status:** {n} {sub} plan{plural(n)}"
    for i, ln in enumerate(lines):
        if ln.strip().startswith("**Quick status:**"):
            lines[i] = target
            return
    die(f"No '**Quick status:**' line found in the {sub}/ sub-index.")


EMPTY_MARKER_RE = re.compile(r"^_No \w+ plans?\._\s*$")


def remove_row(lines: list[str], filename: str, sub: str) -> str:
    """Remove the data row whose File link points at <filename>. Return its
    Decision cell (column 2). Add the '_No <sub> plans._' marker if the table
    is now empty."""
    idx = next(
        (i for i, ln in enumerate(lines) if is_data_row(ln) and filename in ln), None
    )
    if idx is None:
        die(f"No row for {filename} found in the {sub}/ sub-index.")
    decision = split_cells(lines[idx])[1]
    del lines[idx]
    if count_data_rows(lines) == 0:
        # Insert an empty-state marker after the separator row if not present.
        if not any(EMPTY_MARKER_RE.match(ln) for ln in lines):
            sep = next(
                (i for i, ln in enumerate(lines) if re.match(r"\|\s*-{2,}", ln)), None
            )
            if sep is not None:
                lines.insert(sep + 1, "")
                lines.insert(sep + 2, f"_No {sub} plans._")
    return decision


def add_row(lines: list[str], row: str, sub: str) -> None:
    """Append a data row after the last existing row (or after the header
    separator if the table is empty). Strip any '_No <sub> plans._' marker."""
    # Drop empty-state marker (and a possible blank line before it).
    cleaned = []
    for ln in lines:
        if EMPTY_MARKER_RE.match(ln):
            if cleaned and cleaned[-1].strip() == "":
                cleaned.pop()
            continue
        cleaned.append(ln)
    lines[:] = cleaned
    last = max(
        (i for i, ln in enumerate(lines) if is_data_row(ln)),
        default=None,
    )
    if last is None:
        sep = next(
            (i for i, ln in enumerate(lines) if re.match(r"\|\s*-{2,}", ln)), None
        )
        if sep is None:
            die(f"No table separator found in the {sub}/ sub-index; cannot add row.")
        lines.insert(sep + 1, row)
    else:
        lines.insert(last + 1, row)


def build_subindex_row(sub: str, filename: str, decision: str, c3: str, c4: str) -> str:
    link = f"[{filename}](./{filename})"
    return f"| {link} | {decision} | {c3} | {c4} |"


# ---------------------------------------------------------------------------
# Parent _index.md
# ---------------------------------------------------------------------------


def update_parent_index(root: Path, dry: bool) -> dict[str, int]:
    """Recount the parent _index.md from the live sub-indexes and rewrite:
    the per-subfolder bullet counts, the Quick-status totals line, and (caller
    handles the cross-folder-log row). Returns the counts dict."""
    counts = {
        sub: count_data_rows((root / sub / "_index.md").read_text().splitlines())
        for sub in SUBFOLDERS
    }
    parent = root / "_index.md"
    lines = parent.read_text(encoding="utf-8").splitlines()

    for i, ln in enumerate(lines):
        # Bullet lines like: - [`active/`](./active/_index.md) — ... (N plans)
        m = re.match(r"(\s*-\s*\[`(\w+)/`\].*\()\d+ plans?(\).*)$", ln)
        if m and m.group(2) in counts:
            n = counts[m.group(2)]
            lines[i] = f"{m.group(1)}{n} plan{plural(n)}{m.group(3)}"
            continue
        if ln.strip().startswith("**Quick status:**") and "total plans" in ln:
            total = sum(counts.values())
            lines[i] = (
                f"**Quick status:** {total} total plans | "
                f"{counts['active']} active | {counts['paused']} paused | "
                f"{counts['completed']} completed | {counts['abandoned']} abandoned"
            )
    if not dry:
        text = "\n".join(lines)
        parent.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")
    return counts


def update_parent_log_row(root: Path, filename: str, dst: str, dry: bool) -> None:
    """Repoint the moved plan's row in the parent cross-folder log: File link,
    Status column, Subfolder column all reflect the destination subfolder."""
    parent = root / "_index.md"
    lines = parent.read_text(encoding="utf-8").splitlines()
    idx = next(
        (i for i, ln in enumerate(lines) if is_data_row(ln) and filename in ln), None
    )
    if idx is None:
        die(f"No cross-folder-log row for {filename} in the parent _index.md.")
    cells = split_cells(lines[idx])
    # cells: [File, Decision, Status, Subfolder]
    cells[0] = f"[{dst}/{filename}](./{dst}/{filename})"
    cells[2] = STATUS_VALUE[dst]
    cells[3] = f"{dst}/"
    lines[idx] = "| " + " | ".join(cells) + " |"
    if not dry:
        text = "\n".join(lines)
        parent.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")


# ---------------------------------------------------------------------------
# Completion precondition
# ---------------------------------------------------------------------------


def unfinished_tasks(body: list[str]) -> list[str]:
    """Return human-readable markers of not-yet-finished tasks (block a move to
    completed/). Robust to the two task shapes used in this workspace:

      (1) per-task block with its own status line:  `- **Status:** Not started`
      (2) single-bullet task with an inline status:
          `- [ ] **Task 2 — ...** — Owner: X — Status: Not started — ...`

    Signals: an UNCHECKED task checkbox (`- [ ] **Task ...`), or an explicit
    unfinished `Status:` value (bolded or inline, anywhere on the line).
    """
    bad: list[str] = []
    alt = "|".join(re.escape(s) for s in sorted(UNFINISHED_TASK_STATUSES))
    status_re = re.compile(rf"status:\**\s*({alt})\b", re.IGNORECASE)
    for ln in body:
        if re.match(r"\s*-\s*\[\s\]\s*\*\*Task", ln):
            m = re.search(r"\*\*(Task[^*]+?)\*\*", ln)
            bad.append(f"unchecked: {m.group(1).strip() if m else ln.strip()[:60]}")
            continue
        m = status_re.search(ln)
        if m:
            bad.append(f"status: {m.group(1)}")
    return bad


# ---------------------------------------------------------------------------
# Recount mode
# ---------------------------------------------------------------------------


def do_recount(root: Path, dry: bool) -> int:
    for sub in SUBFOLDERS:
        idx = root / sub / "_index.md"
        lines = idx.read_text(encoding="utf-8").splitlines()
        before = next((ln for ln in lines if ln.strip().startswith("**Quick status:**")), "")
        set_subindex_count(lines, sub)
        after = next((ln for ln in lines if ln.strip().startswith("**Quick status:**")), "")
        if not dry:
            text = "\n".join(lines)
            idx.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")
        flag = "" if before == after else "  <- changed"
        print(f"[recount] {sub}/_index.md: {after.replace('**Quick status:** ', '')}{flag}")
    counts = update_parent_index(root, dry)
    print(
        f"[recount] parent _index.md: {sum(counts.values())} total | "
        + " | ".join(f"{counts[s]} {s}" for s in SUBFOLDERS)
    )
    print("OK: recount complete." + (" (dry-run — no files written)" if dry else ""))
    return 0


# ---------------------------------------------------------------------------
# Move mode
# ---------------------------------------------------------------------------


def locate_plan(root: Path, plan_arg: str) -> tuple[str, str]:
    """Return (source_subfolder, filename) for the plan. Accepts a bare
    filename (searched across subfolders) or a 'subfolder/filename' path."""
    plan_arg = plan_arg.strip().lstrip("./")
    if "/" in plan_arg:
        sub, filename = plan_arg.split("/", 1)
        if sub not in SUBFOLDERS:
            die(f"'{sub}' is not a lifecycle subfolder.")
        if not (root / sub / filename).is_file():
            die(f"Plan not found: {root / sub / filename}")
        return sub, filename
    filename = plan_arg
    found = [sub for sub in SUBFOLDERS if (root / sub / filename).is_file()]
    if not found:
        die(f"Plan '{filename}' not found in any of: {', '.join(SUBFOLDERS)}.")
    if len(found) > 1:
        die(f"Plan '{filename}' exists in multiple subfolders ({found}); pass 'subfolder/{filename}'.")
    return found[0], filename


def do_move(root: Path, args: argparse.Namespace) -> int:
    dst = args.to
    if dst not in SUBFOLDERS:
        die(f"--to must be one of: {', '.join(SUBFOLDERS)}.")
    src, filename = locate_plan(root, args.plan)
    if src == dst:
        die(f"Plan is already in '{dst}/'. Nothing to move.")

    src_file = root / src / filename
    dst_file = root / dst / filename
    if dst_file.exists():
        die(f"Destination already exists, refusing to overwrite: {dst_file}")

    # ---- Validate destination-cell args ----
    if dst in ("completed", "abandoned"):
        if not args.date:
            die(f"--date is required when moving to '{dst}/' (fills the '{SUBINDEX_COLS[dst][0]}' column).")
        if not args.note:
            die(f"--note is required when moving to '{dst}/' (fills the '{SUBINDEX_COLS[dst][1]}' column).")
        c3, c4 = args.date, args.note
    else:  # active / paused
        if not args.owner:
            die(f"--owner is required when moving to '{dst}/' (fills the 'Owner' column).")
        if not args.note:
            die(f"--note is required when moving to '{dst}/' (fills the '{SUBINDEX_COLS[dst][1]}' column).")
        c3, c4 = args.owner, args.note

    fm, body = read_frontmatter(src_file)
    if not fm:
        die(f"Plan has no front matter: {src_file}")

    # ---- Completion precondition ----
    if dst == "completed":
        bad = unfinished_tasks(body)
        if bad and not args.force:
            die(
                "Refusing to move to 'completed/': these task Status values are not "
                f"finished: {bad}. Finish them (or pass --force if your plan uses a "
                "shape this check can't read; say so in the session log)."
            )

    if args.dry_run:
        print(f"DRY RUN: would flip status -> {STATUS_VALUE[dst]!r} in {src}/{filename}")
        print(f"DRY RUN: would move {src}/{filename} -> {dst}/{filename}")
        print(f"DRY RUN: would remove row from {src}/_index.md and add to {dst}/_index.md")
        print(f"DRY RUN: would repoint the parent cross-folder-log row + recount all counts")
        return 0

    # ---- 1. status flip + 2. file move ----
    write_frontmatter(src_file, replace_status(fm, STATUS_VALUE[dst]), body)
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_file), str(dst_file))

    try:
        # ---- 3. remove from source sub-index (carry the Decision cell over) ----
        src_idx = root / src / "_index.md"
        sl = src_idx.read_text(encoding="utf-8").splitlines()
        decision = remove_row(sl, filename, src)
        set_subindex_count(sl, src)
        src_idx.write_text("\n".join(sl) + "\n", encoding="utf-8")

        if args.decision:
            decision = args.decision

        # ---- 4. add to destination sub-index ----
        dst_idx = root / dst / "_index.md"
        dl = dst_idx.read_text(encoding="utf-8").splitlines()
        add_row(dl, build_subindex_row(dst, filename, decision, c3, c4), dst)
        set_subindex_count(dl, dst)
        dst_idx.write_text("\n".join(dl) + "\n", encoding="utf-8")

        # ---- 5. parent: cross-folder-log row + recount bullets/totals ----
        update_parent_log_row(root, filename, dst, dry=False)
        counts = update_parent_index(root, dry=False)
    except Exception as e:  # roll back the file move + status flip
        try:
            shutil.move(str(dst_file), str(src_file))
            fm2, body2 = read_frontmatter(src_file)
            write_frontmatter(src_file, replace_status(fm2, STATUS_VALUE[src]), body2)
        except Exception as e2:  # pragma: no cover
            print(f"WARNING: rollback failed: {e2}", file=sys.stderr)
        die(f"Index edit failed; file move rolled back. Cause: {e}")

    print(f"[action_plan_lifecycle_move.py] Flipped status -> {STATUS_VALUE[dst]!r} in {dst}/{filename}")
    print(f"[action_plan_lifecycle_move.py] Moved {src}/{filename} -> {dst}/{filename}")
    print(f"[action_plan_lifecycle_move.py] {src}/_index.md: removed row; {dst}/_index.md: added row")
    print(
        f"[action_plan_lifecycle_move.py] parent _index.md: log row -> {dst}/; counts now "
        + " | ".join(f"{counts[s]} {s}" for s in SUBFOLDERS)
    )
    print(f"OK: moved {filename} '{src}' -> '{dst}'; status '{STATUS_VALUE[dst]}'.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Move a paired action plan between lifecycle subfolders (active/paused/completed/abandoned), keeping status, file location, and all three index surfaces consistent.",
    )
    p.add_argument("--root", required=True, help="Path to the list-decision-action-plans/ folder.")
    p.add_argument("--plan", help="Plan filename (searched across subfolders) or 'subfolder/filename'.")
    p.add_argument("--to", help="Destination subfolder: active | paused | completed | abandoned.")
    p.add_argument("--date", help="Transition date YYYY-MM-DD (the Completed/Abandoned column).")
    p.add_argument("--owner", help="Owner cell (required for moves to active/ or paused/).")
    p.add_argument("--note", help="4th-column cell: Progress (active) / Blocker (paused) / Notes (completed) / Reason (abandoned).")
    p.add_argument("--decision", help="Override the Decision cell; default carries it from the source row.")
    p.add_argument("--force", action="store_true", help="Skip the 'every task finished' precondition for completed/.")
    p.add_argument("--recount", action="store_true", help="Heal drifted counts across every index; no move.")
    p.add_argument("--dry-run", action="store_true", help="Print what would change without writing.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).resolve()
    if not root.is_dir():
        die(f"--root is not a directory: {root}")
    for sub in SUBFOLDERS:
        if not (root / sub / "_index.md").is_file():
            die(f"Expected sub-index missing: {root / sub / '_index.md'}")
    if args.recount:
        return do_recount(root, args.dry_run)
    if not args.plan or not args.to:
        die("Provide --plan and --to (or use --recount).")
    return do_move(root, args)


if __name__ == "__main__":
    sys.exit(main())
