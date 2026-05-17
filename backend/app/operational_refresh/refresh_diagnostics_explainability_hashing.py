"""Stable hashing for v4.1 diagnostics explainability evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .refresh_diagnostics_explainability_models import (
    RefreshDiagnosticsContinuityMetadata,
    RefreshDiagnosticsExplainability,
    RefreshDiagnosticsExplainabilityIdentity,
    RefreshDiagnosticsIntegrityBoundary,
)
from .refresh_diagnostics_explainability_serialization import (
    _export_record,
    export_diagnostics_explainability_identity,
    export_refresh_diagnostics_explainability,
)


def deterministic_diagnostics_explainability_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_diagnostics_explainability_identity(identity: RefreshDiagnosticsExplainabilityIdentity) -> str:
    return deterministic_diagnostics_explainability_hash(export_diagnostics_explainability_identity(identity))


def hash_diagnostics_continuity(metadata: RefreshDiagnosticsContinuityMetadata) -> str:
    return deterministic_diagnostics_explainability_hash(_export_record(metadata))


def hash_diagnostics_integrity(boundary: RefreshDiagnosticsIntegrityBoundary) -> str:
    return deterministic_diagnostics_explainability_hash(_export_record(boundary))


def hash_refresh_diagnostics_explainability(payload: RefreshDiagnosticsExplainability) -> str:
    return deterministic_diagnostics_explainability_hash(export_refresh_diagnostics_explainability(payload))
