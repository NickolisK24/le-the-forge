"""Deterministic hashing for v4.3 continuity and integrity certification."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_continuity_models import (
    CertificationStateSummary,
    ContinuityCertificationDiagnostic,
    ContinuityCertificationExplainability,
    ContinuityCertificationIdentity,
    ContinuityCertificationRecord,
    IntegrityCertificationRecord,
    OrchestrationContinuityIntegrityCertification,
)
from .orchestration_continuity_serialization import (
    export_certification_state_summary,
    export_continuity_certification_diagnostic,
    export_continuity_certification_explainability,
    export_continuity_certification_identity,
    export_continuity_certification_record,
    export_integrity_certification_record,
    export_orchestration_continuity_integrity_certification,
    stable_serialize,
)


def deterministic_continuity_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_continuity_certification_identity(identity: ContinuityCertificationIdentity) -> str:
    return deterministic_continuity_hash(export_continuity_certification_identity(identity))


def hash_continuity_certification_record(
    certification: ContinuityCertificationRecord,
) -> str:
    return deterministic_continuity_hash(export_continuity_certification_record(certification))


def hash_integrity_certification_record(
    certification: IntegrityCertificationRecord,
) -> str:
    return deterministic_continuity_hash(export_integrity_certification_record(certification))


def hash_certification_state_summary(summary: CertificationStateSummary) -> str:
    return deterministic_continuity_hash(export_certification_state_summary(summary))


def hash_continuity_certification_diagnostic(
    diagnostic: ContinuityCertificationDiagnostic,
) -> str:
    return deterministic_continuity_hash(export_continuity_certification_diagnostic(diagnostic))


def hash_continuity_certification_explainability(
    summary: ContinuityCertificationExplainability,
) -> str:
    return deterministic_continuity_hash(export_continuity_certification_explainability(summary))


def hash_orchestration_continuity_integrity_certification(
    certification: OrchestrationContinuityIntegrityCertification,
) -> str:
    return deterministic_continuity_hash(export_orchestration_continuity_integrity_certification(certification))
