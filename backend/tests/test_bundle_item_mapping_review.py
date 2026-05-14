from pathlib import Path

from app.game_data.bundle_item_mapping_review import (
    REQUIRED_CATEGORIES,
    REQUIRED_ENTRY_FIELDS,
    load_mapping_review_fixture,
    validate_mapping_review_fixture,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "bundle_item_type_mapping_review.json"


def _fixture():
    return load_mapping_review_fixture(FIXTURE_PATH)


def _entries(fixture):
    for entries in fixture["categories"].values():
        yield from entries


def test_mapping_review_fixture_loads_and_validates():
    fixture = _fixture()

    errors, warnings = validate_mapping_review_fixture(fixture)

    assert errors == []
    assert warnings == []


def test_mapping_review_fixture_has_required_top_level_shape():
    fixture = _fixture()

    assert fixture["fixture"] == "bundle_item_type_mapping_review"
    assert fixture["production_safe"] is False
    assert fixture["source_report"] == "docs/generated/bundle_item_adapter_map_report.md"
    assert set(fixture["categories"]) == set(REQUIRED_CATEGORIES)


def test_mapping_review_entry_fields_are_complete():
    fixture = _fixture()

    for entry in _entries(fixture):
        assert set(REQUIRED_ENTRY_FIELDS).issubset(entry)
        assert entry["production_safe"] is False
        assert isinstance(entry["notes"], list)


def test_accepted_mappings_are_id_backed_and_conservative():
    accepted = _fixture()["categories"]["accepted"]

    assert len(accepted) == 19
    assert all(entry["match_method"] == "base_type_id" for entry in accepted)
    assert all(entry["forge_item_type"] == entry["bundle_item_type_id"] for entry in accepted)
    assert all(entry["confidence"] == "Verified" for entry in accepted)


def test_adapter_and_review_categories_are_locked():
    categories = _fixture()["categories"]

    assert len(categories["needs_adapter"]) == 15
    assert len(categories["needs_review"]) == 9
    assert len(categories["deferred"]) == 8
    assert len(categories["unsafe"]) == 0
    assert all(entry["match_method"] == "base_type_id" for entry in categories["needs_adapter"])


def test_no_subtype_id_only_or_name_only_accepted_mapping():
    fixture = _fixture()

    for entry in _entries(fixture):
        assert entry["match_method"] != "subtype_id"
    assert all(
        entry["match_method"] not in {"normalized_name", "exact_slug"}
        for entry in fixture["categories"]["accepted"]
    )


def test_spear_is_not_accepted():
    fixture = _fixture()

    accepted_forge_types = {entry["forge_item_type"] for entry in fixture["categories"]["accepted"]}
    review_forge_types = {entry["forge_item_type"] for entry in fixture["categories"]["needs_review"]}

    assert "spear" not in accepted_forge_types
    assert "spear" in review_forge_types


def test_bundle_only_types_remain_review_or_deferred():
    categories = _fixture()["categories"]
    review_bundle_ids = {entry["bundle_item_type_id"] for entry in categories["needs_review"]}
    deferred_bundle_ids = {entry["bundle_item_type_id"] for entry in categories["deferred"]}

    assert {"blessing", "greater_lens", "idol_altar"}.issubset(review_bundle_ids)
    assert {"affix_shard", "rune", "glyph", "key", "bag"}.issubset(deferred_bundle_ids)


def test_fixture_count_matches_current_reviewed_report_split():
    categories = _fixture()["categories"]
    total = sum(len(entries) for entries in categories.values())

    assert total == 51
    assert {
        "accepted": 19,
        "needs_adapter": 15,
        "needs_review": 9,
        "deferred": 8,
        "unsafe": 0,
    } == {category: len(entries) for category, entries in categories.items()}
