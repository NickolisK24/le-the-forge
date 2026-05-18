"""Deterministic hashing for v4.5B.2 support status visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5b_2_support_status_visibility_models import (
    ContinuitySupportVisibility,
    EvidenceBasedSupportVisibility,
    ExperimentalDeprecatedVisibility,
    ExplainabilitySupportVisibility,
    PublicSupportSurfaceVisibility,
    SupportClassificationVisibility,
    SupportDiagnosticRecord,
    SupportStatusIdentity,
    SupportStatusVisibilityIntelligence,
    SupportSummaryRecord,
    SupportVisibilityRecord,
    UnsupportedSupportOperationalStateVisibility,
    UnsupportedSupportStateVisibility,
)
from .v4_5b_2_support_status_visibility_serialization import (
    export_continuity_support_visibility,
    export_evidence_based_support_visibility,
    export_experimental_deprecated_visibility,
    export_explainability_support_visibility,
    export_public_support_surface_visibility,
    export_support_classification_visibility,
    export_support_diagnostic_record,
    export_support_status_identity,
    export_support_summary_record,
    export_support_visibility_record,
    export_unsupported_support_operational_state_visibility,
    export_unsupported_support_state_visibility,
    export_v4_5b_2_support_status_visibility,
    stable_serialize_v4_5b_2_support_status_visibility,
)


def deterministic_v4_5b_2_support_status_visibility_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_2_support_status_visibility(payload).encode("utf-8")
    ).hexdigest()


def hash_support_status_identity(identity: SupportStatusIdentity) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_support_status_identity(identity)
    )


def hash_support_visibility_record(record: SupportVisibilityRecord) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_support_visibility_record(record)
    )


def hash_support_classification_visibility(
    record: SupportClassificationVisibility,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_support_classification_visibility(record)
    )


def hash_public_support_surface_visibility(
    record: PublicSupportSurfaceVisibility,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_public_support_surface_visibility(record)
    )


def hash_unsupported_support_state_visibility(
    record: UnsupportedSupportStateVisibility,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_unsupported_support_state_visibility(record)
    )


def hash_experimental_deprecated_visibility(
    record: ExperimentalDeprecatedVisibility,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_experimental_deprecated_visibility(record)
    )


def hash_evidence_based_support_visibility(
    record: EvidenceBasedSupportVisibility,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_evidence_based_support_visibility(record)
    )


def hash_explainability_support_visibility(
    record: ExplainabilitySupportVisibility,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_explainability_support_visibility(record)
    )


def hash_continuity_support_visibility(record: ContinuitySupportVisibility) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_continuity_support_visibility(record)
    )


def hash_support_summary_record(record: SupportSummaryRecord) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_support_summary_record(record)
    )


def hash_support_diagnostic_record(record: SupportDiagnosticRecord) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_support_diagnostic_record(record)
    )


def hash_unsupported_support_operational_state_visibility(
    record: UnsupportedSupportOperationalStateVisibility,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_unsupported_support_operational_state_visibility(record)
    )


def hash_v4_5b_2_support_status_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> str:
    return deterministic_v4_5b_2_support_status_visibility_hash(
        export_v4_5b_2_support_status_visibility(intelligence)
    )
