"""Fail-visible lifecycle visibility helpers for v4.0 patch foundations."""

from __future__ import annotations

from .lifecycle_models import (
    FAIL_VISIBLE_LIFECYCLE_STATES,
    LIFECYCLE_STATE_PROHIBITED,
    LIFECYCLE_STATE_UNKNOWN,
    LIFECYCLE_STATE_UNSUPPORTED,
    LIFECYCLE_STATES,
    LifecycleState,
    PatchLifecycleFoundation,
    default_lifecycle_states,
    default_lifecycle_visibility_record,
)


def count_lifecycle_states(states: tuple[LifecycleState, ...] | list[LifecycleState]) -> dict[str, int]:
    counts = {state: 0 for state in LIFECYCLE_STATES}
    counts["invalid"] = 0
    for state in states:
        if state.state in counts:
            counts[state.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def invalid_lifecycle_state_ids(states: tuple[LifecycleState, ...] | list[LifecycleState]) -> tuple[str, ...]:
    return tuple(state.state_id for state in states if state.state not in LIFECYCLE_STATES)


def fail_visible_lifecycle_state_ids(states: tuple[LifecycleState, ...] | list[LifecycleState]) -> tuple[str, ...]:
    return tuple(state.state_id for state in states if state.state in FAIL_VISIBLE_LIFECYCLE_STATES and state.fail_visible)


def validate_lifecycle_visibility(foundation: PatchLifecycleFoundation) -> dict[str, object]:
    states = foundation.lifecycle_states
    visibility_records = foundation.visibility_records
    unsupported_ids = tuple(state.state_id for state in states if state.state == LIFECYCLE_STATE_UNSUPPORTED)
    prohibited_ids = tuple(state.state_id for state in states if state.state == LIFECYCLE_STATE_PROHIBITED)
    unknown_ids = tuple(state.state_id for state in states if state.state == LIFECYCLE_STATE_UNKNOWN)
    visibility_unsupported = tuple(
        item for record in visibility_records for item in record.unsupported_state_visibility
    )
    visibility_prohibited = tuple(
        item for record in visibility_records for item in record.prohibited_state_visibility
    )
    visibility_unknown = tuple(item for record in visibility_records for item in record.unknown_state_visibility)
    hidden_state_count = sum(1 for state in states if state.hidden)
    invalid_state_ids = invalid_lifecycle_state_ids(states)
    hidden_visibility_count = sum(1 for record in visibility_records if record.hidden)
    corrective_visibility_count = sum(
        1
        for record in visibility_records
        if record.remediation_enabled
        or record.automatic_resolution_enabled
        or record.corrective_behavior_enabled
        or record.silent_omission_enabled
    )
    state_execution_count = sum(
        1
        for state in states
        if state.executable
        or state.transition_allowed
        or state.authorization_semantics_enabled
        or state.auto_transition_enabled
        or state.silently_corrected
        or state.fallback_applied
    )
    visibility_failures = [
        bool(set(unsupported_ids) - set(visibility_unsupported)),
        bool(set(prohibited_ids) - set(visibility_prohibited)),
        bool(set(unknown_ids) - set(visibility_unknown)),
    ]
    return {
        "state_counts": count_lifecycle_states(states),
        "fail_visible_lifecycle_state_count": len(fail_visible_lifecycle_state_ids(states)),
        "unsupported_state_visibility_count": len(visibility_unsupported),
        "prohibited_state_visibility_count": len(visibility_prohibited),
        "unknown_state_visibility_count": len(visibility_unknown),
        "integrity_warning_visibility_count": sum(
            len(record.integrity_warning_visibility) for record in visibility_records
        ),
        "lifecycle_continuity_visibility_count": sum(
            len(record.lifecycle_continuity_visibility) for record in visibility_records
        ),
        "lineage_gap_visibility_count": sum(len(record.lineage_gap_visibility) for record in visibility_records),
        "hidden_state_count": hidden_state_count,
        "invalid_lifecycle_state_count": len(invalid_state_ids),
        "hidden_visibility_count": hidden_visibility_count,
        "corrective_visibility_count": corrective_visibility_count,
        "state_execution_semantics_count": state_execution_count,
        "unsupported_states_visible": not bool(set(unsupported_ids) - set(visibility_unsupported)),
        "prohibited_states_visible": not bool(set(prohibited_ids) - set(visibility_prohibited)),
        "unknown_states_visible": not bool(set(unknown_ids) - set(visibility_unknown)),
        "visibility_is_descriptive_only": all(record.descriptive_only for record in visibility_records),
        "valid": (
            not any(visibility_failures)
            and hidden_state_count == 0
            and len(invalid_state_ids) == 0
            and hidden_visibility_count == 0
            and corrective_visibility_count == 0
            and state_execution_count == 0
            and all(record.descriptive_only for record in visibility_records)
        ),
    }


def build_default_lifecycle_states() -> tuple[LifecycleState, ...]:
    return default_lifecycle_states()


def build_default_lifecycle_visibility_record():
    return default_lifecycle_visibility_record()
