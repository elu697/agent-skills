# Response patterns

These examples show behavior, not fixed wording. Localize every user-facing
sentence according to the language and locale rules in `SKILL.md`. Keep file
paths and status values unchanged.

Do not include project names or proper names of procedures other than perk
terms.

## Example 1: Standalone entry

Context: The skill is invoked with two open, enabled missions. Both have an
empty `current`. The user supplied no goal or follow-up task.

Canonical English response:

```text
Loaded.

Open missions:
* {file-a} / phase: research / current: (empty) / updated_at: 2026-08-24
* {file-b} / phase: frame / current: (empty) / updated_at: 2026-08-25

Which mission should I continue?
```

Translate the prose into the user's language. Do not implement, emit code, or
produce a patch.

## Example 2: A current action exists

Context: The work file's `current` is `Clarify the back-navigation label`, and
the user asks to continue.

Continue only that action. Do not list all open missions and do not ask the
user to choose.

## Example 3: Success without evidence

Context: `phase` is `execute`, `evidence` is empty, and the user asks to close
the mission as successful.

Do not set `phase` to `done` and do not declare success. Ask for verification
records or keep the mission in `inspect` until `evidence` contains the
performed command, result, or record location.
