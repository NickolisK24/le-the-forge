from app.api_contracts.v2 import standardize_v2_payload


def test_v2_response_contract_preserves_records_and_adds_envelope():
    payload = {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_affix_bundle",
        "result_count": 1,
        "records": [{"canonical_id": "affix:equipment:1", "support_status": "partial"}],
    }

    contracted = standardize_v2_payload(payload, path="/experimental/v2/affixes", status_code=200)

    assert contracted["records"] == payload["records"]
    assert contracted["data"]["records"] == payload["records"]
    assert contracted["meta"]["domain"] == "affixes"
    assert contracted["meta"]["route_version"] == "v2"
    assert contracted["support_summary"]["partial"] == 1
    assert contracted["provenance"]["data_source"] == "v2_affix_bundle"
    assert contracted["debug"]["production_consumer"] is False


def test_v2_error_contract_uses_standard_error_shape():
    payload = {
        "success": False,
        "error": "v2_affix_bundle_missing",
        "message": "v2 affix bundle not found",
    }

    contracted = standardize_v2_payload(payload, path="/experimental/v2/affixes", status_code=404)

    assert contracted["error"]["code"] == "v2_affix_bundle_missing"
    assert contracted["error"]["message"] == "v2 affix bundle not found"
    assert contracted["meta"]["status_code"] == 404
    assert contracted["debug"]["legacy_error_code"] == "v2_affix_bundle_missing"


def test_experimental_v2_routes_expose_standard_envelope(app):
    client = app.test_client()
    routes = [
        "/experimental/v2/affixes",
        "/experimental/v2/affixes/affix:equipment:1",
        "/experimental/v2/affixes/debug",
        "/experimental/v2/items/bases",
        "/experimental/v2/items/bases/item_base:equippable:0:1",
        "/experimental/v2/items/implicits",
        "/experimental/v2/items/debug",
        "/experimental/v2/uniques",
        "/experimental/v2/uniques/unique:1",
        "/experimental/v2/sets",
        "/experimental/v2/sets/set:7",
        "/experimental/v2/uniques/debug",
        "/experimental/v2/sets/debug",
        "/experimental/v2/idols",
        "/experimental/v2/idols/idol:25:0",
        "/experimental/v2/idols/affixes",
        "/experimental/v2/idols/affixes/idol_affix:105",
        "/experimental/v2/idols/debug",
        "/experimental/v2/classes",
        "/experimental/v2/classes/debug",
        "/experimental/v2/classes/class:mage",
        "/experimental/v2/masteries",
        "/experimental/v2/masteries/mastery:mage:runemaster",
        "/experimental/v2/passives",
        "/experimental/v2/passives/debug",
        "/experimental/v2/passives/passive_tree:mg_1",
        "/experimental/v2/passives/passive_tree:mg_1/nodes/passive_node:mg_1:2",
        "/experimental/v2/skills",
        "/experimental/v2/skills/debug",
        "/experimental/v2/skills/trees/skill_tree:fi9",
        "/experimental/v2/skills/trees/skill_tree:fi9/nodes/skill_node:fi9:2",
        "/experimental/v2/skills/skill:fi9/tree",
        "/experimental/v2/skills/skill:fi9",
        "/experimental/v2/stats",
        "/experimental/v2/modifiers",
        "/experimental/v2/modifiers/debug",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route
        body = response.get_json()
        assert {"data", "meta", "support_summary", "warnings", "provenance", "debug"}.issubset(body), route
        assert body["meta"]["route_version"] == "v2"
        assert body["meta"]["read_only"] is True
        assert body["meta"]["production_consumer"] is False

    stat_id = client.get("/experimental/v2/stats").get_json()["records"][0]["canonical_stat_id"]
    stat_detail = client.get(f"/experimental/v2/stats/{stat_id}")
    assert stat_detail.status_code == 200
    assert stat_detail.get_json()["meta"]["domain"] == "stats"

    modifier_id = client.get("/experimental/v2/modifiers").get_json()["records"][0]["canonical_modifier_id"]
    modifier_detail = client.get(f"/experimental/v2/modifiers/{modifier_id}")
    assert modifier_detail.status_code == 200
    assert modifier_detail.get_json()["meta"]["domain"] == "modifiers"


def test_experimental_v2_missing_artifact_uses_error_contract(app, tmp_path):
    app.config["V2_AFFIX_BUNDLE_PATH"] = str(tmp_path / "missing.json")

    response = app.test_client().get("/experimental/v2/affixes")

    assert response.status_code == 404
    body = response.get_json()
    assert body["error"]["code"] == "v2_affix_bundle_missing"
    assert body["meta"]["domain"] == "affixes"
    assert body["debug"]["read_only"] is True


def test_v2_debug_routes_expose_identity_and_value_policy_status(app):
    client = app.test_client()

    skill_debug = client.get("/experimental/v2/skills/debug").get_json()
    assert skill_debug["debug"]["unresolved_skill_identity_count"] >= 0
    assert skill_debug["meta"]["domain"] == "skills"

    modifier_debug = client.get("/experimental/v2/modifiers/debug").get_json()
    assert modifier_debug["debug"]["repository_debug_summary"]["modifiers"]["production_safe"] is False
    assert modifier_debug["support_summary"]["stable_calculable"] == 0
