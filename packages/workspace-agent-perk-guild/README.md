# workspace-agent-perk-guild

一件の状況を、チャットではなく作業ファイルに残す overlay。

実装の手順は別の手続きに任せる。こちらが持つのは、brief、局面、遷移ゲート、作らない完了、親の総括。

## 入れるもの

* SKILL `workspace-agent-perk-guild`
* `/perk-guild-enable` / `/perk-guild-disable`
* 旗があるときの発見用 instruction

## 導入

消費側の `apm.yml` に足す。

```yaml
dependencies:
  apm:
    - git: elu697/agent-skills
      path: packages/workspace-agent-perk-guild
      ref: main
```

足したら、そのプロジェクトの Agent インストールを回す。

## 使い方

`/perk-guild-enable` で、Session と作業ファイル先頭に `perk.guild: enabled` を残す。続けて目標を書いてよい。目標が無い単発は、進行中を一覧してから選ぶ。

有効なあいだは、局面を進めた応答の終わりに status を更新する。証拠の無い success では閉じない。

## ライセンス

[MIT License](../../LICENSE)
