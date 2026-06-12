---
name: compact-memories
description: Run the weekly memory-hygiene pass. Folds raw entries into compacted decisions/ and lessons/, prunes stale daily logs, and reports merges and removals. Usage: /compact-memories
---

# /compact-memories

Run the weekly memory-compaction workflow. Delegates to the topical and daily compactors and reports what was merged, promoted, or pruned.

## Usage

```bash
/compact-memories
```

## Output Structure

- Topical compaction summary — merges into `decisions/` and `lessons/`, duplicates collapsed
- Daily compaction summary — daily logs older than 90 days pruned, orphaned items promoted to the right topical store first
- MEMORY.md index size after the pass (must remain under 4 KB)
- Items that needed human review and were left in place

## Skill Reference

- `compact-agent-memories`
- `compact-agent-topical-memories`
- `compact-agent-daily-memories`
