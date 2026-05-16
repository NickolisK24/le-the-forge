"""Deterministic certification scope construction for v3.7 planning continuity."""

from __future__ import annotations

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_certification_models import (
    V3_7_GRAPH_CERTIFICATION_PHASE_ID,
    V37GraphCertificationIdentity,
    V37GraphCertificationMetadata,
    V37GraphCertificationScope,
    V37GraphCertificationScopeIdentity,
    V37GraphCertificationScopeReference,
)
from .v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from .v3_7_graph_integrity_models import hash_v3_7_graph_integrity_enforcement_result
from .v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from .v3_7_graph_intelligence_models import hash_v3_7_graph_planning_intelligence_aggregation
from .v3_7_graph_models import default_v3_7_graph_provenance


DEFAULT_V37_GRAPH_CERTIFICATION_ID = "v3_7_graph_planning_continuity_certification_default"
DEFAULT_V37_GRAPH_CERTIFICATION_SCOPE_ID = "v3_7_graph_planning_continuity_scope_default"


def build_v3_7_graph_certification_identity() -> V37GraphCertificationIdentity:
    key_payload = {
        "certification_id": DEFAULT_V37_GRAPH_CERTIFICATION_ID,
        "certification_version": "v3.7",
        "phase_id": V3_7_GRAPH_CERTIFICATION_PHASE_ID,
    }
    return V37GraphCertificationIdentity(
        certification_id=DEFAULT_V37_GRAPH_CERTIFICATION_ID,
        certification_version="v3.7",
        phase_id=V3_7_GRAPH_CERTIFICATION_PHASE_ID,
        stable_identity_key=deterministic_hash(key_payload),
    )


def graph_certification_identity_key(identity: V37GraphCertificationIdentity) -> str:
    return deterministic_hash(
        {
            "certification_id": identity.certification_id,
            "certification_version": identity.certification_version,
            "phase_id": identity.phase_id,
        }
    )


def graph_certification_identities_are_unique(
    identities: tuple[V37GraphCertificationIdentity, ...],
) -> bool:
    keys = [identity.stable_identity_key for identity in identities]
    return len(keys) == len(set(keys))


def build_v3_7_graph_certification_scope_identity(
    certification_id: str,
) -> V37GraphCertificationScopeIdentity:
    key_payload = {
        "scope_id": DEFAULT_V37_GRAPH_CERTIFICATION_SCOPE_ID,
        "certification_id": certification_id,
        "scope_version": "v3.7",
        "phase_id": V3_7_GRAPH_CERTIFICATION_PHASE_ID,
    }
    return V37GraphCertificationScopeIdentity(
        scope_id=DEFAULT_V37_GRAPH_CERTIFICATION_SCOPE_ID,
        certification_id=certification_id,
        scope_version="v3.7",
        phase_id=V3_7_GRAPH_CERTIFICATION_PHASE_ID,
        stable_identity_key=deterministic_hash(key_payload),
    )


def graph_certification_scope_identity_key(identity: V37GraphCertificationScopeIdentity) -> str:
    return deterministic_hash(
        {
            "scope_id": identity.scope_id,
            "certification_id": identity.certification_id,
            "scope_version": identity.scope_version,
            "phase_id": identity.phase_id,
        }
    )


def graph_certification_scope_identities_are_unique(
    identities: tuple[V37GraphCertificationScopeIdentity, ...],
) -> bool:
    keys = [identity.stable_identity_key for identity in identities]
    return len(keys) == len(set(keys))


def build_v3_7_graph_certification_scope(
    certification_identity: V37GraphCertificationIdentity | None = None,
) -> V37GraphCertificationScope:
    certification = certification_identity or build_v3_7_graph_certification_identity()
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    integrity = enforce_v3_7_graph_planning_integrity(aggregation)
    identity = build_v3_7_graph_certification_scope_identity(certification.certification_id)
    references = [
        V37GraphCertificationScopeReference(
            reference_id=f"v3_7_certification_scope_{source.source_type}",
            reference_type=source.source_type,
            phase_id=source.source_phase_id,
            artifact_id=source.source_reference_id,
            artifact_hash=source.source_hash,
            provenance_references=source.provenance_references,
            explainability_references=source.explainability_references,
            continuity_hashes=source.continuity_references + (source.source_hash,),
        )
        for source in aggregation.evidence_sources
    ]
    references.append(
        V37GraphCertificationScopeReference(
            reference_id="v3_7_certification_scope_aggregation",
            reference_type="aggregation",
            phase_id=aggregation.identity.phase_id,
            artifact_id=aggregation.identity.aggregation_id,
            artifact_hash=hash_v3_7_graph_planning_intelligence_aggregation(aggregation),
            provenance_references=(aggregation.provenance.provenance_id,),
            explainability_references=aggregation.explainability_reference_ids,
            continuity_hashes=aggregation.continuity_hash_references
            + (hash_v3_7_graph_planning_intelligence_aggregation(aggregation),),
        )
    )
    references.append(
        V37GraphCertificationScopeReference(
            reference_id="v3_7_certification_scope_integrity",
            reference_type="integrity",
            phase_id=integrity.identity.phase_id,
            artifact_id=integrity.identity.enforcement_id,
            artifact_hash=hash_v3_7_graph_integrity_enforcement_result(integrity),
            provenance_references=(integrity.provenance.provenance_id, integrity.policy.provenance.provenance_id),
            explainability_references=integrity.explainability_reference_ids,
            continuity_hashes=integrity.continuity_hash_references
            + (hash_v3_7_graph_integrity_enforcement_result(integrity),),
        )
    )
    return V37GraphCertificationScope(
        identity=identity,
        metadata=(
            V37GraphCertificationMetadata("scope_semantics", "end_to_end_planning_continuity_evidence"),
            V37GraphCertificationMetadata("runtime_capability", "none"),
            V37GraphCertificationMetadata("readiness_boundary", "planning_continuity_not_runtime_readiness"),
        ),
        references=tuple(sorted(references, key=lambda item: item.reference_id)),
        provenance=default_v3_7_graph_provenance(identity.scope_id, "graph_planning_continuity_certification_scope"),
    )


def certification_scope_is_complete(scope: V37GraphCertificationScope) -> bool:
    required = {
        "graph_foundations",
        "governance",
        "compatibility",
        "evaluation",
        "session",
        "scenario",
        "aggregation",
        "integrity",
    }
    return required.issubset({reference.reference_type for reference in scope.references}) and all(
        reference.artifact_hash
        and reference.provenance_references
        and reference.explainability_references
        and reference.continuity_hashes
        for reference in scope.references
    )
