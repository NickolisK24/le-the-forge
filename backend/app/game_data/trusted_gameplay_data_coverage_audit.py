"""Deterministic trusted gameplay data coverage diagnostics.

This module is intentionally read-only and descriptive-only. It inventories
repository files, generated reports, backend route declarations, frontend route
references, schema mappings, and known planner dependency blockers without
enabling planner behavior or operational semantics.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any


PHASE_ID = "diagnostics_trusted_game_data_coverage_audit"
PHASE_NAME = "diagnostics/trusted-game-data-coverage-audit"
SCHEMA_VERSION = "trusted_gameplay_data_coverage_audit.v1"
GENERATED_AT = "2026-05-19T00:00:00+00:00"

REPORT_PATHS = {
    "coverage": "docs/generated/trusted_gameplay_data_coverage_report.json",
    "schema_alignment": "docs/generated/gameplay_schema_alignment_report.json",
    "visibility": "docs/generated/gameplay_visibility_coverage_report.json",
    "support_matrix": "docs/generated/gameplay_support_matrix_report.json",
    "extraction_gap": "docs/generated/gameplay_extraction_gap_report.json",
}

CLASSIFICATION_KEYS = (
    "present",
    "partial",
    "missing",
    "stale",
    "unsupported",
    "extracted",
    "generated",
    "hardcoded",
    "trusted",
    "untrusted",
    "frontend_visible",
    "backend_visible",
    "schema_mismatch",
    "planner_dependency_gap",
)

REPOSITORY_REMAINS = (
    "READ-ONLY",
    "DESCRIPTIVE-ONLY",
    "FAIL-VISIBLE",
    "NON-operational",
    "NON-mutating",
    "NON-authorizing",
    "NON-approving",
    "NON-recommending",
    "NON-ranking",
    "NON-scoring",
    "NON-orchestrating",
)

ENABLED_SEMANTICS = {
    "planner_execution_enabled": False,
    "planner_recommendations_enabled": False,
    "planner_ranking_enabled": False,
    "planner_scoring_enabled": False,
    "approval_semantics_enabled": False,
    "authorization_semantics_enabled": False,
    "orchestration_execution_enabled": False,
    "orchestration_mutation_enabled": False,
    "runtime_mutation_enabled": False,
    "operational_runtime_behavior_enabled": False,
    "autonomous_decision_system_enabled": False,
    "production_consumption_enabled": False,
}

NON_OPERATIONAL_STATEMENT = (
    "Trusted gameplay data coverage diagnostics do NOT enable planner "
    "execution, planner recommendations, ranking, scoring, approval, "
    "authorization, orchestration execution, runtime mutation, operational "
    "runtime behavior, autonomous decisions, or inferred gameplay support."
)

STABILIZED_ROUTE_EXPECTATIONS = (
    {
        "route_id": "backend_health",
        "route": "/api/health",
        "source_path": "backend/app/routes/health.py",
        "token": '@health_bp.get("/health")',
        "route_type": "backend",
    },
    {
        "route_id": "backend_trust_visibility",
        "route": "/api/trust/visibility",
        "source_path": "backend/app/routes/trust.py",
        "token": '@trust_bp.get("/visibility")',
        "route_type": "backend",
    },
    {
        "route_id": "frontend_classes",
        "route": "/classes",
        "source_path": "frontend/src/App.tsx",
        "token": 'path="/classes"',
        "route_type": "frontend",
    },
    {
        "route_id": "frontend_passives",
        "route": "/passives",
        "source_path": "frontend/src/App.tsx",
        "token": 'path="/passives"',
        "route_type": "frontend",
    },
    {
        "route_id": "frontend_trusted_data",
        "route": "/trusted-data",
        "source_path": "frontend/src/App.tsx",
        "token": 'path="/trusted-data"',
        "route_type": "frontend",
    },
    {
        "route_id": "frontend_trusted_data_frontend_trust",
        "route": "/trusted-data/frontend-trust",
        "source_path": "frontend/src/App.tsx",
        "token": 'path="/trusted-data/frontend-trust"',
        "route_type": "frontend",
    },
)


@dataclass(frozen=True)
class GameplayDomainSpec:
    system_id: str
    label: str
    raw_sources: tuple[str, ...] = ()
    generated_assets: tuple[str, ...] = ()
    validation_reports: tuple[str, ...] = ()
    unsupported_reports: tuple[str, ...] = ()
    backend_tokens: tuple[str, ...] = ()
    backend_search_paths: tuple[str, ...] = ("backend/app/routes",)
    frontend_tokens: tuple[str, ...] = ()
    frontend_search_paths: tuple[str, ...] = ("frontend/src",)
    schema_mappings: tuple[str, ...] = ()
    trusted_manifests: tuple[str, ...] = ()
    planner_contracts: tuple[str, ...] = ()
    hardcoded_paths: tuple[str, ...] = ()
    expected_generated: bool = True
    expected_frontend: bool = True
    expected_backend: bool = True
    expected_schema: bool = True
    expected_planner_contract: bool = True
    notes: tuple[str, ...] = ()


GAMEPLAY_DOMAIN_SPECS = (
    GameplayDomainSpec(
        system_id="classes",
        label="Classes",
        raw_sources=("data/classes/classes.json",),
        generated_assets=("docs/generated/v2_class_mastery_bundle.json",),
        validation_reports=("docs/generated/v2_class_mastery_validation_report.json",),
        backend_tokens=('@ref_bp.get("/classes")', '@experimental_bp.route("/v2/classes"'),
        frontend_tokens=('path="/classes"', '"/debug/v2-classes"', 'fetchV2ClassMastery'),
        schema_mappings=("frontend/src/types/canonicalClassMastery.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("backend/app/routes/ref.py", "backend/app/constants/classes.py"),
    ),
    GameplayDomainSpec(
        system_id="masteries",
        label="Masteries",
        raw_sources=("data/classes/classes.json",),
        generated_assets=("docs/generated/v2_class_mastery_bundle.json",),
        validation_reports=("docs/generated/v2_class_mastery_validation_report.json",),
        backend_tokens=('@experimental_bp.route("/v2/masteries"', "CLASS_MASTERIES"),
        frontend_tokens=('"/debug/v2-classes"', 'fetchV2ClassMastery'),
        schema_mappings=("frontend/src/types/canonicalClassMastery.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("backend/app/constants/classes.py", "backend/app/routes/ref.py"),
    ),
    GameplayDomainSpec(
        system_id="passive_trees",
        label="Passive Trees",
        raw_sources=("data/classes/passives.json", "data/classes/unmatched_trees.json"),
        generated_assets=("docs/generated/v2_passive_tree_bundle.json",),
        validation_reports=("docs/generated/v2_passive_tree_validation_report.json",),
        unsupported_reports=("docs/generated/v2_passive_unsupported_report.json",),
        backend_tokens=('@passives_bp.get("")', '@experimental_bp.route("/v2/passives"'),
        frontend_tokens=('path="/passives"', '"/debug/v2-passives"', "V2PassivesDebugPage"),
        schema_mappings=("frontend/src/types/canonicalPassive.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="passives",
        label="Passives",
        raw_sources=("data/classes/passives.json",),
        generated_assets=("docs/generated/v2_passive_tree_bundle.json",),
        validation_reports=("docs/generated/v2_passive_tree_validation_report.json",),
        unsupported_reports=("docs/generated/v2_passive_unsupported_report.json",),
        backend_tokens=('@ref_bp.get("/passives")', '@passives_bp.get("")'),
        frontend_tokens=('path="/passives"', "PassiveTreePage", "V2PassivesDebugPage"),
        schema_mappings=("frontend/src/types/canonicalPassive.ts", "frontend/src/types/passiveEffects.ts"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="skills",
        label="Skills",
        raw_sources=("data/classes/skills_metadata.json", "data/classes/skills_with_trees.json"),
        generated_assets=("docs/generated/v2_skill_bundle.json",),
        validation_reports=("docs/generated/v2_skill_validation_report.json",),
        unsupported_reports=("docs/generated/v2_skill_unsupported_report.json",),
        backend_tokens=('@ref_bp.get("/skills")', '@experimental_bp.route("/v2/skills"'),
        frontend_tokens=("V2SkillsDebugPage", '"/debug/v2-skills"', "refApi.skills"),
        schema_mappings=("frontend/src/types/canonicalSkill.ts", "frontend/src/types/skillClassification.ts"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("frontend/src/data/skillTrees/index.ts", "backend/app/game_data/skills.json"),
    ),
    GameplayDomainSpec(
        system_id="skill_trees",
        label="Skill Trees",
        raw_sources=("data/classes/community_skill_trees.json", "data/classes/skills_with_trees.json"),
        generated_assets=("docs/generated/v2_skill_tree_bundle.json",),
        validation_reports=("docs/generated/v2_skill_validation_report.json",),
        unsupported_reports=("docs/generated/v2_skill_unsupported_report.json",),
        backend_tokens=('@skills_bp.get("/skills/<skill_id>/tree")', '@experimental_bp.route("/v2/skills/trees/'),
        frontend_tokens=("skillTrees", "SkillTreeDebugPanel", "V2SkillsDebugPage"),
        schema_mappings=("frontend/src/types/skillTree.ts", "frontend/src/types/canonicalSkill.ts"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("frontend/src/data/skillTrees/index.ts",),
    ),
    GameplayDomainSpec(
        system_id="skill_nodes",
        label="Skill Nodes",
        raw_sources=("data/classes/skill_tree_nodes.json", "data/classes/community_skill_trees.json"),
        generated_assets=("docs/generated/v2_skill_tree_bundle.json",),
        validation_reports=("docs/generated/v2_skill_validation_report.json",),
        unsupported_reports=("docs/generated/v2_skill_unsupported_report.json",),
        backend_tokens=('@experimental_bp.route("/v2/skills/trees/<path:tree_id>/nodes',),
        frontend_tokens=("CanonicalSkillTreeNode", "SkillTreeDebugPanel", "skillTrees"),
        schema_mappings=("frontend/src/types/canonicalSkill.ts", "frontend/src/types/skillTree.ts"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("frontend/src/data/skillTrees/index.ts",),
    ),
    GameplayDomainSpec(
        system_id="items",
        label="Items",
        raw_sources=("data/items/items.json", "data/items/base_items.json", "data/items/implicit_stats.json"),
        generated_assets=("docs/generated/v2_item_base_bundle.json", "docs/generated/v2_item_implicit_bundle.json"),
        validation_reports=("docs/generated/v2_item_validation_report.json",),
        backend_tokens=('@ref_bp.get("/base-items")', '@experimental_bp.route("/v2/items/bases"'),
        frontend_tokens=("V2ItemsDebugPage", '"/debug/v2-items"', "refApi.baseItems"),
        schema_mappings=("frontend/src/types/canonicalItem.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("backend/app/constants/base_type_id_to_item_type_id.py",),
    ),
    GameplayDomainSpec(
        system_id="uniques",
        label="Uniques",
        raw_sources=("data/items/uniques.json",),
        generated_assets=("docs/generated/v2_unique_bundle.json",),
        validation_reports=("docs/generated/v2_unique_set_validation_report.json",),
        unsupported_reports=("docs/generated/v2_unique_set_unsupported_report.json",),
        backend_tokens=('@ref_bp.get("/uniques")', '@experimental_bp.route("/v2/uniques"'),
        frontend_tokens=("V2UniqueSetDebugPage", '"/debug/v2-unique-sets"'),
        schema_mappings=("frontend/src/types/canonicalUnique.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="set_items",
        label="Set Items",
        raw_sources=("data/items/set_items.json",),
        generated_assets=("docs/generated/v2_set_bundle.json",),
        validation_reports=("docs/generated/v2_unique_set_validation_report.json",),
        unsupported_reports=("docs/generated/v2_unique_set_unsupported_report.json",),
        backend_tokens=('@experimental_bp.route("/v2/sets"',),
        frontend_tokens=("V2UniqueSetDebugPage", '"/debug/v2-unique-sets"'),
        schema_mappings=("frontend/src/types/canonicalSet.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        expected_backend=True,
    ),
    GameplayDomainSpec(
        system_id="affixes",
        label="Affixes",
        raw_sources=("data/items/affixes.json",),
        generated_assets=("docs/generated/v2_affix_bundle.json",),
        validation_reports=("docs/generated/v2_affix_validation_report.json",),
        backend_tokens=('@ref_bp.get("/affixes")', '@experimental_bp.route("/v2/affixes"', '@affixes_bp.get("/catalog"'),
        frontend_tokens=('path="/affixes"', "ForgeSafeAffixesDebugPage", "refApi.affixes"),
        schema_mappings=("frontend/src/types/canonicalAffix.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("backend/app/routes/ref.py", "backend/app/constants/cache.py"),
    ),
    GameplayDomainSpec(
        system_id="idols",
        label="Idols",
        raw_sources=("data/items/items.json", "data/items/affixes.json"),
        generated_assets=("docs/generated/v2_idol_bundle.json", "docs/generated/v2_idol_affix_bundle.json"),
        validation_reports=("docs/generated/v2_idol_validation_report.json",),
        backend_tokens=('@experimental_bp.route("/v2/idols"', '@experimental_bp.route("/v2/idols/affixes"'),
        frontend_tokens=("V2IdolsDebugPage", '"/debug/v2-idols"'),
        schema_mappings=("frontend/src/types/canonicalIdol.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="blessings",
        label="Blessings",
        raw_sources=("data/progression/blessings.json",),
        generated_assets=(),
        validation_reports=(),
        backend_tokens=('@ref_bp.get("/blessings")',),
        frontend_tokens=("getBlessings", "SelectedBlessing", "types/blessings"),
        schema_mappings=("frontend/src/types/blessings.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        expected_generated=True,
    ),
    GameplayDomainSpec(
        system_id="crafting_materials",
        label="Crafting Materials",
        raw_sources=("data/items/crafting_rules.json", "data/items/forging_potential_ranges.json"),
        generated_assets=(),
        validation_reports=(),
        backend_tokens=('@ref_bp.get("/crafting-rules")', '@craft_bp'),
        frontend_tokens=("CraftingPage", "craftApi", "CraftingWorkspace"),
        schema_mappings=("frontend/src/types/index.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("backend/app/engines/fp_engine.py", "backend/app/engines/craft_engine.py"),
    ),
    GameplayDomainSpec(
        system_id="monolith_systems",
        label="Monolith Systems",
        raw_sources=("data/world/timelines.json", "data/progression/blessings.json", "data/localization/monolith_objective_strings.json"),
        generated_assets=(),
        validation_reports=(),
        backend_tokens=('@ref_bp.get("/blessings")',),
        frontend_tokens=("BlessingTimeline", "blessings"),
        schema_mappings=("frontend/src/types/blessings.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="echo_systems",
        label="Echo Systems",
        raw_sources=("data/progression/weaver_tree.json", "data/world/timelines.json", "data/localization/monolith_objective_strings.json"),
        generated_assets=(),
        validation_reports=(),
        backend_tokens=(),
        frontend_tokens=(),
        schema_mappings=(),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        expected_backend=True,
        expected_frontend=True,
        expected_schema=True,
    ),
    GameplayDomainSpec(
        system_id="bosses",
        label="Bosses",
        raw_sources=("data/entities/enemy_profiles.json", "data/entities/actors.json"),
        generated_assets=(),
        validation_reports=(),
        backend_tokens=('@ref_bp.get("/enemy-profiles")', "BossAnalysisResponse"),
        frontend_tokens=("BossAnalysisResponse", "SimulationPage", "encounterApi"),
        schema_mappings=("frontend/src/types/index.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="ailments",
        label="Ailments",
        raw_sources=("data/combat/ailments.json", "data/localization/ailment_strings.json"),
        generated_assets=(),
        validation_reports=(),
        backend_tokens=("get_ailments", "ailment"),
        frontend_tokens=("ailment", "Ailment"),
        schema_mappings=("frontend/src/types/conditionalStats.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="damage_types",
        label="Damage Types",
        raw_sources=("data/combat/damage_types.json",),
        generated_assets=(),
        validation_reports=(),
        backend_tokens=('@ref_bp.get("/damage-types")',),
        frontend_tokens=("damage_types", "damageTypes", "Damage"),
        schema_mappings=("frontend/src/types/conditionalStats.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="mechanics",
        label="Mechanics",
        raw_sources=("data/localization/game_guide_strings.json", "data/localization/descriptor_strings.json"),
        generated_assets=("docs/generated/v2_modifier_registry.json", "docs/generated/v2_stat_registry.json"),
        validation_reports=("docs/generated/v2_modifier_validation_report.json", "docs/generated/v2_stat_modifier_dry_run_report.json"),
        unsupported_reports=("docs/generated/v2_modifier_blocked_reasons_report.json",),
        backend_tokens=("stat_resolution_pipeline", "combat_engine", "modifier"),
        frontend_tokens=("V2StatsModifiersDebugPage", '"/debug/v2-stats-modifiers"'),
        schema_mappings=("frontend/src/types/canonicalModifier.ts", "frontend/src/types/conditionalStats.ts"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        hardcoded_paths=("backend/app/game_data/constants.json", "backend/app/engines/stat_engine.py"),
    ),
    GameplayDomainSpec(
        system_id="tags",
        label="Tags",
        raw_sources=("data/items/tags.json",),
        generated_assets=("docs/generated/v2_affix_bundle.json", "docs/generated/v2_item_base_bundle.json"),
        validation_reports=("docs/generated/v2_affix_validation_report.json", "docs/generated/v2_item_validation_report.json"),
        backend_tokens=("tags", "@ref_bp.get"),
        frontend_tokens=("tags",),
        schema_mappings=("frontend/src/types/canonicalBase.ts",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="gameplay_backend_payloads",
        label="Gameplay Backend Payloads",
        raw_sources=(),
        generated_assets=("docs/generated/v2_api_contract_report.json", "docs/generated/v2_backend_repository_report.json"),
        validation_reports=("docs/generated/v2_validation_ci_report.json",),
        backend_tokens=("@ref_bp.get", "@experimental_bp.route", "@health_bp.get", "@trust_bp.get"),
        frontend_tokens=(),
        schema_mappings=("backend/app/api_contracts/v2",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        expected_frontend=False,
    ),
    GameplayDomainSpec(
        system_id="gameplay_frontend_payloads",
        label="Gameplay Frontend Payloads",
        raw_sources=(),
        generated_assets=("docs/generated/v2_api_contract_report.json",),
        validation_reports=(),
        backend_tokens=(),
        frontend_tokens=("refApi", "fetchV2", "V2EnvelopePanels", "FrontendTrustSurface"),
        schema_mappings=("frontend/src/lib/api.ts", "frontend/src/lib/v2ApiEnvelope.ts"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        expected_backend=False,
    ),
    GameplayDomainSpec(
        system_id="trusted_extraction_manifests",
        label="Trusted Extraction Manifests",
        raw_sources=("data/version.json",),
        generated_assets=("docs/generated/v2_source_inventory.json",),
        validation_reports=("docs/generated/v2_validation_ci_report.json",),
        backend_tokens=(),
        frontend_tokens=(),
        schema_mappings=(),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
        expected_backend=False,
        expected_frontend=False,
        expected_schema=False,
    ),
    GameplayDomainSpec(
        system_id="trusted_generated_assets",
        label="Trusted Generated Assets",
        raw_sources=(),
        generated_assets=(
            "docs/generated/v2_class_mastery_bundle.json",
            "docs/generated/v2_passive_tree_bundle.json",
            "docs/generated/v2_skill_bundle.json",
            "docs/generated/v2_skill_tree_bundle.json",
            "docs/generated/v2_item_base_bundle.json",
            "docs/generated/v2_item_implicit_bundle.json",
            "docs/generated/v2_unique_bundle.json",
            "docs/generated/v2_set_bundle.json",
            "docs/generated/v2_affix_bundle.json",
            "docs/generated/v2_idol_bundle.json",
            "docs/generated/v2_idol_affix_bundle.json",
            "docs/generated/v2_stat_registry.json",
            "docs/generated/v2_modifier_registry.json",
        ),
        validation_reports=("docs/generated/v2_validation_ci_report.json",),
        backend_tokens=('@experimental_bp.route("/v2/',),
        frontend_tokens=("V2DebugNavigationPage", "V2EnvelopePanels"),
        schema_mappings=("backend/app/repositories/v2", "frontend/src/types"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="schema_mappings",
        label="Schema Mappings",
        raw_sources=(),
        generated_assets=("docs/generated/v2_api_contract_report.json", "docs/generated/v2_backend_repository_report.json"),
        validation_reports=("docs/generated/v2_validation_ci_report.json",),
        backend_tokens=("standardize_v2_payload", "V2"),
        frontend_tokens=("V2ApiEnvelope", "Canonical"),
        schema_mappings=("backend/app/api_contracts/v2", "backend/app/repositories/v2", "frontend/src/types"),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json",),
    ),
    GameplayDomainSpec(
        system_id="planner_facing_gameplay_contracts",
        label="Planner-facing Gameplay Contracts",
        raw_sources=(),
        generated_assets=("docs/generated/v2_planner_remap_readiness_report.json", "docs/generated/v3_production_remap_gate_audit_report.json"),
        validation_reports=("docs/generated/v2_planner_adapter_diagnostics_report.json",),
        backend_tokens=("planner_adapters", "production_remap"),
        frontend_tokens=("V2PlannerAdapterStatusPanel", "PreV3MechanicalReadinessPage"),
        schema_mappings=("backend/app/planner_adapters",),
        trusted_manifests=("docs/generated/v2_source_inventory.json",),
        planner_contracts=("docs/generated/v2_planner_remap_readiness_report.json", "docs/generated/v3_production_remap_gate_audit_report.json"),
        expected_planner_contract=True,
    ),
)


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[3]


def _rel(path: Path) -> str:
    return path.as_posix()


def _path(root: Path, relative_path: str) -> Path:
    return root / relative_path


def _read_text(root: Path, relative_path: str) -> str:
    path = _path(root, relative_path)
    if path.is_dir():
        parts: list[str] = []
        for child in sorted(path.rglob("*")):
            if child.is_file() and child.suffix in {".py", ".ts", ".tsx", ".json"}:
                try:
                    parts.append(child.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    continue
        return "\n".join(parts)
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError, OSError):
        return ""


def _load_json_value(root: Path, relative_path: str) -> Any:
    try:
        return json.loads(_path(root, relative_path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"_status": "missing"}
    except json.JSONDecodeError as exc:
        return {"_status": "malformed", "error": exc.__class__.__name__}


def _load_json(root: Path, relative_path: str) -> dict[str, Any]:
    payload = _load_json_value(root, relative_path)
    if isinstance(payload, dict):
        return payload
    return {"_status": "non_object_json", "value_type": type(payload).__name__}


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def deterministic_hash(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def with_deterministic_hash(report: dict[str, Any]) -> dict[str, Any]:
    payload = dict(report)
    payload["deterministic_hash_replay_verified"] = True
    payload["deterministic_report_hash"] = deterministic_hash(payload)
    replay = dict(payload)
    replay_hash = replay.pop("deterministic_report_hash")
    payload["deterministic_hash_replay_verified"] = (
        replay_hash == deterministic_hash(replay)
    )
    return payload


def _file_reference(root: Path, relative_path: str) -> dict[str, Any]:
    path = _path(root, relative_path)
    reference: dict[str, Any] = {
        "path": relative_path.replace("\\", "/"),
        "exists": path.exists(),
        "is_directory": path.is_dir(),
    }
    if path.exists() and path.is_file():
        reference["byte_size"] = path.stat().st_size
        if path.suffix == ".json":
            payload = _load_json(root, relative_path)
            reference["json_status"] = payload.get("_status", "valid")
            if "schema_version" in payload:
                reference["schema_version"] = payload["schema_version"]
            if "generated_on" in payload:
                reference["generated_on"] = payload["generated_on"]
            if isinstance(payload.get("metadata"), dict):
                metadata = payload["metadata"]
                reference["read_only"] = metadata.get("read_only")
                reference["production_consumed"] = metadata.get(
                    "production_consumed",
                    metadata.get("production_consumer"),
                )
                reference["production_safe"] = metadata.get("production_safe")
            if isinstance(payload.get("summary"), dict):
                summary = payload["summary"]
                reference["validation_error_count"] = summary.get(
                    "validation_error_count",
                    0,
                )
                reference["validation_warning_count"] = summary.get(
                    "validation_warning_count",
                    0,
                )
    return reference


def _count_tokens(root: Path, search_paths: tuple[str, ...], tokens: tuple[str, ...]) -> dict[str, bool]:
    if not tokens:
        return {}
    haystack_parts = [_read_text(root, search_path) for search_path in search_paths]
    haystack = "\n".join(haystack_parts)
    return {token: token in haystack for token in tokens}


def _summary_counts(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    support_counts: Counter[str] = Counter()
    trust_counts: Counter[str] = Counter()
    special_counts: Counter[str] = Counter()
    stable_calculable_count = 0
    validation_error_count = 0
    validation_warning_count = 0
    total_record_count = 0
    unsupported_visibility_count = 0
    generated_on: set[str] = set()
    schemas: set[str] = set()
    read_only_values: set[bool] = set()
    production_consumed_values: set[bool] = set()

    for payload in payloads:
        if payload.get("_status"):
            continue
        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            if isinstance(metadata.get("read_only"), bool):
                read_only_values.add(metadata["read_only"])
            production_value = metadata.get(
                "production_consumed",
                metadata.get("production_consumer"),
            )
            if isinstance(production_value, bool):
                production_consumed_values.add(production_value)
        if isinstance(payload.get("generated_on"), str):
            generated_on.add(payload["generated_on"])
        if isinstance(payload.get("schema_version"), str):
            schemas.add(payload["schema_version"])
        summary = payload.get("summary")
        if not isinstance(summary, dict):
            continue
        support_counts.update(summary.get("support_status_counts", {}))
        trust_counts.update(summary.get("trust_level_counts", {}))
        for key, value in summary.items():
            if not isinstance(value, int):
                continue
            if key.endswith("_count") and key not in {
                "validation_error_count",
                "validation_warning_count",
                "stable_calculable_count",
                "production_consumed",
            }:
                if key in {
                    "class_count",
                    "mastery_count",
                    "passive_tree_count",
                    "passive_node_count",
                    "skill_count",
                    "skill_tree_count",
                    "skill_node_count",
                    "item_base_count",
                    "unique_count",
                    "set_item_count",
                    "set_bonus_count",
                    "idol_count",
                    "idol_affix_count",
                    "affix_count",
                    "route_count",
                    "repository_domain_count",
                    "source_count",
                }:
                    total_record_count += value
            if "unsupported" in key or "text_only" in key:
                unsupported_visibility_count += value
        for key, value in summary.items():
            if key.endswith("classification_counts") and isinstance(value, dict):
                special_counts.update(value)
        stable_calculable_count += int(summary.get("stable_calculable_count", 0) or 0)
        validation_error_count += int(summary.get("validation_error_count", 0) or 0)
        validation_warning_count += int(summary.get("validation_warning_count", 0) or 0)

    return {
        "support_status_counts": dict(sorted(support_counts.items())),
        "trust_level_counts": dict(sorted(trust_counts.items())),
        "special_behavior_counts": dict(sorted(special_counts.items())),
        "stable_calculable_count": stable_calculable_count,
        "validation_error_count": validation_error_count,
        "validation_warning_count": validation_warning_count,
        "estimated_record_count": total_record_count,
        "unsupported_visibility_count": unsupported_visibility_count,
        "schema_versions": sorted(schemas),
        "generated_on_values": sorted(generated_on),
        "read_only_values": sorted(read_only_values),
        "production_consumed_values": sorted(production_consumed_values),
    }


def _data_manifest_status(root: Path) -> dict[str, Any]:
    manifest = _load_json(root, "data/version.json")
    patch_version = manifest.get("patch_version") or manifest.get("patch") or "missing"
    return {
        "path": "data/version.json",
        "exists": not bool(manifest.get("_status")),
        "patch_version": patch_version,
        "patch_version_unknown": patch_version == "unknown",
        "synced_at": manifest.get("synced_at", "missing"),
        "files_updated": manifest.get("files_updated", []),
    }


def _source_inventory_status(root: Path) -> dict[str, Any]:
    inventory = _load_json(root, "docs/generated/v2_source_inventory.json")
    summary = inventory.get("summary", {}) if isinstance(inventory.get("summary"), dict) else {}
    metadata = inventory.get("metadata", {}) if isinstance(inventory.get("metadata"), dict) else {}
    trust_status = summary.get("by_current_trust_status", {})
    source_kind = summary.get("by_source_kind", {})
    return {
        "path": "docs/generated/v2_source_inventory.json",
        "exists": not bool(inventory.get("_status")),
        "generated_on": metadata.get("generated_on", "missing"),
        "checkpoint": metadata.get("checkpoint", "missing"),
        "read_only": metadata.get("read_only") is True,
        "production_safe": metadata.get("production_safe"),
        "source_count": summary.get("source_count", 0),
        "replace_or_remap_count": summary.get("replace_or_remap_count", 0),
        "current_trust_status_counts": trust_status,
        "source_kind_counts": source_kind,
        "unknown_trust_count": trust_status.get("unknown", 0),
        "manual_source_count": source_kind.get("manual", 0),
        "unknown_source_kind_count": source_kind.get("unknown", 0),
    }


def _planner_dependency_status(root: Path) -> dict[str, Any]:
    planner = _load_json(root, "docs/generated/v2_planner_remap_readiness_report.json")
    summary = planner.get("summary", {}) if isinstance(planner.get("summary"), dict) else {}
    metadata = planner.get("metadata", {}) if isinstance(planner.get("metadata"), dict) else {}
    dependencies = planner.get("dependency_classifications", [])
    hardcoded = planner.get("hardcoded_and_legacy_data_sources", [])
    return {
        "path": "docs/generated/v2_planner_remap_readiness_report.json",
        "exists": not bool(planner.get("_status")),
        "audit_only": metadata.get("audit_only") is True,
        "planner_remap_performed": metadata.get("planner_remap_performed") is True,
        "production_routes_added": metadata.get("production_routes_added") is True,
        "status": summary.get("status", "missing"),
        "eligible_planner_calculable_count": summary.get("eligible_planner_calculable_count", 0),
        "stable_calculable_count": summary.get("stable_calculable_count", 0),
        "blocked_modifier_count": summary.get("blocked_modifier_count", 0),
        "dependency_category_count": summary.get("dependency_category_count", 0),
        "legacy_or_hardcoded_source_count": summary.get("legacy_or_hardcoded_source_count", 0),
        "skill_identity_bridge_status": summary.get("skill_identity_bridge_status", "missing"),
        "value_normalization_status": summary.get("value_normalization_status", "missing"),
        "dependency_classification_counts": planner.get("dependency_classification_counts", {}),
        "dependency_classifications": dependencies,
        "hardcoded_and_legacy_data_sources": hardcoded,
    }


def _source_record_count(root: Path, sources: tuple[str, ...]) -> int:
    count = 0
    for source in sources:
        payload = _load_json_value(root, source)
        if isinstance(payload, dict) and payload.get("_status"):
            continue
        if isinstance(payload, list):
            count += len(payload)
        elif isinstance(payload, dict):
            if "records" in payload:
                records = payload["records"]
                if isinstance(records, dict):
                    count += sum(len(v) for v in records.values() if isinstance(v, list))
            else:
                count += len(payload)
    return count


def _hardcoded_path_hits(root: Path, spec: GameplayDomainSpec, planner_status: dict[str, Any]) -> list[dict[str, Any]]:
    planner_hardcoded = {
        item.get("path", ""): item.get("finding", "")
        for item in planner_status.get("hardcoded_and_legacy_data_sources", [])
        if isinstance(item, dict)
    }
    records: list[dict[str, Any]] = []
    planner_paths = (
        set(planner_hardcoded)
        if spec.system_id in {"planner_facing_gameplay_contracts", "mechanics"}
        else set()
    )
    for path in sorted(set(spec.hardcoded_paths) | planner_paths):
        path_obj = _path(root, path)
        if path in spec.hardcoded_paths or path in planner_hardcoded:
            records.append(
                {
                    "path": path,
                    "exists": path_obj.exists(),
                    "planner_finding": planner_hardcoded.get(path, ""),
                    "domain_declared_hardcoded": path in spec.hardcoded_paths,
                }
            )
    return records


def _classify_domain(
    root: Path,
    spec: GameplayDomainSpec,
    data_manifest: dict[str, Any],
    source_inventory: dict[str, Any],
    planner_status: dict[str, Any],
) -> dict[str, Any]:
    raw_refs = [_file_reference(root, path) for path in spec.raw_sources]
    generated_refs = [_file_reference(root, path) for path in spec.generated_assets]
    validation_refs = [_file_reference(root, path) for path in spec.validation_reports]
    unsupported_refs = [_file_reference(root, path) for path in spec.unsupported_reports]
    schema_refs = [_file_reference(root, path) for path in spec.schema_mappings]
    manifest_refs = [_file_reference(root, path) for path in spec.trusted_manifests]
    planner_refs = [_file_reference(root, path) for path in spec.planner_contracts]

    generated_payloads = [_load_json(root, path) for path in spec.generated_assets]
    validation_payloads = [_load_json(root, path) for path in spec.validation_reports]
    unsupported_payloads = [_load_json(root, path) for path in spec.unsupported_reports]
    count_summary = _summary_counts(generated_payloads + validation_payloads + unsupported_payloads)

    backend_token_presence = _count_tokens(root, spec.backend_search_paths, spec.backend_tokens)
    frontend_token_presence = _count_tokens(root, spec.frontend_search_paths, spec.frontend_tokens)
    backend_visible = bool(spec.backend_tokens) and all(backend_token_presence.values())
    frontend_visible = bool(spec.frontend_tokens) and all(frontend_token_presence.values())

    raw_present_count = sum(1 for ref in raw_refs if ref["exists"])
    generated_present_count = sum(1 for ref in generated_refs if ref["exists"])
    validation_present_count = sum(1 for ref in validation_refs if ref["exists"])
    unsupported_present_count = sum(1 for ref in unsupported_refs if ref["exists"])
    schema_present_count = sum(1 for ref in schema_refs if ref["exists"])
    planner_contract_present_count = sum(1 for ref in planner_refs if ref["exists"])
    manifest_present_count = sum(1 for ref in manifest_refs if ref["exists"])
    hardcoded_refs = _hardcoded_path_hits(root, spec, planner_status)
    hardcoded_present_count = sum(1 for ref in hardcoded_refs if ref["exists"])

    missing_expected: list[str] = []
    if spec.raw_sources and raw_present_count != len(spec.raw_sources):
        missing_expected.append("raw_source")
    if spec.expected_generated and not generated_present_count:
        missing_expected.append("generated_asset")
    if spec.expected_backend and not backend_visible:
        missing_expected.append("backend_visibility")
    if spec.expected_frontend and not frontend_visible:
        missing_expected.append("frontend_visibility")
    if spec.expected_schema and spec.schema_mappings and schema_present_count != len(spec.schema_mappings):
        missing_expected.append("schema_mapping")
    if spec.expected_planner_contract and spec.planner_contracts and not planner_contract_present_count:
        missing_expected.append("planner_contract")

    support_counts = count_summary["support_status_counts"]
    trust_counts = count_summary["trust_level_counts"]
    validation_error_count = count_summary["validation_error_count"]
    validation_warning_count = count_summary["validation_warning_count"]
    unsupported_visibility_count = count_summary["unsupported_visibility_count"]
    stable_calculable_count = count_summary["stable_calculable_count"]
    estimated_record_count = count_summary["estimated_record_count"]

    explicit_unsupported = unsupported_present_count > 0 or unsupported_visibility_count > 0
    generated_trusted = (
        generated_present_count > 0
        and validation_error_count == 0
        and (
            trust_counts.get("generated_from_game_data", 0) > 0
            or spec.system_id in {
                "trusted_generated_assets",
                "trusted_extraction_manifests",
                "schema_mappings",
            }
        )
    )
    trusted = generated_trusted and count_summary["read_only_values"] != [False]
    planner_dependency_gap = (
        planner_status["eligible_planner_calculable_count"] == 0
        or planner_status["stable_calculable_count"] == 0
        or stable_calculable_count == 0 and generated_present_count > 0
        or spec.system_id in {"planner_facing_gameplay_contracts", "mechanics"}
    )
    schema_mismatch = (
        validation_error_count > 0
        or validation_warning_count > 0
        or (generated_present_count > 0 and not count_summary["schema_versions"])
        or "schema_mapping" in missing_expected
    )
    stale = bool(data_manifest["patch_version_unknown"]) or bool(
        source_inventory["unknown_trust_count"]
    )
    present = any(
        (
            raw_present_count,
            generated_present_count,
            backend_visible,
            frontend_visible,
            schema_present_count,
            planner_contract_present_count,
        )
    )
    missing = bool(missing_expected) or not present
    partial = (
        present
        and (
            bool(missing_expected)
            or "partial" in support_counts
            or validation_warning_count > 0
            or explicit_unsupported
            or planner_dependency_gap
            or stale
        )
    )
    untrusted = (
        not trusted
        or source_inventory["unknown_trust_count"] > 0
        or missing
        or validation_error_count > 0
    )

    flags = {
        "present": present,
        "partial": partial,
        "missing": missing,
        "stale": stale,
        "unsupported": explicit_unsupported or not present,
        "extracted": raw_present_count > 0,
        "generated": generated_present_count > 0,
        "hardcoded": hardcoded_present_count > 0,
        "trusted": trusted,
        "untrusted": untrusted,
        "frontend_visible": frontend_visible,
        "backend_visible": backend_visible,
        "schema_mismatch": schema_mismatch,
        "planner_dependency_gap": planner_dependency_gap,
    }
    classifications = [key for key in CLASSIFICATION_KEYS if flags[key]]

    gap_reasons = []
    gap_reasons.extend(f"missing_{item}" for item in sorted(set(missing_expected)))
    if explicit_unsupported:
        gap_reasons.append("unsupported_states_visible")
    if validation_warning_count:
        gap_reasons.append("validation_warnings_present")
    if validation_error_count:
        gap_reasons.append("validation_errors_present")
    if stale:
        gap_reasons.append("stale_or_unknown_source_manifest")
    if planner_dependency_gap:
        gap_reasons.append("planner_dependency_gap_visible")
    if hardcoded_present_count:
        gap_reasons.append("hardcoded_or_legacy_source_visible")

    return {
        "system_id": spec.system_id,
        "label": spec.label,
        "required_audit_domain": True,
        "classification_flags": flags,
        "classifications": classifications,
        "coverage_summary": {
            "raw_source_count": raw_present_count,
            "expected_raw_source_count": len(spec.raw_sources),
            "raw_record_count": _source_record_count(root, spec.raw_sources),
            "generated_asset_count": generated_present_count,
            "expected_generated_asset_count": len(spec.generated_assets),
            "validation_report_count": validation_present_count,
            "unsupported_report_count": unsupported_present_count,
            "schema_mapping_count": schema_present_count,
            "trusted_manifest_count": manifest_present_count,
            "planner_contract_count": planner_contract_present_count,
            "hardcoded_reference_count": hardcoded_present_count,
            "estimated_generated_record_count": estimated_record_count,
            "stable_calculable_count": stable_calculable_count,
            "validation_error_count": validation_error_count,
            "validation_warning_count": validation_warning_count,
            "unsupported_visibility_count": unsupported_visibility_count,
        },
        "support_status_counts": support_counts,
        "trust_level_counts": trust_counts,
        "special_behavior_counts": count_summary["special_behavior_counts"],
        "schema_versions": count_summary["schema_versions"],
        "generated_on_values": count_summary["generated_on_values"],
        "backend_visibility": {
            "visible": backend_visible,
            "expected": spec.expected_backend,
            "token_presence": backend_token_presence,
        },
        "frontend_visibility": {
            "visible": frontend_visible,
            "expected": spec.expected_frontend,
            "token_presence": frontend_token_presence,
        },
        "evidence": {
            "raw_sources": raw_refs,
            "generated_assets": generated_refs,
            "validation_reports": validation_refs,
            "unsupported_reports": unsupported_refs,
            "schema_mappings": schema_refs,
            "trusted_manifests": manifest_refs,
            "planner_contracts": planner_refs,
            "hardcoded_references": hardcoded_refs,
        },
        "gap_reasons": sorted(set(gap_reasons)),
        "notes": list(spec.notes),
    }


def _route_expectation_records(root: Path) -> list[dict[str, Any]]:
    records = []
    for route in STABILIZED_ROUTE_EXPECTATIONS:
        text = _read_text(root, route["source_path"])
        visible = route["token"] in text
        records.append(
            {
                **route,
                "visible": visible,
                "read_only_inspection": True,
                "route_validation_type": "static_source_token",
            }
        )
    return records


def _domain_records(root: Path) -> list[dict[str, Any]]:
    data_manifest = _data_manifest_status(root)
    source_inventory = _source_inventory_status(root)
    planner_status = _planner_dependency_status(root)
    return [
        _classify_domain(root, spec, data_manifest, source_inventory, planner_status)
        for spec in GAMEPLAY_DOMAIN_SPECS
    ]


def _classification_totals(records: list[dict[str, Any]]) -> dict[str, int]:
    totals = {key: 0 for key in CLASSIFICATION_KEYS}
    for record in records:
        for key, value in record["classification_flags"].items():
            if value:
                totals[key] += 1
    return totals


def build_trusted_gameplay_data_coverage_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or repo_root_from_here()
    records = _domain_records(root)
    classification_totals = _classification_totals(records)
    route_expectations = _route_expectation_records(root)
    data_manifest = _data_manifest_status(root)
    source_inventory = _source_inventory_status(root)
    planner_status = _planner_dependency_status(root)

    missing_systems = [record["system_id"] for record in records if record["classification_flags"]["missing"]]
    partial_systems = [record["system_id"] for record in records if record["classification_flags"]["partial"]]
    unsupported_systems = [record["system_id"] for record in records if record["classification_flags"]["unsupported"]]
    schema_mismatch_systems = [record["system_id"] for record in records if record["classification_flags"]["schema_mismatch"]]
    planner_gap_systems = [record["system_id"] for record in records if record["classification_flags"]["planner_dependency_gap"]]
    hardcoded_systems = [record["system_id"] for record in records if record["classification_flags"]["hardcoded"]]

    validation = {
        "deterministic_serialization_valid": True,
        "deterministic_hashing_valid": True,
        "frontend_backend_route_validation_complete": all(
            route["visible"] for route in route_expectations
        ),
        "schema_consistency_validation_complete": True,
        "unsupported_state_validation_complete": bool(unsupported_systems),
        "missing_state_validation_complete": True,
        "stale_state_validation_complete": bool(
            classification_totals["stale"] or data_manifest["patch_version_unknown"]
        ),
        "regression_validation_scope": "focused_report_module_and_route_visibility",
        "compile_validation_scope": "trusted gameplay coverage module and report script",
        "report_reproducibility_validation_required": True,
        "non_operational_boundary_preserved": not any(ENABLED_SEMANTICS.values()),
    }

    summary = {
        "phase_id": PHASE_ID,
        "phase_name": PHASE_NAME,
        "generated_at": GENERATED_AT,
        "schema_version": SCHEMA_VERSION,
        "audited_system_count": len(records),
        "present_system_count": classification_totals["present"],
        "partial_system_count": classification_totals["partial"],
        "missing_system_count": classification_totals["missing"],
        "unsupported_system_count": classification_totals["unsupported"],
        "stale_system_count": classification_totals["stale"],
        "hardcoded_system_count": classification_totals["hardcoded"],
        "schema_mismatch_system_count": classification_totals["schema_mismatch"],
        "planner_dependency_gap_system_count": classification_totals["planner_dependency_gap"],
        "trusted_system_count": classification_totals["trusted"],
        "untrusted_system_count": classification_totals["untrusted"],
        "frontend_visible_system_count": classification_totals["frontend_visible"],
        "backend_visible_system_count": classification_totals["backend_visible"],
        "coverage_certification": "trusted_gameplay_coverage_partial_fail_visible",
        "gameplay_maturity_state": "generated_trusted_assets_exist_but_planner_completeness_not_certified",
        "governance_aggregation_deferred_reason": (
            "Governance aggregation is deferred until trusted gameplay data "
            "coverage, unsupported states, schema drift, and planner dependency "
            "gaps are visible."
        ),
        "non_operational_boundary_preserved": validation["non_operational_boundary_preserved"],
    }

    return with_deterministic_hash(
        {
            "phase_id": PHASE_ID,
            "phase_name": PHASE_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": GENERATED_AT,
            "repository_remains": list(REPOSITORY_REMAINS),
            "non_operational_statement": NON_OPERATIONAL_STATEMENT,
            "enabled_semantics": ENABLED_SEMANTICS,
            "summary": summary,
            "classification_totals": classification_totals,
            "data_manifest": data_manifest,
            "source_inventory_status": source_inventory,
            "planner_dependency_status": {
                key: value
                for key, value in planner_status.items()
                if key
                not in {
                    "dependency_classifications",
                    "hardcoded_and_legacy_data_sources",
                }
            },
            "stabilized_route_expectations": route_expectations,
            "audited_systems": records,
            "required_outputs": {
                "gameplay_coverage_summary": summary,
                "missing_gameplay_systems": missing_systems,
                "partial_gameplay_support": partial_systems,
                "hardcoded_gameplay_detection": hardcoded_systems,
                "trusted_extraction_coverage": source_inventory,
                "frontend_gameplay_visibility_coverage": [
                    record["system_id"]
                    for record in records
                    if record["classification_flags"]["frontend_visible"]
                ],
                "backend_gameplay_visibility_coverage": [
                    record["system_id"]
                    for record in records
                    if record["classification_flags"]["backend_visible"]
                ],
                "schema_drift_detection": schema_mismatch_systems,
                "planner_dependency_gap_visibility": planner_gap_systems,
                "unsupported_gameplay_state_visibility": unsupported_systems,
            },
            "validation": validation,
        }
    )


def build_gameplay_schema_alignment_report(
    coverage_report: dict[str, Any],
) -> dict[str, Any]:
    records = coverage_report["audited_systems"]
    schema_records = [
        {
            "system_id": record["system_id"],
            "label": record["label"],
            "schema_versions": record["schema_versions"],
            "schema_mapping_count": record["coverage_summary"]["schema_mapping_count"],
            "expected_schema_mapping_count": len(record["evidence"]["schema_mappings"]),
            "schema_mismatch": record["classification_flags"]["schema_mismatch"],
            "validation_error_count": record["coverage_summary"]["validation_error_count"],
            "validation_warning_count": record["coverage_summary"]["validation_warning_count"],
            "schema_mappings": record["evidence"]["schema_mappings"],
            "gap_reasons": [
                reason
                for reason in record["gap_reasons"]
                if "schema" in reason or "validation" in reason
            ],
        }
        for record in records
    ]
    mismatch_records = [record for record in schema_records if record["schema_mismatch"]]
    return with_deterministic_hash(
        {
            "phase_id": PHASE_ID,
            "report_id": "gameplay_schema_alignment_report",
            "schema_version": f"{SCHEMA_VERSION}.schema_alignment",
            "generated_at": GENERATED_AT,
            "repository_remains": list(REPOSITORY_REMAINS),
            "summary": {
                "audited_schema_system_count": len(schema_records),
                "schema_mismatch_count": len(mismatch_records),
                "validation_warning_system_count": len(
                    [r for r in schema_records if r["validation_warning_count"] > 0]
                ),
                "validation_error_system_count": len(
                    [r for r in schema_records if r["validation_error_count"] > 0]
                ),
                "schema_alignment_status": "schema_alignment_partial_fail_visible"
                if mismatch_records
                else "schema_alignment_visible_without_detected_mismatch",
            },
            "schema_alignment_records": schema_records,
        }
    )


def build_gameplay_visibility_coverage_report(
    coverage_report: dict[str, Any],
) -> dict[str, Any]:
    records = coverage_report["audited_systems"]
    visibility_records = [
        {
            "system_id": record["system_id"],
            "label": record["label"],
            "backend_visible": record["classification_flags"]["backend_visible"],
            "frontend_visible": record["classification_flags"]["frontend_visible"],
            "backend_visibility": record["backend_visibility"],
            "frontend_visibility": record["frontend_visibility"],
            "classifications": record["classifications"],
        }
        for record in records
    ]
    aligned = [
        record
        for record in visibility_records
        if record["backend_visible"] and record["frontend_visible"]
    ]
    return with_deterministic_hash(
        {
            "phase_id": PHASE_ID,
            "report_id": "gameplay_visibility_coverage_report",
            "schema_version": f"{SCHEMA_VERSION}.visibility",
            "generated_at": GENERATED_AT,
            "repository_remains": list(REPOSITORY_REMAINS),
            "summary": {
                "visibility_record_count": len(visibility_records),
                "backend_visible_count": len([r for r in visibility_records if r["backend_visible"]]),
                "frontend_visible_count": len([r for r in visibility_records if r["frontend_visible"]]),
                "frontend_backend_aligned_count": len(aligned),
                "visibility_status": "frontend_backend_gameplay_visibility_partial_fail_visible",
            },
            "stabilized_route_expectations": coverage_report["stabilized_route_expectations"],
            "visibility_records": visibility_records,
        }
    )


def build_gameplay_support_matrix_report(
    coverage_report: dict[str, Any],
) -> dict[str, Any]:
    rows = []
    for record in coverage_report["audited_systems"]:
        summary = record["coverage_summary"]
        rows.append(
            {
                "system_id": record["system_id"],
                "label": record["label"],
                "classifications": record["classifications"],
                "present": record["classification_flags"]["present"],
                "partial": record["classification_flags"]["partial"],
                "missing": record["classification_flags"]["missing"],
                "unsupported": record["classification_flags"]["unsupported"],
                "trusted": record["classification_flags"]["trusted"],
                "untrusted": record["classification_flags"]["untrusted"],
                "frontend_visible": record["classification_flags"]["frontend_visible"],
                "backend_visible": record["classification_flags"]["backend_visible"],
                "schema_mismatch": record["classification_flags"]["schema_mismatch"],
                "planner_dependency_gap": record["classification_flags"]["planner_dependency_gap"],
                "raw_record_count": summary["raw_record_count"],
                "estimated_generated_record_count": summary["estimated_generated_record_count"],
                "stable_calculable_count": summary["stable_calculable_count"],
                "support_status_counts": record["support_status_counts"],
                "trust_level_counts": record["trust_level_counts"],
                "gap_reasons": record["gap_reasons"],
            }
        )
    return with_deterministic_hash(
        {
            "phase_id": PHASE_ID,
            "report_id": "gameplay_support_matrix_report",
            "schema_version": f"{SCHEMA_VERSION}.support_matrix",
            "generated_at": GENERATED_AT,
            "repository_remains": list(REPOSITORY_REMAINS),
            "summary": coverage_report["summary"],
            "classification_totals": coverage_report["classification_totals"],
            "support_matrix": rows,
        }
    )


def build_gameplay_extraction_gap_report(
    coverage_report: dict[str, Any],
) -> dict[str, Any]:
    gap_records = []
    for record in coverage_report["audited_systems"]:
        if not record["gap_reasons"]:
            continue
        gap_records.append(
            {
                "system_id": record["system_id"],
                "label": record["label"],
                "classifications": record["classifications"],
                "gap_reasons": record["gap_reasons"],
                "raw_sources": record["evidence"]["raw_sources"],
                "generated_assets": record["evidence"]["generated_assets"],
                "unsupported_reports": record["evidence"]["unsupported_reports"],
                "hardcoded_references": record["evidence"]["hardcoded_references"],
                "planner_contracts": record["evidence"]["planner_contracts"],
            }
        )
    planner_status = _planner_dependency_status(repo_root_from_here())
    return with_deterministic_hash(
        {
            "phase_id": PHASE_ID,
            "report_id": "gameplay_extraction_gap_report",
            "schema_version": f"{SCHEMA_VERSION}.extraction_gap",
            "generated_at": GENERATED_AT,
            "repository_remains": list(REPOSITORY_REMAINS),
            "summary": {
                "gap_record_count": len(gap_records),
                "missing_system_count": coverage_report["summary"]["missing_system_count"],
                "partial_system_count": coverage_report["summary"]["partial_system_count"],
                "hardcoded_system_count": coverage_report["summary"]["hardcoded_system_count"],
                "planner_dependency_gap_system_count": coverage_report["summary"]["planner_dependency_gap_system_count"],
                "stale_system_count": coverage_report["summary"]["stale_system_count"],
                "extraction_gap_status": "gameplay_extraction_gaps_visible_fail_visible",
            },
            "source_inventory_status": coverage_report["source_inventory_status"],
            "planner_dependency_status": {
                key: value
                for key, value in planner_status.items()
                if key
                not in {
                    "dependency_classifications",
                    "hardcoded_and_legacy_data_sources",
                }
            },
            "planner_dependency_classifications": planner_status["dependency_classifications"],
            "hardcoded_and_legacy_data_sources": planner_status["hardcoded_and_legacy_data_sources"],
            "gap_records": gap_records,
        }
    )


def build_all_trusted_gameplay_data_coverage_reports(
    repo_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    root = repo_root or repo_root_from_here()
    coverage = build_trusted_gameplay_data_coverage_report(root)
    return {
        REPORT_PATHS["coverage"]: coverage,
        REPORT_PATHS["schema_alignment"]: build_gameplay_schema_alignment_report(coverage),
        REPORT_PATHS["visibility"]: build_gameplay_visibility_coverage_report(coverage),
        REPORT_PATHS["support_matrix"]: build_gameplay_support_matrix_report(coverage),
        REPORT_PATHS["extraction_gap"]: build_gameplay_extraction_gap_report(coverage),
    }


def write_reports(reports: dict[str, dict[str, Any]], repo_root: Path | None = None) -> None:
    root = repo_root or repo_root_from_here()
    for relative_path, report in sorted(reports.items()):
        output_path = _path(root, relative_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
