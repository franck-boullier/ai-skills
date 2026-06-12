# Connectivity Check Template

Use this template in **Step 9** to write the test entry at:
`[MEMORY-STORE-ROOT]/test/connectivity-check-YYYY-MM-DD.md`

(For `[MEMORY-MODE] = agent`, `[MEMORY-STORE-ROOT]` is `[AGENT-ROOT]/memories/`. For `workspace` and `workspace-confirm-and-update`, it is `[MEMORY-ROOT]/memories/` — the workspace's tier-2 memory store root.)

**Before writing the file, resolve all placeholders:**

| Placeholder | Replace with |
| --- | --- |
| `[generate a UUID]` | A freshly generated UUID (e.g., `f47ac10b-58cc-4372-a567-0e02b2c3d479`) |
| `YYYY-MM-DD` | Today's date in both the filename and the file body |
| `[STORAGE-TYPE]` | Confirmed backend type from Step 2 |
| `[STORAGE-PROVIDER]` | Confirmed provider from Step 2 |
| `[STORAGE-LOCATION]` | Fully qualified path confirmed in Step 2 |

---

```markdown
---
doc-id: [generate a UUID]
title: Connectivity Check — YYYY-MM-DD
description: Initial connectivity verification written by build-agent-memory during agent setup.
category: test
created: YYYY-MM-DD
retention: permanent
---

# Connectivity Check

This entry was written by the `build-agent-memory` skill during initial setup to confirm that the configured storage backend is reachable and writable.

**Backend:** [STORAGE-TYPE] — [STORAGE-PROVIDER] / [STORAGE-LOCATION]
**Test date:** YYYY-MM-DD
**Result:** PASS
```
