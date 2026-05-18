"""Deterministic hashing for v4.5A.2 drift propagation intelligence."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5a_2_drift_propagation_models import (
    CrossBoundaryPropagationVisibility,
    DriftPropagationIdentity,
    DriftPropagationIntelligence,
    PropagationChainRecord,
    PropagationClassificationRecord,
    PropagationContinuityRecord,
    PropagationDiagnosticRecord,
    PropagationEvidenceChain,
    PropagationExplainabilityVisibility,
    PropagationSeverityAccumulation,
    UnsupportedPropagationVisibility,
)
from .v4_5a_2_drift_propagation_serialization import (
    export_cross_boundary_propagation_visibility,
    export_drift_propagation_identity,
    export_propagation_chain_record,
    export_propagation_classification_record,
    export_propagation_continuity_record,
    export_propagation_diagnostic_record,
    export_propagation_evidence_chain,
    export_propagation_explainability_visibility,
    export_propagation_severity_accumulation,
    export_unsupported_propagation_visibility,
    export_v4_5a_2_drift_propagation_intelligence,
    stable_serialize_v4_5a_2_drift_propagation,
)


def deterministic_v4_5a_2_drift_propagation_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_2_drift_propagation(payload).encode("utf-8")
    ).hexdigest()


def hash_drift_propagation_identity(identity: DriftPropagationIdentity) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_drift_propagation_identity(identity)
    )


def hash_propagation_chain(record: PropagationChainRecord) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_propagation_chain_record(record)
    )


def hash_propagation_classification(record: PropagationClassificationRecord) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_propagation_classification_record(record)
    )


def hash_propagation_evidence_chain(record: PropagationEvidenceChain) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_propagation_evidence_chain(record)
    )


def hash_propagation_continuity(record: PropagationContinuityRecord) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_propagation_continuity_record(record)
    )


def hash_propagation_severity_accumulation(
    record: PropagationSeverityAccumulation,
) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_propagation_severity_accumulation(record)
    )


def hash_propagation_explainability(
    record: PropagationExplainabilityVisibility,
) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_propagation_explainability_visibility(record)
    )


def hash_cross_boundary_propagation(
    record: CrossBoundaryPropagationVisibility,
) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_cross_boundary_propagation_visibility(record)
    )


def hash_propagation_diagnostic(record: PropagationDiagnosticRecord) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_propagation_diagnostic_record(record)
    )


def hash_unsupported_propagation_visibility(
    record: UnsupportedPropagationVisibility,
) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_unsupported_propagation_visibility(record)
    )


def hash_v4_5a_2_drift_propagation_intelligence(
    intelligence: DriftPropagationIntelligence,
) -> str:
    return deterministic_v4_5a_2_drift_propagation_hash(
        export_v4_5a_2_drift_propagation_intelligence(intelligence)
    )
