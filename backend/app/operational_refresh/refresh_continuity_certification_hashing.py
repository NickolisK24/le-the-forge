"""Deterministic hashing for v4.1 refresh continuity certification."""

from __future__ import annotations

import hashlib
from typing import Any

from .refresh_continuity_certification_models import (
    RefreshContinuityCertification,
    RefreshContinuityCertificationIdentity,
    RefreshContinuityDiagnostics,
    RefreshContinuityExplainability,
    RefreshContinuityIntegrityBoundary,
    RefreshContinuityMetadata,
)
from .refresh_continuity_certification_serialization import stable_serialize
from .refresh_continuity_certification_serialization import export_refresh_continuity_certification


def deterministic_continuity_certification_hash(value: Any) -> str:
    if isinstance(value, RefreshContinuityCertification):
        value = export_refresh_continuity_certification(value)
    return hashlib.sha256(stable_serialize(value).encode("utf-8")).hexdigest()


def hash_continuity_certification_identity(identity: RefreshContinuityCertificationIdentity) -> str:
    return deterministic_continuity_certification_hash(identity)


def hash_refresh_continuity_certification(payload: RefreshContinuityCertification) -> str:
    return deterministic_continuity_certification_hash(payload)


def hash_continuity_metadata(metadata: RefreshContinuityMetadata) -> str:
    return deterministic_continuity_certification_hash(metadata)


def hash_continuity_diagnostics(diagnostics: RefreshContinuityDiagnostics) -> str:
    return deterministic_continuity_certification_hash(diagnostics)


def hash_continuity_explainability(explainability: RefreshContinuityExplainability) -> str:
    return deterministic_continuity_certification_hash(explainability)


def hash_continuity_integrity(boundary: RefreshContinuityIntegrityBoundary) -> str:
    return deterministic_continuity_certification_hash(boundary)
