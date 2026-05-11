def test_experimental_catalog_disabled(client, app):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = False
    response = client.get("/api/affixes/experimental/forge-safe-affixes")
    assert response.status_code == 404


def test_experimental_catalog_legacy_route_disabled(client, app):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = False
    response = client.get("/api/experimental/forge-safe-affixes")
    assert response.status_code == 404
