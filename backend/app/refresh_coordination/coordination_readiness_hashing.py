"""Deterministic hashing for v4.2 coordination readiness certification."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_readiness_models import (
    CoordinationReadinessCertification,
    CoordinationReadinessDiagnostic,
    CoordinationReadinessGovernance,
    CoordinationReadinessIdentity,
    CoordinationReadinessRecord,
    DescriptiveReadinessClassification,
    LayerReadinessReference,
    PhaseEvidenceReference,
    ReadinessStateVisibility,
)
from .coordination_readiness_serialization import (
    export_coordination_readiness_certification,
    export_coordination_readiness_diagnostic,
    export_coordination_readiness_governance,
    export_coordination_readiness_identity,
    export_coordination_readiness_record,
    export_descriptive_readiness_classification,
    export_layer_readiness_reference,
    export_phase_evidence_reference,
    export_readiness_state_visibility,
    stable_serialize,
)


def deterministic_coordination_readiness_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_readiness_identity(identity: CoordinationReadinessIdentity) -> str:
    return deterministic_coordination_readiness_hash(export_coordination_readiness_identity(identity))


def hash_phase_evidence_reference(reference: PhaseEvidenceReference) -> str:
    return deterministic_coordination_readiness_hash(export_phase_evidence_reference(reference))


def hash_layer_readiness_reference(reference: LayerReadinessReference) -> str:
    return deterministic_coordination_readiness_hash(export_layer_readiness_reference(reference))


def hash_coordination_readiness_record(record: CoordinationReadinessRecord) -> str:
    return deterministic_coordination_readiness_hash(export_coordination_readiness_record(record))


def hash_readiness_state_visibility(visibility: ReadinessStateVisibility) -> str:
    return deterministic_coordination_readiness_hash(export_readiness_state_visibility(visibility))


def hash_descriptive_readiness_classification(classification: DescriptiveReadinessClassification) -> str:
    return deterministic_coordination_readiness_hash(export_descriptive_readiness_classification(classification))


def hash_coordination_readiness_diagnostic(diagnostic: CoordinationReadinessDiagnostic) -> str:
    return deterministic_coordination_readiness_hash(export_coordination_readiness_diagnostic(diagnostic))


def hash_coordination_readiness_governance(governance: CoordinationReadinessGovernance) -> str:
    return deterministic_coordination_readiness_hash(export_coordination_readiness_governance(governance))


def hash_coordination_readiness_certification(certification: CoordinationReadinessCertification) -> str:
    return deterministic_coordination_readiness_hash(export_coordination_readiness_certification(certification))
