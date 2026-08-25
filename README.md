# agent-skills

Public APM packages maintained in this repository. Each directory under
`packages/` is independently consumable.

## Installation

Add the package you want to the consumer project's `apm.yml`:

```yaml
dependencies:
  apm:
    - git: elu697/agent-skills
      path: packages/workspace-agent-perk-guild
      ref: main
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
| `workspace-agent-perk-guild` | Keeps one mission's state in a durable file and supports evidence-gated or build-nothing closure | [README](packages/workspace-agent-perk-guild/README.md) |

When adding a package, create `packages/<name>/`, document it in that
directory, and add it to this table.

## License

[MIT License](LICENSE)
