"""Fail-visible visibility helpers for v4.1 refresh drift certification."""

from __future__ import annotations

from .refresh_drift_certification_models import (
    DRIFT_LAYER_DEPENDENCY,
    DRIFT_LAYER_LINEAGE,
    DRIFT_LAYER_MANIFEST,
    DRIFT_LAYER_SCHEMA,
    DRIFT_LAYER_SEQUENCING,
    DRIFT_STATE_BLOCKED,
    DRIFT_STATE_CROSS_LAYER_CONFLICT,
    DRIFT_STATE_LINEAGE_DISCONTINUITY,
    DRIFT_STATE_PROHIBITED,
    DRIFT_STATE_PROVENANCE_DISCONTINUITY,
    DRIFT_STATE_REPLAY_DISCONTINUITY,
    DRIFT_STATE_ROLLBACK_DISCONTINUITY,
    DRIFT_STATE_STALE,
    DRIFT_STATE_UNSUPPORTED,
    DRIFT_STATES,
    FAIL_VISIBLE_DRIFT_STATES,
    PROHIBITED_DRIFT_DOMAINS,
    RefreshDriftCertification,
    RefreshDriftObservation,
    default_refresh_drift_certification,
    default_refresh_drift_observations,
)


def count_drift_observation_states(observations: tuple[RefreshDriftObservation, ...] | list[RefreshDriftObservation]) -> dict[str, int]:
    counts = {state: 0 for state in DRIFT_STATES}
    counts["invalid"] = 0
    for observation in observations:
        if observation.state in counts:
            counts[observation.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_drift_observation_ids(observations: tuple[RefreshDriftObservation, ...] | list[RefreshDriftObservation]) -> tuple[str, ...]:
    return tuple(
        observation.observation_id
        for observation in observations
        if observation.state in FAIL_VISIBLE_DRIFT_STATES and observation.fail_visible
    )


def validate_refresh_drift_visibility(certification: RefreshDriftCertification) -> dict[str, object]:
    state_counts = count_drift_observation_states(certification.drift_observations)
    observations_by_layer = {
        layer: tuple(observation.observation_id for observation in certification.drift_observations if observation.source_layer == layer)
        for layer in (DRIFT_LAYER_MANIFEST, DRIFT_LAYER_DEPENDENCY, DRIFT_LAYER_LINEAGE, DRIFT_LAYER_SCHEMA, DRIFT_LAYER_SEQUENCING)
    }
    blocked_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_BLOCKED)
    unsupported_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_UNSUPPORTED)
    stale_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_STALE)
    prohibited_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_PROHIBITED)
    conflict_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_CROSS_LAYER_CONFLICT)
    lineage_gap_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_LINEAGE_DISCONTINUITY)
    provenance_gap_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_PROVENANCE_DISCONTINUITY)
    replay_gap_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_REPLAY_DISCONTINUITY)
    rollback_gap_ids = tuple(item.observation_id for item in certification.drift_observations if item.state == DRIFT_STATE_ROLLBACK_DISCONTINUITY)
    layer = certification.layer_visibility
    classification = certification.classification_visibility
    blocked = certification.blocked_state_visibility
    unsupported = certification.unsupported_state_visibility
    hidden_observation_count = sum(1 for item in certification.drift_observations if item.hidden)
    observation_execution_count = sum(
        1
        for item in certification.drift_observations
        if item.drift_remediation_enabled
        or item.automatic_drift_correction_enabled
        or item.automatic_repair_enabled
        or item.refresh_execution_enabled
        or item.orchestration_enabled
        or item.automatic_sequencing_enabled
        or item.schema_migration_execution_enabled
        or item.planner_integration_enabled
        or item.production_consumption_enabled
        or item.runtime_mutation_enabled
        or item.silent_drift_suppression_enabled
    )
    prohibited_domains_visible = set(PROHIBITED_DRIFT_DOMAINS).issubset(set(unsupported.prohibited_drift_domains))
    classifications_visible = set(item.classification for item in certification.drift_observations).issubset(
        set(classification.classification_references)
    )
    visibility_failures = [
        bool(set(observations_by_layer[DRIFT_LAYER_MANIFEST]) - set(layer.manifest_drift_ids)),
        bool(set(observations_by_layer[DRIFT_LAYER_DEPENDENCY]) - set(layer.dependency_drift_ids)),
        bool(set(observations_by_layer[DRIFT_LAYER_LINEAGE]) - set(layer.lineage_drift_ids)),
        bool(set(observations_by_layer[DRIFT_LAYER_SCHEMA]) - set(layer.schema_drift_ids)),
        bool(set(observations_by_layer[DRIFT_LAYER_SEQUENCING]) - set(layer.sequencing_drift_ids)),
        bool(set(conflict_ids) - set(layer.cross_layer_conflict_ids)),
        bool(set(blocked_ids) - set(blocked.blocked_drift_ids)),
        bool(set(unsupported_ids) - set(unsupported.unsupported_drift_ids)),
        bool(set(stale_ids) - set(unsupported.stale_drift_ids)),
        bool(set(prohibited_ids) - set(unsupported.prohibited_drift_ids)),
        bool(set(lineage_gap_ids) - set(blocked.lineage_discontinuity_visibility)),
        bool(set(provenance_gap_ids) - set(blocked.provenance_discontinuity_visibility)),
        bool(set(replay_gap_ids) - set(blocked.replay_discontinuity_visibility)),
        bool(set(rollback_gap_ids) - set(blocked.rollback_discontinuity_visibility)),
        not prohibited_domains_visible,
        not classifications_visible,
    ]
    return {
        "observation_state_counts": state_counts,
        "fail_visible_observation_count": len(fail_visible_drift_observation_ids(certification.drift_observations)),
        "manifest_drift_visibility_count": len(layer.manifest_drift_ids),
        "dependency_drift_visibility_count": len(layer.dependency_drift_ids),
        "lineage_drift_visibility_count": len(layer.lineage_drift_ids),
        "schema_drift_visibility_count": len(layer.schema_drift_ids),
        "sequencing_drift_visibility_count": len(layer.sequencing_drift_ids),
        "cross_layer_conflict_visibility_count": len(layer.cross_layer_conflict_ids),
        "blocked_drift_visibility_count": len(blocked.blocked_drift_ids),
        "unsupported_drift_visibility_count": len(unsupported.unsupported_drift_ids),
        "stale_drift_visibility_count": len(unsupported.stale_drift_ids),
        "prohibited_drift_visibility_count": len(unsupported.prohibited_drift_ids),
        "unresolved_drift_visibility_count": len(blocked.unresolved_drift_ids),
        "lineage_discontinuity_visibility_count": len(blocked.lineage_discontinuity_visibility),
        "provenance_discontinuity_visibility_count": len(blocked.provenance_discontinuity_visibility),
        "replay_discontinuity_visibility_count": len(blocked.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility_count": len(blocked.rollback_discontinuity_visibility),
        "prohibited_drift_domain_visibility_count": len(unsupported.prohibited_drift_domains),
        "classification_visibility_count": len(classification.classification_references),
        "severity_visibility_count": len(classification.severity_references),
        "failure_visibility_count": len(unsupported.failure_visibility),
        "hidden_observation_count": hidden_observation_count,
        "invalid_observation_state_count": state_counts["invalid"],
        "observation_execution_semantics_count": observation_execution_count,
        "manifest_drift_visible": not bool(set(observations_by_layer[DRIFT_LAYER_MANIFEST]) - set(layer.manifest_drift_ids)),
        "dependency_drift_visible": not bool(set(observations_by_layer[DRIFT_LAYER_DEPENDENCY]) - set(layer.dependency_drift_ids)),
        "lineage_drift_visible": not bool(set(observations_by_layer[DRIFT_LAYER_LINEAGE]) - set(layer.lineage_drift_ids)),
        "schema_drift_visible": not bool(set(observations_by_layer[DRIFT_LAYER_SCHEMA]) - set(layer.schema_drift_ids)),
        "sequencing_drift_visible": not bool(set(observations_by_layer[DRIFT_LAYER_SEQUENCING]) - set(layer.sequencing_drift_ids)),
        "cross_layer_conflict_visible": not bool(set(conflict_ids) - set(layer.cross_layer_conflict_ids)),
        "blocked_drift_visible": not bool(set(blocked_ids) - set(blocked.blocked_drift_ids)),
        "unsupported_drift_visible": not bool(set(unsupported_ids) - set(unsupported.unsupported_drift_ids)),
        "stale_drift_visible": not bool(set(stale_ids) - set(unsupported.stale_drift_ids)),
        "prohibited_drift_visible": not bool(set(prohibited_ids) - set(unsupported.prohibited_drift_ids)),
        "lineage_discontinuity_visible": not bool(set(lineage_gap_ids) - set(blocked.lineage_discontinuity_visibility)),
        "provenance_discontinuity_visible": not bool(set(provenance_gap_ids) - set(blocked.provenance_discontinuity_visibility)),
        "replay_discontinuity_visible": not bool(set(replay_gap_ids) - set(blocked.replay_discontinuity_visibility)),
        "rollback_discontinuity_visible": not bool(set(rollback_gap_ids) - set(blocked.rollback_discontinuity_visibility)),
        "prohibited_drift_domains_visible": prohibited_domains_visible,
        "classifications_visible": classifications_visible,
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *certification.drift_observations,
                certification.layer_visibility,
                certification.classification_visibility,
                certification.continuity_metadata,
                certification.lineage_visibility,
                certification.provenance_visibility,
                certification.replay_visibility,
                certification.rollback_visibility,
                certification.blocked_state_visibility,
                certification.unsupported_state_visibility,
                certification.diagnostics,
                certification.governance,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_observation_count == 0
            and state_counts["invalid"] == 0
            and observation_execution_count == 0
        ),
    }


def build_default_refresh_drift_observations() -> tuple[RefreshDriftObservation, ...]:
    return default_refresh_drift_observations()


def build_default_refresh_drift_certification() -> RefreshDriftCertification:
    return default_refresh_drift_certification()
