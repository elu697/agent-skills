# workspace-agent-perk-guild

An overlay that keeps one mission's state in a work file instead of relying on
volatile chat context.

It leaves implementation mechanics to the active execution procedure. The
overlay owns the mission brief, phase doctrine, transition gates,
build-nothing completion, and parent-level closure.

All user-facing messages follow the user's explicit language preference,
conversation language, or environment locale. Skill instructions and
machine-readable state remain in English.

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
      ref: main
```

Then run the consumer project's Agent or APM installation command.

## Usage

Run `/perk-guild-enable` to persist `perk.guild: enabled` in the session and
work file. A goal may follow the command. Without a goal, the skill lists open
missions and asks which one to continue.

While enabled, it updates status before ending any response that advances the
mission. It does not accept evidence-free success.

Run `/perk-guild-disable` to stop applying the overlay to the current mission
without erasing mission state.

## License

[MIT License](../../LICENSE)
