"""Stable hashing for v4.1 schema evolution governance evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .schema_evolution_governance_models import (
    SchemaContinuityMetadata,
    SchemaEvolutionDiagnostics,
    SchemaEvolutionGovernance,
    SchemaEvolutionIdentity,
)
from .schema_evolution_governance_serialization import (
    export_schema_continuity_metadata,
    export_schema_evolution_diagnostics,
    export_schema_evolution_governance,
    export_schema_evolution_identity,
)


def deterministic_schema_evolution_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_schema_evolution_identity(identity: SchemaEvolutionIdentity) -> str:
    return deterministic_schema_evolution_hash(export_schema_evolution_identity(identity))


def hash_schema_continuity(metadata: SchemaContinuityMetadata) -> str:
    return deterministic_schema_evolution_hash(export_schema_continuity_metadata(metadata))


def hash_schema_diagnostics(diagnostics: SchemaEvolutionDiagnostics) -> str:
    return deterministic_schema_evolution_hash(export_schema_evolution_diagnostics(diagnostics))


def hash_schema_evolution_governance(governance: SchemaEvolutionGovernance) -> str:
    return deterministic_schema_evolution_hash(export_schema_evolution_governance(governance))
