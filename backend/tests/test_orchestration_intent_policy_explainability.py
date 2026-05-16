from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_intent_policy_explainability import (
    explain_orchestration_intent_policy_mappings,
    export_orchestration_intent_policy_mapping_explainability_result,
    hash_orchestration_intent_policy_mapping_explainability_result,
    serialize_orchestration_intent_policy_mapping_explainability_result,
)
from app.runtime_orchestration.orchestration_intent_policy_mapper import map_orchestration_intent_policies
from app.runtime_orchestration.orchestration_intent_policy_mapping_models import (
    MAPPING_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    MAPPING_EXPLAINABILITY_STABLE,
    OrchestrationIntentPolicyMappingInput,
)
from app.runtime_orchestration.orchestration_intent_policy_mapping_registry import (
    build_orchestration_intent_policy_mapping_registry,
    default_orchestration_intent_policy_mapping_registry,
)


def _registry():
    return default_orchestration_intent_policy_mapping_registry()


def _explain(registry=None, mapping=None):
    source_registry = registry or _registry()
    source_mapping = mapping or map_orchestration_intent_policies(
        OrchestrationIntentPolicyMappingInput(mapping_registry=source_registry)
    )
    return explain_orchestration_intent_policy_mappings(source_registry, source_mapping)


def _export(result=None):
    return export_orchestration_intent_policy_mapping_explainability_result(result or _explain())


def _record(registry, mapping_id):
    return next(record for record in registry.records if record.identifier.mapping_id == mapping_id)


def _replace_record(registry, mapping_id, replacement):
    return build_orchestration_intent_policy_mapping_registry(
        tuple(
            replacement if record.identifier.mapping_id == mapping_id else record
            for record in registry.records
        )
    )


def test_mapping_explainability_generates_stable_visibility():
    result = _export()

    assert result["mapping_explainability_status"] == MAPPING_EXPLAINABILITY_STABLE
    assert result["supported_explanation_count"] == 7
    assert result["unsupported_explanation_count"] == 1
    assert result["prohibited_explanation_count"] == 1
    assert result["policy_applicability_visibility_count"] == 31
    assert result["governance_boundary_visibility_count"] == 35
    assert result["compatibility_domain_visibility_count"] == 10
    assert result["dependency_domain_visibility_count"] == 5
    assert result["blocker_domain_visibility_count"] == 11
    assert result["unsupported_domain_visibility_count"] == 4
    assert result["prohibited_domain_visibility_count"] == 5
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["mapping_execution_enabled"] is False


def test_mapping_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_intent_policy_mapping_explainability_result(first) == serialize_orchestration_intent_policy_mapping_explainability_result(second)
    assert hash_orchestration_intent_policy_mapping_explainability_result(first) == hash_orchestration_intent_policy_mapping_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_compatibility_check_explains_policy_applicability():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["mapping_id"] == "v3_6.mapping.compatibility-check")

    assert "v3_6.policy.modeling.allowed" in record["policy_applicability_visibility"]
    assert "v3_6.policy.governance-boundary.allowed" in record["policy_applicability_visibility"]
    assert "compatibility_matrix" in record["compatibility_domain_visibility"]
    assert "compatibility_pre_analysis_only" in record["governance_boundary_visibility"]
    assert "compatibility-check intent maps to policy modeling before compatibility evaluation" in record["mapping_rationale_visibility"]
    assert "v3_6.mapping.compatibility-check.replay" in record["provenance_visibility"]


def test_unsupported_and_prohibited_mappings_explain_fail_visible_domains():
    result = _export()
    unsupported = next(item for item in result["explanation_records"] if item["mapping_id"] == "v3_6.mapping.unsupported-domain")
    prohibited = next(item for item in result["explanation_records"] if item["mapping_id"] == "v3_6.mapping.prohibited-domain")

    assert unsupported["mapping_state"] == "mapping_unsupported"
    assert "v3_6.policy.autonomy.unsupported" in unsupported["policy_applicability_visibility"]
    assert "autonomous_orchestration" in unsupported["unsupported_domain_visibility"]
    assert "unsupported_domain_blocker" in unsupported["blocker_domain_visibility"]
    assert prohibited["mapping_state"] == "mapping_prohibited"
    assert "v3_6.policy.execution.prohibited" in prohibited["policy_applicability_visibility"]
    assert "orchestration_execution" in prohibited["prohibited_domain_visibility"]
    assert "prohibited_execution_blocker" in prohibited["blocker_domain_visibility"]


def test_explainability_gap_is_fail_visible_for_unexplained_mapping():
    registry = _registry()
    target = _record(registry, "v3_6.mapping.informational")
    changed = replace(target, mapping_rationale=())
    changed_registry = _replace_record(registry, target.identifier.mapping_id, changed)
    mapping = map_orchestration_intent_policies(
        OrchestrationIntentPolicyMappingInput(mapping_registry=changed_registry)
    )
    result = _export(_explain(changed_registry, mapping))
    record = next(item for item in result["explanation_records"] if item["mapping_id"] == target.identifier.mapping_id)

    assert result["mapping_explainability_status"] == MAPPING_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    assert record["explanation_status"] == MAPPING_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
