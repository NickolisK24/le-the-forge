"""Declarative governance dependency models for v3.5 orchestration planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


@dataclass(frozen=True)
class GovernanceDependencyLineage:
    source_governance_contract_id: str
    target_orchestration_scope_id: str
    upstream_dependency_ids: tuple[str, ...]
    downstream_dependency_ids: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    compatibility_lineage_references: tuple[str, ...]
    environment_lineage_references: tuple[str, ...]


@dataclass(frozen=True)
class GovernanceDependencyContract:
    dependency_id: str
    dependency_domain: str
    required_evidence_ids: tuple[str, ...]
    provided_evidence_ids: tuple[str, ...]
    source_contract_id: str
    target_scope_id: str
    lineage: GovernanceDependencyLineage
    compatibility_requirements: tuple[str, ...]
    compatibility_evidence_ids: tuple[str, ...]
    environment_requirements: tuple[str, ...]
    environment_evidence_ids: tuple[str, ...]
    unsupported_reasons: tuple[str, ...]
    prohibited_reasons: tuple[str, ...]
    blocker_reasons: tuple[str, ...]
    manual_review_reasons: tuple[str, ...]
    dependency_supported: bool = True
    dependency_prohibited: bool = False
    compatibility_verified: bool = True
    environment_verified: bool = True
    external_dependency_fetching_enabled: bool = False
    automatic_remediation_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    audit_log_writing_enabled: bool = False
    production_consumption_enabled: bool = False


def default_governance_dependency_lineage() -> GovernanceDependencyLineage:
    return GovernanceDependencyLineage(
        source_governance_contract_id="v3_5_governance_consumption_contract",
        target_orchestration_scope_id="orchestration-scope-v3-5-governance-consumption",
        upstream_dependency_ids=("v3_4_closeout_and_v3_5_readiness",),
        downstream_dependency_ids=("v3_5_orchestration_readiness_evaluation",),
        replay_lineage_references=("replay-lineage-v3-5-governance-consumption",),
        rollback_lineage_references=("rollback-lineage-v3-5-governance-consumption",),
        compatibility_lineage_references=("v3_4_governance_chain_compatible",),
        environment_lineage_references=("non_production_environment_isolated",),
    )


def default_governance_dependency_contract() -> GovernanceDependencyContract:
    return GovernanceDependencyContract(
        dependency_id="v3-5-governance-dependency-resolution",
        dependency_domain="governance_consumption_planning",
        required_evidence_ids=(
            "v3_4_closeout_and_v3_5_readiness",
            "v3_5_governance_consumption_contract",
            "v3_5_orchestration_readiness_evaluation",
        ),
        provided_evidence_ids=(
            "v3_4_closeout_and_v3_5_readiness",
            "v3_5_governance_consumption_contract",
            "v3_5_orchestration_readiness_evaluation",
        ),
        source_contract_id="v3_5_governance_consumption_contract",
        target_scope_id="orchestration-scope-v3-5-governance-consumption",
        lineage=default_governance_dependency_lineage(),
        compatibility_requirements=("v3_4_governance_chain_compatible",),
        compatibility_evidence_ids=("v3_4_governance_chain_compatible",),
        environment_requirements=("non_production_environment_isolated",),
        environment_evidence_ids=("non_production_environment_isolated",),
        unsupported_reasons=(),
        prohibited_reasons=(),
        blocker_reasons=(),
        manual_review_reasons=(),
    )


def export_governance_dependency_lineage(lineage: GovernanceDependencyLineage) -> dict[str, Any]:
    data = asdict(lineage)
    for field in (
        "upstream_dependency_ids",
        "downstream_dependency_ids",
        "replay_lineage_references",
        "rollback_lineage_references",
        "compatibility_lineage_references",
        "environment_lineage_references",
    ):
        data[field] = sorted(data[field])
    return data


def export_governance_dependency_contract(contract: GovernanceDependencyContract) -> dict[str, Any]:
    data = asdict(contract)
    data["lineage"] = export_governance_dependency_lineage(contract.lineage)
    for field in (
        "required_evidence_ids",
        "provided_evidence_ids",
        "compatibility_requirements",
        "compatibility_evidence_ids",
        "environment_requirements",
        "environment_evidence_ids",
        "unsupported_reasons",
        "prohibited_reasons",
        "blocker_reasons",
        "manual_review_reasons",
    ):
        data[field] = sorted(data[field])
    return data


def serialize_governance_dependency_contract(contract: GovernanceDependencyContract) -> str:
    return stable_serialize(export_governance_dependency_contract(contract))


def hash_governance_dependency_contract(contract: GovernanceDependencyContract) -> str:
    return deterministic_hash(export_governance_dependency_contract(contract))
