"""Deterministic hashing for v4.5B.1 trust visibility foundations."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5b_1_trust_visibility_foundation_models import (
    GovernanceTransparencyVisibility,
    PublicExplainabilityVisibility,
    PublicIntegrityVisibility,
    PublicTrustDiagnosticRecord,
    PublicTrustEvidenceVisibility,
    TrustSummaryRecord,
    TrustVisibilityFoundationIntelligence,
    TrustVisibilityIdentity,
    TrustVisibilityRecord,
    UnsupportedPublicTrustVisibility,
    UnsupportedStateVisibility,
)
from .v4_5b_1_trust_visibility_foundation_serialization import (
    export_governance_transparency_visibility,
    export_public_explainability_visibility,
    export_public_integrity_visibility,
    export_public_trust_diagnostic_record,
    export_public_trust_evidence_visibility,
    export_trust_summary_record,
    export_trust_visibility_identity,
    export_trust_visibility_record,
    export_unsupported_public_trust_visibility,
    export_unsupported_state_visibility,
    export_v4_5b_1_trust_visibility_foundation,
    stable_serialize_v4_5b_1_trust_visibility_foundation,
)


def deterministic_v4_5b_1_trust_visibility_foundation_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_1_trust_visibility_foundation(payload).encode("utf-8")
    ).hexdigest()


def hash_trust_visibility_identity(identity: TrustVisibilityIdentity) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_trust_visibility_identity(identity)
    )


def hash_trust_visibility_record(record: TrustVisibilityRecord) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_trust_visibility_record(record)
    )


def hash_public_trust_evidence_visibility(
    record: PublicTrustEvidenceVisibility,
) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_public_trust_evidence_visibility(record)
    )


def hash_unsupported_state_visibility(record: UnsupportedStateVisibility) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_unsupported_state_visibility(record)
    )


def hash_governance_transparency_visibility(
    record: GovernanceTransparencyVisibility,
) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_governance_transparency_visibility(record)
    )


def hash_trust_summary_record(record: TrustSummaryRecord) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_trust_summary_record(record)
    )


def hash_public_explainability_visibility(
    record: PublicExplainabilityVisibility,
) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_public_explainability_visibility(record)
    )


def hash_public_integrity_visibility(record: PublicIntegrityVisibility) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_public_integrity_visibility(record)
    )


def hash_public_trust_diagnostic_record(
    record: PublicTrustDiagnosticRecord,
) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_public_trust_diagnostic_record(record)
    )


def hash_unsupported_public_trust_visibility(
    record: UnsupportedPublicTrustVisibility,
) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_unsupported_public_trust_visibility(record)
    )


def hash_v4_5b_1_trust_visibility_foundation(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> str:
    return deterministic_v4_5b_1_trust_visibility_foundation_hash(
        export_v4_5b_1_trust_visibility_foundation(intelligence)
    )
