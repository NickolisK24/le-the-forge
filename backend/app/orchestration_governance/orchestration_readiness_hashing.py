"""Deterministic hashing for v4.3 orchestration readiness certification."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_readiness_models import (
    OrchestrationReadinessCertification,
    ReadinessCertificationIdentity,
    ReadinessCertificationRecord,
    ReadinessDiagnostic,
    ReadinessExplainability,
    ReadinessStateSummary,
)
from .orchestration_readiness_serialization import (
    export_orchestration_readiness_certification,
    export_readiness_certification_identity,
    export_readiness_certification_record,
    export_readiness_diagnostic,
    export_readiness_explainability,
    export_readiness_state_summary,
    stable_serialize,
)


def deterministic_readiness_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_readiness_certification_identity(identity: ReadinessCertificationIdentity) -> str:
    return deterministic_readiness_hash(export_readiness_certification_identity(identity))


def hash_readiness_certification_record(
    certification: ReadinessCertificationRecord,
) -> str:
    return deterministic_readiness_hash(export_readiness_certification_record(certification))


def hash_readiness_state_summary(summary: ReadinessStateSummary) -> str:
    return deterministic_readiness_hash(export_readiness_state_summary(summary))


def hash_readiness_diagnostic(diagnostic: ReadinessDiagnostic) -> str:
    return deterministic_readiness_hash(export_readiness_diagnostic(diagnostic))


def hash_readiness_explainability(summary: ReadinessExplainability) -> str:
    return deterministic_readiness_hash(export_readiness_explainability(summary))


def hash_orchestration_readiness_certification(
    certification: OrchestrationReadinessCertification,
) -> str:
    return deterministic_readiness_hash(export_orchestration_readiness_certification(certification))
