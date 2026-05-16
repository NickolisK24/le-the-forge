from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    DEPENDENCY_BLOCKED,
    DEPENDENCY_ENVIRONMENT_MISMATCH,
    DEPENDENCY_INCOMPATIBLE,
    DEPENDENCY_LINEAGE_GAP,
    DEPENDENCY_MISSING,
    DEPENDENCY_PROHIBITED,
    DEPENDENCY_REQUIRES_MANUAL_REVIEW,
    DEPENDENCY_SATISFIED,
    DEPENDENCY_UNSUPPORTED,
    default_governance_dependency_contract,
    default_governance_dependency_resolution_input,
    export_governance_dependency_resolution_result,
    hash_dependency_resolution_result,
    resolve_governance_dependency,
    serialize_governance_dependency_resolution_result,
)
from scripts.report_v3_5_governance_dependency_resolution import (
    build_v3_5_governance_dependency_resolution_report,
)


def _base_input():
    return default_governance_dependency_resolution_input()


def _base_contract():
    return default_governance_dependency_contract()


def _result(source=None):
    return resolve_governance_dependency(source or _base_input())


def _export(source=None):
    return export_governance_dependency_resolution_result(_result(source))


def test_deterministic_dependency_classification():
    first = _export()
    second = _export()

    assert first["dependency_status"] == DEPENDENCY_SATISFIED
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["planning_only"] is True


def test_stable_serialization():
    first = _result()
    second = _result()

    assert serialize_governance_dependency_resolution_result(first) == serialize_governance_dependency_resolution_result(second)


def test_stable_deterministic_hash_output():
    first = _result()
    second = _result()

    assert hash_dependency_resolution_result(first) == hash_dependency_resolution_result(second)


def test_satisfied_evidence_preservation():
    result = _export()

    assert result["satisfied_evidence"] == sorted(_base_contract().required_evidence_ids)
    assert result["missing_evidence"] == []


def test_missing_evidence_preservation():
    contract = _base_contract()
    source = replace(_base_input(), contract=replace(contract, provided_evidence_ids=contract.provided_evidence_ids[:-1]))
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_MISSING
    assert result["missing_evidence"] == ["v3_5_orchestration_readiness_evaluation"]


def test_blocker_ordering_stability():
    contract = replace(
        _base_contract(),
        provided_evidence_ids=(),
        blocker_reasons=("z_blocker", "a_blocker"),
    )
    source = replace(_base_input(), contract=contract)
    first = _export(source)["blockers"]
    second = _export(source)["blockers"]

    assert [row["blocker_id"] for row in first] == [row["blocker_id"] for row in second]
    assert [row["deterministic_rank"] for row in first] == sorted(row["deterministic_rank"] for row in first)


def test_blocked_dependency_visibility():
    source = replace(_base_input(), contract=replace(_base_contract(), blocker_reasons=("governance_blocker_visible",)))
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_BLOCKED
    assert result["blockers"][0]["blocker_id"] == "blocked:governance_blocker_visible"


def test_unsupported_reason_preservation():
    source = replace(
        _base_input(),
        contract=replace(
            _base_contract(),
            dependency_supported=False,
            unsupported_reasons=("unsupported_dependency_scope",),
        ),
    )
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_UNSUPPORTED
    assert result["unsupported_reasons"] == ["dependency_not_supported", "unsupported_dependency_scope"]


def test_prohibited_reason_preservation():
    source = replace(_base_input(), contract=replace(_base_contract(), dependency_domain="runtime_execution"))
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_PROHIBITED
    assert result["prohibited_reasons"] == ["prohibited_domain:runtime_execution"]


def test_manual_review_preservation():
    source = replace(
        _base_input(),
        contract=replace(_base_contract(), manual_review_reasons=("dependency_owner_review_required",)),
    )
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_REQUIRES_MANUAL_REVIEW
    assert result["manual_review_reasons"] == ["dependency_owner_review_required"]


def test_compatibility_failure_visibility():
    source = replace(_base_input(), contract=replace(_base_contract(), compatibility_verified=False))
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_INCOMPATIBLE
    assert result["compatibility_failures"] == ["compatibility_not_verified"]


def test_environment_mismatch_visibility():
    source = replace(
        _base_input(),
        contract=replace(_base_contract(), environment_evidence_ids=(), environment_verified=False),
    )
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_ENVIRONMENT_MISMATCH
    assert "environment_not_verified" in result["environment_mismatches"]
    assert "missing:non_production_environment_isolated" in result["environment_mismatches"]


def test_lineage_gap_visibility():
    contract = _base_contract()
    source = replace(
        _base_input(),
        contract=replace(
            contract,
            lineage=replace(
                contract.lineage,
                replay_lineage_references=(),
                rollback_lineage_references=(),
            ),
        ),
    )
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_LINEAGE_GAP
    assert result["lineage_gaps"] == ["replay_lineage_references", "rollback_lineage_references"]


def test_cross_scope_lineage_propagation_visibility():
    contract = _base_contract()
    source = replace(
        _base_input(),
        contract=replace(
            contract,
            lineage=replace(
                contract.lineage,
                upstream_dependency_ids=("v3_4_closeout_and_v3_5_readiness", "v3_5_governance_consumption_contract"),
                downstream_dependency_ids=(
                    "v3_5_orchestration_readiness_evaluation",
                    "v3_5_governance_dependency_resolution",
                ),
            ),
        ),
    )
    result = _export(source)
    lineage = result["lineage_propagation"]

    assert result["dependency_status"] == DEPENDENCY_SATISFIED
    assert lineage["upstream_dependency_ids"] == [
        "v3_4_closeout_and_v3_5_readiness",
        "v3_5_governance_consumption_contract",
    ]
    assert lineage["downstream_dependency_ids"] == [
        "v3_5_governance_dependency_resolution",
        "v3_5_orchestration_readiness_evaluation",
    ]
    assert lineage["non_executable"] is True
    assert lineage["external_graph_lookup_enabled"] is False
    assert lineage["automatic_repair_enabled"] is False


def test_multiple_blocker_aggregation():
    contract = _base_contract()
    source = replace(
        _base_input(),
        contract=replace(
            contract,
            dependency_domain="runtime_execution",
            provided_evidence_ids=(),
            blocker_reasons=("governance_blocker_visible",),
            dependency_supported=False,
            unsupported_reasons=("unsupported_dependency_scope",),
            compatibility_verified=False,
            environment_evidence_ids=(),
            environment_verified=False,
            manual_review_reasons=("dependency_owner_review_required",),
            lineage=replace(contract.lineage, replay_lineage_references=()),
        ),
    )
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_PROHIBITED
    assert result["missing_evidence"]
    assert result["unsupported_reasons"]
    assert result["prohibited_reasons"] == ["prohibited_domain:runtime_execution"]
    assert result["manual_review_reasons"]
    assert result["compatibility_failures"]
    assert result["environment_mismatches"]
    assert result["lineage_gaps"]
    assert len(result["blockers"]) >= 8


def test_non_execution_guarantees():
    result = _export()

    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["audit_log_writing_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["external_dependency_fetching_enabled"] is False
    assert result["automatic_remediation_enabled"] is False


def test_prohibited_behavior_is_not_exposed():
    source = replace(
        _base_input(),
        contract=replace(_base_contract(), external_dependency_fetching_enabled=True, automatic_remediation_enabled=True),
    )
    result = _export(source)

    assert result["dependency_status"] == DEPENDENCY_PROHIBITED
    assert result["external_dependency_fetching_enabled"] is False
    assert result["automatic_remediation_enabled"] is False
    assert any(
        row["blocker_id"] == "prohibited:execution_fetch_mutation_or_remediation_behavior_detected"
        for row in result["blockers"]
    )


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_governance_dependency_resolution_report()
    second = build_v3_5_governance_dependency_resolution_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_dependency_resolution_status"] == DEPENDENCY_SATISFIED
    assert distribution[DEPENDENCY_SATISFIED] == 2
    assert distribution[DEPENDENCY_MISSING] == 1
    assert distribution[DEPENDENCY_BLOCKED] == 1
    assert distribution[DEPENDENCY_UNSUPPORTED] == 1
    assert distribution[DEPENDENCY_PROHIBITED] == 2
    assert distribution[DEPENDENCY_REQUIRES_MANUAL_REVIEW] == 1
    assert distribution[DEPENDENCY_INCOMPATIBLE] == 1
    assert distribution[DEPENDENCY_ENVIRONMENT_MISMATCH] == 1
    assert distribution[DEPENDENCY_LINEAGE_GAP] == 1


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_governance_dependency_resolution_report()["explicit_non_execution_guarantees"]

    assert guarantees["runtime_execution_enabled"] is False
    assert guarantees["orchestration_execution_enabled"] is False
    assert guarantees["routing_behavior_enabled"] is False
    assert guarantees["mutation_behavior_enabled"] is False
    assert guarantees["audit_log_writing_enabled"] is False
    assert guarantees["production_consumption_enabled"] is False
    assert guarantees["external_dependency_fetching_enabled"] is False
    assert guarantees["automatic_remediation_enabled"] is False
