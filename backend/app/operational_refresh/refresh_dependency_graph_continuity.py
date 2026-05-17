"""Continuity validation for v4.1 refresh dependency graph evidence."""

from __future__ import annotations

from .refresh_dependency_graph_models import RefreshDependencyGraph, default_refresh_dependency_graph


def validate_dependency_graph_lineage_continuity(graph: RefreshDependencyGraph) -> dict[str, object]:
    lineage_reference = graph.identity.lineage_reference
    lineage_chains = graph.lineage_chains
    chain_reference_visible = any(chain.graph_lineage_reference == lineage_reference for chain in lineage_chains)
    continuity_reference_visible = lineage_reference in graph.continuity_metadata.lineage_continuity_references
    discontinuity_visible = any(chain.lineage_discontinuity_visibility for chain in lineage_chains)
    hidden_resolution_count = sum(1 for chain in lineage_chains if chain.hidden_lineage_resolution_enabled)
    execution_count = sum(1 for chain in lineage_chains if chain.execution_enabled or chain.automatic_lineage_repair_enabled)
    return {
        "valid": (
            chain_reference_visible
            and continuity_reference_visible
            and graph.continuity_metadata.lineage_continuity_preserved
            and discontinuity_visible
            and hidden_resolution_count == 0
            and execution_count == 0
        ),
        "lineage_reference": lineage_reference,
        "lineage_chain_count": len(lineage_chains),
        "lineage_chain_reference_visible": chain_reference_visible,
        "lineage_continuity_reference_visible": continuity_reference_visible,
        "lineage_continuity_preserved": graph.continuity_metadata.lineage_continuity_preserved,
        "lineage_discontinuity_visibility_count": sum(
            len(chain.lineage_discontinuity_visibility) for chain in lineage_chains
        ),
        "hidden_lineage_resolution_count": hidden_resolution_count,
        "lineage_execution_semantics_count": execution_count,
    }


def validate_dependency_graph_provenance_continuity(graph: RefreshDependencyGraph) -> dict[str, object]:
    provenance_reference = graph.identity.provenance_reference
    provenance_chains = graph.provenance_chains
    chain_reference_visible = any(
        chain.graph_provenance_reference == provenance_reference for chain in provenance_chains
    )
    continuity_reference_visible = provenance_reference in graph.continuity_metadata.provenance_continuity_references
    discontinuity_visible = any(chain.provenance_discontinuity_visibility for chain in provenance_chains)
    no_inferred_provenance = all(not chain.inferred_provenance_allowed for chain in provenance_chains)
    hidden_resolution_count = sum(1 for chain in provenance_chains if chain.hidden_provenance_resolution_enabled)
    execution_count = sum(1 for chain in provenance_chains if chain.execution_enabled)
    return {
        "valid": (
            chain_reference_visible
            and continuity_reference_visible
            and graph.continuity_metadata.provenance_continuity_preserved
            and discontinuity_visible
            and no_inferred_provenance
            and hidden_resolution_count == 0
            and execution_count == 0
        ),
        "provenance_reference": provenance_reference,
        "provenance_chain_count": len(provenance_chains),
        "provenance_chain_reference_visible": chain_reference_visible,
        "provenance_continuity_reference_visible": continuity_reference_visible,
        "provenance_continuity_preserved": graph.continuity_metadata.provenance_continuity_preserved,
        "provenance_discontinuity_visibility_count": sum(
            len(chain.provenance_discontinuity_visibility) for chain in provenance_chains
        ),
        "no_inferred_provenance": no_inferred_provenance,
        "hidden_provenance_resolution_count": hidden_resolution_count,
        "provenance_execution_semantics_count": execution_count,
    }


def validate_dependency_graph_replay_continuity(graph: RefreshDependencyGraph) -> dict[str, object]:
    continuity_visible = graph.replay_metadata.replay_id in graph.continuity_metadata.replay_continuity_references
    discontinuity_visible = bool(graph.replay_metadata.replay_discontinuity_visibility)
    return {
        "valid": (
            continuity_visible
            and discontinuity_visible
            and graph.continuity_metadata.replay_continuity_preserved
            and graph.continuity_metadata.replay_safe
            and graph.replay_metadata.replay_safe
            and not graph.replay_metadata.live_replay_enabled
            and not graph.replay_metadata.dependency_execution_enabled
        ),
        "replay_reference": graph.replay_metadata.replay_id,
        "replay_continuity_reference_visible": continuity_visible,
        "replay_discontinuity_visibility_count": len(graph.replay_metadata.replay_discontinuity_visibility),
        "replay_continuity_preserved": graph.continuity_metadata.replay_continuity_preserved,
        "replay_safe": graph.continuity_metadata.replay_safe and graph.replay_metadata.replay_safe,
        "live_replay_enabled": graph.replay_metadata.live_replay_enabled,
        "dependency_execution_enabled": graph.replay_metadata.dependency_execution_enabled,
    }


def validate_dependency_graph_rollback_continuity(graph: RefreshDependencyGraph) -> dict[str, object]:
    continuity_visible = graph.rollback_metadata.rollback_id in graph.continuity_metadata.rollback_continuity_references
    discontinuity_visible = bool(graph.rollback_metadata.rollback_discontinuity_visibility)
    return {
        "valid": (
            continuity_visible
            and discontinuity_visible
            and graph.continuity_metadata.rollback_continuity_preserved
            and graph.continuity_metadata.rollback_safe
            and graph.rollback_metadata.rollback_safe
            and not graph.rollback_metadata.automatic_rollback_enabled
            and not graph.rollback_metadata.recovery_execution_enabled
        ),
        "rollback_reference": graph.rollback_metadata.rollback_id,
        "rollback_continuity_reference_visible": continuity_visible,
        "rollback_discontinuity_visibility_count": len(graph.rollback_metadata.rollback_discontinuity_visibility),
        "rollback_continuity_preserved": graph.continuity_metadata.rollback_continuity_preserved,
        "rollback_safe": graph.continuity_metadata.rollback_safe and graph.rollback_metadata.rollback_safe,
        "automatic_rollback_enabled": graph.rollback_metadata.automatic_rollback_enabled,
        "recovery_execution_enabled": graph.rollback_metadata.recovery_execution_enabled,
    }


def validate_dependency_graph_continuity(graph: RefreshDependencyGraph | None = None) -> dict[str, object]:
    source = graph or default_refresh_dependency_graph()
    lineage = validate_dependency_graph_lineage_continuity(source)
    provenance = validate_dependency_graph_provenance_continuity(source)
    replay = validate_dependency_graph_replay_continuity(source)
    rollback = validate_dependency_graph_rollback_continuity(source)
    return {
        "valid": lineage["valid"] and provenance["valid"] and replay["valid"] and rollback["valid"],
        "lineage_continuity_valid": lineage["valid"],
        "provenance_continuity_valid": provenance["valid"],
        "replay_continuity_valid": replay["valid"],
        "rollback_continuity_valid": rollback["valid"],
        "lineage_continuity": lineage,
        "provenance_continuity": provenance,
        "replay_continuity": replay,
        "rollback_continuity": rollback,
    }
