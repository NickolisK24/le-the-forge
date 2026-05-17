"""Lifecycle lineage normalization for v4.0 patch foundations."""

from __future__ import annotations

from .lifecycle_models import LifecycleLineageRecord, default_lifecycle_lineage_record
from .lifecycle_serialization import export_lifecycle_lineage_record


def lifecycle_lineage_key(record: LifecycleLineageRecord) -> str:
    return "|".join((record.lineage_scope, record.lineage_reference_id, str(record.deterministic_order)))


def normalize_lifecycle_lineage(record: LifecycleLineageRecord) -> LifecycleLineageRecord:
    exported = export_lifecycle_lineage_record(record)
    return LifecycleLineageRecord(**exported)


def validate_lifecycle_lineage_continuity(record: LifecycleLineageRecord) -> dict[str, object]:
    return {
        "lineage_reference_id": record.lineage_reference_id,
        "lineage_key": lifecycle_lineage_key(record),
        "prior_bundle_reference_count": len(record.prior_bundle_references),
        "successor_reference_count": len(record.successor_references),
        "continuity_reference_count": len(record.continuity_references),
        "rollback_reference_count": len(record.rollback_references),
        "provenance_continuity_reference_count": len(record.provenance_continuity_references),
        "trusted_bundle_reference_count": len(record.trusted_bundle_references),
        "refresh_chain_reference_count": len(record.refresh_chain_references),
        "fail_visible_lineage_gap_count": len(record.fail_visible_lineage_gap_ids),
        "lineage_preserved": record.lineage_preserved,
        "replay_safe": record.replay_safe,
        "rollback_safe": record.rollback_safe,
        "descriptive_only": record.descriptive_only,
        "execution_enabled": record.execution_enabled,
        "automatic_transition_enabled": record.automatic_transition_enabled,
        "hidden_lineage_gap_correction_enabled": record.hidden_lineage_gap_correction_enabled,
        "valid": (
            record.lineage_preserved
            and record.replay_safe
            and record.rollback_safe
            and record.descriptive_only
            and not record.execution_enabled
            and not record.automatic_transition_enabled
            and not record.hidden_lineage_gap_correction_enabled
            and bool(record.prior_bundle_references)
            and bool(record.continuity_references)
            and bool(record.rollback_references)
            and bool(record.provenance_continuity_references)
            and bool(record.trusted_bundle_references)
            and bool(record.refresh_chain_references)
        ),
    }


def build_default_lifecycle_lineage_record() -> LifecycleLineageRecord:
    return default_lifecycle_lineage_record()
