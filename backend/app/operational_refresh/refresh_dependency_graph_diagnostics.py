"""Deterministic diagnostics for v4.1 refresh dependency graphs."""

from __future__ import annotations

from typing import Any

from .refresh_dependency_graph_continuity import validate_dependency_graph_continuity
from .refresh_dependency_graph_hashing import (
    hash_dependency_graph_diagnostics,
    hash_refresh_dependency_graph,
)
from .refresh_dependency_graph_integrity import enabled_dependency_graph_capability_flags
from .refresh_dependency_graph_models import RefreshDependencyGraph, default_refresh_dependency_graph
from .refresh_dependency_graph_visibility import validate_refresh_dependency_visibility


def build_dependency_graph_diagnostics(graph: RefreshDependencyGraph | None = None) -> dict[str, Any]:
    source = graph or default_refresh_dependency_graph()
    visibility = validate_refresh_dependency_visibility(source)
    continuity = validate_dependency_graph_continuity(source)
    enabled_flags = enabled_dependency_graph_capability_flags(source)
    return {
        "graph_hash": hash_refresh_dependency_graph(source),
        "diagnostics_hash": hash_dependency_graph_diagnostics(source.diagnostics_visibility),
        "visibility_validation": visibility,
        "continuity_validation": continuity,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "blocked_dependency_edges": sorted(source.blocked_state_visibility.blocked_dependency_edges),
        "circular_dependency_edges": sorted(source.blocked_state_visibility.circular_dependency_edges),
        "lineage_discontinuity_visibility": sorted(
            source.blocked_state_visibility.lineage_discontinuity_visibility
        ),
        "provenance_discontinuity_visibility": sorted(
            source.blocked_state_visibility.provenance_discontinuity_visibility
        ),
        "replay_discontinuity_visibility": sorted(source.blocked_state_visibility.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility": sorted(
            source.blocked_state_visibility.rollback_discontinuity_visibility
        ),
        "unsupported_dependency_nodes": sorted(source.unsupported_state_visibility.unsupported_dependency_nodes),
        "unsupported_dependency_edges": sorted(source.unsupported_state_visibility.unsupported_dependency_edges),
        "unsupported_dependency_providers": sorted(source.unsupported_state_visibility.unsupported_dependency_providers),
        "stale_dependency_edges": sorted(source.unsupported_state_visibility.stale_dependency_edges),
        "prohibited_dependency_edges": sorted(source.unsupported_state_visibility.prohibited_dependency_edges),
        "prohibited_dependency_domains": sorted(source.unsupported_state_visibility.prohibited_dependency_domains),
        "drift_visibility": sorted(source.drift_visibility.stale_relationships + source.drift_visibility.dependency_drift_references),
        "integrity_visibility": sorted(source.diagnostics_visibility.integrity_visibility),
        "warning_visibility": sorted(source.diagnostics_visibility.warning_visibility),
        "blocker_visibility": sorted(source.diagnostics_visibility.blocker_visibility),
        "diagnostics_visible": source.diagnostics_visibility.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics_visibility.descriptive_only,
        "remediation_absent": not source.diagnostics_visibility.remediation_enabled,
        "silent_fallback_absent": not source.diagnostics_visibility.silent_fallback_enabled,
        "automatic_recovery_absent": not source.diagnostics_visibility.automatic_recovery_enabled,
        "fail_visible_warning_count": (
            len(source.blocked_state_visibility.circular_dependency_edges)
            + len(source.blocked_state_visibility.lineage_discontinuity_visibility)
            + len(source.blocked_state_visibility.provenance_discontinuity_visibility)
            + len(source.blocked_state_visibility.replay_discontinuity_visibility)
            + len(source.blocked_state_visibility.rollback_discontinuity_visibility)
            + len(source.unsupported_state_visibility.unsupported_dependency_nodes)
            + len(source.unsupported_state_visibility.unsupported_dependency_edges)
            + len(source.unsupported_state_visibility.stale_dependency_edges)
            + len(source.unsupported_state_visibility.prohibited_dependency_edges)
            + len(source.unsupported_state_visibility.prohibited_dependency_domains)
        ),
    }
