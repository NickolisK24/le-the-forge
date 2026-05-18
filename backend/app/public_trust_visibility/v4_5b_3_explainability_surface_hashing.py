"""Deterministic hashing for v4.5B.3 explainability surfaces."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5b_3_explainability_surface_models import (
    ContinuityExplanationVisibility,
    EvidenceToExplanationMapping,
    ExplainabilitySurfaceIdentity,
    ExplainabilitySurfaceIntelligence,
    ExplainabilitySurfaceRecord,
    ExplanationDiagnosticRecord,
    ExplanationSummaryRecord,
    LimitationExplanationVisibility,
    PublicTrustExplanationVisibility,
    SupportStateExplanationSurface,
    UnsupportedExplanationOperationalStateVisibility,
    UnsupportedStateExplanationVisibility,
)
from .v4_5b_3_explainability_surface_serialization import (
    export_continuity_explanation_visibility,
    export_evidence_to_explanation_mapping,
    export_explainability_surface_identity,
    export_explainability_surface_record,
    export_explanation_diagnostic_record,
    export_explanation_summary_record,
    export_limitation_explanation_visibility,
    export_public_trust_explanation_visibility,
    export_support_state_explanation_surface,
    export_unsupported_explanation_operational_state_visibility,
    export_unsupported_state_explanation_visibility,
    export_v4_5b_3_explainability_surfaces,
    stable_serialize_v4_5b_3_explainability_surfaces,
)


def deterministic_v4_5b_3_explainability_surface_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_3_explainability_surfaces(payload).encode("utf-8")
    ).hexdigest()


def hash_explainability_surface_identity(
    identity: ExplainabilitySurfaceIdentity,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_explainability_surface_identity(identity)
    )


def hash_explainability_surface_record(record: ExplainabilitySurfaceRecord) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_explainability_surface_record(record)
    )


def hash_support_state_explanation_surface(
    record: SupportStateExplanationSurface,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_support_state_explanation_surface(record)
    )


def hash_evidence_to_explanation_mapping(record: EvidenceToExplanationMapping) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_evidence_to_explanation_mapping(record)
    )


def hash_limitation_explanation_visibility(
    record: LimitationExplanationVisibility,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_limitation_explanation_visibility(record)
    )


def hash_public_trust_explanation_visibility(
    record: PublicTrustExplanationVisibility,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_public_trust_explanation_visibility(record)
    )


def hash_continuity_explanation_visibility(
    record: ContinuityExplanationVisibility,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_continuity_explanation_visibility(record)
    )


def hash_unsupported_state_explanation_visibility(
    record: UnsupportedStateExplanationVisibility,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_unsupported_state_explanation_visibility(record)
    )


def hash_explanation_summary_record(record: ExplanationSummaryRecord) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_explanation_summary_record(record)
    )


def hash_explanation_diagnostic_record(record: ExplanationDiagnosticRecord) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_explanation_diagnostic_record(record)
    )


def hash_unsupported_explanation_operational_state_visibility(
    record: UnsupportedExplanationOperationalStateVisibility,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_unsupported_explanation_operational_state_visibility(record)
    )


def hash_v4_5b_3_explainability_surfaces(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> str:
    return deterministic_v4_5b_3_explainability_surface_hash(
        export_v4_5b_3_explainability_surfaces(intelligence)
    )
