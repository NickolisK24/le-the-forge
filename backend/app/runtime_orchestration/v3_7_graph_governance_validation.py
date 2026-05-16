"""Fail-visible validation for v3.7 graph governance boundary intelligence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_governance_explainability import (
    V37_GOVERNANCE_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_governance,
)
from .v3_7_graph_governance_models import (
    V37_DOMAIN_PROHIBITED,
    V37_DOMAIN_UNSUPPORTED,
    V37_EDGE_PROHIBITED_STRUCTURAL,
    V37_EDGE_UNSUPPORTED_STRUCTURAL,
    V37_GOVERNANCE_VISIBILITY_VISIBLE,
    V37GraphGovernanceMap,
    validate_v3_7_governance_hash_stability,
    validate_v3_7_governance_serialization_stability,
    hash_v3_7_governance_map,
)
from .v3_7_graph_governance_provenance import (
    V37_GOVERNANCE_PROVENANCE_PRESERVED,
    audit_v3_7_graph_governance_provenance,
)


V37_GOVERNANCE_VALIDATION_STABLE = "v3_7_graph_governance_validation_stable"
V37_GOVERNANCE_VALIDATION_BLOCKED = "v3_7_graph_governance_validation_blocked"
V37_GOVERNANCE_PROHIBITED_RELATIONSHIP_VISIBLE = (
    "v3_7_graph_governance_prohibited_relationship_visible"
)
V37_GOVERNANCE_UNSUPPORTED_RELATIONSHIP_VISIBLE = (
    "v3_7_graph_governance_unsupported_relationship_visible"
)
V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_NODE_RELATIONSHIP = (
    "v3_7_graph_governance_blocked_by_prohibited_node_relationship"
)
V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_EDGE_RELATIONSHIP = (
    "v3_7_graph_governance_blocked_by_prohibited_edge_relationship"
)
V37_GOVERNANCE_BLOCKED_BY_UNSUPPORTED_DOMAIN_CONNECTION = (
    "v3_7_graph_governance_blocked_by_unsupported_domain_connection"
)
V37_GOVERNANCE_BLOCKED_BY_CONTINUITY_VIOLATION = (
    "v3_7_graph_governance_blocked_by_continuity_violation"
)
V37_GOVERNANCE_BLOCKED_BY_INCOMPATIBLE_CLASSIFICATION = (
    "v3_7_graph_governance_blocked_by_incompatible_classification"
)
V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_CROSS_DOMAIN_STRUCTURE = (
    "v3_7_graph_governance_blocked_by_prohibited_cross_domain_structure"
)
V37_GOVERNANCE_BLOCKED_BY_UNSUPPORTED_CONFIGURATION = (
    "v3_7_graph_governance_blocked_by_unsupported_configuration"
)
V37_GOVERNANCE_BLOCKED_BY_MISSING_METADATA = "v3_7_graph_governance_blocked_by_missing_metadata"
V37_GOVERNANCE_BLOCKED_BY_PROVENANCE_DISCONTINUITY = (
    "v3_7_graph_governance_blocked_by_provenance_discontinuity"
)
V37_GOVERNANCE_BLOCKED_BY_EXPLAINABILITY_DISCONTINUITY = (
    "v3_7_graph_governance_blocked_by_explainability_discontinuity"
)
V37_GOVERNANCE_BLOCKED_BY_SERIALIZATION_INSTABILITY = (
    "v3_7_graph_governance_blocked_by_serialization_instability"
)
V37_GOVERNANCE_BLOCKED_BY_HASH_INSTABILITY = "v3_7_graph_governance_blocked_by_hash_instability"
V37_GOVERNANCE_BLOCKED_BY_EXECUTION_CAPABILITY = (
    "v3_7_graph_governance_blocked_by_execution_capability"
)


@dataclass(frozen=True)
class V37GraphGovernanceValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphGovernanceValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    prohibited_relationship_visible_count: int
    unsupported_relationship_visible_count: int
    prohibited_edge_relationship_count: int
    unsupported_edge_relationship_count: int
    missing_metadata_count: int
    governance_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    serialization_stable: bool
    hash_stable: bool
    non_execution_guarantee_preserved: bool
    deterministic_governance_hash: str
    findings: tuple[V37GraphGovernanceValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_governance(
    governance_map: V37GraphGovernanceMap,
) -> V37GraphGovernanceValidationResult:
    findings: list[V37GraphGovernanceValidationFinding] = []
    domain_ids = {domain.domain_id for domain in governance_map.domains}
    domain_classifications = {
        domain.domain_id: domain.domain_classification
        for domain in governance_map.domains
    }
    node_ids = {classification.node_id for classification in governance_map.node_classifications}
    _add_visibility_findings(governance_map, findings)
    _add_metadata_findings(governance_map, findings, domain_ids, domain_classifications)
    _add_relationship_findings(governance_map, findings, node_ids)
    _add_continuity_findings(governance_map, findings)
    _add_non_execution_findings(governance_map, findings)

    serialization = validate_v3_7_governance_serialization_stability(governance_map)
    if not serialization["stable"]:
        findings.append(
            _finding(
                V37_GOVERNANCE_BLOCKED_BY_SERIALIZATION_INSTABILITY,
                "governance_map",
                governance_map.graph_id,
                "governance serialization is unstable",
            )
        )
    hashing = validate_v3_7_governance_hash_stability(governance_map)
    if not hashing["stable"]:
        findings.append(
            _finding(
                V37_GOVERNANCE_BLOCKED_BY_HASH_INSTABILITY,
                "governance_map",
                governance_map.graph_id,
                "governance hash is unstable",
            )
        )

    provenance = audit_v3_7_graph_governance_provenance(governance_map)
    if provenance.provenance_status != V37_GOVERNANCE_PROVENANCE_PRESERVED:
        findings.append(
            _finding(
                V37_GOVERNANCE_BLOCKED_BY_PROVENANCE_DISCONTINUITY,
                "governance_map",
                governance_map.graph_id,
                "governance provenance continuity is incomplete",
            )
        )

    explainability = explain_v3_7_graph_governance(governance_map)
    if explainability.explainability_status != V37_GOVERNANCE_EXPLAINABILITY_STABLE:
        findings.append(
            _finding(
                V37_GOVERNANCE_BLOCKED_BY_EXPLAINABILITY_DISCONTINUITY,
                "governance_map",
                governance_map.graph_id,
                "governance explainability continuity is incomplete",
            )
        )

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    missing_metadata_count = sum(
        1 for finding in findings if finding.status == V37_GOVERNANCE_BLOCKED_BY_MISSING_METADATA
    )
    result = V37GraphGovernanceValidationResult(
        validation_status=(
            V37_GOVERNANCE_VALIDATION_STABLE
            if error_count == 0
            else V37_GOVERNANCE_VALIDATION_BLOCKED
        ),
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        prohibited_relationship_visible_count=sum(
            1 for finding in findings if finding.status == V37_GOVERNANCE_PROHIBITED_RELATIONSHIP_VISIBLE
        ),
        unsupported_relationship_visible_count=sum(
            1 for finding in findings if finding.status == V37_GOVERNANCE_UNSUPPORTED_RELATIONSHIP_VISIBLE
        ),
        prohibited_edge_relationship_count=sum(
            1
            for classification in governance_map.edge_classifications
            if classification.governance_classification == V37_EDGE_PROHIBITED_STRUCTURAL
        ),
        unsupported_edge_relationship_count=sum(
            1
            for classification in governance_map.edge_classifications
            if classification.governance_classification == V37_EDGE_UNSUPPORTED_STRUCTURAL
        ),
        missing_metadata_count=missing_metadata_count,
        governance_continuity_preserved=not _continuity_gaps(governance_map),
        provenance_continuity_preserved=provenance.provenance_status == V37_GOVERNANCE_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=(
            explainability.explainability_status == V37_GOVERNANCE_EXPLAINABILITY_STABLE
        ),
        replay_continuity_preserved=provenance.replay_continuity_preserved,
        rollback_continuity_preserved=provenance.rollback_continuity_preserved,
        serialization_stable=serialization["stable"],
        hash_stable=hashing["stable"],
        non_execution_guarantee_preserved=_non_execution_guarantee_preserved(governance_map),
        deterministic_governance_hash=hash_v3_7_governance_map(governance_map),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(
        result,
        deterministic_validation_hash=hash_v3_7_graph_governance_validation_result(result),
    )


def export_v3_7_graph_governance_validation_finding(
    finding: V37GraphGovernanceValidationFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_governance_validation_result(
    result: V37GraphGovernanceValidationResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_governance_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_governance_validation_result(
    result: V37GraphGovernanceValidationResult,
) -> str:
    return stable_serialize(export_v3_7_graph_governance_validation_result(result))


def hash_v3_7_graph_governance_validation_result(
    result: V37GraphGovernanceValidationResult,
) -> str:
    data = export_v3_7_graph_governance_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphGovernanceValidationFinding:
    return V37GraphGovernanceValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )


def _add_visibility_findings(
    governance_map: V37GraphGovernanceMap,
    findings: list[V37GraphGovernanceValidationFinding],
) -> None:
    for finding in governance_map.findings:
        if finding.visibility_status != V37_GOVERNANCE_VISIBILITY_VISIBLE:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_UNSUPPORTED_CONFIGURATION,
                    finding.subject_type,
                    finding.subject_id,
                    "relationship visibility is missing",
                )
            )
            continue
        status = (
            V37_GOVERNANCE_PROHIBITED_RELATIONSHIP_VISIBLE
            if finding.finding_kind == "prohibited_relationship"
            else V37_GOVERNANCE_UNSUPPORTED_RELATIONSHIP_VISIBLE
        )
        findings.append(
            _finding(
                status,
                finding.subject_type,
                finding.subject_id,
                finding.reason,
                severity="visibility",
            )
        )


def _add_metadata_findings(
    governance_map: V37GraphGovernanceMap,
    findings: list[V37GraphGovernanceValidationFinding],
    domain_ids: set[str],
    domain_classifications: dict[str, str],
) -> None:
    for classification in governance_map.node_classifications:
        if not classification.governance_domain_ids:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_MISSING_METADATA,
                    "node_governance",
                    classification.node_id,
                    "node governance domain metadata is missing",
                )
            )
        if set(classification.governance_domain_ids) - domain_ids:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_INCOMPATIBLE_CLASSIFICATION,
                    "node_governance",
                    classification.node_id,
                    "node references unknown governance domains",
                )
            )
        _add_domain_classification_findings(
            "node_governance",
            classification.node_id,
            classification.governance_domain_ids,
            domain_classifications,
            findings,
        )
    for classification in governance_map.edge_classifications:
        if not classification.governance_domain_ids:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_MISSING_METADATA,
                    "edge_governance",
                    classification.edge_id,
                    "edge governance domain metadata is missing",
                )
            )
        if set(classification.governance_domain_ids) - domain_ids:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_INCOMPATIBLE_CLASSIFICATION,
                    "edge_governance",
                    classification.edge_id,
                    "edge references unknown governance domains",
                )
            )
        _add_domain_classification_findings(
            "edge_governance",
            classification.edge_id,
            classification.governance_domain_ids,
            domain_classifications,
            findings,
        )


def _add_relationship_findings(
    governance_map: V37GraphGovernanceMap,
    findings: list[V37GraphGovernanceValidationFinding],
    node_ids: set[str],
) -> None:
    for classification in governance_map.node_classifications:
        if classification.governance_classification == "prohibited":
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_NODE_RELATIONSHIP,
                    "node_governance",
                    classification.node_id,
                    "node governance classification is prohibited",
                )
            )
    for classification in governance_map.edge_classifications:
        if classification.source_node_id not in node_ids or classification.target_node_id not in node_ids:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_INCOMPATIBLE_CLASSIFICATION,
                    "edge_governance",
                    classification.edge_id,
                    "edge governance references an unknown node",
                )
            )
        if classification.governance_classification == V37_EDGE_PROHIBITED_STRUCTURAL:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_EDGE_RELATIONSHIP,
                    "edge_governance",
                    classification.edge_id,
                    "edge governance classification is prohibited",
                )
            )
        if classification.governance_classification == V37_EDGE_UNSUPPORTED_STRUCTURAL:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_UNSUPPORTED_DOMAIN_CONNECTION,
                    "edge_governance",
                    classification.edge_id,
                    "edge governance classification is unsupported",
                )
            )
        if classification.edge_implies_execution_flow or classification.traversal_execution_enabled:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_EXECUTION_CAPABILITY,
                    "edge_governance",
                    classification.edge_id,
                    "edge governance metadata implies execution capability",
                )
            )


def _add_domain_classification_findings(
    subject_type: str,
    subject_id: str,
    governance_domain_ids: tuple[str, ...],
    domain_classifications: dict[str, str],
    findings: list[V37GraphGovernanceValidationFinding],
) -> None:
    for domain_id in governance_domain_ids:
        classification = domain_classifications.get(domain_id)
        if classification == V37_DOMAIN_PROHIBITED:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_CROSS_DOMAIN_STRUCTURE,
                    subject_type,
                    subject_id,
                    f"subject references prohibited governance domain {domain_id}",
                )
            )
        if classification == V37_DOMAIN_UNSUPPORTED:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_UNSUPPORTED_CONFIGURATION,
                    subject_type,
                    subject_id,
                    f"subject references unsupported governance domain {domain_id}",
                )
            )


def _add_continuity_findings(
    governance_map: V37GraphGovernanceMap,
    findings: list[V37GraphGovernanceValidationFinding],
) -> None:
    for subject_type, subject_id, message in _continuity_gaps(governance_map):
        findings.append(
            _finding(
                V37_GOVERNANCE_BLOCKED_BY_CONTINUITY_VIOLATION,
                subject_type,
                subject_id,
                message,
            )
        )


def _add_non_execution_findings(
    governance_map: V37GraphGovernanceMap,
    findings: list[V37GraphGovernanceValidationFinding],
) -> None:
    expected_false = {
        "graph_execution_enabled": governance_map.graph_execution_enabled,
        "node_execution_enabled": governance_map.node_execution_enabled,
        "edge_traversal_execution_enabled": governance_map.edge_traversal_execution_enabled,
        "runtime_orchestration_enabled": governance_map.runtime_orchestration_enabled,
        "routing_enabled": governance_map.routing_enabled,
        "scheduling_enabled": governance_map.scheduling_enabled,
        "dispatch_enabled": governance_map.dispatch_enabled,
        "optimization_enabled": governance_map.optimization_enabled,
        "recommendation_enabled": governance_map.recommendation_enabled,
        "autonomous_orchestration_enabled": governance_map.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": governance_map.runtime_mutation_enabled,
        "graph_evaluation_execution_enabled": governance_map.graph_evaluation_execution_enabled,
    }
    expected_true = {
        "governance_metadata_does_not_enable_orchestration": (
            governance_map.governance_metadata_does_not_enable_orchestration
        ),
        "structural_governance_artifact_only": governance_map.structural_governance_artifact_only,
        "non_executable": governance_map.non_executable,
    }
    for field_name, value in expected_false.items():
        if value:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_EXECUTION_CAPABILITY,
                    "governance_flag",
                    field_name,
                    "execution-capable governance flag must remain false",
                )
            )
    for field_name, value in expected_true.items():
        if not value:
            findings.append(
                _finding(
                    V37_GOVERNANCE_BLOCKED_BY_EXECUTION_CAPABILITY,
                    "governance_flag",
                    field_name,
                    "non-executable governance flag must remain true",
                )
            )


def _continuity_gaps(
    governance_map: V37GraphGovernanceMap,
) -> tuple[tuple[str, str, str], ...]:
    if not governance_map.continuity_evidence:
        return (("governance_map", governance_map.graph_id, "governance continuity evidence is missing"),)
    continuity = governance_map.continuity_evidence[0]
    gaps: list[tuple[str, str, str]] = []
    expected_domains = {domain.domain_id for domain in governance_map.domains}
    expected_rules = {rule.rule_id for rule in governance_map.rules}
    expected_nodes = {item.node_id for item in governance_map.node_classifications}
    expected_edges = {item.edge_id for item in governance_map.edge_classifications}
    expected_findings = {item.finding_id for item in governance_map.findings}
    if expected_domains - set(continuity.domain_ids):
        gaps.append(("continuity", continuity.continuity_id, "domain continuity references are incomplete"))
    if expected_rules - set(continuity.rule_ids):
        gaps.append(("continuity", continuity.continuity_id, "rule continuity references are incomplete"))
    if expected_nodes - set(continuity.node_classification_ids):
        gaps.append(("continuity", continuity.continuity_id, "node classification continuity references are incomplete"))
    if expected_edges - set(continuity.edge_classification_ids):
        gaps.append(("continuity", continuity.continuity_id, "edge classification continuity references are incomplete"))
    if expected_findings - set(continuity.finding_ids):
        gaps.append(("continuity", continuity.continuity_id, "finding continuity references are incomplete"))
    if not continuity.replay_lineage_references or not continuity.rollback_lineage_references:
        gaps.append(("continuity", continuity.continuity_id, "replay or rollback continuity is missing"))
    return tuple(gaps)


def _non_execution_guarantee_preserved(governance_map: V37GraphGovernanceMap) -> bool:
    return (
        governance_map.governance_metadata_does_not_enable_orchestration
        and governance_map.structural_governance_artifact_only
        and governance_map.non_executable
        and not governance_map.graph_execution_enabled
        and not governance_map.node_execution_enabled
        and not governance_map.edge_traversal_execution_enabled
        and not governance_map.runtime_orchestration_enabled
        and not governance_map.routing_enabled
        and not governance_map.scheduling_enabled
        and not governance_map.dispatch_enabled
        and not governance_map.optimization_enabled
        and not governance_map.recommendation_enabled
        and not governance_map.autonomous_orchestration_enabled
        and not governance_map.runtime_mutation_enabled
        and not governance_map.graph_evaluation_execution_enabled
        and all(
            not classification.edge_implies_execution_flow
            and not classification.traversal_execution_enabled
            for classification in governance_map.edge_classifications
        )
    )
