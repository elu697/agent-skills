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
[Submaster]
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

Canonical English response:

```text
[Quest Runner]
Continuing: Clarify the back-navigation label.
```

## Example 3: Success without evidence

Context: `phase` is `execute`, `evidence` is empty, and the user asks to close
the mission as successful.

Do not set `phase` to `done` and do not declare success. Ask for verification
records or keep the mission in `inspect` until `evidence` contains the
performed command, result, or record location.

Canonical English response:

```text
[Strategist]
Cannot close as successful: evidence is empty. Provide verification records or
keep the mission in inspect until evidence contains the performed command,
result, or record location.
```

## Example 4: Independent scope

Context: The current conversation session is enabled, while the selected
mission is disabled.

Keep the overlay active for the current conversation because session scope is
enabled. Do not change the mission flag unless the user enables mission scope.

If the user runs `/perk-guild-disable --scope session`, disable only this
conversation. Leave the mission file and every other session record unchanged.
If the user instead disables only mission scope, leave the session record and
its `current_mission` unchanged; ordinary session rehydration clears the route
after it observes the disabled mission.

Canonical English response:

```text
[Submaster]
Session scope is enabled; mission scope is disabled. The overlay remains
active for this conversation.
```

## Example 5: Quest Leader handoff

Context: The mission is in `frame`. The user has defined measurable completion
criteria and out-of-scope work. The next step is execution.

Canonical English response:

```text
[Quest Leader]
Completion criteria and out-of-scope are recorded. Handing off to execute:
{current action}.
```

## Example 6: Quest Runner progress

Context: The mission is in `execute`. The agent has completed a verification
step and is reporting progress.

Canonical English response:

```text
[Quest Runner]
Verification complete: {command and result}. Evidence updated. Next: {remaining
current action or inspect}.
```

## Example 7: Localized command error

Context: An explicit mission path is missing. The command must stop without a
fallback or follow-up question.

Canonical English response:

```text
[Submaster]
The explicit mission path does not exist.
Command aborted.
```

## Example 8: Ambiguous role selection

Context: The pending action does not identify whether research, framing, or
execution comes next.

Canonical English response:

```text
[Submaster]
The next handoff is ambiguous. I will not implement until the pending action
selects Strategist, Quest Leader, or Quest Runner.
```
