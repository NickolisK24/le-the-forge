from pathlib import Path

from scripts.report_v2_source_inventory import (
    build_inventory,
    classify_source,
)


def test_generated_report_is_audit_record_not_runtime_source():
    source = classify_source(Path("docs/generated/example_report.json"))

    assert source["data_category"] == "generated_files"
    assert source["source_kind"] == "generated"
    assert source["current_trust_status"] == "partial"
    assert source["should_remain_for_v2"] == "yes_audit_record"
    assert source["should_be_replaced_or_remapped"] is False


def test_manual_backend_mapping_requires_remap():
    source = classify_source(Path("backend/app/constants/item_type_to_slot.py"))

    assert source["data_category"] == "items"
    assert source["source_kind"] == "manual"
    assert source["should_be_replaced_or_remapped"] is True
    assert source["migration_priority"] == "critical"


def test_fixture_remains_test_only():
    source = classify_source(Path("backend/tests/fixtures/sample_character.json"))

    assert source["data_category"] == "fixtures"
    assert source["source_kind"] == "fixture"
    assert source["current_trust_status"] == "unsupported"
    assert source["should_remain_for_v2"] == "test_only"


def test_inventory_metadata_and_consumer_detection(tmp_path):
    root = tmp_path
    data_path = root / "data" / "classes" / "classes.json"
    consumer_path = root / "frontend" / "src" / "logic" / "loadClasses.ts"
    data_path.parent.mkdir(parents=True)
    consumer_path.parent.mkdir(parents=True)
    data_path.write_text("[]", encoding="utf-8")
    consumer_path.write_text("fetch('/data/classes/classes.json')", encoding="utf-8")

    report = build_inventory(root, [data_path, consumer_path])

    assert report["metadata"]["read_only"] is True
    assert report["metadata"]["production_safe"] is False
    assert report["summary"]["source_count"] == 2
    classes_source = next(
        source
        for source in report["sources"]
        if source["source_path"] == "data/classes/classes.json"
    )
    assert classes_source["current_consumer_paths"] == [
        "frontend/src/logic/loadClasses.ts"
    ]
