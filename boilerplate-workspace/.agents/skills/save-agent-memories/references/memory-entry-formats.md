---
title: Memory Entry Formats — Templates by Category
description: >-
  Distilled reference for save-agent-memories. Provides MAGI-compatible YAML
  frontmatter fields and Markdown body templates for each memory category:
  decision, correction, preference, lesson, person, project, activity,
  environment fact, pattern, and daily session log. Also covers file naming
  conventions and the sub-folder README pattern.
purpose: reference
tags:
  - memory-entry
  - templates
  - magi
  - frontmatter
  - categories
audience: ai-agent
---

# Memory Entry Formats — Templates by Category

---

## Common YAML Frontmatter (all Tier 2 files)

Every Tier 2 file must begin with MAGI-compatible YAML frontmatter:

```yaml
---
doc-id: <UUID v7>
title: <descriptive title>
description: <one-sentence summary for progressive discovery>
category: <decision | correction | preference | lesson | person | project | activity | analysis | daily-log>
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - <tag-1>
  - <tag-2>
---
```

> **`doc-id` must be a real UUID v7** — a 32-hex-digit string in the form `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`. Do not use placeholder text like `<UUID>` or `generated-uuid`. Generate one with `python3 -c "import uuid; print(uuid.uuid4())"` or equivalent. Example: `doc-id: f3a7c912-0b4e-4d81-9e23-8c1a5b2d7f40`.

Add these optional fields when applicable:

| Optional field | When to add |
|----------------|-------------|
| `classification-confidence: low` | When the category assignment was ambiguous |
| `retention: <duration>` | When the agent's memory policy defines an expiry (e.g. `retention: 30d`, `retention: session`) |
| `origin: correction` | When this file was created as a result of a user correction, not an initial event |

---

## Decision

**Target path:** `memory/decisions/<slug>/README.md`
**Sub-folder:** yes — create `memory/decisions/<slug>/` with a `README.md`.

```markdown
---
doc-id: <UUID>
title: Decision: <short title>
description: <one-sentence summary of the decision and the problem it solved>
category: decision
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - decision
  - <domain-tag>
---

# Decision: <Title>

**Date:** YYYY-MM-DD
**Status:** active | superseded | deferred

## The Decision

<One paragraph describing what was decided.>

## Reasoning

<Why this option was chosen. What problem it solves.>

## Alternatives Considered

| Alternative | Why rejected |
|-------------|--------------|
| <option A>  | <reason>     |
| <option B>  | <reason>     |

## Trade-offs

<What is gained and what is given up.>

## Affected Areas

<Systems, people, workflows affected by this decision.>
```

**Naming slug:** use kebab-case with a date prefix when helpful — e.g. `2026-04-05-auth-provider` or `supabase-switch`.

---

## Correction

**Target:** update the **existing** relevant file — do not create a new one.
**If no existing file covers the corrected fact:** create one using the most appropriate category template and add `origin: correction` to its frontmatter.

At the bottom of the existing file, append:

```markdown
---

### Correction — YYYY-MM-DD

**Original:** <what the file previously stated>
**Corrected:** <the accurate version>
**Source:** User correction during session.
```

Update `last-updated` in the frontmatter.

---

## Preference

**Target path:** `memory/preferences/<slug>.md`
**Sub-folder:** no — flat file.

```markdown
---
doc-id: <UUID>
title: Preference: <short title>
description: <one-sentence summary>
category: preference
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - preference
  - <domain-tag>
---

# Preference: <Title>

**Area:** communication | formatting | working-rhythm | domain-specific | other
**Stated:** YYYY-MM-DD

## Preference

<Clear statement of what the user prefers.>

## Context

<When this preference applies and why it matters.>

## Examples

<Optional: concrete examples of what the user likes vs. dislikes.>
```

---

## Lesson

**Target path:** `memory/lessons/<slug>.md`
**Sub-folder:** no — flat file.

```markdown
---
doc-id: <UUID>
title: Lesson: <short title>
description: <one-sentence summary of the lesson>
category: lesson
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - lesson
  - <domain-tag>
---

# Lesson: <Title>

**Date:** YYYY-MM-DD

## Context

<What was happening when this lesson was learned.>

## What Happened

<The mistake, unexpected outcome, or discovery.>

## What Was Learned

<The insight or principle extracted.>

## Action Taken

<What changed as a result — behavior, process, or approach.>
```

---

## Person

**Target path:** `memory/people/<slug>.md`
**Sub-folder:** no — flat file per person.

```markdown
---
doc-id: <UUID>
title: Person: <Full Name>
description: <one-sentence summary of who this person is and their relevance>
category: person
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - person
  - <role-tag>
---

# <Full Name>

**Role / Title:** <current role>
**Organization:** <company or context>
**Introduced:** YYYY-MM-DD

## Relationship

<How this person relates to the agent's user and work.>

## Key Facts

- <Fact 1>
- <Fact 2>

## Interactions

<Log of notable interactions, if any. Add chronologically.>
```

**Naming slug:** kebab-case of the person's full name — e.g. `mark-willis` or `ausie-widawati`.

---

## Project

**Target path:** `memory/projects/<slug>/README.md`
**Sub-folder:** yes.

```markdown
---
doc-id: <UUID>
title: Project: <Name>
description: <one-sentence summary of the project and its goal>
category: project
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - project
  - <domain-tag>
---

# Project: <Name>

**Status:** active | paused | archived
**Started:** YYYY-MM-DD
**Goal:** <one sentence>

## Overview

<Brief description of the project, its scope, and key stakeholders.>

## Current State

<Where things stand as of `last-updated`.>

## Key Milestones

| Milestone | Target date | Status |
|-----------|-------------|--------|
| <m1>      | YYYY-MM-DD  | done / in-progress / pending |

## Open Items

- <item 1>
```

---

## Activity

**Target path:** `memory/activities/<slug>/README.md`
**Sub-folder:** yes.

```markdown
---
doc-id: <UUID>
title: Activity: <Name>
description: <one-sentence summary of the ongoing activity>
category: activity
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - activity
  - <domain-tag>
---

# Activity: <Name>

**Status:** active | paused | completed
**Started:** YYYY-MM-DD

## Description

<What this activity involves and why it matters across sessions.>

## Recent Progress

<What has happened most recently. Update each session.>

## Next Actions

- <action 1>
```

---

## Environment Fact / Pattern

Environment facts and short patterns are written **directly to the MEMORY.md index** under the relevant section (Environment, Recent Decisions, User Preferences, Lessons). They are not a separate Tier 2 file.

For recurring patterns with significant detail, create a file at `memory/analysis/<slug>.md` using this template:

```markdown
---
doc-id: <UUID>
title: Pattern: <Name>
description: <one-sentence summary of the recurring theme>
category: analysis
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - pattern
  - <domain-tag>
---

# Pattern: <Name>

**First noticed:** YYYY-MM-DD
**Frequency:** <approximate cadence>

## Pattern Description

<What recurs. How it manifests.>

## Evidence

| Date | Instance |
|------|----------|
| YYYY-MM-DD | <example> |

## Implication

<What this pattern means for the agent's work or the user's context.>
```

---

## Daily Session Log

**Target path:** `memory/daily/YYYY-MM-DD.md`
**Sub-folder:** no.

```markdown
---
doc-id: <UUID>
title: Daily Log — YYYY-MM-DD
description: <one-sentence summary of the session's main focus>
category: daily-log
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags:
  - daily-log
  - <session-theme-tag>
---

# Daily Log — YYYY-MM-DD

**Session focus:** <brief description>

## Key Events

### Decisions Made
- <decision summary> → see [decisions/<slug>/README.md](../decisions/<slug>/README.md)

### Corrections Received
- <what was corrected>

### People Introduced
- <name> — <context>

### Environment Changes
- <what changed>

## Open Items Carried Forward

- <item 1>
- <item 2>
```

After writing, append to `memory/daily/README.md`:

```markdown
- [YYYY-MM-DD](YYYY-MM-DD.md) — <one-sentence session summary>
```

**Never add a pointer to `MEMORY.md` for a daily log.**
