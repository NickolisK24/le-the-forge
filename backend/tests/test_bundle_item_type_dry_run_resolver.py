from app.game_data.bundle_item_type_dry_run_resolver import (
    MATCH_ACCEPTED_DIRECT,
    MATCH_ADAPTER_TRANSLATION,
    MATCH_NONE,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
    BundleItemTypeDryRunResolver,
    summarize_resolutions,
)


def _resolver():
    return BundleItemTypeDryRunResolver()


def test_accepted_direct_mapping_resolves_with_matching_base_type_id():
    result = _resolver().resolve("belt", base_type_id=2)

    assert result.status == STATUS_RESOLVED
    assert result.bundle_item_type_id == "belt"
    assert result.match_source == MATCH_ACCEPTED_DIRECT
    assert result.production_safe is False


def test_accepted_direct_mapping_requires_base_type_id_context():
    result = _resolver().resolve("belt")

    assert result.status == STATUS_NEEDS_CONTEXT
    assert result.bundle_item_type_id is None
    assert result.match_source == MATCH_NONE
    assert any("base_type_id is required" in warning for warning in result.warnings)


def test_adapter_translation_resolves_with_matching_base_type_id():
    result = _resolver().resolve("helm", base_type_id=0)

    assert result.status == STATUS_RESOLVED
    assert result.bundle_item_type_id == "helmet"
    assert result.match_source == MATCH_ADAPTER_TRANSLATION
    assert result.production_safe is False


def test_collapsed_weapon_slug_without_base_type_id_needs_context():
    result = _resolver().resolve("axe")

    assert result.status == STATUS_NEEDS_CONTEXT
    assert result.bundle_item_type_id is None
    assert any("base_type_id is required" in warning for warning in result.warnings)


def test_idol_shape_alias_without_base_type_id_needs_context():
    result = _resolver().resolve("idol_1x1")

    assert result.status == STATUS_NEEDS_CONTEXT
    assert result.bundle_item_type_id is None
    assert any("base_type_id is required" in warning for warning in result.warnings)


def test_spear_does_not_resolve():
    result = _resolver().resolve("spear", base_type_id=14)

    assert result.status == STATUS_NEEDS_REVIEW
    assert result.bundle_item_type_id is None
    assert result.match_source == MATCH_NONE


def test_unknown_item_type_returns_unresolved():
    result = _resolver().resolve("unknown_type", base_type_id=999)

    assert result.status == STATUS_UNRESOLVED
    assert result.bundle_item_type_id is None
    assert result.match_source == MATCH_NONE


def test_no_result_has_production_safe_true():
    resolver = _resolver()
    results = [
        resolver.resolve("belt", 2),
        resolver.resolve("helm", 0),
        resolver.resolve("axe"),
        resolver.resolve("spear"),
        resolver.resolve("unknown_type"),
    ]

    assert all(result.production_safe is False for result in results)


def test_subtype_id_alone_is_ignored_and_warned():
    result = _resolver().resolve("belt", subtype_id=1)

    assert result.status == STATUS_NEEDS_CONTEXT
    assert result.bundle_item_type_id is None
    assert any("subtype_id was provided but ignored" in warning for warning in result.warnings)


def test_name_only_matching_does_not_resolve():
    result = _resolver().resolve("helmet")

    assert result.status == STATUS_UNRESOLVED
    assert result.bundle_item_type_id is None


def test_resolver_returns_structured_diagnostics():
    data = _resolver().resolve("helm", 0).to_dict()

    assert data == {
        "forge_item_type": "helm",
        "base_type_id": 0,
        "status": "resolved",
        "bundle_item_type_id": "helmet",
        "match_source": "adapter_translation",
        "production_safe": False,
        "warnings": [],
        "notes": ["Resolved through simple_slug_rename translation."],
    }


def test_summary_counts_results_and_subtype_warnings():
    resolver = _resolver()
    summary = summarize_resolutions(
        [
            resolver.resolve("belt", 2),
            resolver.resolve("axe"),
            resolver.resolve("spear"),
            resolver.resolve("unknown_type"),
            resolver.resolve("belt", subtype_id=1),
        ]
    )

    assert summary["total_attempted"] == 5
    assert summary["counts"]["resolved"] == 1
    assert summary["counts"]["needs_context"] == 2
    assert summary["counts"]["needs_review"] == 1
    assert summary["counts"]["unresolved"] == 1
    assert summary["subtype_id_only_matching_attempted"] is False
    assert summary["subtype_id_context_warnings_seen"] is True
