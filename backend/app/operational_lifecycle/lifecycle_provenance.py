"""Lifecycle provenance continuity helpers for v4.0 foundations."""

from __future__ import annotations

from .lifecycle_models import LifecycleProvenanceRecord, default_lifecycle_provenance_record
from .lifecycle_serialization import export_lifecycle_provenance_record


def lifecycle_provenance_key(record: LifecycleProvenanceRecord) -> str:
    return "|".join(
        (
            record.provenance_scope,
            record.source_patch_reference,
            record.extraction_reference,
            record.schema_reference,
            record.provenance_reference_id,
        )
    )


def normalize_lifecycle_provenance(record: LifecycleProvenanceRecord) -> LifecycleProvenanceRecord:
    exported = export_lifecycle_provenance_record(record)
    return LifecycleProvenanceRecord(**exported)


def validate_lifecycle_provenance_continuity(record: LifecycleProvenanceRecord) -> dict[str, object]:
    return {
        "provenance_reference_id": record.provenance_reference_id,
        "provenance_key": lifecycle_provenance_key(record),
        "provenance_preserved": record.provenance_preserved,
        "no_inferred_provenance": record.no_inferred_provenance and not record.inferred_provenance_allowed,
        "hidden": record.hidden,
        "descriptive_only": record.descriptive_only,
        "execution_enabled": record.execution_enabled,
        "continuity_reference_count": len(record.continuity_references),
        "source_evidence_reference_count": len(record.source_evidence_references),
        "trusted_bundle_reference_present": bool(record.trusted_bundle_reference),
        "refresh_chain_reference_present": bool(record.refresh_chain_reference),
        "provenance_continuity_visible": bool(record.continuity_references),
        "valid": (
            record.provenance_preserved
            and record.no_inferred_provenance
            and not record.inferred_provenance_allowed
            and not record.hidden
            and record.descriptive_only
            and not record.execution_enabled
            and bool(record.continuity_references)
            and bool(record.source_evidence_references)
            and bool(record.trusted_bundle_reference)
            and bool(record.refresh_chain_reference)
        ),
    }


def build_default_lifecycle_provenance_record() -> LifecycleProvenanceRecord:
    return default_lifecycle_provenance_record()
