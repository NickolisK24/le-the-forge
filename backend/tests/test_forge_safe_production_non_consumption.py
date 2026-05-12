from pathlib import Path

import pytest


SENTINEL_AFFIX_ID = 99999999
SENTINEL_AFFIX_NAME = "__SENTINEL_FORGE_SAFE_DO_NOT_CONSUME__"
SENTINEL_MODIFIER_ID = "__SENTINEL_MODIFIER_DO_NOT_CONSUME__"
SENTINEL_BUNDLE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "forge_safe_affix_bundle_sentinel.json"
)


@pytest.fixture
def forge_safe_bundle_flags(app):
    previous = {
        "FORGE_SAFE_AFFIX_CATALOG_ENABLED": app.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED"),
        "FORGE_SAFE_AFFIX_BUNDLE_ENABLED": app.config.get("FORGE_SAFE_AFFIX_BUNDLE_ENABLED"),
        "FORGE_SAFE_AFFIX_BUNDLE_PATH": app.config.get("FORGE_SAFE_AFFIX_BUNDLE_PATH"),
        "FORGE_SAFE_AFFIX_EXPORT_PATH": app.config.get("FORGE_SAFE_AFFIX_EXPORT_PATH"),
    }
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_PATH"] = str(SENTINEL_BUNDLE_PATH)
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = ""
    yield
    app.config.update(previous)


def test_ref_affixes_ignores_forge_safe_bundle_flags(client, forge_safe_bundle_flags):
    # Migration safety guard: forge-safe bundle data is allowed only in
    # experimental/debug paths until comparison and migration gates are complete.
    response = client.get("/api/ref/affixes?tag=__production_non_consumption_guard__")

    assert response.status_code == 200
    body = response.get_json()
    assert set(body) == {"data", "meta", "errors"}
    assert body["errors"] is None
    assert isinstance(body["data"], list)
    assert not _contains_sentinel(body["data"])


def test_experimental_affix_catalog_consumes_sentinel_bundle(client, forge_safe_bundle_flags):
    response = client.get("/experimental/forge-safe-affixes?include_modifiers=true")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["experimental"] is True
    assert body["read_only"] is True
    assert body["production_consumer"] is False
    assert body["data_source"] == "forge_safe_affix_bundle"
    assert body["records"][0]["affix_id"] == SENTINEL_AFFIX_ID
    assert body["records"][0]["affix_name"] == SENTINEL_AFFIX_NAME
    assert body["records"][0]["modifiers"][0]["modifier_id"] == SENTINEL_MODIFIER_ID


def test_crafting_engine_does_not_load_forge_safe_bundle(
    app,
    forge_safe_bundle_flags,
    monkeypatch,
):
    from app.engines.craft_engine import apply_craft_action
    from data.repositories.forge_safe_affix_bundle_repository import (
        ForgeSafeAffixBundleRepository,
    )

    monkeypatch.setattr(
        ForgeSafeAffixBundleRepository,
        "load",
        _fail_if_forge_safe_bundle_is_loaded,
    )
    legacy_item = {"forge_potential": 100, "affixes": []}
    legacy_result = apply_craft_action(
        legacy_item,
        "add_affix",
        affix_name="Increased Spell Damage",
        target_tier=1,
    )

    assert legacy_result["success"] is True
    assert legacy_item["affixes"][0]["name"] == "Increased Spell Damage"
    assert SENTINEL_AFFIX_NAME not in str(legacy_result)
    assert SENTINEL_MODIFIER_ID not in str(legacy_result)
    assert SENTINEL_AFFIX_NAME not in str(legacy_item)
    assert SENTINEL_MODIFIER_ID not in str(legacy_item)


def test_stat_aggregation_ignores_forge_safe_bundle_flags(app, forge_safe_bundle_flags):
    from app.engines.stat_engine import aggregate_stats, get_affix_value

    base = aggregate_stats("Mage", "Sorcerer", [], [], [])
    with_sentinel = aggregate_stats(
        "Mage",
        "Sorcerer",
        [],
        [],
        [{"name": SENTINEL_AFFIX_NAME, "tier": 5}],
    )
    with_legacy_affix = aggregate_stats(
        "Mage",
        "Sorcerer",
        [],
        [],
        [{"name": "Added Health", "tier": 2}],
    )

    assert get_affix_value(SENTINEL_AFFIX_NAME, 5) == 0
    assert with_sentinel.to_dict() == base.to_dict()
    assert with_legacy_affix.max_health > base.max_health


def test_simulate_stats_endpoint_ignores_forge_safe_bundle_flags(client, forge_safe_bundle_flags):
    base_response = client.post(
        "/api/simulate/stats",
        json={"character_class": "Mage", "mastery": "Sorcerer"},
    )
    sentinel_response = client.post(
        "/api/simulate/stats",
        json={
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "gear_affixes": [{"name": SENTINEL_AFFIX_NAME, "tier": 5}],
        },
    )
    legacy_response = client.post(
        "/api/simulate/stats",
        json={
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "gear_affixes": [{"name": "Added Health", "tier": 2}],
        },
    )

    assert base_response.status_code == 200
    assert sentinel_response.status_code == 200
    assert legacy_response.status_code == 200

    base = base_response.get_json()["data"]
    sentinel = sentinel_response.get_json()["data"]
    legacy = legacy_response.get_json()["data"]

    assert sentinel == base
    assert legacy["max_health"] > base["max_health"]
    assert SENTINEL_AFFIX_NAME not in str(sentinel)
    assert SENTINEL_MODIFIER_ID not in str(sentinel)


def test_planner_guard_entry_point_gap_is_documented():
    # TODO: Add a planner-specific non-consumption guard when there is a stable
    # planner route/service that resolves affix data independently from importer
    # parsing. Current production planner-adjacent tests cover import parsing,
    # while affix resolution behavior is guarded here through ref, crafting,
    # stat aggregation, and simulation entry points.
    assert SENTINEL_BUNDLE_PATH.exists()


def _contains_sentinel(records):
    return any(
        SENTINEL_AFFIX_NAME in str(record)
        or str(SENTINEL_AFFIX_ID) in str(record.get("id", ""))
        or str(SENTINEL_AFFIX_ID) in str(record.get("affix_id", ""))
        or SENTINEL_MODIFIER_ID in str(record)
        for record in records
    )


def _fail_if_forge_safe_bundle_is_loaded(self, *args, **kwargs):
    raise AssertionError("Production path attempted to load the forge-safe affix bundle.")
