"""Fail-visible visibility helpers for v4.1 refresh manifest foundations."""

from __future__ import annotations

from .refresh_manifest_models import (
    FAIL_VISIBLE_REFRESH_MANIFEST_STATES,
    REFRESH_MANIFEST_STATE_BLOCKED,
    REFRESH_MANIFEST_STATE_PROHIBITED,
    REFRESH_MANIFEST_STATE_STALE,
    REFRESH_MANIFEST_STATE_UNKNOWN,
    REFRESH_MANIFEST_STATE_UNSUPPORTED,
    REFRESH_MANIFEST_STATES,
    RefreshManifest,
    RefreshManifestState,
    default_refresh_manifest,
    default_refresh_manifest_states,
)


def count_refresh_manifest_states(states: tuple[RefreshManifestState, ...] | list[RefreshManifestState]) -> dict[str, int]:
    counts = {state: 0 for state in REFRESH_MANIFEST_STATES}
    counts["invalid"] = 0
    for state in states:
        if state.state in counts:
            counts[state.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def invalid_refresh_manifest_state_ids(
    states: tuple[RefreshManifestState, ...] | list[RefreshManifestState],
) -> tuple[str, ...]:
    return tuple(state.state_id for state in states if state.state not in REFRESH_MANIFEST_STATES)


def fail_visible_refresh_manifest_state_ids(
    states: tuple[RefreshManifestState, ...] | list[RefreshManifestState],
) -> tuple[str, ...]:
    return tuple(state.state_id for state in states if state.state in FAIL_VISIBLE_REFRESH_MANIFEST_STATES and state.fail_visible)


def validate_refresh_manifest_visibility(manifest: RefreshManifest) -> dict[str, object]:
    states = manifest.states
    unsupported_ids = tuple(state.state_id for state in states if state.state == REFRESH_MANIFEST_STATE_UNSUPPORTED)
    unknown_ids = tuple(state.state_id for state in states if state.state == REFRESH_MANIFEST_STATE_UNKNOWN)
    blocked_ids = tuple(state.state_id for state in states if state.state == REFRESH_MANIFEST_STATE_BLOCKED)
    prohibited_ids = tuple(state.state_id for state in states if state.state == REFRESH_MANIFEST_STATE_PROHIBITED)
    stale_ids = tuple(state.state_id for state in states if state.state == REFRESH_MANIFEST_STATE_STALE)
    visibility_unsupported = tuple(
        item for record in manifest.unsupported_state_visibility for item in record.unsupported_states
    )
    visibility_unknown = tuple(item for record in manifest.unsupported_state_visibility for item in record.unknown_states)
    visibility_blocked = tuple(item for record in manifest.unsupported_state_visibility for item in record.blocked_states)
    visibility_prohibited = tuple(item for record in manifest.unsupported_state_visibility for item in record.prohibited_states)
    visibility_stale = tuple(item for record in manifest.unsupported_state_visibility for item in record.stale_states)
    prohibited_domains = tuple(
        domain for record in manifest.prohibited_domain_visibility for domain in record.prohibited_domains
    )
    visible_blocked_reasons = tuple(
        reason for record in manifest.prohibited_domain_visibility for reason in record.visible_blocked_reasons
    )
    hidden_state_count = sum(1 for state in states if state.hidden)
    invalid_state_ids = invalid_refresh_manifest_state_ids(states)
    corrective_state_count = sum(
        1
        for state in states
        if state.automatic_resolution_enabled
        or state.silent_fallback_enabled
        or state.remediation_enabled
        or state.runtime_mutation_enabled
    )
    state_execution_count = sum(1 for state in states if state.executable)
    hidden_visibility_count = sum(
        1
        for record in (
            *manifest.source_lineage,
            *manifest.extraction_lineage,
            *manifest.patch_lineage,
            *manifest.schema_version_visibility,
            *manifest.dependency_visibility,
            *manifest.validation_visibility,
            *manifest.prohibited_domain_visibility,
            *manifest.unsupported_state_visibility,
            *manifest.diagnostics_visibility,
        )
        if getattr(record, "hidden_source_resolution_enabled", False)
        or getattr(record, "hidden_extraction_fallback_enabled", False)
        or getattr(record, "hidden_patch_resolution_enabled", False)
        or getattr(record, "hidden_schema_inference_enabled", False)
        or getattr(record, "hidden_dependency_resolution_enabled", False)
        or getattr(record, "silent_validation_fallback_enabled", False)
        or getattr(record, "hidden_operational_behavior_enabled", False)
        or getattr(record, "hidden_unsupported_state_resolution_enabled", False)
        or getattr(record, "silent_fallback_enabled", False)
    )
    corrective_visibility_count = sum(
        1
        for record in (
            *manifest.validation_visibility,
            *manifest.unsupported_state_visibility,
            *manifest.diagnostics_visibility,
        )
        if getattr(record, "remediation_enabled", False)
        or getattr(record, "automatic_recovery_enabled", False)
        or getattr(record, "automatic_validation_execution_enabled", False)
    )
    visibility_failures = [
        bool(set(unsupported_ids) - set(visibility_unsupported)),
        bool(set(unknown_ids) - set(visibility_unknown)),
        bool(set(blocked_ids) - set(visibility_blocked)),
        bool(set(prohibited_ids) - set(visibility_prohibited)),
        bool(set(stale_ids) - set(visibility_stale)),
    ]
    return {
        "state_counts": count_refresh_manifest_states(states),
        "fail_visible_refresh_manifest_state_count": len(fail_visible_refresh_manifest_state_ids(states)),
        "unsupported_state_visibility_count": len(visibility_unsupported),
        "unknown_state_visibility_count": len(visibility_unknown),
        "blocked_state_visibility_count": len(visibility_blocked),
        "prohibited_state_visibility_count": len(visibility_prohibited),
        "stale_state_visibility_count": len(visibility_stale),
        "prohibited_domain_visibility_count": len(prohibited_domains),
        "visible_blocked_reason_count": len(visible_blocked_reasons),
        "dependency_warning_visibility_count": sum(
            len(record.missing_dependency_visibility)
            + len(record.stale_dependency_visibility)
            + len(record.prohibited_dependency_visibility)
            for record in manifest.dependency_visibility
        ),
        "trust_warning_visibility_count": sum(
            len(record.untrusted_source_visibility) + len(record.ambiguous_trust_visibility)
            for record in manifest.trust_visibility
        ),
        "validation_warning_visibility_count": sum(
            len(record.validation_warning_visibility)
            + len(record.validation_blocker_visibility)
            + len(record.unsupported_validation_visibility)
            for record in manifest.validation_visibility
        ),
        "diagnostics_warning_visibility_count": sum(
            len(record.warning_visibility)
            + len(record.blocker_visibility)
            + len(record.unsupported_state_visibility)
            + len(record.prohibited_domain_visibility)
            for record in manifest.diagnostics_visibility
        ),
        "governance_limitation_count": len(manifest.governance_visibility.explicit_limitations),
        "governance_prohibition_count": len(manifest.governance_visibility.explicit_prohibitions),
        "hidden_state_count": hidden_state_count,
        "invalid_refresh_manifest_state_count": len(invalid_state_ids),
        "corrective_state_count": corrective_state_count,
        "state_execution_semantics_count": state_execution_count,
        "hidden_visibility_count": hidden_visibility_count,
        "corrective_visibility_count": corrective_visibility_count,
        "unsupported_states_visible": not bool(set(unsupported_ids) - set(visibility_unsupported)),
        "unknown_states_visible": not bool(set(unknown_ids) - set(visibility_unknown)),
        "blocked_states_visible": not bool(set(blocked_ids) - set(visibility_blocked)),
        "prohibited_states_visible": not bool(set(prohibited_ids) - set(visibility_prohibited)),
        "stale_states_visible": not bool(set(stale_ids) - set(visibility_stale)),
        "prohibited_domains_visible": len(prohibited_domains) == len(visible_blocked_reasons),
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *manifest.source_lineage,
                *manifest.extraction_lineage,
                *manifest.patch_lineage,
                *manifest.schema_version_visibility,
                *manifest.dependency_visibility,
                *manifest.trust_visibility,
                *manifest.validation_visibility,
                *manifest.prohibited_domain_visibility,
                *manifest.unsupported_state_visibility,
                *manifest.diagnostics_visibility,
                manifest.governance_visibility,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_state_count == 0
            and len(invalid_state_ids) == 0
            and corrective_state_count == 0
            and state_execution_count == 0
            and hidden_visibility_count == 0
            and corrective_visibility_count == 0
            and len(prohibited_domains) == len(visible_blocked_reasons)
        ),
    }


def build_default_refresh_manifest_states() -> tuple[RefreshManifestState, ...]:
    return default_refresh_manifest_states()


def build_default_refresh_manifest() -> RefreshManifest:
    return default_refresh_manifest()
