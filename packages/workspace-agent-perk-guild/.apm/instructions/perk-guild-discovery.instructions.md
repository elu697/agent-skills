---
description: Discovers perk-guild from independently scoped mission and conversation-session records.
applyTo: "**"
---

# Perk / Guild discovery

Load `workspace-agent-perk-guild` first when either condition is true:

* the nested YAML field path `perk.guild` resolves to `enabled` in the
  selected work file;
* the same nested field resolves to `enabled` in the current conversation's
  record at
  `<workspace-root>/.ai-agent/perk-guild/sessions/<session-key>.yaml`.

`perk.guild` is a nested YAML field path, not a literal key.

Canonicalize open workspace roots and any existing explicit/contextual mission
path with `realpath`. Resolve `<workspace-root>` from that mission path,
current work-file context, or the only open workspace root. Accept a path only
when it is inside exactly one open workspace root. If resolution is ambiguous,
do not read or write session state and return any assistant-authored error as
a localized Submaster message.

Before reading a session record, inspect each path component from
`<workspace-root>/.ai-agent/perk-guild` through `sessions` without following
links. Reject a symlinked state directory or any symlink component in that
range.

Resolve only the current host-provided conversation identifier. Compute the
session key as the SHA-256 digest of its UTF-8 bytes, encoded as full lowercase
hexadecimal. Never persist the raw identifier or use another conversation's
record.

When no stable identifier is available, use only the current conversation's
in-memory state. It is lost after context compression, closing the
conversation, or restarting the host. Do not use a workspace-global fallback.

Ignore the legacy `.ai-agent/perk-guild.yaml` file. It is not authoritative
for either scope.

After scoped state resolution, read the bundled `references/roles.md`.
Validate `active_role` against the pending action. Ordinary discovery must
repair stale `active_role` only in enabled records actually loaded; never
repair disabled, unselected, or merely discovered records.

`current_mission` is session routing metadata. Ordinary session rehydration
clears `current_mission` when its target is missing, outside the workspace
root, disabled, `done`, or `skip`. Otherwise it may normalize the loaded value.
A mission-only command never updates this field.

Prefix the next assistant-authored prose message with exactly one role label,
localized for the user. For a locale without a documented translation, use
the canonical English label.

Keep the full doctrine in the skill. This instruction performs discovery only.
The skill localizes user-facing output to the user's language and locale.
