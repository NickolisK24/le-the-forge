import json
from pathlib import Path
import shutil
import uuid

import pytest

from app.game_data.bundle_item_diff import (
    ItemDiffResult,
    STATUS_FAIL,
    STATUS_WARN,
    _inspect_subtype_identity_risk,
    run_item_bundle_diff,
)


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def bundle_root():
    root = Path(__file__).resolve().parent / "_bundle_item_diff_tmp" / uuid.uuid4().hex
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _bundle(root: Path) -> Path:
    bundle = root / "data_bundle"
    _write_json(bundle / "metadata.json", {"bundle_id": "test"})
    _write_json(bundle / "manifest.json", {"bundle_id": "test"})
    _write_json(
        bundle / "families" / "item_types.json",
        {
            "family": "item_types",
            "record_count": 2,
            "records": [
                {"id": "helm", "base_type_id": 0, "game_id": 0, "name": "Helmet"},
                {"id": "body_armor", "base_type_id": 1, "game_id": 1, "name": "Body Armor"},
            ],
        },
    )
    _write_json(
        bundle / "families" / "base_items.json",
        {
            "family": "base_items",
            "record_count": 2,
            "records": [
                {
                    "id": "helm__0__a",
                    "base_type_id": 0,
                    "subtype_id": 0,
                    "name": "A",
                    "item_type": "helm",
                    "requirements": {"level": 1, "class": None, "mastery": None},
                    "implicit_refs": [],
                    "tags": [],
                },
                {
                    "id": "body_armor__0__b",
                    "base_type_id": 1,
                    "subtype_id": 0,
                    "name": "B",
                    "item_type": "body_armor",
                    "requirements": {"level": 1, "class": None, "mastery": None},
                    "implicit_refs": [],
                    "tags": [],
                },
            ],
        },
    )
    return bundle


def test_fake_bundle_loads_with_expected_warnings(bundle_root):
    result = run_item_bundle_diff(_bundle(bundle_root))

    assert result.status == STATUS_WARN
    assert result.bundle_item_types_count == 2
    assert result.bundle_base_items_count == 2


def test_duplicate_bundle_item_type_ids_fail(bundle_root):
    bundle = _bundle(bundle_root)
    item_types_path = bundle / "families" / "item_types.json"
    data = json.loads(item_types_path.read_text(encoding="utf-8"))
    data["records"][1]["id"] = "helm"
    _write_json(item_types_path, data)

    result = run_item_bundle_diff(bundle)

    assert result.status == STATUS_FAIL
    assert any("Duplicate bundle item_type IDs" in finding.message for finding in result.findings)


def test_duplicate_base_item_composite_ids_fail(bundle_root):
    bundle = _bundle(bundle_root)
    base_items_path = bundle / "families" / "base_items.json"
    data = json.loads(base_items_path.read_text(encoding="utf-8"))
    data["records"][1]["base_type_id"] = 0
    data["records"][1]["subtype_id"] = 0
    _write_json(base_items_path, data)

    result = run_item_bundle_diff(bundle)

    assert result.status == STATUS_FAIL
    assert any("Duplicate bundle base_type_id/subtype_id" in finding.message for finding in result.findings)


def test_repeated_subtype_ids_across_base_types_are_allowed(bundle_root):
    result = run_item_bundle_diff(_bundle(bundle_root))

    assert result.status != STATUS_FAIL
    assert any("subtype_id values repeat across base types" in finding.message for finding in result.findings)


def test_missing_bundle_file_fails(bundle_root):
    bundle = _bundle(bundle_root)
    (bundle / "families" / "base_items.json").unlink()

    result = run_item_bundle_diff(bundle)

    assert result.status == STATUS_FAIL
    assert any("Missing bundle family file" in finding.message for finding in result.findings)


def test_subtype_id_only_identity_warning_is_reported():
    result = ItemDiffResult()

    _inspect_subtype_identity_risk({"subtype_id_to_item_type_id": {0: "helm"}}, result)

    assert result.status == STATUS_WARN
    assert result.subtype_identity_risks
