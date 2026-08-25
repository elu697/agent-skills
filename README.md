# agent-skills

APM パッケージの公開場所。`packages/` 配下に、パッケージを 1 ディレクトリずつ置く。

## 使い方

消費側の `apm.yml` に足す。

```yaml
dependencies:
  apm:
    - git: elu697/agent-skills
      path: packages/workspace-agent-perk-guild
      ref: main
```

足したら、そのプロジェクトの Agent インストールを回す。

## パッケージの足し方

`packages/<name>/apm.yml` と `.apm/skills/<skill-name>/SKILL.md` を置く。slash-command は `.apm/prompts/`、発見用 instruction は `.apm/instructions/`。

## いま入っているもの

* `workspace-agent-perk-guild` — 状況の正本、brief、局面の教義、遷移ゲート、作らない完了、親の総括。`/perk-guild-enable` / `/perk-guild-disable`

## ライセンス

[MIT License](LICENSE)
