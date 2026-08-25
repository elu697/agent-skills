---
description: Discovers perk-guild and loads its overlay when an enabled flag exists.
applyTo: "**"
---

# Perk / Guild discovery

Load `workspace-agent-perk-guild` first when a work file's frontmatter contains
`perk.guild: enabled` or when `/perk-guild-enable` was invoked in the current
session.

Keep the full doctrine in the skill. This instruction performs discovery only.
The skill localizes user-facing output to the user's language and locale.
