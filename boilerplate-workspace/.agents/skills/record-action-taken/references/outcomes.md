# Reference — The four outcomes

Every resolution must be assigned exactly one of these four outcomes. The vocabulary is deliberately narrow so the resolved-actions archive can be queried unambiguously: `done/` is "we did it", `cancelled/` is "we explicitly stopped", and so on.

If the caller proposes a synonym ("complete", "won't do", "scrapped", "moot"), do not silently map it. Re-prompt with the four canonical values and let them pick.

## `done`

The work the action described **was performed and is no longer pending**. This is the only outcome that implies a positive completion event — the action's intent is fulfilled.

Use when: the action was carried out, even partially, and no further work on it is expected.

Do not use when: the action is no longer relevant for reasons unrelated to whether the work happened (use `obsolete` instead), or when the work was not done and explicitly will not be done (use `cancelled`).

## `skipped`

The action was deliberately **passed over for now**, but it was a deliberate "no-go" decision rather than a permanent abandonment. The implication is "we considered it and chose not to act". The action might be revived later (re-resolution) if circumstances change.

Use when: a person or agent explicitly decided not to act on this item in the current cycle. The reason is usually scope, prioritisation, or timing.

Do not use when: the action is structurally no longer relevant (`obsolete`), or when the entire action was abandoned with no expectation of revisiting (`cancelled`).

## `obsolete`

The world changed and the action **no longer makes sense**. Something upstream (a project pivot, a deprecated dependency, a cancelled feature, a reorg) has rendered the action moot. There is nothing to do, regardless of intent.

Use when: the situation that motivated the action no longer exists. Mark obsolete; do not attempt to do the work or mark it `done`.

Do not use when: the action is still meaningful but you chose not to do it (`skipped`), or when the work simply was completed (`done`).

## `cancelled`

The action is **explicitly retired**. This is the strongest "no" — distinct from `skipped` (which is "not now") and from `obsolete` (which is "no longer applies"). Cancelled actions are not expected to come back.

Use when: a deliberate decision was made to abandon the action permanently. Often paired with a brief resolution note explaining why.

Do not use when: the action might still be revived (`skipped`), or when context made it irrelevant rather than rejected (`obsolete`).

## Disambiguation tips

- "Did we actually carry out the work?" If yes → `done`.
- "Will we revisit this?" If yes → `skipped`. If no → continue.
- "Did the world change so the action no longer applies?" If yes → `obsolete`. If no → `cancelled`.

When in doubt, ASK the caller — the four-way vocabulary is small enough to present in full ("done, skipped, obsolete, or cancelled?"). Never default silently.

## Re-resolution between outcomes

A `skipped` action that turns out to be needed becomes `done` (re-resolution). A `done` action that was actually wrong can become `cancelled` (re-resolution). Every transition is recorded in `resolution-history`; the file moves between per-outcome subfolders accordingly. See `re-resolution.md`.
