# Memory Policies Reference

## Memory Update Triggers

The agent updates memory through a defined cycle: session start → read index + relevant topical files; during session → accumulate context; after significant event → write updates.

There are **two fundamentally different trigger categories** that must always be documented separately. They write to different destinations and follow different `MEMORY.md` update rules. See `daily-vs-topical-memory.md` for the full distinction.

### Topical memory triggers (selective, event-driven → topical stores + conditional MEMORY.md update)

| Event | Memory destination |
| --- | --- |
| A decision is made | `decisions/` |
| A correction is received | Relevant `preferences/` or fact entry |
| A new project is discussed | New or updated `projects/` file |
| A lesson is learned from a mistake | `lessons/` |
| A new person is introduced | `people/` |
| A recurring pattern is noticed | `MEMORY.md` index |

Extend this table with domain-specific triggers during Step 4 (e.g., "A contract is reviewed → write risk flags to `contracts/`").

### Daily log trigger (always, at session end → `memories/daily/` only, never MEMORY.md)

| Event | Memory destination |
| --- | --- |
| Session ends | Write `memories/daily/YYYY-MM-DD.md`; append one line to `memories/daily/README.md`; **do NOT touch `MEMORY.md`** |

This trigger fires at the end of **every** session without exception — regardless of whether any topical event occurred. The daily log and topical memory operations are separate: they use different destinations, different formats, and different `MEMORY.md` update rules. Never conflate them.

## Default Retention Policies

Use these as a starting point and adjust to the agent's domain and `RULES.md` data handling constraints.

| Category | Default retention |
| --- | --- |
| Decisions | Indefinitely (annual review recommended) |
| Preferences | Indefinitely (updated in place) |
| Projects | Duration of project + 90 days |
| Daily logs | 90 days, then summarize and prune |
| Lessons | Indefinitely |
| Code snippets | 7 days unless marked important |
| PII | Session only (unless `RULES.md` explicitly permits longer) |
| Health details | Forgotten after medically irrelevant |
| One-off queries | Never stored |
| Test entries | Kept permanently as setup verification records |

## Weekly Hygiene Cycle

Memory maintenance is not optional. A weekly self-audit covers:

1. **Memory hygiene** — Scan recent daily logs, extract important patterns, prune stale entries, verify the index is under 4 KB.
2. **Token efficiency** — Check whether any content in always-loaded files could be moved to on-demand stores.
3. **Contradiction detection** — Identify entries that conflict with each other or with recent decisions.

## DOs

- Keep `MEMORY.md` under 4 KB — it loads at every session start; a bloated index leaves less context for actual work. The 4 KB limit (raised from an earlier 4 KB target) accounts for mandatory structural elements and absolute storage paths, which can be 150–200 characters each on Windows. When the index approaches 4 KB, condense prose entries — not navigation links, which cannot be shortened without changing the storage configuration.
- Treat `MEMORY.md` as an index, not a database — pointers to stores, not the details themselves.
- Define explicit triggers for when memory gets updated — "After every significant conversation" is vague; "After every decision, correction, or new project introduction" is specific.
- Separate identity from memory — `SOUL.md`, `RULES.md`, and `IDENTITY.md` must never be modified by the memory system.
- Use structured formats for topical stores — consistent schema (date, decision, reasoning, alternatives, affected parties) makes retrieval reliable.
- Define retention policies for all categories — especially PII, health, and financial data.
- Version-control memory with git — provides an audit trail and the ability to recover from memory poisoning.
- Include a `lessons/` store — mistakes and learnings are among the highest-value memories.
- Plan for the cold-start period — the first 2–4 weeks, memory is sparse and the agent feels generic; the compounding effect kicks in around week 4.
- Use `root_prefix` in `MEMORY.md` YAML frontmatter and write README.md link targets relative to it — prevents repeating long absolute paths throughout the index while keeping the Storage backend path fully qualified.

## DON'Ts

- Do not store everything — memory is a curation exercise, not a recording exercise.
- Do not allow untrusted external content to modify memory directly — summarize before committing; verbatim storage is a poisoning vector.
- Do not store sensitive data without explicit retention policies.
- Do not treat daily logs as the primary memory — they are raw journals; the index and topical stores are the curated layer.
- Do not allow the memory index to grow unbounded — if it exceeds 4 KB, prune prose entries and move details to topical stores. Prefer `root_prefix` + relative link targets so you don't repeat long absolute paths throughout the index (keep the Storage backend path fully qualified).
- Do not skip memory maintenance — without weekly hygiene, the agent starts making recommendations based on outdated information.
- Do not let memory modify identity — if the agent learns something that contradicts its Soul or Rules, flag it for human review, not silent override.
- Do not confuse memory with the knowledge base — memory is dynamic (accumulated from experience); the knowledge base is static (reference material provided by the builder).
- Do not add individual daily log pointers to `MEMORY.md` — the sole navigation reference is the one-time bootstrap pointer `[Daily log index](memories/daily/README.md)`, established during setup. See `daily-vs-topical-memory.md` for the full daily log rule set.

## Memory Poisoning Prevention

1. **Separate identity from memory** — `SOUL.md` and `RULES.md` are never auto-updated by the agent.
2. **Summarize, do not store verbatim** — External content (emails, documents) is summarized before being committed to memory.
3. **Human review gates** — The agent can draft memory updates, but a human should approve structural changes to the index.
4. **Git history** — Version-controlling memory provides an audit trail; if behavior changes unexpectedly, the diff shows what changed.

## MEMORY.md Completeness Checklist

- [ ] The index is under 4 KB
- [ ] The directory structure for topical stores is defined
- [ ] Explicit triggers for memory updates are documented
- [ ] Retention policies define how long each category of information is kept
- [ ] The format for each topical store is specified
- [ ] External content handling is addressed (summarize, do not store verbatim)
- [ ] The cold-start period is acknowledged and planned for
- [ ] Memory and identity are clearly separated
- [ ] Version control (git) is used for memory files
