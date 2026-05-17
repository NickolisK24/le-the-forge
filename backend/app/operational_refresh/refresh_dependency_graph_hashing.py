"""Stable hashing for v4.1 refresh dependency graph governance evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .refresh_dependency_graph_models import (
    RefreshDependencyContinuityMetadata,
    RefreshDependencyDiagnosticsVisibility,
    RefreshDependencyGraph,
    RefreshDependencyGraphIdentity,
)
from .refresh_dependency_graph_serialization import (
    export_continuity_metadata,
    export_dependency_graph_identity,
    export_diagnostics_visibility,
    export_refresh_dependency_graph,
)


def deterministic_refresh_dependency_graph_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_dependency_graph_identity(identity: RefreshDependencyGraphIdentity) -> str:
    return deterministic_refresh_dependency_graph_hash(export_dependency_graph_identity(identity))


def hash_dependency_graph_continuity(metadata: RefreshDependencyContinuityMetadata) -> str:
    return deterministic_refresh_dependency_graph_hash(export_continuity_metadata(metadata))


def hash_dependency_graph_diagnostics(visibility: RefreshDependencyDiagnosticsVisibility) -> str:
    return deterministic_refresh_dependency_graph_hash(export_diagnostics_visibility(visibility))


def hash_refresh_dependency_graph(graph: RefreshDependencyGraph) -> str:
    return deterministic_refresh_dependency_graph_hash(export_refresh_dependency_graph(graph))
