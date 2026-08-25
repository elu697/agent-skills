from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILL = PACKAGE_ROOT / ".apm/skills/workspace-agent-perk-guild/SKILL.md"
ENABLE = PACKAGE_ROOT / ".apm/prompts/perk-guild-enable.prompt.md"
DISABLE = PACKAGE_ROOT / ".apm/prompts/perk-guild-disable.prompt.md"
DISCOVERY = (
    PACKAGE_ROOT / ".apm/instructions/perk-guild-discovery.instructions.md"
)
README = PACKAGE_ROOT / "README.md"
ROOT_README = PACKAGE_ROOT.parents[1] / "README.md"
MANIFEST = PACKAGE_ROOT / "apm.yml"
ROLES = PACKAGE_ROOT / ".apm/skills/workspace-agent-perk-guild/references/roles.md"
PHASES = PACKAGE_ROOT / ".apm/skills/workspace-agent-perk-guild/references/phases.md"
EXAMPLES = PACKAGE_ROOT / ".apm/skills/workspace-agent-perk-guild/references/examples.md"
SMOKE_INSTALL = PACKAGE_ROOT / "tests/smoke_install.sh"
FIXTURES = PACKAGE_ROOT / "tests/fixtures"
DESIGN = (
    PACKAGE_ROOT.parents[1]
    / "docs/superpowers/specs/2026-08-25-guild-role-model-design.md"
)
PLAN = (
    PACKAGE_ROOT.parents[1]
    / "docs/superpowers/plans/2026-08-25-guild-role-model.md"
)
CI = PACKAGE_ROOT.parents[1] / ".github/workflows/test.yml"

ALLOWED_ROLE_LABELS = {
    "[Submaster]",
    "[サブマスター]",
    "[Strategist]",
    "[参謀]",
    "[Quest Leader]",
    "[クエストリーダー]",
    "[Quest Runner]",
    "[クエストランナー]",
}


def load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text())


def normalized_prose(text: str) -> str:
    return " ".join(text.split())


def canonical_text_responses(markdown: str) -> list[str]:
    responses = []
    for match in re.finditer(r"```text\n(.*?)\n```", markdown, re.DOTALL):
        preceding = markdown[: match.start()].rstrip()
        marker = normalized_prose(preceding.rsplit("\n\n", 1)[-1])
        if marker.startswith("Canonical") and (
            "response" in marker.lower() or "output" in marker.lower()
        ):
            responses.append(match.group(1))
    return responses


def path_decision(
    target_kind: str,
    canonicalize: str,
    workspace_matches: int,
    state_component_symlink: bool,
) -> str:
    if state_component_symlink:
        return "reject"
    if workspace_matches != 1:
        return "reject"
    if target_kind == "existing" and canonicalize != "target-realpath":
        return "reject"
    if target_kind == "new" and canonicalize != "nearest-existing-parent-realpath":
        return "reject"
    return "allow"


def chat_session_action(
    session_persisted: bool,
    mission_persisted: bool,
    existing: list[dict[str, str]],
    session_alias: str | None,
) -> str:
    if not session_persisted or not mission_persisted:
        return "none"
    if session_alias is None:
        return "none"
    for entry in existing:
        if entry.get("session_alias") == session_alias:
            return "upsert"
    return "append"


def mission_decision(
    scope: str,
    explicit_path: str | None,
    contextual_mission: bool,
    goal: str,
) -> str:
    if scope == "session":
        return "session-only"
    if explicit_path == "missing":
        return "error"
    if explicit_path == "existing":
        return "use-explicit"
    if contextual_mission:
        return "use-context"
    if goal:
        slug = re.sub(r"[^a-z0-9]+", "-", goal.lower()).strip("-")
        return f"create:{slug}.md"
    if scope == "both":
        return "session-only"
    return "error"


class PerkGuildContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text()
        cls.enable = ENABLE.read_text()
        cls.disable = DISABLE.read_text()
        cls.discovery = DISCOVERY.read_text()
        cls.readme = README.read_text()
        cls.root_readme = ROOT_README.read_text()
        cls.roles = ROLES.read_text()
        cls.phases = PHASES.read_text()
        cls.examples = EXAMPLES.read_text()
        cls.smoke_install = SMOKE_INSTALL.read_text()
        cls.design = DESIGN.read_text()
        cls.plan = PLAN.read_text()
        cls.ci = CI.read_text()

    def test_yaml_path_is_declared_as_nested_not_literal(self) -> None:
        for text in (self.skill, self.enable, self.discovery):
            self.assertIn(
                "`perk.guild` is a nested YAML field path, not a literal key",
                text,
            )

    def test_session_key_is_always_sha256_and_raw_id_is_not_persisted(self) -> None:
        for text in (self.skill, self.enable, self.disable):
            self.assertIn("SHA-256", text)
            self.assertIn("lowercase hexadecimal", text)
            self.assertNotIn('session_id: "<opaque-host-session-id>"', text)

    def test_workspace_root_is_portable_and_unambiguous(self) -> None:
        all_runtime_text = "\n".join(
            (self.skill, self.enable, self.disable, self.discovery)
        )
        self.assertNotIn("folder:this", all_runtime_text)
        self.assertIn("<workspace-root>/.ai-agent/perk-guild/sessions/", all_runtime_text)
        self.assertIn("exactly one workspace root", all_runtime_text)

    def test_workspace_global_flag_is_legacy_only(self) -> None:
        all_runtime_text = "\n".join(
            (self.skill, self.enable, self.disable, self.discovery)
        )
        self.assertNotIn("folder:this/.ai-agent/perk-guild.yaml", all_runtime_text)
        self.assertIn("legacy", all_runtime_text.lower())

    def test_current_mission_resolution_and_cleanup_are_defined(self) -> None:
        self.assertIn(
            "explicit mission path > current work-file context > `current_mission`",
            self.skill,
        )
        for state in ("missing", "`done`", "`skip`"):
            self.assertIn(state, self.skill)

    def test_commands_report_scoped_and_effective_state(self) -> None:
        for text in (self.enable, self.disable):
            for field in (
                "session:",
                "mission:",
                "effective:",
                "session_persisted:",
                "mission_persisted:",
            ):
                self.assertIn(field, text)
            self.assertNotRegex(text, r"(?m)^persisted:")

    def test_missing_session_id_is_explicitly_ephemeral(self) -> None:
        for text in (self.skill, self.enable, self.discovery, self.readme):
            self.assertRegex(text, r"lost\s+after\s+context\s+compression")

    def test_legacy_workspace_flag_is_ignored(self) -> None:
        for text in (self.skill, self.readme):
            self.assertIn(".ai-agent/perk-guild.yaml", text)
            self.assertIn("legacy", text.lower())

    def test_release_reference_and_catalog_match_redesign(self) -> None:
        tag = "workspace-agent-perk-guild-v0.2.0"
        self.assertIn(f"ref: {tag}", self.readme)
        self.assertIn(f"ref: {tag}", self.root_readme)
        self.assertIn("conversation-session", self.root_readme)

    def test_manifest_version_matches_release(self) -> None:
        self.assertIn("version: 0.2.0", MANIFEST.read_text())

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
        self.assertIn("[Submaster]\nLoaded.", self.examples)
        self.assertNotIn("Do not prefix responses with role labels", self.phases)

    def test_role_is_persisted_in_both_scopes(self) -> None:
        self.assertGreaterEqual(self.skill.count("active_role:"), 2)
        self.assertIn("action-based selection overrides phase hints", self.roles)

    def test_commands_initialize_visible_submaster_role(self) -> None:
        for text in (self.enable, self.disable):
            self.assertIn("[Submaster]", text)

    def test_enable_persists_submaster_in_session_and_mission_examples(
        self,
    ) -> None:
        self.assertGreaterEqual(self.enable.count("active_role: submaster"), 2)
        self.assertIn("in-memory Submaster initialization", self.enable)
        self.assertIn(
            "keep enablement and\n   `active_role: submaster` only in the current conversation context",
            self.enable,
        )

    def test_disable_does_not_persist_active_role(self) -> None:
        self.assertIn("Do not persist or overwrite", self.disable)
        self.assertIn("`active_role`", self.disable)
        self.assertNotIn("active_role: submaster", self.disable)

    def test_discovery_repairs_role_from_pending_action(self) -> None:
        self.assertIn("references/roles.md", self.discovery)
        self.assertIn(
            "repair stale `active_role` only in enabled records actually loaded",
            normalized_prose(self.discovery),
        )

    def test_public_docs_explain_visible_roles(self) -> None:
        for role in ("Submaster", "Strategist", "Quest Leader", "Quest Runner"):
            self.assertIn(role, self.readme)
        self.assertIn("one role label", self.readme)
        self.assertIn("visible guild roles", self.root_readme)

    def test_every_canonical_response_block_has_exactly_one_allowed_label(
        self,
    ) -> None:
        documents = {
            "enable": self.enable,
            "disable": self.disable,
            "examples": self.examples,
        }
        for name, markdown in documents.items():
            responses = canonical_text_responses(markdown)
            self.assertTrue(responses, f"{name} has no canonical response blocks")
            for response in responses:
                non_empty = [line.strip() for line in response.splitlines() if line.strip()]
                self.assertIn(non_empty[0], ALLOWED_ROLE_LABELS, (name, response))
                label_lines = [
                    line
                    for line in non_empty
                    if re.fullmatch(r"\[[^\]]+\]", line)
                ]
                self.assertEqual([non_empty[0]], label_lines, (name, response))

    def test_errors_and_ambiguous_role_fallback_are_submaster_messages(
        self,
    ) -> None:
        for command in (self.enable, self.disable):
            self.assertIn("Canonical localized error response:", command)
            self.assertIn(
                "Error responses begin with the localized Submaster label",
                command,
            )
        for text in (self.roles, self.skill):
            self.assertIn(
                "If role selection is genuinely ambiguous, use `submaster`",
                text,
            )
        self.assertIn(
            "Host- or tool-rendered UI events are outside this message contract",
            self.roles,
        )

    def test_scope_scenarios_have_exact_write_sets(self) -> None:
        fixture = load_fixture("scope_scenarios.json")
        for scenario in fixture["scope_write_sets"]:
            scope = scenario["scope"]
            operation = scenario["operation"]
            expected = {
                "session": {"session"},
                "mission": {"mission"},
                "both": {"session", "mission"},
            }[scope]
            if operation == "enable" and scope == "both":
                expected.add("current_mission")
            self.assertEqual(expected, set(scenario["expected_writes"]), scenario["name"])
            self.assertTrue(
                expected.isdisjoint(scenario["forbidden_writes"]),
                scenario["name"],
            )

    def test_scope_and_routing_metadata_contract_is_explicit(self) -> None:
        normalized_skill = normalized_prose(self.skill)
        self.assertIn(
            "Mission-only commands never write the session record, "
            "including `active_role` and `current_mission`.",
            normalized_skill,
        )
        self.assertIn(
            "Session-only commands never create or modify mission state.",
            normalized_skill,
        )
        self.assertIn(
            "A mission-only disable leaves `current_mission` unchanged.",
            normalized_prose(self.disable),
        )
        for text in (self.skill, self.discovery):
            normalized = normalized_prose(text).lower()
            self.assertIn(
                "repair stale `active_role` only in enabled records actually loaded",
                normalized,
            )
            self.assertIn(
                "ordinary session rehydration clears `current_mission`",
                normalized,
            )

    def test_effective_state_scenarios_use_union_of_scopes(self) -> None:
        fixture = load_fixture("scope_scenarios.json")
        for scenario in fixture["effective_state"]:
            actual = (
                "enabled"
                if "enabled" in (scenario["session"], scenario["mission"])
                else "disabled"
            )
            self.assertEqual(scenario["effective"], actual, scenario)

    def test_active_role_repairs_only_loaded_enabled_records(self) -> None:
        fixture = load_fixture("scope_scenarios.json")
        for scenario in fixture["active_role_conflicts"]:
            expected_repairs = []
            for scope, record in scenario["loaded"].items():
                if (
                    record is not None
                    and record["enabled"]
                    and record["active_role"] != scenario["pending_role"]
                ):
                    expected_repairs.append(scope)
            self.assertEqual(
                scenario["expected_repairs"],
                expected_repairs,
                scenario["name"],
            )

    def test_mission_creation_decision_table_matches_scenarios(self) -> None:
        fixture = load_fixture("mission_creation_scenarios.json")
        for scenario in fixture["scenarios"]:
            actual = mission_decision(
                scenario["scope"],
                scenario["explicit_path"],
                scenario["contextual_mission"],
                scenario["goal"],
            )
            self.assertEqual(scenario["expected"], actual, scenario["name"])

        self.assertIn("### Authoritative mission creation decision table", self.enable)
        expected_rows = (
            "| `session` | Never create or modify mission state. |",
            "| `mission` or `both` with an explicit existing path | Use that path. |",
            "| `mission` or `both` with an explicit missing path | Return an error. |",
            "| No explicit path and a contextual mission | Use the contextual mission. |",
            "| No mission and a non-empty goal | Create deterministically under `<workspace-root>/.ai-agent/plan/`; reuse the same derived name. |",
            "| `both`, no mission, and no goal | Enable session scope and report mission skipped. |",
            "| `mission`, no mission, and no goal | Return an error. |",
        )
        for row in expected_rows:
            self.assertIn(row, self.enable)

    def test_breaking_migration_requires_explicit_reenable(self) -> None:
        fixture = load_fixture("safety_scenarios.json")["migration"]
        self.assertEqual("breaking", fixture["kind"])
        self.assertEqual("ignore-and-preserve", fixture["legacy_action"])
        for text in (self.readme, self.skill, self.enable, self.disable):
            normalized = normalized_prose(text)
            self.assertIn("breaking migration", normalized.lower())
            self.assertIn("/perk-guild-enable --scope", normalized)
            self.assertIn("ignored and left untouched", normalized)
            self.assertIn("delete the legacy file when satisfied", normalized)

    def test_session_privacy_schema_uses_alias_and_vcs_exclusion(self) -> None:
        fixture = load_fixture("safety_scenarios.json")["privacy"]
        self.assertEqual("uuidv4", fixture["session_alias"])
        self.assertTrue(fixture["session_alias_reused"])
        self.assertEqual("sha256", fixture["session_filename_key"])
        self.assertEqual(
            ["session_alias", "kind", "note"],
            fixture["mission_chat_session_fields"],
        )
        self.assertEqual(["*", "!.gitignore"], fixture["sessions_gitignore_lines"])
        for text in (self.skill, self.enable):
            normalized = normalized_prose(text)
            self.assertIn("session_alias: \"<uuid-v4>\"", text)
            self.assertIn("random UUIDv4", normalized)
            self.assertIn(
                "<workspace-root>/.ai-agent/perk-guild/sessions/.gitignore",
                normalized,
            )
            self.assertRegex(text, r"(?m)^\s*\*\s*$\n^\s*!\.gitignore\s*$")
            self.assertIn("never rotate", normalized)
        conversation_section = self.skill.split(
            "## Conversation-session record",
            1,
        )[1].split("## Brief", 1)[0]
        self.assertIn("reuse its `session_alias`", normalized_prose(conversation_section).lower())
        self.assertIn("idempotently ensure", normalized_prose(conversation_section).lower())
        self.assertIn("reuse its `session_alias`", self.enable)
        status_section = self.skill.split("## Status", 1)[1].split(
            "## Conversation-session record",
            1,
        )[0]
        mission_yaml = status_section.split("```yaml", 1)[1].split("```", 1)[0]
        self.assertIn("chat_sessions: []", mission_yaml)
        self.assertNotIn("session_key:", mission_yaml)
        self.assertIn("session_alias", status_section)
        park_section = self.skill.split("## Park and resume", 1)[1].split(
            "## Authority direction",
            1,
        )[0]
        self.assertIn("session_alias", park_section)
        self.assertNotIn("session_key", park_section)
        self.assertIn(
            "If session state is not persisted, do not append",
            self.skill,
        )

    def test_mission_chat_sessions_forbid_sensitive_fields(self) -> None:
        fixture = load_fixture("safety_scenarios.json")["privacy"]
        status_section = self.skill.split("## Status", 1)[1].split(
            "## Conversation-session record",
            1,
        )[0]
        enable_mission_section = self.enable.split("### Step 5: Persist mission scope", 1)[1]
        for field in fixture["mission_forbidden_fields"]:
            if field == "raw_host_id":
                patterns = ("raw host identifier", "raw_host_id")
            else:
                patterns = (f"Never write `{field}`", f"never write `{field}`")
            for text in (status_section, enable_mission_section):
                self.assertTrue(
                    any(pattern.lower() in text.lower() for pattern in patterns),
                    (field, text[:200]),
                )

    def test_session_key_stays_in_session_record_only(self) -> None:
        conversation_section = self.skill.split(
            "## Conversation-session record",
            1,
        )[1].split("## Brief", 1)[0]
        self.assertIn("session_key:", conversation_section)
        self.assertIn("<session-key>.yaml", conversation_section)
        mission_status = self.skill.split("## Status", 1)[1].split(
            "## Conversation-session record",
            1,
        )[0]
        mission_yaml = mission_status.split("```yaml", 1)[1].split("```", 1)[0]
        self.assertNotIn("session_key:", mission_yaml)
        enable_session_section = self.enable.split(
            "### Step 3: Resolve and persist session scope",
            1,
        )[1].split("### Step 4", 1)[0]
        self.assertIn("session_key:", enable_session_section)
        enable_mission_section = self.enable.split(
            "### Step 5: Persist mission scope",
            1,
        )[1].split("### Step 6", 1)[0]
        self.assertNotIn("session_key:", enable_mission_section)
        self.assertNotIn("session_key:", self.discovery)

    def test_discovery_enforces_session_path_safety(self) -> None:
        normalized = normalized_prose(self.discovery)
        self.assertIn("realpath", normalized)
        self.assertIn("exactly one open workspace root", normalized)
        self.assertIn(
            "Reject a symlinked state directory or any symlink component",
            self.discovery,
        )
        self.assertIn("<workspace-root>/.ai-agent/perk-guild", self.discovery)
        self.assertIn("sessions", self.discovery)
        self.assertIn("SHA-256", self.discovery)
        self.assertNotIn("session_key:", self.discovery)

    def test_design_and_plan_capture_privacy_and_path_safety(self) -> None:
        fixture = load_fixture("safety_scenarios.json")["privacy"]
        for text in (self.design, self.plan):
            normalized = normalized_prose(text)
            self.assertIn("sessions/.gitignore", normalized)
            self.assertIn("session_alias", normalized)
            self.assertIn("atomic", normalized.lower())
            self.assertIn("symlink", normalized.lower())
            self.assertIn("realpath", normalized.lower())
            for field in fixture["mission_chat_session_fields"]:
                self.assertIn(field, normalized)
            self.assertIn("session_key", normalized)
            self.assertTrue(
                "raw host identifier" in normalized or "raw_host_id" in normalized
            )

    def test_missing_session_id_scenarios_report_both_persistence_flags(
        self,
    ) -> None:
        fixture = load_fixture("safety_scenarios.json")
        for scenario in fixture["missing_session_id"]:
            session_persisted = scenario["stable_session_id"] and scenario["scope"] in (
                "session",
                "both",
            )
            mission_persisted = scenario["mission_written"]
            append_chat_session = session_persisted and mission_persisted
            self.assertEqual(
                scenario["session_persisted"],
                session_persisted,
                scenario["name"],
            )
            self.assertEqual(
                scenario["mission_persisted"],
                mission_persisted,
                scenario["name"],
            )
            self.assertEqual(
                scenario["append_chat_session"],
                append_chat_session,
                scenario["name"],
            )

    def test_path_and_atomic_write_contracts_are_consistent(self) -> None:
        fixture = load_fixture("safety_scenarios.json")
        for scenario in fixture["path_contracts"]:
            actual = path_decision(
                scenario["target_kind"],
                scenario["canonicalize"],
                scenario["workspace_matches"],
                scenario["state_component_symlink"],
            )
            self.assertEqual(scenario["expected"], actual, scenario["name"])

        for text in (self.skill, self.enable):
            normalized = normalized_prose(text)
            self.assertIn("nearest existing parent", normalized)
            self.assertIn("exactly one open workspace root", normalized)
        for text in (self.skill, self.enable, self.disable):
            normalized = normalized_prose(text)
            self.assertIn("realpath", normalized)
            self.assertIn(
                "Reject a symlinked state directory or any symlink component",
                text,
            )
            self.assertIn("temporary file in the same directory", normalized)
            self.assertIn("rename or replace", normalized)
            self.assertIn("Never truncate", normalized)

    def test_smoke_script_is_targeted_and_checks_all_runtime_references(
        self,
    ) -> None:
        self.assertIn('TARGET="${1:-cursor}"', self.smoke_install)
        for target in ("cursor", "claude", "copilot", "codex"):
            self.assertRegex(self.smoke_install, rf"(?m)^\s*{target}\)")
        self.assertIn("references/roles.md", self.smoke_install)
        self.assertIn("tests excluded", self.smoke_install)

    def test_ci_covers_all_targets_and_pack_dry_run(self) -> None:
        self.assertIn("matrix:", self.ci)
        for target in ("cursor", "claude", "copilot", "codex"):
            self.assertIn(target, self.ci)
        self.assertIn(
            'bash tests/smoke_install.sh "${{ matrix.target }}"',
            self.ci,
        )
        self.assertIn("apm pack --dry-run --offline --json", self.ci)

    def test_public_metadata_introduces_scopes_and_visible_roles(self) -> None:
        manifest = MANIFEST.read_text()
        for text in (self.root_readme, self.readme, manifest):
            normalized = normalized_prose(text)
            self.assertIn("independent mission and conversation-session scopes", normalized)
            self.assertIn("visible guild roles", normalized)

    def test_design_and_plan_capture_settled_persistence_rules(self) -> None:
        for text in (self.design, self.plan):
            normalized = normalized_prose(text)
            self.assertIn(
                "Mission-only commands never write session `active_role` or "
                "`current_mission`.",
                normalized,
            )
            self.assertIn(
                "Disable does not persist a replacement `active_role`",
                normalized,
            )
            self.assertIn("session_persisted", normalized)
            self.assertIn("mission_persisted", normalized)

    def test_skill_mission_enable_follows_decision_table_not_generic_create(
        self,
    ) -> None:
        enable_section = self.skill.split("## Enable and disable", 1)[1].split(
            "## Legacy workspace flag",
            1,
        )[0]
        self.assertNotIn("create it before adding the flag", enable_section)
        self.assertIn("explicit", enable_section.lower())
        self.assertIn("always an error", enable_section.lower())
        self.assertIn("deterministic", enable_section.lower())

    def test_enable_gitignore_precedes_session_record_write(self) -> None:
        step3 = self.enable.split(
            "### Step 3: Resolve and persist session scope",
            1,
        )[1].split("### Step 4", 1)[0]
        gitignore_pos = step3.find("sessions/.gitignore")
        session_write_pos = step3.find("sessions/<session-key>.yaml")
        self.assertNotEqual(gitignore_pos, -1)
        self.assertNotEqual(session_write_pos, -1)
        self.assertLess(gitignore_pos, session_write_pos)
        normalized = normalized_prose(step3)
        self.assertIn("before writing any session record", normalized.lower())

    def test_mission_chat_sessions_starts_empty_and_upserts_by_alias(self) -> None:
        status_section = self.skill.split("## Status", 1)[1].split(
            "## Conversation-session record",
            1,
        )[0]
        mission_yaml = status_section.split("```yaml", 1)[1].split("```", 1)[0]
        self.assertIn("chat_sessions: []", mission_yaml)
        enable_mission = self.enable.split("### Step 5: Persist mission scope", 1)[
            1
        ].split("### Step 6", 1)[0]
        normalized_enable = normalized_prose(enable_mission)
        self.assertIn("chat_sessions: []", enable_mission)
        self.assertIn("upsert", normalized_enable.lower())
        self.assertIn("session_alias", normalized_enable.lower())
        self.assertIn("never duplicate", normalized_enable.lower())

    def test_chat_session_idempotence_scenarios(self) -> None:
        fixture = load_fixture("chat_session_scenarios.json")
        self.assertEqual("chat_sessions: []", fixture["initial_state"])
        self.assertEqual("session_alias", fixture["upsert_by"])
        for scenario in fixture["scenarios"]:
            existing = scenario.get("existing_chat_sessions", [])
            actual = chat_session_action(
                scenario["session_persisted"],
                scenario["mission_persisted"],
                existing,
                scenario.get("session_alias"),
            )
            self.assertEqual(scenario["expected_action"], actual, scenario["name"])
            if scenario["expected_action"] == "none":
                expected_count = 0
            elif scenario["expected_action"] == "append":
                expected_count = len(existing) + 1
            else:
                expected_count = len(existing)
            self.assertEqual(
                scenario["expected_count"],
                expected_count,
                scenario["name"],
            )

    def test_codex_documentation_requires_compile(self) -> None:
        self.assertIn("apm compile", self.readme.lower())
        self.assertIn("apm compile", self.smoke_install)
        self.assertIn("AGENTS.md", self.smoke_install)

    def test_migration_readme_includes_mission_path_example(self) -> None:
        migration = self.readme.split("## Migration from 0.1.x", 1)[1].split(
            "## Development",
            1,
        )[0]
        self.assertIn("/perk-guild-enable --scope mission", migration)
        self.assertTrue(
            ".ai-agent/plan/" in migration or "login-home" in migration,
            migration,
        )


if __name__ == "__main__":
    unittest.main()
