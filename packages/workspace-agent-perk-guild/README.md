# workspace-agent-perk-guild

An overlay with independent mission and conversation-session scopes and
visible guild roles, keeping durable mission state outside volatile chat
context.

It leaves implementation mechanics to the active execution procedure. The
overlay owns the mission brief, phase doctrine, transition gates,
build-nothing completion, and parent-level closure.

All user-facing messages follow the user's explicit language preference,
conversation language, or environment locale. Skill instructions and
machine-readable state remain in English.

## Guild roles

When the overlay is active, every user-visible assistant message starts with
exactly one role label. Labels communicate authority, not personality; keep
prose concise and avoid ornamental roleplay.

| Role | Responsibility |
| --- | --- |
| Guild Master | Human intent and final authority (user only) |
| Submaster | Rehydration, intent preservation, skip/done, parent closure |
| Strategist | Research, risk, evidence review, approval or rejection |
| Quest Leader | Scope, completion criteria, `current`, execution handoff |
| Quest Runner | Execution, verification, progress or failure reporting |

The agent never speaks as Guild Master. `/perk-guild-enable` and
`/perk-guild-disable` initialize the visible Submaster role. Discovery repairs
stale role state from pending actions.

Display labels are localized (for example, `[Submaster]` or `[サブマスター]`).
Canonical role IDs in skill state remain English (`submaster`, `strategist`,
`quest_leader`, `quest_runner`).

## State scopes

Mission and conversation-session state are independent scopes:

* Mission scope is stored in the mission work file as
  the nested YAML field `perk.guild: enabled`.
* Session scope is stored at
  `<workspace-root>/.ai-agent/perk-guild/sessions/<session-key>.yaml`.
  The key is the full lowercase hexadecimal SHA-256 digest of the
  host-provided conversation identifier. Each record also owns a random UUIDv4
  `session_alias` that mission indexes may reference. The raw identifier and
  `session_key` are never copied into mission state.

The session directory is workspace-local routing state. Enablement idempotently
ensures `sessions/.gitignore` excludes all session records while retaining the
`.gitignore` itself. State writes use `realpath` containment checks, reject
symlinked components under `.ai-agent/perk-guild/sessions`, and replace YAML
atomically via a same-directory temporary file.

The overlay is active when either the current session or selected mission is
enabled. No workspace-global boolean flag is used. If the host does not expose
a stable conversation identifier, session scope remains in memory for the
current conversation without falling back to shared workspace state. This
in-memory state is lost after context compression, closing the conversation,
or restarting the host.

## Included

* Skill: `workspace-agent-perk-guild`
* `/perk-guild-enable` / `/perk-guild-disable`
* Discovery instruction for `perk.guild: enabled`

## Installation

Add the package to the consumer's `apm.yml`:

```yaml
dependencies:
  apm:
    - git: elu697/agent-skills
      path: packages/workspace-agent-perk-guild
      ref: workspace-agent-perk-guild-v0.2.0
```

Then run the consumer project's Agent or APM installation command. For Codex
consumers, also run `apm compile` after install to generate `AGENTS.md` from
the installed discovery instruction.

## Usage

Run `/perk-guild-enable` to enable the requested scope. Session-only
enablement never creates or modifies a mission. Mission-only enablement never
writes session `active_role` or `current_mission`.

Both commands accept `--scope session`, `--scope mission`, or `--scope both`.
The default is `both`.

While enabled, it updates status before ending any response that advances the
mission. It does not accept evidence-free success.

Run `/perk-guild-disable` to stop applying the overlay at the selected scope
without erasing mission state or changing unrelated conversations.

Each command reports `session`, `mission`, and `effective` separately, followed
by independent `session_persisted` and `mission_persisted` booleans. Disabling
one scope leaves the overlay active while the other scope remains enabled.

Session disablement removes only the current session record. Enabled records
do not expire automatically, allowing the same conversation to restore its
scope when reopened.

## Migration from 0.1.x

Moving from 0.1.x to 0.2.0 is a breaking migration, not an automatic migration.
The former workspace-global `.ai-agent/perk-guild.yaml` file is ignored and
left untouched.

After upgrading, run one of:

```text
/perk-guild-enable --scope session
/perk-guild-enable --scope mission .ai-agent/plan/login-home.md
/perk-guild-enable --scope both
```

For mission scope, pass an explicit mission path or current work-file context.
A bare `--scope mission` without a path or goal returns an error.

Verify the new scoped state, then delete the legacy file when satisfied.
Mission flags in work-file frontmatter remain valid.

## Development

Run the contract tests:

```bash
python3 -m unittest tests/test_contract.py -v
```

Run a clean-room local APM installation:

```bash
bash tests/smoke_install.sh
```

## License

[MIT License](../../LICENSE)
