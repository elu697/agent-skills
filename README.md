# agent-skills

Public APM packages maintained in this repository. The perk-guild package
provides independent mission and conversation-session scopes with visible
guild roles. Each directory under `packages/` is independently consumable.

## Installation

Add the package you want to the consumer project's `apm.yml`:

```yaml
dependencies:
  apm:
    - git: elu697/agent-skills
      path: packages/workspace-agent-perk-guild
      ref: workspace-agent-perk-guild-v0.2.0
```

Then install the declared dependencies:

```bash
apm install
```

If the project wraps APM with its own setup command, use that command instead.
For reproducible installations, replace `main` with a release tag or commit
SHA.

## Packages

| Package | Purpose | Documentation |
| --- | --- | --- |
| `workspace-agent-perk-guild` | Keeps independent mission and conversation-session state with evidence-gated or build-nothing closure; uses visible guild roles so each assistant message carries one localized role label | [README](packages/workspace-agent-perk-guild/README.md) |

When adding a package, create `packages/<name>/`, document it in that
directory, and add it to this table.

## License

[MIT License](LICENSE)
