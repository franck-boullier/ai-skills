# Dedicated Memory vs Shared Memory

This document is the **canonical definition** of these terms for the `build-agent-memory` skill. Other reference files link here instead of redefining them.

## Dedicated memory

**Dedicated memory** is this agent’s **own** persistent Tier 2 store: the `memories/` tree rooted at the destination confirmed during setup (`[AGENT-MEMORY-ROOT]` — same logical location as `[STORAGE-LOCATION]` in `MEMORY.md`).

It holds everything that belongs to **this agent’s** sessions and domain: environment facts, projects, decisions, preferences, people, lessons, domain-specific categories, and `test/`. The agent reads and writes here by default.

**In `MEMORY.md`:** Introduced under the heading **Dedicated memory** (or equivalent), followed by Environment, domain sections, and topical README links — all under that agent’s tree.

**Standalone agent:** Only dedicated memory exists. There is no shared store.

## Shared memory

**Shared memory** is **organizational** context that **multiple agents** are expected to read (and sometimes write) from a **single** store so everyone sees the same facts.

Typical content: company profile, mission, team structure, org-wide policies, shared glossary — anything that would **fork** if each agent kept a private copy.

**In `MEMORY.md`:** A single **Shared memory** section at the end of the index: a **pointer** to the shared store’s index (e.g. `[shared-store-path]/README.md`) and this agent’s access level (read-only vs read-write for named categories). **Do not** paste shared content into dedicated memory.

**Backend:** May use the same backend type as dedicated memory or a different one; Probe 5 records the explicit configuration.

## Rules (non-negotiable)

| Rule | Rationale |
| --- | --- |
| **No duplication** | Shared facts live in the shared store only. Copying them into `memories/` creates two sources of truth that diverge. |
| **Pointers, not mirrors** | `MEMORY.md` references the shared store path; it does not embed full shared documents. |
| **Write to the right place** | Categories owned by the org go to the shared path (if this agent has write access). Everything else goes to dedicated `memories/`. |
| **Dedicated stays agent-specific** | Per-user secrets, per-application projects, and agent-specific lessons stay in dedicated memory unless the builder explicitly designates a category as shared. |

## Quick decision

| Question | If yes → |
| --- | --- |
| Would another agent need the **same** fact to stay aligned? | Candidate for **shared** memory (if multi-agent). |
| Is it specific to **this** user, **this** agent’s workflow, or **this** project? | **Dedicated** memory. |

## See also

- `storage-backends.md` — where shared fits in backend selection and probe flow
- `memory-model.md` — Tier 1 index vs Tier 2 topical layout (applies to both dedicated and shared trees)
