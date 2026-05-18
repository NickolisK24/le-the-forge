"""Deterministic hashing for v4.5A.3 integrity degradation intelligence."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5a_3_integrity_degradation_models import (
    ContinuityDegradationVisibility,
    CrossBoundaryIntegrityVisibility,
    DegradationClassificationRecord,
    DegradationEvidenceChain,
    DegradationRecord,
    DegradationSeverityAccumulation,
    ExplainabilityDegradationVisibility,
    IntegrityDegradationDiagnostic,
    IntegrityDegradationIdentity,
    IntegrityDegradationIntelligence,
    UnsupportedDegradationVisibility,
)
from .v4_5a_3_integrity_degradation_serialization import (
    export_continuity_degradation_visibility,
    export_cross_boundary_integrity_visibility,
    export_degradation_classification_record,
    export_degradation_evidence_chain,
    export_degradation_record,
    export_degradation_severity_accumulation,
    export_explainability_degradation_visibility,
    export_integrity_degradation_diagnostic,
    export_integrity_degradation_identity,
    export_unsupported_degradation_visibility,
    export_v4_5a_3_integrity_degradation_intelligence,
    stable_serialize_v4_5a_3_integrity_degradation,
)


def deterministic_v4_5a_3_integrity_degradation_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_3_integrity_degradation(payload).encode("utf-8")
    ).hexdigest()


def hash_integrity_degradation_identity(
    identity: IntegrityDegradationIdentity,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_integrity_degradation_identity(identity)
    )


def hash_degradation_record(record: DegradationRecord) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_degradation_record(record)
    )


def hash_degradation_classification(
    record: DegradationClassificationRecord,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_degradation_classification_record(record)
    )


def hash_degradation_evidence_chain(record: DegradationEvidenceChain) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_degradation_evidence_chain(record)
    )


def hash_continuity_degradation(record: ContinuityDegradationVisibility) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_continuity_degradation_visibility(record)
    )


def hash_degradation_severity_accumulation(
    record: DegradationSeverityAccumulation,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_degradation_severity_accumulation(record)
    )


def hash_explainability_degradation(
    record: ExplainabilityDegradationVisibility,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_explainability_degradation_visibility(record)
    )


def hash_cross_boundary_integrity(
    record: CrossBoundaryIntegrityVisibility,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_cross_boundary_integrity_visibility(record)
    )


def hash_integrity_degradation_diagnostic(
    record: IntegrityDegradationDiagnostic,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_integrity_degradation_diagnostic(record)
    )


def hash_unsupported_degradation_visibility(
    record: UnsupportedDegradationVisibility,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_unsupported_degradation_visibility(record)
    )


def hash_v4_5a_3_integrity_degradation_intelligence(
    intelligence: IntegrityDegradationIntelligence,
) -> str:
    return deterministic_v4_5a_3_integrity_degradation_hash(
        export_v4_5a_3_integrity_degradation_intelligence(intelligence)
    )
