"""Deterministic hashing for v4.5A.4 drift explainability intelligence."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5a_4_drift_explainability_models import (
    DriftCauseVisibility,
    DriftExplainabilityIdentity,
    DriftExplainabilityIntelligence,
    EvidenceExplanationMapping,
    ExplanationCompletenessVisibility,
    ExplanationConfidenceVisibility,
    ExplanationDiagnostic,
    ExplanationRecord,
    IntegrityDegradationExplanation,
    PropagationExplanationChain,
    UnsupportedExplanationVisibility,
)
from .v4_5a_4_drift_explainability_serialization import (
    export_drift_cause_visibility,
    export_drift_explainability_identity,
    export_evidence_explanation_mapping,
    export_explanation_completeness_visibility,
    export_explanation_confidence_visibility,
    export_explanation_diagnostic,
    export_explanation_record,
    export_integrity_degradation_explanation,
    export_propagation_explanation_chain,
    export_unsupported_explanation_visibility,
    export_v4_5a_4_drift_explainability_intelligence,
    stable_serialize_v4_5a_4_drift_explainability,
)


def deterministic_v4_5a_4_drift_explainability_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_4_drift_explainability(payload).encode("utf-8")
    ).hexdigest()


def hash_drift_explainability_identity(
    identity: DriftExplainabilityIdentity,
) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_drift_explainability_identity(identity)
    )


def hash_explanation_record(record: ExplanationRecord) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_explanation_record(record)
    )


def hash_drift_cause_visibility(record: DriftCauseVisibility) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_drift_cause_visibility(record)
    )


def hash_propagation_explanation_chain(
    record: PropagationExplanationChain,
) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_propagation_explanation_chain(record)
    )


def hash_integrity_degradation_explanation(
    record: IntegrityDegradationExplanation,
) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_integrity_degradation_explanation(record)
    )


def hash_evidence_explanation_mapping(record: EvidenceExplanationMapping) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_evidence_explanation_mapping(record)
    )


def hash_explanation_completeness_visibility(
    record: ExplanationCompletenessVisibility,
) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_explanation_completeness_visibility(record)
    )


def hash_explanation_confidence_visibility(
    record: ExplanationConfidenceVisibility,
) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_explanation_confidence_visibility(record)
    )


def hash_explanation_diagnostic(record: ExplanationDiagnostic) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_explanation_diagnostic(record)
    )


def hash_unsupported_explanation_visibility(
    record: UnsupportedExplanationVisibility,
) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_unsupported_explanation_visibility(record)
    )


def hash_v4_5a_4_drift_explainability_intelligence(
    intelligence: DriftExplainabilityIntelligence,
) -> str:
    return deterministic_v4_5a_4_drift_explainability_hash(
        export_v4_5a_4_drift_explainability_intelligence(intelligence)
    )
