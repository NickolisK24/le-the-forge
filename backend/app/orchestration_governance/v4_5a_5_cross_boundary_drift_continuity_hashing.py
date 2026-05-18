"""Deterministic hashing for v4.5A.5 cross-boundary drift continuity."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5a_5_cross_boundary_drift_continuity_models import (
    BoundaryPairContinuityRecord,
    CrossBoundaryContinuityDiagnostic,
    CrossBoundaryContinuityIdentity,
    CrossBoundaryContinuityRecord,
    CrossBoundaryDriftContinuityIntelligence,
    CrossBoundaryEvidenceContinuity,
    DegradationContinuityPreservation,
    DriftContinuityPreservation,
    ExplanationContinuityPreservation,
    PropagationContinuityPreservation,
    UnsupportedCrossBoundaryVisibility,
)
from .v4_5a_5_cross_boundary_drift_continuity_serialization import (
    export_boundary_pair_continuity_record,
    export_cross_boundary_continuity_diagnostic,
    export_cross_boundary_continuity_identity,
    export_cross_boundary_continuity_record,
    export_cross_boundary_evidence_continuity,
    export_degradation_continuity_preservation,
    export_drift_continuity_preservation,
    export_explanation_continuity_preservation,
    export_propagation_continuity_preservation,
    export_unsupported_cross_boundary_visibility,
    export_v4_5a_5_cross_boundary_drift_continuity,
    stable_serialize_v4_5a_5_cross_boundary_drift_continuity,
)


def deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
    payload: Any,
) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_5_cross_boundary_drift_continuity(payload).encode(
            "utf-8"
        )
    ).hexdigest()


def hash_cross_boundary_continuity_identity(
    identity: CrossBoundaryContinuityIdentity,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_cross_boundary_continuity_identity(identity)
    )


def hash_cross_boundary_continuity_record(
    record: CrossBoundaryContinuityRecord,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_cross_boundary_continuity_record(record)
    )


def hash_boundary_pair_continuity_record(
    record: BoundaryPairContinuityRecord,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_boundary_pair_continuity_record(record)
    )


def hash_drift_continuity_preservation(
    record: DriftContinuityPreservation,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_drift_continuity_preservation(record)
    )


def hash_propagation_continuity_preservation(
    record: PropagationContinuityPreservation,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_propagation_continuity_preservation(record)
    )


def hash_degradation_continuity_preservation(
    record: DegradationContinuityPreservation,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_degradation_continuity_preservation(record)
    )


def hash_explanation_continuity_preservation(
    record: ExplanationContinuityPreservation,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_explanation_continuity_preservation(record)
    )


def hash_cross_boundary_evidence_continuity(
    record: CrossBoundaryEvidenceContinuity,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_cross_boundary_evidence_continuity(record)
    )


def hash_cross_boundary_continuity_diagnostic(
    record: CrossBoundaryContinuityDiagnostic,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_cross_boundary_continuity_diagnostic(record)
    )


def hash_unsupported_cross_boundary_visibility(
    record: UnsupportedCrossBoundaryVisibility,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_unsupported_cross_boundary_visibility(record)
    )


def hash_v4_5a_5_cross_boundary_drift_continuity(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> str:
    return deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
        export_v4_5a_5_cross_boundary_drift_continuity(intelligence)
    )
