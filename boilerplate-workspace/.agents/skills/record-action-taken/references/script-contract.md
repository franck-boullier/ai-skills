# Reference — `resolve_action.py` contract

The bundled helper at `scripts/resolve_action.py` performs the deterministic core of an action resolution. The orchestrating skill (the agent reading SKILL.md) is responsible for everything **before** invoking the script — reading MEMORY.md, ASK-BACK on missing outcome, fuzzy ID search, privacy ASK-BEFORE, deriving the `resolved-by` actor — and for surfacing the script's output back to the caller.

The script never parses MEMORY.md. All paths are passed in explicitly so the contract between the agent and the script is narrow and testable.

## Invocation

```bash
python scripts/resolve_action.py \
  --shared-root <abs-path-to-shared-actions-folder> \
  [--local-root <abs-path-to-caller-agent-actions-folder>] \
  --id <A-uuidv7> \
  --outcome <done|skipped|obsolete|cancelled> \
  [--note "<resolution note>"] \
  --resolved-by "<actor>" \
  [--resolved-at <iso8601>]
```

## Arguments

| Flag | Required | Notes |
| --- | --- | --- |
| `--shared-root` | yes | Absolute path to the source-of-truth actions folder (e.g. `<workspace>/memories/actions`). The script writes here. |
| `--local-root` | no | Absolute path to the caller-agent's local actions folder, when applicable. The script mirrors changes here. Skipped silently if the local folder has no record for the given id. |
| `--id` | yes | The action's UUIDv7 in the canonical `A-<uuid>` form. The script validates the structure and rejects malformed values. |
| `--outcome` | yes | One of `done`, `skipped`, `obsolete`, `cancelled`. The script rejects any other value. |
| `--note` | no | The resolution note. Defaults to `"No note provided."` when omitted. |
| `--resolved-by` | yes | Caller identity. Use `"user"` for human invocations and the agent name otherwise. |
| `--resolved-at` | no | ISO-8601 UTC timestamp. Defaults to `now()` in UTC, formatted `YYYY-MM-DDTHH:MM:SSZ`. |

## Successful output (stdout)

A single JSON object on success:

```json
{
  "id": "A-019e011c-829f-7f3b-ae23-f9a500c77a51",
  "outcome": "done",
  "new-path": "/abs/path/memories/actions/done/A-019e011c-...md",
  "resolved-at": "2026-05-07T06:25:06Z",
  "was-re-resolution": false
}
```

`new-path` is the final on-disk location of the record. `was-re-resolution` is `true` if the action was already in a per-outcome subfolder when the script ran.

## Error output (stderr)

A JSON error object and a non-zero exit code:

```json
{"error": "<code>", "message": "<human-readable message>"}
```

| Code | Meaning |
| --- | --- |
| `bad_id` | The id is missing, malformed, or not a UUIDv7. |
| `bad_outcome` | The outcome is not in the controlled vocabulary. |
| `bad_root` | `--shared-root` (or `--local-root`) does not exist. |
| `bad_record` | The record file is missing frontmatter or has invalid YAML. |
| `not_found` | No record exists at any path (open or per-outcome) for the given id. The agent's contract is to do fuzzy-search **before** calling the script with an alternate id. |
| `missing_dependency` | PyYAML is not installed. |
| `unexpected` | An exception bubbled up; the message contains the original error. |

## Atomicity guarantees

Each individual file write uses `os.replace` against a same-directory temp file, which is atomic on POSIX and on Windows.

Across multiple files (the record itself, the open INDEX, the destination INDEX, plus the local mirrors), the script wraps every operation in a transaction. If any step after the first fails, every prior step is rolled back to its pre-resolution state before the script exits with an error. The record is never left in a half-resolved state on disk.

## What the script does NOT do

- It does not parse MEMORY.md. Roots come in as arguments.
- It does not perform fuzzy description search. If the id is not found, it returns `not_found` and lets the agent decide what to do.
- It does not invoke `format-md-for-progressive-disclosure`. Per-outcome `INDEX.md` initialisation uses the bundled template at `references/index-template.md`. The agent may run `format-md-for-progressive-disclosure` separately if the host environment requires that skill's specific formatting conventions.
- It does not delete records. Even `cancelled` is a status with its own folder.
- It does not validate or alter `id`, `description`, `owner`, `due-date`, `priority`, `source`, `created-at`. These are immutable in this skill.

## Why this split

Putting the deterministic mutations behind a single script means the agent does not have to do brittle multi-file edits in a row, the rollback semantics are testable in isolation, and the human-facing behaviours (ASK-BACK, ASK-BEFORE, fuzzy search, summarising the result) can evolve independently from the on-disk contract.
