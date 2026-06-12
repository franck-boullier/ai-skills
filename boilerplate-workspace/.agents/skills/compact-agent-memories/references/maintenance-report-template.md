---
title: Maintenance Report Template
description: >-
  Distilled reference for compact-agent-memories. Defines the structure of the
  unified maintenance report produced at Step 7, the contradiction table format
  used at Step 3, and guidance on what each section must include.
purpose: reference
tags:
  - maintenance-report
  - contradiction-table
  - reporting
audience: ai-agent
---

# Maintenance Report Template

## When to Produce the Report

Step 7 always runs, even if no compaction was performed. A "memory is healthy" outcome is still a valid report outcome.

---

## Contradiction Table (Step 3 — before any writes)

Present this table before any write action when contradictions are found. Do not start sub-skill execution until the user has reviewed and resolved each row (or explicitly deferred it).

```markdown
## Cross-Store Contradictions Found — Requires Human Resolution

| Entry A | Entry B | Store(s) | Nature of contradiction | Recommended resolution |
|---------|---------|----------|------------------------|----------------------|
| <source, date, summary of fact A> | <source, date, summary of fact B> | <store names> | <brief plain-language description> | <what the agent recommends> |
```

**If no contradictions found:** do not show the table. Proceed directly with sub-skill execution.

**If contradictions found:**

1. Present the table.
2. Wait for human response.
3. Sub-skills may proceed with content independent of the contradiction.
4. Hold Step 6 (index rebuild) until all contradictions are resolved.
5. Record each resolution in the report under "Contradictions".

---

## Unified Maintenance Report (Step 7)

```markdown
# Memory Maintenance Report — <YYYY-MM-DD>
Agent: <agent-name> (<agents/<kebab-case-name>/>)

## Summary

- Run completed: <timestamp>
- Identity context: SOUL.md and RULES.md loaded successfully [OR: default values
  hierarchy applied — SOUL.md was absent]
- Index size: <X KB before> → <Y KB after>
- Sub-skills invoked: compact-agent-daily-memories [YES/NO], compact-agent-topical-memories [YES/NO]

## Daily Log Reorganization

[If skipped:]
Not due — no completed calendar months have accumulated flat daily files.

[If run:]
- Monthly folders created: <list, or "none">
- Quarterly folders created: <list, or "none">
- Periods covered: <range>
- Gaps (missing daily files): <list, or "none">

## Topical Store Compaction

[If skipped:]
Not due — no topical store met merge, archive, prune, or oversize thresholds.

[If run:]
Per-store summary:
| Store | Merged | Archived | Pruned | New entries created | Notes |
|-------|--------|----------|--------|---------------------|-------|
| decisions/ | | | | | |
| projects/ | | | | | |
| activities/ | | | | | |
| lessons/ | | | | | |
| preferences/ | | | | | |
| people/ | | | | | |
| analysis/ | | | | | |

## Contradictions

[If none found:]
No cross-store contradictions detected.

[If found:]
| Contradiction | Resolution | Status |
|---------------|------------|--------|
| <summary> | <what the user decided> | Resolved / Pending |

## MEMORY.md Index

- Size before: <X KB>
- Size after: <Y KB>
- Entries added: <n>
- Entries removed: <n>
- Entries updated: <n>
- Entries demoted to stores (to stay under 4 KB): <list, or "none">
- Backend used: <backend category>

## Items Requiring Human Review

[Include any of the following that apply:]
- Pending contradiction resolutions (list)
- Failed write operations (list paths + error)
- Malformed files encountered (list paths + issue)
- Scheduled maintenance next due: <date>

[If nothing requires review:]
No items requiring human review.
```

---

## Guidance on Each Section

### Summary section

Always present. Provides the at-a-glance view of what the run did (or confirmed didn't need doing). Include the values hierarchy substitution notice here if the default was used.

### Daily log reorganization / Topical store compaction

Use "Not due" language rather than omitting the section entirely — a human reviewing the report needs to see that the orchestrator checked and found nothing to do, not that it forgot to check.

### Contradictions

If resolved synchronously (user responded in-session), record the resolution. If deferred (user said "I'll handle it later"), note the pending status and ask whether to proceed with the index rebuild.

### MEMORY.md Index

Always show before/after size. If the 4 KB limit required demotion of entries, list exactly which entries were moved and to which stores — this is the most operationally relevant part of the report for users who manage memory manually.

### Items Requiring Human Review

This section is the agent's handoff to the user. Even a clean run may have a "next scheduled maintenance" reminder here. Any failed writes or unresolved contradictions must appear here so they are not silently lost.

---

## Persistence (Optional)

Optionally save the report to `memory/maintenance/YYYY-MM-DD-maintenance.md`. After saving, invoke `format-md-for-progressive-disclosure` with context hint:
`"Weekly memory maintenance report for agent <agent-name>, YYYY-MM-DD. Category: maintenance-report. Audience: ai-agent."`
