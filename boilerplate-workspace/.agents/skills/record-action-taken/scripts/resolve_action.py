#!/usr/bin/env python3
"""
resolve_action.py — atomic helper for the record-action-taken skill.

Performs the deterministic core of an action resolution:
  * validates the UUIDv7 id,
  * locates the existing record (open path or per-outcome subfolder),
  * merges resolution metadata into the frontmatter (preserving every
    original field),
  * appends a "## Resolution" or "## Resolution Event N" block to the body,
  * moves the file to the new outcome subfolder (or leaves it in place
    when the outcome did not change),
  * updates the open and per-outcome INDEX.md files **in the live workspace
    schema** (markdown-link IDs, the real column sets, and the
    "**Quick status:** N … actions" count line — see below),
  * mirrors every change into the caller-agent's local actions root when
    one is supplied,
  * rolls back every partial change if any step fails.

The script never parses MEMORY.md. The orchestrating agent reads MEMORY.md,
extracts the storage roots, and passes them in as explicit arguments.

INDEX schema (must match the on-disk convention — this is what the
2026-05-31 fix corrected; the prior version assumed raw-id rows + an
8-column outcome table that matched no live file):

    Open index (INDEX.md):
        | ID | Description | Owner | Due | Priority | Created |
    Per-outcome index (done|skipped|obsolete|cancelled / INDEX.md):
        | ID | Description | Owner | Resolved | Note |

    * The ID cell is a markdown link: `[A-<id>](./A-<id>.md)`.
    * `Resolved` is a date (YYYY-MM-DD), derived from `resolved-at`.
    * Each index carries a `**Quick status:** N <label> actions` line kept in
      sync with the row count; per-outcome indexes show `_No <outcome> actions._`
      when empty.
    * On open→outcome (and outcome→outcome) moves, the Description and Owner
      cells are carried over from the existing row so the resolved row matches
      what was shown while the action was open.

On success, prints a JSON object on stdout:

  {"id": "A-...", "outcome": "done",
   "new-path": "/abs/path/done/A-...md",
   "resolved-at": "2026-05-07T10:00:00Z",
   "was-re-resolution": false}

On error, prints a JSON object on stderr and exits non-zero:

  {"error": "<code>", "message": "<human-readable message>"}

Dependencies: PyYAML (install with `pip install --break-system-packages pyyaml`).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(json.dumps({
        "error": "missing_dependency",
        "message": "PyYAML is required. Install with: pip install --break-system-packages pyyaml",
    }) + "\n")
    sys.exit(2)


OUTCOMES = ("done", "skipped", "obsolete", "cancelled")
INDEX_FILENAME = "INDEX.md"
RECORD_PREFIX = "A-"
HERE = Path(__file__).resolve().parent


# ---------- error helpers ----------

class ResolveError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def die(code: str, message: str) -> "Any":
    sys.stderr.write(json.dumps({"error": code, "message": message}) + "\n")
    sys.exit(1)


# ---------- UUIDv7 validation ----------

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def validate_uuidv7(action_id: str) -> str:
    """Accept the canonical 'A-<uuidv7>' shape and return the UUID portion."""
    if not action_id:
        raise ResolveError("bad_id", "id must be a valid UUIDv7 (got empty)")
    if not action_id.startswith(RECORD_PREFIX):
        raise ResolveError("bad_id", f"id must start with {RECORD_PREFIX!r}")
    candidate = action_id[len(RECORD_PREFIX):]
    if not _UUID_RE.match(candidate):
        raise ResolveError("bad_id", f"id must be a valid UUIDv7 (got {action_id!r})")
    try:
        u = uuid.UUID(candidate)
    except ValueError as exc:  # pragma: no cover
        raise ResolveError("bad_id", f"id must be a valid UUIDv7: {exc}")
    if u.version != 7:
        raise ResolveError("bad_id", f"id must be a UUIDv7 (got version {u.version})")
    return candidate


# ---------- frontmatter / record I/O ----------

_FM_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?(.*)$", re.DOTALL)


def parse_record(text: str) -> tuple[dict, str]:
    m = _FM_RE.match(text)
    if not m:
        raise ResolveError("bad_record", "record is missing YAML frontmatter")
    fm_text, body = m.group(1), m.group(2)
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as exc:
        raise ResolveError("bad_record", f"frontmatter is not valid YAML: {exc}")
    if not isinstance(fm, dict):
        raise ResolveError("bad_record", "frontmatter must be a YAML mapping")
    return fm, body


def serialize_record(fm: dict, body: str) -> str:
    fm_text = yaml.safe_dump(
        fm,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    if not body.endswith("\n"):
        body = body + "\n"
    return f"---\n{fm_text}---\n\n{body.lstrip(chr(10))}"


# ---------- locate the record ----------

@dataclass
class Location:
    path: Path
    is_open: bool
    current_outcome: str | None  # None when is_open


def locate_record(shared_root: Path, action_id: str) -> Location | None:
    open_path = shared_root / f"{action_id}.md"
    if open_path.is_file():
        return Location(open_path, is_open=True, current_outcome=None)
    for outcome in OUTCOMES:
        p = shared_root / outcome / f"{action_id}.md"
        if p.is_file():
            return Location(p, is_open=False, current_outcome=outcome)
    return None


# ---------- frontmatter merge ----------

def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def update_frontmatter(
    fm: dict,
    outcome: str,
    resolved_at: str,
    resolved_by: str,
    note: str,
) -> dict:
    """Return a new frontmatter dict with resolution metadata applied."""
    new_fm = dict(fm)  # shallow copy is fine; we never mutate nested objects
    history = list(new_fm.get("resolution-history") or [])
    history.append({
        "resolved-at": resolved_at,
        "resolved-by": resolved_by,
        "status": outcome,
        "note": note,
    })
    new_fm["status"] = outcome
    new_fm["resolved-at"] = resolved_at
    new_fm["resolved-by"] = resolved_by
    new_fm["resolution-status"] = outcome
    new_fm["resolution-note"] = note
    new_fm["resolution-history"] = history
    return new_fm


def append_resolution_block(
    body: str,
    outcome: str,
    resolved_at: str,
    resolved_by: str,
    note: str,
    event_index: int,
) -> str:
    """Append a markdown resolution section to the body."""
    header = "## Resolution" if event_index == 1 else f"## Resolution Event {event_index}"
    body = body.rstrip()
    block = (
        f"\n\n{header}\n"
        f"**Resolved as:** {outcome}\n"
        f"**At:** {resolved_at}\n"
        f"**By:** {resolved_by}\n\n"
        f"{note}\n"
    )
    return body + block + "\n"


# ---------- INDEX.md handling ----------
#
# These functions encode the LIVE on-disk index convention (see the module
# docstring). Every helper operates on whole-file text so the Transaction can
# write atomically and roll back.

OPEN_HEADER = (
    "| ID | Description | Owner | Due | Priority | Created |\n"
    "| --- | --- | --- | --- | --- | --- |\n"
)
OUTCOME_HEADER = (
    "| ID | Description | Owner | Resolved | Note |\n"
    "| --- | --- | --- | --- | --- |\n"
)

# Per-outcome presentation, matching the live INDEX.md headers.
OUTCOME_TITLE = {
    "done": "Completed",
    "skipped": "Skipped",
    "obsolete": "Obsolete",
    "cancelled": "Cancelled",
}
OUTCOME_DESC = {
    "done": "Actions resolved with outcome `done`.",
    "skipped": "Actions resolved with outcome `skipped` (conscious decision not to act).",
    "obsolete": "Actions resolved with outcome `obsolete` (became irrelevant before being acted on).",
    "cancelled": "Actions resolved with outcome `cancelled` (withdrawn by the creator).",
}

_QUICK_RE = re.compile(r"^\*\*Quick status:\*\*.*$", re.MULTILINE)
_MARKER_RE = re.compile(r"^_No \w+ actions\._\s*$", re.MULTILINE)


def quick_label(outcome: str | None) -> str:
    """Quick-status label: 'open' for the open index; 'completed' for done;
    the outcome name otherwise (matches the live files)."""
    if outcome is None:
        return "open"
    return "completed" if outcome == "done" else outcome


def empty_marker(outcome: str) -> str:
    return f"_No {outcome} actions._"


def _esc(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def id_link(action_id: str) -> str:
    return f"[{action_id}](./{action_id}.md)"


def is_data_row(line: str) -> bool:
    """A table data row begins with '| [' (a markdown link in the ID cell)."""
    return line.lstrip().startswith("| [")


def split_cells(row: str) -> list[str]:
    inner = row.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def count_rows(text: str) -> int:
    return sum(1 for ln in text.splitlines() if is_data_row(ln))


def set_quick_status(text: str, outcome: str | None) -> str:
    """Rewrite the '**Quick status:** N <label> actions' line from the row
    count. No-op if the index has no such line (non-standard index)."""
    n = count_rows(text)
    line = f"**Quick status:** {n} {quick_label(outcome)} actions"
    if _QUICK_RE.search(text):
        return _QUICK_RE.sub(lambda _m: line, text, count=1)
    return text


def derive_description(fm: dict, body: str) -> str:
    """Fallback description (used only when no existing index row is found to
    carry over from): the body's first H1, minus an 'Action —' prefix."""
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            text = line[2:].strip()
            text = re.sub(r"^Action\s*[—-]\s*", "", text)
            return _esc(text)
    return _esc(str(fm.get("description") or fm.get("id") or "(no description)"))


def make_outcome_row(
    cells: list[str] | None,
    fm: dict,
    body: str,
    action_id: str,
    resolved_date: str,
    note: str,
) -> str:
    """Build a per-outcome row `| ID | Description | Owner | Resolved | Note |`.
    Description/Owner/ID are carried over from the removed source row when
    available (keeps the resolved row consistent with the open row); otherwise
    derived from the record."""
    if cells and len(cells) >= 3:
        id_cell, desc, owner = cells[0], cells[1], cells[2]
    else:
        id_cell = id_link(action_id)
        desc = derive_description(fm, body)
        owner = _esc(str(fm.get("owner", "")))
    return f"| {id_cell} | {desc} | {owner} | {resolved_date} | {_esc(note)} |\n"


def remove_row(text: str, action_id: str) -> tuple[str, list[str] | None]:
    """Remove the data row that references action_id (matched anywhere in the
    row, so it works regardless of raw-id vs [link] formatting). Return
    (new_text, removed_cells | None)."""
    lines = text.splitlines(keepends=True)
    for i, ln in enumerate(lines):
        if is_data_row(ln) and action_id in ln:
            cells = split_cells(ln)
            del lines[i]
            return "".join(lines), cells
    return text, None


def outcome_index_template(outcome: str) -> str:
    """Full per-outcome INDEX.md scaffold in the live shape (no frontmatter —
    the live files start at the H1)."""
    return (
        f"# {OUTCOME_TITLE[outcome]} Actions — Index\n\n"
        f"{OUTCOME_DESC[outcome]}\n\n"
        f"**Quick status:** 0 {quick_label(outcome)} actions\n\n"
        f"---\n\n"
        f"{OUTCOME_HEADER}"
    )


def open_index_template() -> str:
    return (
        "# Open Actions — Index\n\n"
        "Pending action items that have not yet been resolved.\n\n"
        "**Quick status:** 0 open actions\n\n"
        "---\n\n"
        f"{OPEN_HEADER}"
    )


def add_outcome_row(text: str, outcome: str, row: str) -> str:
    """Scaffold the index if empty, drop any empty-state marker, append the row."""
    if not text.strip():
        text = outcome_index_template(outcome)
    text = _MARKER_RE.sub("", text).rstrip() + "\n"
    return text + row


def finalize_outcome(text: str, outcome: str) -> str:
    """Recount the Quick-status line; (re)insert the empty marker if the table
    is now empty."""
    if not text.strip():
        text = outcome_index_template(outcome)
    text = set_quick_status(text, outcome)
    if count_rows(text) == 0 and not _MARKER_RE.search(text):
        text = text.rstrip() + f"\n\n{empty_marker(outcome)}\n"
    return text


# ---------- Transaction ----------

@dataclass
class Op:
    """A pending or applied filesystem change, with enough info to undo."""
    kind: str                      # "write" | "delete"
    path: Path
    new_content: str | None = None # for "write"
    backup: bytes | None = None    # original bytes for restore (None if file did not exist)


@dataclass
class Transaction:
    ops: list[Op] = field(default_factory=list)
    applied: list[Op] = field(default_factory=list)

    def write(self, path: Path, content: str) -> None:
        self.ops.append(Op(kind="write", path=path, new_content=content))

    def delete(self, path: Path) -> None:
        self.ops.append(Op(kind="delete", path=path))

    def commit(self) -> None:
        try:
            for op in self.ops:
                if op.kind == "write":
                    op.path.parent.mkdir(parents=True, exist_ok=True)
                    if op.path.exists():
                        op.backup = op.path.read_bytes()
                    self._atomic_write(op.path, op.new_content or "")
                    self.applied.append(op)
                elif op.kind == "delete":
                    if op.path.exists():
                        op.backup = op.path.read_bytes()
                        op.path.unlink()
                    self.applied.append(op)
        except Exception:
            self.rollback()
            raise

    def rollback(self) -> None:
        for op in reversed(self.applied):
            try:
                if op.kind == "write":
                    if op.backup is None:
                        if op.path.exists():
                            op.path.unlink()
                    else:
                        self._atomic_write_bytes(op.path, op.backup)
                elif op.kind == "delete":
                    if op.backup is not None:
                        self._atomic_write_bytes(op.path, op.backup)
            except Exception:
                pass
        self.applied.clear()

    @staticmethod
    def _atomic_write(path: Path, text: str) -> None:
        Transaction._atomic_write_bytes(path, text.encode("utf-8"))

    @staticmethod
    def _atomic_write_bytes(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=str(path.parent), delete=False, prefix=".tmp_", suffix=".swp"
        ) as fh:
            fh.write(data)
            tmp_name = fh.name
        os.replace(tmp_name, path)


# ---------- main planner ----------

def _read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _stage_index_updates(
    tx: Transaction,
    root: Path,
    loc: Location,
    outcome: str,
    fm: dict,
    body: str,
    full_id: str,
    resolved_at: str,
    note: str,
) -> None:
    """Stage the open/per-outcome INDEX.md edits for one root (shared or local),
    in the live schema, with carry-over and Quick-status recounting."""
    resolved_date = resolved_at[:10]
    open_index = root / INDEX_FILENAME
    dest_index = root / outcome / INDEX_FILENAME

    if loc.is_open:
        new_open, removed = remove_row(_read_or_empty(open_index), full_id)
        new_open = set_quick_status(new_open, None)
        if not new_open.strip():
            new_open = open_index_template()
        tx.write(open_index, new_open)

        row = make_outcome_row(removed, fm, body, full_id, resolved_date, note)
        dest = add_outcome_row(_read_or_empty(dest_index), outcome, row)
        dest = finalize_outcome(dest, outcome)
        tx.write(dest_index, dest)

    elif loc.current_outcome != outcome:
        src_index = root / loc.current_outcome / INDEX_FILENAME
        new_src, removed = remove_row(_read_or_empty(src_index), full_id)
        new_src = finalize_outcome(new_src, loc.current_outcome)
        tx.write(src_index, new_src)

        row = make_outcome_row(removed, fm, body, full_id, resolved_date, note)
        dest = add_outcome_row(_read_or_empty(dest_index), outcome, row)
        dest = finalize_outcome(dest, outcome)
        tx.write(dest_index, dest)
    # else: re-resolution, outcome unchanged → no index touch (per spec).


def plan_resolution(args: argparse.Namespace) -> dict:
    shared_root = Path(args.shared_root).resolve()
    if not shared_root.is_dir():
        raise ResolveError("bad_root", f"shared-root does not exist: {shared_root}")
    local_root = Path(args.local_root).resolve() if args.local_root else None
    if local_root is not None and not local_root.is_dir():
        raise ResolveError("bad_root", f"local-root does not exist: {local_root}")

    if args.outcome not in OUTCOMES:
        raise ResolveError(
            "bad_outcome",
            "outcome must be one of: " + ", ".join(OUTCOMES),
        )

    # 1. Validate id.
    full_id = args.id
    validate_uuidv7(full_id)

    # 2. Locate.
    loc = locate_record(shared_root, full_id)
    if loc is None:
        raise ResolveError("not_found", f"No record found for {full_id}")

    # 3. Read.
    record_text = loc.path.read_text(encoding="utf-8")
    fm, body = parse_record(record_text)

    is_re_resolution = not loc.is_open
    outcome_changed = is_re_resolution and (loc.current_outcome != args.outcome)
    file_will_move = loc.is_open or outcome_changed

    # 4. Compute new state.
    resolved_at = args.resolved_at or now_iso()
    note = args.note if args.note is not None else "No note provided."
    new_fm = update_frontmatter(fm, args.outcome, resolved_at, args.resolved_by, note)
    event_n = len(new_fm["resolution-history"])
    new_body = append_resolution_block(
        body, args.outcome, resolved_at, args.resolved_by, note, event_n
    )
    new_record_text = serialize_record(new_fm, new_body)

    # 5. Compute paths.
    new_outcome_dir = shared_root / args.outcome
    new_record_path = new_outcome_dir / f"{full_id}.md"

    # 6. Build the transaction.
    tx = Transaction()

    if file_will_move:
        tx.write(new_record_path, new_record_text)
        tx.delete(loc.path)
    else:
        # Re-resolution, outcome unchanged: rewrite in place.
        tx.write(loc.path, new_record_text)

    # Index updates (shared root). Carry Description/Owner over from the
    # existing row; recount Quick-status; handle empty markers.
    _stage_index_updates(
        tx, shared_root, loc, args.outcome, fm, body, full_id, resolved_at, note
    )

    # Local mirror, if applicable.
    if local_root is not None:
        local_loc = locate_record(local_root, full_id)
        if local_loc is not None:
            local_record_text = local_loc.path.read_text(encoding="utf-8")
            local_fm, local_body = parse_record(local_record_text)
            local_new_fm = update_frontmatter(
                local_fm, args.outcome, resolved_at, args.resolved_by, note
            )
            local_event_n = len(local_new_fm["resolution-history"])
            local_new_body = append_resolution_block(
                local_body, args.outcome, resolved_at, args.resolved_by, note, local_event_n
            )
            local_new_text = serialize_record(local_new_fm, local_new_body)

            local_new_path = local_root / args.outcome / f"{full_id}.md"
            local_file_will_move = local_loc.is_open or (
                local_loc.current_outcome != args.outcome
            )
            if local_file_will_move:
                tx.write(local_new_path, local_new_text)
                tx.delete(local_loc.path)
            else:
                tx.write(local_loc.path, local_new_text)

            _stage_index_updates(
                tx, local_root, local_loc, args.outcome,
                local_fm, local_body, full_id, resolved_at, note,
            )

    # 7. Commit (atomic per file; rollback on any failure).
    tx.commit()

    return {
        "id": full_id,
        "outcome": args.outcome,
        "new-path": str(new_record_path if file_will_move else loc.path),
        "resolved-at": resolved_at,
        "was-re-resolution": is_re_resolution,
    }


# ---------- CLI ----------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="resolve_action.py",
        description="Atomic resolution helper for the record-action-taken skill.",
    )
    p.add_argument("--shared-root", required=True,
                   help="Absolute path to the shared actions folder (the source of truth).")
    p.add_argument("--local-root", default=None,
                   help="Optional absolute path to the caller-agent's local actions folder.")
    p.add_argument("--id", required=True,
                   help="The action id, e.g. 'A-01928a3c-2f1e-7c2d-8b1a-...'.")
    p.add_argument("--outcome", required=True, choices=OUTCOMES,
                   help="One of: " + ", ".join(OUTCOMES))
    p.add_argument("--note", default=None,
                   help="Resolution note. Defaults to 'No note provided.' when omitted.")
    p.add_argument("--resolved-by", required=True,
                   help="Caller identity ('user' for human invocations; agent name otherwise).")
    p.add_argument("--resolved-at", default=None,
                   help="Optional ISO-8601 UTC timestamp; defaults to current UTC.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = plan_resolution(args)
    except ResolveError as exc:
        sys.stderr.write(json.dumps({"error": exc.code, "message": exc.message}) + "\n")
        return 1
    except Exception as exc:  # pragma: no cover
        sys.stderr.write(json.dumps({"error": "unexpected", "message": str(exc)}) + "\n")
        return 1
    sys.stdout.write(json.dumps(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
