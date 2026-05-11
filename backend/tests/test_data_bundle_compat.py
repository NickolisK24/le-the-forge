import json
from pathlib import Path
import shutil
import uuid

import pytest

from app.game_data.bundle_compat import (
    STATUS_COMPATIBLE_WITH_WARNINGS,
    STATUS_INCOMPATIBLE,
    check_bundle_compatibility,
)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def bundle_root():
    root = Path(__file__).resolve().parent / "_bundle_compat_tmp" / uuid.uuid4().hex
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _bundle(root: Path) -> Path:
    bundle = root / "data_bundle"
    bundle_id = "test-bundle"
    families = [
        {
            "family": "metadata",
            "path": "metadata.json",
            "requirement_level": "Required Now",
            "readiness_level": "Normalized",
            "canonical_migration_state": "Hybrid",
            "feature_status": "Advisory",
            "validation_status": "warning",
            "deferred": False,
            "stale": False,
            "consumer_contract": {"fallback_policy": "warn"},
        },
        {
            "family": "base_items",
            "path": "families/base_items.json",
            "requirement_level": "Required Now",
            "readiness_level": "Raw Extracted",
            "canonical_migration_state": "Hybrid",
            "feature_status": "Advisory",
            "validation_status": "deferred",
            "deferred": True,
            "stale": False,
            "consumer_contract": {"fallback_policy": "block"},
        },
    ]
    _write_json(
        bundle / "metadata.json",
        {
            "bundle_id": bundle_id,
            "game_version": "1.4.6",
            "build_number": "22986002",
            "data_patch": "1.4.6",
            "bundle_schema_version": "1.0.0",
        },
    )
    _write_json(
        bundle / "manifest.json",
        {
            "bundle_id": bundle_id,
            "manifest_schema_version": "1.0.0",
            "consumer_contract": {"default_action_on_unknown_family": "ignore"},
            "action_summary": {
                "load": [],
                "warn": ["metadata"],
                "degrade": [],
                "block": ["base_items"],
                "ignore": [],
            },
            "families": families,
        },
    )
    _write_json(
        bundle / "validation_status.json",
        {
            "bundle_id": bundle_id,
            "status": "warning",
            "family_status": {
                "metadata": {"status": "warning", "action_required": "warn"},
                "base_items": {"status": "deferred", "action_required": "block"},
            },
        },
    )
    _write_json(
        bundle / "reports" / "known_gaps.json",
        {"bundle_id": bundle_id, "gaps": [{"gap_id": "gap.one"}]},
    )
    _write_text(bundle / "reports" / "migration_notes.md", "# Notes\n")
    return bundle


def test_valid_warning_bundle_returns_compatible_with_warnings(bundle_root):
    result = check_bundle_compatibility(_bundle(bundle_root))

    assert result.status == STATUS_COMPATIBLE_WITH_WARNINGS
    assert result.bundle_id == "test-bundle"
    assert result.known_gap_count == 1


def test_missing_metadata_returns_incompatible(bundle_root):
    bundle = _bundle(bundle_root)
    (bundle / "metadata.json").unlink()

    result = check_bundle_compatibility(bundle)

    assert result.status == STATUS_INCOMPATIBLE
    assert any("Missing metadata.json" in error for error in result.errors)


def test_bundle_id_mismatch_returns_incompatible(bundle_root):
    bundle = _bundle(bundle_root)
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    metadata["bundle_id"] = "different"
    _write_json(bundle / "metadata.json", metadata)

    result = check_bundle_compatibility(bundle)

    assert result.status == STATUS_INCOMPATIBLE
    assert any("bundle_id mismatch" in error for error in result.errors)


def test_block_actions_are_reported_but_not_incompatible(bundle_root):
    result = check_bundle_compatibility(_bundle(bundle_root))

    assert result.status == STATUS_COMPATIBLE_WITH_WARNINGS
    assert "base_items" in result.blocked_families
    assert not result.errors


def test_missing_known_gaps_warns_but_does_not_fail(bundle_root):
    bundle = _bundle(bundle_root)
    (bundle / "reports" / "known_gaps.json").unlink()

    result = check_bundle_compatibility(bundle)

    assert result.status == STATUS_COMPATIBLE_WITH_WARNINGS
    assert any("known_gaps.json" in warning for warning in result.warnings)
    assert not result.errors
