from copy import deepcopy
from pathlib import Path

from app.game_data.bundle_item_adapter_translations import (
    get_adapter_translations,
    load_adapter_translations_fixture,
    validate_adapter_translations_fixture,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "bundle_item_type_adapter_translations.json"


def _fixture():
    return load_adapter_translations_fixture(FIXTURE_PATH)


def _translations():
    return _fixture()["translations"]


def test_adapter_translations_fixture_loads_and_validates():
    fixture = _fixture()

    errors, warnings = validate_adapter_translations_fixture(fixture)

    assert errors == []
    assert warnings == []


def test_adapter_translations_are_developer_only_and_not_production_safe():
    fixture = _fixture()

    assert fixture["production_safe"] is False
    assert all(translation["production_safe"] is False for translation in fixture["translations"])


def test_translation_count_and_required_context_are_locked():
    translations = _translations()

    assert len(translations) == 15
    assert all("base_type_id" in translation["required_context"] for translation in translations)
    assert all(translation["required_context"] != ["subtype_id"] for translation in translations)


def test_no_name_only_or_spear_translation_exists():
    translations = _translations()

    assert "spear" not in {translation["forge_item_type"] for translation in translations}
    assert all(translation["source"] == "base_type_id" for translation in translations)
    assert all(translation.get("match_method") != "subtype_id" for translation in translations)


def test_weapon_split_translations_exist_for_collapsed_slugs():
    translations = _translations()
    by_pair = {
        (translation["forge_item_type"], translation["bundle_base_type_id"]): translation
        for translation in translations
    }

    assert by_pair[("axe", 5)]["bundle_item_type_id"] == "one_handed_axe"
    assert by_pair[("axe", 12)]["bundle_item_type_id"] == "two_handed_axe"
    assert by_pair[("mace", 7)]["bundle_item_type_id"] == "one_handed_maces"
    assert by_pair[("mace", 13)]["bundle_item_type_id"] == "two_handed_mace"
    assert by_pair[("sword", 9)]["bundle_item_type_id"] == "one_handed_sword"
    assert by_pair[("sword", 16)]["bundle_item_type_id"] == "two_handed_sword"
    assert {
        by_pair[("axe", 5)]["translation_type"],
        by_pair[("axe", 12)]["translation_type"],
    } == {"weapon_type_distinction"}


def test_idol_split_translations_exist():
    translations = _translations()
    idol = {
        translation["bundle_base_type_id"]: translation["bundle_item_type_id"]
        for translation in translations
        if translation["forge_item_type"] == "idol_1x1"
    }

    assert idol == {
        25: "idol_1x1_eterra",
        26: "idol_1x1_lagon",
    }


def test_polearm_maps_only_to_two_handed_spear_with_base_type_context():
    polearm = [translation for translation in _translations() if translation["forge_item_type"] == "polearm"]

    assert len(polearm) == 1
    assert polearm[0]["bundle_item_type_id"] == "two_handed_spear"
    assert polearm[0]["bundle_base_type_id"] == 14
    assert polearm[0]["required_context"] == ["base_type_id"]


def test_duplicate_conflicting_mappings_are_rejected():
    fixture = _fixture()
    duplicate = deepcopy(fixture["translations"][0])
    duplicate["bundle_item_type_id"] = "conflicting_helmet"
    fixture["translations"].append(duplicate)

    errors, _warnings = validate_adapter_translations_fixture(fixture)

    assert any("conflicts with another translation" in error for error in errors)


def test_subtype_only_context_is_rejected():
    fixture = _fixture()
    fixture["translations"][0]["required_context"] = ["subtype_id"]

    errors, _warnings = validate_adapter_translations_fixture(fixture)

    assert any("must require base_type_id context" in error for error in errors)
    assert any("must not require only subtype_id context" in error for error in errors)


def test_get_adapter_translations_returns_read_only_copy():
    translations = get_adapter_translations(FIXTURE_PATH)
    translations[0]["forge_item_type"] = "mutated"

    assert _translations()[0]["forge_item_type"] == "helm"
