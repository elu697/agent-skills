#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-cursor}"
SMOKE_ROOT="$(mktemp -d)"
trap 'rm -rf "$SMOKE_ROOT"' EXIT

case "$TARGET" in
  cursor)
    SKILL_ROOT=".agents/skills/workspace-agent-perk-guild"
    ENABLE_PATH=".cursor/commands/perk-guild-enable.md"
    DISABLE_PATH=".cursor/commands/perk-guild-disable.md"
    DISCOVERY_PATH=".cursor/rules/perk-guild-discovery.mdc"
    ;;
  claude)
    SKILL_ROOT=".claude/skills/workspace-agent-perk-guild"
    ENABLE_PATH=".claude/commands/perk-guild-enable.md"
    DISABLE_PATH=".claude/commands/perk-guild-disable.md"
    DISCOVERY_PATH=".claude/rules/perk-guild-discovery.md"
    ;;
  copilot)
    SKILL_ROOT=".agents/skills/workspace-agent-perk-guild"
    ENABLE_PATH=".github/prompts/perk-guild-enable.prompt.md"
    DISABLE_PATH=".github/prompts/perk-guild-disable.prompt.md"
    DISCOVERY_PATH=".github/instructions/perk-guild-discovery.instructions.md"
    ;;
  codex)
    SKILL_ROOT=".agents/skills/workspace-agent-perk-guild"
    ENABLE_PATH=""
    DISABLE_PATH=""
    DISCOVERY_PATH=""
    ;;
  *)
    printf 'Unsupported smoke target: %s\n' "$TARGET" >&2
    exit 2
    ;;
esac

cat >"$SMOKE_ROOT/apm.yml" <<EOF
name: workspace-agent-perk-guild-smoke
version: 0.0.0
targets:
  - "$TARGET"
dependencies:
  apm:
    - path: "$PACKAGE_ROOT"
EOF

(
  cd "$SMOKE_ROOT"
  apm install --target "$TARGET" --only apm
)

test -f "$SMOKE_ROOT/$SKILL_ROOT/SKILL.md"
test -f "$SMOKE_ROOT/$SKILL_ROOT/references/roles.md"
test -f "$SMOKE_ROOT/$SKILL_ROOT/references/phases.md"
test -f "$SMOKE_ROOT/$SKILL_ROOT/references/examples.md"
test ! -e "$SMOKE_ROOT/$SKILL_ROOT/tests"

if [[ -n "$ENABLE_PATH" ]]; then
  test -f "$SMOKE_ROOT/$ENABLE_PATH"
  test -f "$SMOKE_ROOT/$DISABLE_PATH"
  test -f "$SMOKE_ROOT/$DISCOVERY_PATH"
fi

if [[ "$TARGET" == "codex" ]]; then
  (
    cd "$SMOKE_ROOT"
    apm compile --target codex
  )
  test -f "$SMOKE_ROOT/AGENTS.md"
  grep -Fq "repair stale \`active_role\` only in enabled records actually loaded" \
    "$SMOKE_ROOT/AGENTS.md"
fi

printf 'Clean-room install passed for %s: all supported runtime files and references/roles.md deployed; tests excluded.\n' "$TARGET"
