# Guild Role Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make perk-guild visibly operate through a localized five-seat guild roster, with exactly one agent role per user-visible assistant message.

**Architecture:** Add a bundled `roles.md` reference as the single role doctrine, persist canonical `active_role` IDs in both mission and session state, and make role selection action-based with phase hints as fallback. Commands and discovery initialize or repair role state, while response examples and contract tests enforce visible labels without theatrical prose.

**Tech Stack:** Markdown Agent Skills, APM prompts and instructions, YAML state examples, Python `unittest`, Bash clean-room APM smoke test.

## Global Constraints

- The user exclusively occupies `guild_master`; the agent never speaks as Guild Master.
- Canonical IDs are `guild_master`, `submaster`, `strategist`, `quest_leader`, and `quest_runner`.
- Every user-visible assistant message starts with exactly one role label, localized for the user.
- A message never switches roles midway or contains multiple role sections.
- Labels communicate authority only; do not add fantasy dialect, catchphrases, emoji, or ornamental roleplay.
- Select roles from the action performed, not from `phase` alone.
- Keep Skill instructions and machine-readable state in English; localize display labels.
- Integrate this behavior into the pending `0.2.0` release rather than introducing another version bump.

## Final Release Decisions

- Scoped commands mutate only requested state. Mission-only commands never
  write session `active_role` or `current_mission`. Session-only commands never
  write mission state; `both` may write both.
- Ordinary discovery and rehydration repair `active_role` only in enabled
  records actually loaded. `current_mission` is session routing metadata and
  ordinary session rehydration clears stale, disabled, `done`, or `skip`
  routes.
- Disable does not persist a replacement `active_role` into a deleted session
  record or disabled mission.
- Every assistant-authored prose response, including errors and ambiguous-role
  fallback, starts with one allowed label. Host/tool UI is outside the
  contract; undocumented locales use English labels.
- Enable owns the authoritative mission creation table. Goal-based mission
  names are deterministic and reused; `both` without a mission or goal skips
  mission creation, while mission-only fails.
- The 0.1.x to 0.2.0 transition is a breaking migration. Legacy global state is
  ignored and untouched until the user explicitly reenables a scope and later
  deletes the legacy file.
- Session records use SHA-256 `session_key` filenames and reusable random UUIDv4
  `session_alias` values. Mission `chat_sessions` start as `[]`. Upsert by
  `session_alias` when session state is persisted; store only `session_alias`,
  `kind`, and `note`; never `session_key` or a raw host identifier
  (`raw_host_id`). Never duplicate.
  Do not append when session state is in memory only. Create
  `sessions/.gitignore` before writing any session record.
- Canonical path containment with `realpath`, symlink rejection from
  `.ai-agent/perk-guild` through `sessions`, and atomic same-directory YAML
  replacement apply to all state writes.
- Outputs keep `session`, `mission`, and `effective` separate and report
  `session_persisted` and `mission_persisted` booleans.
- JSON scenario fixtures cover scope write sets, effective state, mission
  creation, role conflicts, missing IDs, migration, privacy, and path safety.
- CI runs contract tests and `apm pack --dry-run --offline --json`, plus
  clean-install smoke tests for cursor, claude, copilot, and codex. Codex smoke
  runs `apm compile` and asserts `AGENTS.md` contains the discovery contract.

---

### Task 1: Core Role Doctrine and Persistence

**Files:**
- Create: `packages/workspace-agent-perk-guild/.apm/skills/workspace-agent-perk-guild/references/roles.md`
- Modify: `packages/workspace-agent-perk-guild/.apm/skills/workspace-agent-perk-guild/SKILL.md`
- Modify: `packages/workspace-agent-perk-guild/.apm/skills/workspace-agent-perk-guild/references/phases.md`
- Modify: `packages/workspace-agent-perk-guild/.apm/skills/workspace-agent-perk-guild/references/examples.md`
- Test: `packages/workspace-agent-perk-guild/tests/test_contract.py`

**Interfaces:**
- Produces: canonical role IDs and localized display-label mapping in `roles.md`.
- Produces: `active_role: <canonical-id>` in mission and session schemas.
- Consumes: existing mission `phase`, `current`, and session `current_mission`.

- [x] **Step 1: Write failing role-contract tests**

Add paths beside the existing constants:

```python
ROLES = PACKAGE_ROOT / ".apm/skills/workspace-agent-perk-guild/references/roles.md"
PHASES = PACKAGE_ROOT / ".apm/skills/workspace-agent-perk-guild/references/phases.md"
EXAMPLES = PACKAGE_ROOT / ".apm/skills/workspace-agent-perk-guild/references/examples.md"
```

Extend `setUpClass`:

```python
cls.roles = ROLES.read_text()
cls.phases = PHASES.read_text()
cls.examples = EXAMPLES.read_text()
```

Add these tests:

```python
def test_guild_roster_and_localized_labels_are_defined(self) -> None:
    expected = {
        "guild_master": ("[Guild Master]", "[ギルドマスター]"),
        "submaster": ("[Submaster]", "[サブマスター]"),
        "strategist": ("[Strategist]", "[参謀]"),
        "quest_leader": ("[Quest Leader]", "[クエストリーダー]"),
        "quest_runner": ("[Quest Runner]", "[クエストランナー]"),
    }
    for role_id, labels in expected.items():
        self.assertIn(f"`{role_id}`", self.roles)
        for label in labels:
            self.assertIn(label, self.roles)

def test_agent_never_speaks_as_guild_master(self) -> None:
    self.assertIn("The agent never speaks as `guild_master`", self.roles)

def test_every_user_visible_message_has_one_role(self) -> None:
    self.assertIn("exactly one role label", self.roles)
    self.assertIn("[Submaster]\\nLoaded.", self.examples)
    self.assertNotIn("Do not prefix responses with role labels", self.phases)

def test_role_is_persisted_in_both_scopes(self) -> None:
    self.assertGreaterEqual(self.skill.count("active_role:"), 2)
    self.assertIn("action-based selection overrides phase hints", self.roles)
```

- [x] **Step 2: Run the tests and verify RED**

Run:

```bash
cd packages/workspace-agent-perk-guild
python3 -m unittest tests/test_contract.py -v
```

Expected: the four new tests fail because `roles.md`, role labels, and
`active_role` do not exist, and `phases.md` still prohibits labels.

- [x] **Step 3: Create the role doctrine**

Create `references/roles.md` with:

```markdown
# Guild roles

Every user-visible assistant message starts with exactly one role label, localized for the user. A message never switches roles midway. Labels communicate authority,
not personality; keep prose concise and avoid fantasy dialect, catchphrases,
emoji, and ornamental roleplay.

The agent never speaks as `guild_master`.

| Canonical ID | English | Japanese | Responsibility |
| --- | --- | --- | --- |
| `guild_master` | `[Guild Master]` | `[ギルドマスター]` | Human intent and final authority |
| `submaster` | `[Submaster]` | `[サブマスター]` | Rehydration, intent preservation, skip/done, parent closure |
| `strategist` | `[Strategist]` | `[参謀]` | Research, risk, evidence review, approval or rejection |
| `quest_leader` | `[Quest Leader]` | `[クエストリーダー]` | Scope, completion criteria, `current`, execution handoff |
| `quest_runner` | `[Quest Runner]` | `[クエストランナー]` | Execution, verification, progress or failure reporting |

Select the role from the action performed:

* rehydrate, list missions, preserve intent, skip, done, parent summary -> `submaster`
* research, inspect evidence, assess risk, approve, reject -> `strategist`
* define scope, completion criteria, `current`, or handoff -> `quest_leader`
* execute `current`, verify, report progress or failure -> `quest_runner`

Phase hints are `research -> strategist`, `frame -> quest_leader`,
`execute -> quest_runner`, `inspect -> strategist`, and
`skip|done -> submaster`. action-based selection overrides phase hints.

Authority flows from Guild Master to Submaster to Quest Leader to Quest Runner.
The Strategist returns approval or rejection with an alternative course to the
Submaster and does not order the Quest Runner directly.
```

- [x] **Step 4: Integrate role selection and persistence into `SKILL.md`**

Add a `Guild role` section after response localization:

```markdown
## Guild role

Read [references/roles.md](references/roles.md) before composing any
user-visible response. Select one role from the action performed, prefix the
message with its localized label, and keep that role for the whole message.

Persist the canonical ID as `active_role` only in the enabled record being
advanced. On handoff, write the next role before ending the message. On
rehydration, use a valid persisted role only when it matches the pending
action; otherwise derive and repair it only in enabled records actually loaded.
Never persist or speak as `guild_master`.
```

Add `active_role: submaster` to both YAML examples:

```yaml
active_role: submaster
```

Update rehydration to read and validate `active_role` after resolving session
and mission state. Replace generic parent/child terminology in the authority
section with the canonical role flow while retaining the existing
execution-procedure boundary.

- [x] **Step 5: Update phase hints and response examples**

Replace the first paragraph of `phases.md` with:

```markdown
Roles and phases are orthogonal. Read only the current phase doctrine, then
select the role from the action performed. Use the phase-to-role hints in
`roles.md` only when the action does not select a role.
```

Update each canonical response in `examples.md` to begin with one label. The
standalone example becomes:

```text
[Submaster]
Loaded.

Open missions:
* {file-a} / phase: research / current: (empty) / updated_at: 2026-08-24
* {file-b} / phase: frame / current: (empty) / updated_at: 2026-08-25

Which mission should I continue?
```

Add concise labeled examples for Strategist evidence rejection, Quest Leader
handoff, and Quest Runner progress. Do not put multiple labels in one example.

- [x] **Step 6: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest tests/test_contract.py -v
```

Expected: all contract tests pass.

### Task 2: Command and Discovery Role Integration

**Files:**
- Modify: `packages/workspace-agent-perk-guild/.apm/prompts/perk-guild-enable.prompt.md`
- Modify: `packages/workspace-agent-perk-guild/.apm/prompts/perk-guild-disable.prompt.md`
- Modify: `packages/workspace-agent-perk-guild/.apm/instructions/perk-guild-discovery.instructions.md`
- Test: `packages/workspace-agent-perk-guild/tests/test_contract.py`

**Interfaces:**
- Consumes: canonical role IDs from bundled `roles.md`.
- Produces: scoped `active_role: submaster` persistence on enable,
  label-only Submaster reporting on disable, and action-based repair only in
  enabled records actually loaded during discovery.

- [x] **Step 1: Write failing command integration tests**

Add:

```python
def test_commands_initialize_visible_submaster_role(self) -> None:
    for text in (self.enable, self.disable):
        self.assertIn("[Submaster]", text)
    self.assertIn("active_role: submaster", self.enable)
    self.assertNotIn("active_role: submaster", self.disable)

def test_discovery_repairs_role_from_pending_action(self) -> None:
    self.assertIn("references/roles.md", self.discovery)
    self.assertIn("repair `active_role`", self.discovery)
```

- [x] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests/test_contract.py -v
```

Expected: the tests fail because command output labels and scoped discovery
repair are not yet documented.

- [x] **Step 3: Update enable and disable prompts**

In the enable prompt's scoped session and mission YAML examples, add:

```yaml
active_role: submaster
```

Require the command's user-facing result to start with the localized Submaster
label. After enablement, the Submaster either enters standalone mode or writes
the next role before handing off. Disable remains a Submaster operation but
does not persist a replacement `active_role`.

- [x] **Step 4: Update discovery**

After scoped state resolution, require discovery to:

```markdown
Read the bundled `references/roles.md`. Validate `active_role` against the
pending action, repair stale `active_role` only in enabled records actually loaded, and prefix
the next user-visible message with exactly one role label, localized for the
user.
```

- [x] **Step 5: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest tests/test_contract.py -v
```

Expected: all contract tests pass.

### Task 3: Public Documentation

**Files:**
- Modify: `README.md`
- Modify: `packages/workspace-agent-perk-guild/README.md`
- Test: `packages/workspace-agent-perk-guild/tests/test_contract.py`

**Interfaces:**
- Produces: public explanation of the visible roster and one-message-one-role
  contract.

- [x] **Step 1: Write a failing documentation test**

Add:

```python
def test_public_docs_explain_visible_roles(self) -> None:
    for role in ("Submaster", "Strategist", "Quest Leader", "Quest Runner"):
        self.assertIn(role, self.readme)
    self.assertIn("one role label", self.readme)
    self.assertIn("visible guild roles", self.root_readme)
```

- [x] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests/test_contract.py -v
```

Expected: the documentation test fails.

- [x] **Step 3: Document the roster**

Add a `Guild roles` section to the package README. Explain the four agent roles,
reserve Guild Master for the user, and state that labels are localized while
canonical IDs remain English.

Update the root catalog description to mention visible guild roles.

- [x] **Step 4: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest tests/test_contract.py -v
```

Expected: all contract tests pass.

### Task 4: Full Package Verification

**Files:**
- Verify: `.github/workflows/test.yml`
- Verify: `packages/workspace-agent-perk-guild/tests/smoke_install.sh`
- Verify: all modified package files

**Interfaces:**
- Consumes: complete role-enabled `0.2.0` package.
- Produces: verified APM package with tests excluded from installed runtime.

- [x] **Step 1: Run contract tests**

```bash
cd packages/workspace-agent-perk-guild
python3 -m unittest tests/test_contract.py -v
```

Expected: all tests pass with no failures.

- [x] **Step 2: Run target-by-target clean-room installs**

```bash
for target in cursor claude copilot codex; do
  bash tests/smoke_install.sh "$target"
done
```

Expected: every supported target deploys `SKILL.md` and all bundled references,
including `references/roles.md`; target-supported commands and discovery files
land at the locally observed paths; Codex additionally compiles `AGENTS.md`;
tests remain outside runtime skill paths.

- [x] **Step 3: Run APM pack dry-run**

```bash
apm pack --dry-run --offline --json
```

Expected: JSON contains `"ok": true`, with no warnings or errors.

- [x] **Step 4: Check formatting and prohibited content**

From the repository root:

```bash
git diff --check
```

Expected: no output and exit code 0.

Check that runtime documents contain no `folder:this`, raw session identifiers,
mission `session_key` references, single `persisted:` output, or the obsolete
prohibition `Do not prefix responses with role labels`.

- [x] **Step 5: Review the complete diff**

```bash
git status --short
git diff --stat
git diff
```

Confirm the release remains `0.2.0`, README references remain
`workspace-agent-perk-guild-v0.2.0`, tests are outside `.apm`, CI keeps normal
policy enforcement, and no unrelated files changed. Do not commit, push,
create a tag, or attempt remote tag installation in this fix wave.
