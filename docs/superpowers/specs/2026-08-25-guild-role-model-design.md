# Guild Role Model Design

## Goal

Make perk-guild behavior visible and attributable without turning responses
into theatrical roleplay. Every user-visible assistant message carries exactly
one localized guild-role label.

## Roster

The user exclusively occupies `guild_master`. The agent never speaks as the
Guild Master.

| Canonical ID | English label | Japanese label | Responsibility |
| --- | --- | --- | --- |
| `guild_master` | `[Guild Master]` | `[ギルドマスター]` | Human intent and final authority |
| `submaster` | `[Submaster]` | `[サブマスター]` | Rehydration, intent preservation, skip/done decisions, parent closure |
| `strategist` | `[Strategist]` | `[参謀]` | Research, risk analysis, evidence review, approval or rejection |
| `quest_leader` | `[Quest Leader]` | `[クエストリーダー]` | Scope, measurable completion, `current`, execution handoff |
| `quest_runner` | `[Quest Runner]` | `[クエストランナー]` | Execution, verification, progress and failure reporting |

Canonical IDs remain in English. Display labels follow the user's explicit
language, current conversation language, or host locale.
For locales without a documented translation, display the canonical English
label.

## Message Contract

Every user-visible assistant message starts with exactly one role label. A
message does not contain multiple role sections or switch roles midway.
This includes assistant-authored errors and ambiguous-role fallbacks. Host- or
tool-rendered UI events are outside the contract.

The label communicates authority, not personality. Prose remains concise and
professional. Do not add fantasy dialect, catchphrases, emoji, or ornamental
roleplay.

Meaningful role transitions may appear as separate progress messages. Short
tasks need not exercise every role.

## Role Selection

Select the role from the action performed in the current message, not from
`phase` alone:

| Action | Role |
| --- | --- |
| Rehydrate, list missions, preserve intent, skip, done, parent summary | `submaster` |
| Research, inspect evidence, assess risk, approve, reject | `strategist` |
| Define scope, completion criteria, `current`, or execution handoff | `quest_leader` |
| Execute `current`, run verification, report progress or failure | `quest_runner` |

An `execute` mission can therefore produce a Strategist message while evidence
is being reviewed. When a message would require two roles, stop at the
handoff and continue in a later message under the next role.

## Authority

Authority flows in one direction:

```text
Guild Master -> Submaster -> Quest Leader -> Quest Runner
```

The Strategist reviews evidence independently. It returns approval, rejection,
and an alternative course to the Submaster. It does not issue execution orders
directly to the Quest Runner.

The Quest Runner may return progress, failure, evidence, or a request for
clarification. It must not expand scope.

## Persistence

Add `active_role` to both independent scopes:

```yaml
# Mission work-file frontmatter
active_role: quest_leader
```

```yaml
# Conversation-session record
active_role: quest_leader
```

When a role hands work to another role, write the next canonical role ID before
ending the message. On rehydration:

1. Read the selected mission and current session record.
2. Use a valid persisted `active_role` when it matches the pending action.
3. Otherwise derive the role from the action table and repair stale
   `active_role` only in enabled records actually loaded.

Never persist `guild_master` as an agent role.

Scoped commands mutate only their requested scope. Mission-only commands never
write session `active_role` or `current_mission`. Session-only commands never
write mission state. `both` may update both.

`current_mission` is session routing metadata. Update it only when session
scope is active or during ordinary session rehydration. Mission-only disable
leaves it unchanged; later session rehydration clears it when the route is
missing, outside the workspace, disabled, `done`, or `skip`.

Disable does not persist a replacement `active_role` into a deleted session
record or disabled mission.

## Existing Phase Integration

Roles and phases are orthogonal. Phases constrain what work is valid; roles
identify who is speaking and what authority that message has.

The default phase-to-role hints are:

```text
research -> strategist
frame    -> quest_leader
execute  -> quest_runner
inspect  -> strategist
skip     -> submaster
done     -> submaster
```

Action-based selection overrides these hints.

## Error Handling

If `active_role` is absent, unknown, or incompatible with the pending action,
derive a valid role and update scoped state. Do not block the mission solely
because role metadata is stale.

If role selection is genuinely ambiguous, use `submaster`, state the handoff
decision concisely, and avoid implementation until the next role is known.

## Mission Creation

The enable command owns the authoritative decision table:

| Scope and inputs | Result |
| --- | --- |
| `session` | Never create or modify a mission. |
| Mission-active scope with explicit existing path | Use it. |
| Mission-active scope with explicit missing path | Error. |
| No explicit path and a contextual mission | Use it. |
| No mission and non-empty goal | Create deterministically under `<workspace-root>/.ai-agent/plan/`, reusing the same derived name. |
| `both`, no mission, no goal | Enable session and report mission skipped. |
| `mission`, no mission, no goal | Error. |

## Privacy and Write Safety

The SHA-256 `session_key` remains the session filename/key. Each session record
also owns a random UUIDv4 `session_alias`, reused for that record. Mission
`chat_sessions` entries contain only `session_alias`, `kind`, and a short
`note`. They never contain `session_key` or a raw host identifier, and no entry
is appended when session state is not persisted.

The workspace-local session directory is excluded from VCS by an idempotently
maintained `sessions/.gitignore` containing `*` and `!.gitignore`.

Canonicalize open workspace roots and existing mission paths with `realpath`.
For a new target, canonicalize the nearest existing parent and prove the final
path remains inside exactly one root. Reject symlinks from
`.ai-agent/perk-guild` through `sessions`. Write YAML atomically with a
same-directory temporary file followed by rename or replace.

Command output keeps `session`, `mission`, and `effective` separate and reports
`session_persisted` and `mission_persisted` independently.

## Breaking Migration

The 0.1.x to 0.2.0 transition is a breaking migration. The legacy
`.ai-agent/perk-guild.yaml` remains ignored and untouched. After upgrading,
users explicitly run `/perk-guild-enable --scope session`, `mission`, or
`both`, verify the new state, then delete the legacy file when satisfied.

## Testing

Extend the contract tests to verify:

* all five canonical IDs and localized labels are documented;
* every response example starts with exactly one role label;
* `guild_master` is reserved for the user;
* mission and session schemas include `active_role`;
* action-based selection overrides phase hints;
* scope-specific write sets and effective-state union are scenario-tested;
* mission creation follows the authoritative decision table;
* session aliases, VCS privacy, canonical paths, and atomic writes are covered;
* outputs expose `session_persisted` and `mission_persisted`;
* the former prohibition on role labels is absent;
* clean-room APM installation still excludes tests.
