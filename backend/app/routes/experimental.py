"""Experimental read-only data consumption routes.

These endpoints are disabled by default. They expose controlled internal
consumption layers without replacing production planner, crafting, simulation,
or existing affix behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from app.normalization.v2 import (
    V2ModifierRegistry,
    V2ModifierRegistryError,
    V2StatRegistry,
    V2StatRegistryError,
)
from app.repositories.v2.affix_repository import V2AffixBundleError, V2AffixRepository
from app.repositories.v2.class_mastery_repository import V2ClassMasteryBundleError, V2ClassMasteryRepository
from app.repositories.v2.idol_repository import V2IdolBundleError, V2IdolRepository
from app.repositories.v2.item_repository import V2ItemBundleError, V2ItemRepository
from app.repositories.v2.passive_repository import V2PassiveBundleError, V2PassiveRepository
from app.repositories.v2.skill_repository import V2SkillBundleError, V2SkillRepository
from app.repositories.v2.unique_set_repository import V2UniqueSetBundleError, V2UniqueSetRepository
from data.loaders.forge_safe_affix_bundle_loader import ForgeSafeAffixBundleLoaderError
from data.loaders.forge_safe_affixes_loader import ForgeSafeAffixLoaderError
from data.repositories.forge_safe_affix_bundle_repository import ForgeSafeAffixBundleRepository
from data.repositories.forge_safe_affix_repository import ForgeSafeAffixRepository
from app.services.forge_safe_affix_comparison_service import (
    CompareOptions,
    compare_legacy_to_forge_safe_bundle,
)


experimental_bp = Blueprint("experimental", __name__)

DEFAULT_LIMIT = 50
MAX_LIMIT = 100
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_V2_AFFIX_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_affix_bundle.json"
DEFAULT_V2_ITEM_BASE_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_item_base_bundle.json"
DEFAULT_V2_ITEM_IMPLICIT_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_item_implicit_bundle.json"
DEFAULT_V2_UNIQUE_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_unique_bundle.json"
DEFAULT_V2_SET_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_set_bundle.json"
DEFAULT_V2_IDOL_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_idol_bundle.json"
DEFAULT_V2_IDOL_AFFIX_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_idol_affix_bundle.json"
DEFAULT_V2_CLASS_MASTERY_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_class_mastery_bundle.json"
DEFAULT_V2_PASSIVE_TREE_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_passive_tree_bundle.json"
DEFAULT_V2_SKILL_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_skill_bundle.json"
DEFAULT_V2_SKILL_TREE_BUNDLE_PATH = ROOT / "docs" / "generated" / "v2_skill_tree_bundle.json"
DEFAULT_V2_STAT_REGISTRY_PATH = ROOT / "docs" / "generated" / "v2_stat_registry.json"
DEFAULT_V2_MODIFIER_REGISTRY_PATH = ROOT / "docs" / "generated" / "v2_modifier_registry.json"


@experimental_bp.route("/forge-safe-affixes", methods=["GET"])
def forge_safe_affix_catalog():
    """Query the controlled Forge-safe affix repository."""

    if not current_app.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return jsonify({
            "success": False,
            "error": "experimental_catalog_disabled",
            "message": "Forge-safe affix catalog is disabled.",
        }), 404

    parsed = _parse_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400

    if _bundle_catalog_enabled():
        return _forge_safe_affix_bundle_catalog(parsed)
    return _forge_safe_canonical_affix_catalog(parsed)


@experimental_bp.route("/forge-safe-affixes/compare-legacy", methods=["GET"])
def compare_forge_safe_affixes_to_legacy():
    """Compare legacy Forge affix data to the Forge-safe bundle."""

    if not current_app.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return jsonify({
            "success": False,
            "error": "experimental_catalog_disabled",
            "message": "Forge-safe affix catalog is disabled.",
        }), 404
    if not _bundle_catalog_enabled():
        return jsonify({
            "success": False,
            "error": "bundle_catalog_disabled",
            "message": "FORGE_SAFE_AFFIX_BUNDLE_ENABLED must be true for legacy comparison.",
        }), 404

    parsed = _parse_compare_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400

    bundle_path = _configured_bundle_path()
    if not bundle_path:
        return jsonify({
            "success": False,
            "error": "missing_bundle_path",
            "message": "FORGE_SAFE_AFFIX_BUNDLE_PATH is not configured.",
        }), 503

    try:
        report = compare_legacy_to_forge_safe_bundle(
            str(bundle_path),
            options=CompareOptions(
                include_details=parsed["include_details"],
                limit=parsed["limit"],
            ),
        )
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "bundle_file_missing",
            "message": str(exc),
        }), 404
    except (ForgeSafeAffixBundleLoaderError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": "bundle_validation_failed",
            "message": str(exc),
        }), 422

    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "legacy_vs_forge_safe_bundle",
        "query": {
            "include_details": parsed["include_details"],
            "limit": parsed["limit"],
        },
        "comparison": report,
    })


@experimental_bp.route("/forge-safe-affixes/<affix_id>", methods=["GET"])
def forge_safe_affix_detail(affix_id: str):
    """Return one controlled Forge-safe affix record."""

    if not current_app.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return jsonify({
            "success": False,
            "error": "experimental_catalog_disabled",
            "message": "Forge-safe affix catalog is disabled.",
        }), 404

    parsed = _parse_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400
    parsed["affix_id"] = affix_id
    parsed["limit"] = 1
    parsed["offset"] = 0

    if _bundle_catalog_enabled():
        return _forge_safe_affix_bundle_catalog(parsed, detail=True)
    return _forge_safe_canonical_affix_catalog(parsed, detail=True)


@experimental_bp.route("/v2/affixes", methods=["GET"])
def v2_affix_catalog():
    """Query the read-only v2 canonical affix bundle."""

    parsed = _parse_v2_affix_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400

    try:
        repository = _load_v2_affix_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_affix_bundle_missing",
            "message": str(exc),
        }), 404
    except V2AffixBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_affix_bundle_invalid",
            "message": str(exc),
        }), 422

    if parsed["affix_id"]:
        record = repository.get_affix(parsed["affix_id"])
        records = [record] if record is not None else []
    else:
        records = repository.filter_affixes(
            query=parsed["q"],
            slot=parsed["slot"],
            item_type=parsed["item_type"],
            class_id=parsed["class_id"],
            support_status=parsed["support_status"],
            limit=parsed["limit"],
            offset=parsed["offset"],
        )

    return jsonify(_v2_affix_response(repository, records, parsed))


@experimental_bp.route("/v2/affixes/<path:affix_id>", methods=["GET"])
def v2_affix_detail(affix_id: str):
    """Return one v2 canonical affix record by canonical ID."""

    try:
        repository = _load_v2_affix_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_affix_bundle_missing",
            "message": str(exc),
        }), 404
    except V2AffixBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_affix_bundle_invalid",
            "message": str(exc),
        }), 422

    record = repository.get_affix(affix_id)
    if record is None:
        return jsonify({
            "success": False,
            "error": "affix_not_found",
            "message": f"v2 affix not found: {affix_id}",
        }), 404

    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_affix_bundle",
        "source_path": str(repository.bundle_path),
        "record": record,
    })


@experimental_bp.route("/v2/affixes/debug", methods=["GET"])
def v2_affix_debug():
    """Return a debug summary for the read-only v2 affix bundle."""

    try:
        repository = _load_v2_affix_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_affix_bundle_missing",
            "message": str(exc),
        }), 404
    except V2AffixBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_affix_bundle_invalid",
            "message": str(exc),
        }), 422

    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_affix_bundle",
        "debug_summary": repository.debug_summary(),
    })


@experimental_bp.route("/v2/items/bases", methods=["GET"])
def v2_item_bases():
    """Query the read-only v2 item base bundle."""

    parsed = _parse_v2_item_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400
    try:
        repository = _load_v2_item_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_missing",
            "message": str(exc),
        }), 404
    except V2ItemBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_invalid",
            "message": str(exc),
        }), 422

    records = repository.filter_bases(
        query=parsed["q"],
        slot=parsed["slot"],
        item_type=parsed["item_type"],
        class_id=parsed["class_id"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    return jsonify(_v2_item_base_response(repository, records, parsed))


@experimental_bp.route("/v2/items/bases/<path:item_base_id>", methods=["GET"])
def v2_item_base_detail(item_base_id: str):
    """Return one v2 item base by canonical ID."""

    try:
        repository = _load_v2_item_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_missing",
            "message": str(exc),
        }), 404
    except V2ItemBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_invalid",
            "message": str(exc),
        }), 422

    record = repository.get_base(item_base_id)
    if record is None:
        return jsonify({
            "success": False,
            "error": "item_base_not_found",
            "message": f"v2 item base not found: {item_base_id}",
        }), 404
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_item_base_bundle",
        "source_path": str(repository.base_bundle_path),
        "record": record,
        "implicits": repository.get_implicits_for_base(item_base_id),
    })


@experimental_bp.route("/v2/items/implicits", methods=["GET"])
def v2_item_implicits():
    """Query the read-only v2 item implicit bundle."""

    parsed = _parse_v2_item_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400
    try:
        repository = _load_v2_item_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_missing",
            "message": str(exc),
        }), 404
    except V2ItemBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_invalid",
            "message": str(exc),
        }), 422

    if parsed["base_id"]:
        records = repository.get_implicits_for_base(parsed["base_id"])
    else:
        records = repository.list_implicits(limit=parsed["limit"], offset=parsed["offset"])
    return jsonify(_v2_item_implicit_response(repository, records, parsed))


@experimental_bp.route("/v2/items/debug", methods=["GET"])
def v2_item_debug():
    """Return a debug summary for read-only v2 item bundles."""

    try:
        repository = _load_v2_item_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_missing",
            "message": str(exc),
        }), 404
    except V2ItemBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_item_bundle_invalid",
            "message": str(exc),
        }), 422

    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_item_bundles",
        "debug_summary": repository.debug_summary(),
    })


@experimental_bp.route("/v2/uniques", methods=["GET"])
def v2_uniques():
    """Query the read-only v2 unique bundle."""

    parsed = _parse_v2_item_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400
    try:
        repository = _load_v2_unique_set_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_missing",
            "message": str(exc),
        }), 404
    except V2UniqueSetBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_invalid",
            "message": str(exc),
        }), 422

    records = repository.filter_uniques(
        query=parsed["q"],
        slot=parsed["slot"],
        item_type=parsed["item_type"],
        class_id=parsed["class_id"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    return jsonify(_v2_unique_response(repository, records, parsed))


@experimental_bp.route("/v2/uniques/<path:unique_id>", methods=["GET"])
def v2_unique_detail(unique_id: str):
    """Return one v2 unique record by canonical ID."""

    try:
        repository = _load_v2_unique_set_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_missing",
            "message": str(exc),
        }), 404
    except V2UniqueSetBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_invalid",
            "message": str(exc),
        }), 422
    record = repository.get_unique(unique_id)
    if record is None:
        return jsonify({
            "success": False,
            "error": "unique_not_found",
            "message": f"v2 unique not found: {unique_id}",
        }), 404
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_unique_bundle",
        "source_path": str(repository.unique_bundle_path),
        "record": record,
    })


@experimental_bp.route("/v2/sets", methods=["GET"])
def v2_sets():
    """Query the read-only v2 set bundle."""

    parsed = _parse_v2_item_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400
    try:
        repository = _load_v2_unique_set_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_missing",
            "message": str(exc),
        }), 404
    except V2UniqueSetBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_invalid",
            "message": str(exc),
        }), 422
    records = repository.list_sets(limit=parsed["limit"], offset=parsed["offset"])
    return jsonify(_v2_set_response(repository, records, parsed))


@experimental_bp.route("/v2/sets/<path:set_id>", methods=["GET"])
def v2_set_detail(set_id: str):
    """Return one v2 set group with items and bonuses."""

    try:
        repository = _load_v2_unique_set_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_missing",
            "message": str(exc),
        }), 404
    except V2UniqueSetBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_invalid",
            "message": str(exc),
        }), 422
    record = repository.get_set(set_id)
    if record is None:
        return jsonify({
            "success": False,
            "error": "set_not_found",
            "message": f"v2 set not found: {set_id}",
        }), 404
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_set_bundle",
        "source_path": str(repository.set_bundle_path),
        "record": record,
        "items": repository.get_set_items(set_id),
        "bonuses": repository.get_set_bonuses(set_id),
    })


@experimental_bp.route("/v2/uniques/debug", methods=["GET"])
def v2_unique_debug():
    """Return a debug summary for read-only v2 unique bundle."""

    return _v2_unique_set_debug("v2_unique_bundle")


@experimental_bp.route("/v2/sets/debug", methods=["GET"])
def v2_set_debug():
    """Return a debug summary for read-only v2 set bundle."""

    return _v2_unique_set_debug("v2_set_bundle")


@experimental_bp.route("/v2/idols", methods=["GET"])
def v2_idols():
    """Query the read-only v2 idol bundle."""

    parsed = _parse_v2_idol_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_idol_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_missing", "message": str(exc)}), 404
    except V2IdolBundleError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_invalid", "message": str(exc)}), 422
    records = repository.filter_idols(
        query=parsed["q"],
        shape=parsed["shape"],
        class_id=parsed["class_id"],
        mastery=parsed["mastery"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    return jsonify(_v2_idol_response(repository, records, parsed, data_source="v2_idol_bundle"))


@experimental_bp.route("/v2/idols/<path:idol_id>", methods=["GET"])
def v2_idol_detail(idol_id: str):
    """Return one v2 idol record by canonical ID."""

    try:
        repository = _load_v2_idol_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_missing", "message": str(exc)}), 404
    except V2IdolBundleError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_idol(idol_id)
    if record is None:
        return jsonify({"success": False, "error": "idol_not_found", "message": f"v2 idol not found: {idol_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_idol_bundle", "source_path": str(repository.idol_bundle_path), "record": record})


@experimental_bp.route("/v2/idols/affixes", methods=["GET"])
def v2_idol_affixes():
    """Query the read-only v2 idol affix bundle."""

    parsed = _parse_v2_idol_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_idol_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_missing", "message": str(exc)}), 404
    except V2IdolBundleError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_invalid", "message": str(exc)}), 422
    records = repository.filter_affixes(
        query=parsed["q"],
        idol_type=parsed["idol_type"] or parsed["shape"],
        class_id=parsed["class_id"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    return jsonify(_v2_idol_affix_response(repository, records, parsed))


@experimental_bp.route("/v2/idols/affixes/<path:affix_id>", methods=["GET"])
def v2_idol_affix_detail(affix_id: str):
    """Return one v2 idol affix by canonical ID."""

    try:
        repository = _load_v2_idol_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_missing", "message": str(exc)}), 404
    except V2IdolBundleError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_affix(affix_id)
    if record is None:
        return jsonify({"success": False, "error": "idol_affix_not_found", "message": f"v2 idol affix not found: {affix_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_idol_affix_bundle", "source_path": str(repository.idol_affix_bundle_path), "record": record})


@experimental_bp.route("/v2/idols/debug", methods=["GET"])
def v2_idol_debug():
    """Return a debug summary for read-only v2 idol bundles."""

    try:
        repository = _load_v2_idol_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_missing", "message": str(exc)}), 404
    except V2IdolBundleError as exc:
        return jsonify({"success": False, "error": "v2_idol_bundle_invalid", "message": str(exc)}), 422
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_idol_bundles", "debug_summary": repository.debug_summary()})


@experimental_bp.route("/v2/classes", methods=["GET"])
def v2_classes():
    """Query the read-only v2 class bundle."""

    parsed = _parse_v2_class_mastery_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_class_mastery_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_missing", "message": str(exc)}), 404
    except V2ClassMasteryBundleError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_invalid", "message": str(exc)}), 422
    records = repository.filter_classes(query=parsed["q"], limit=parsed["limit"], offset=parsed["offset"])
    return jsonify(_v2_class_mastery_response(repository, records, parsed, data_source="v2_class_mastery_bundle", record_kind="classes"))


@experimental_bp.route("/v2/classes/debug", methods=["GET"])
def v2_class_mastery_debug():
    """Return a debug summary for read-only v2 class/mastery bundle."""

    try:
        repository = _load_v2_class_mastery_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_missing", "message": str(exc)}), 404
    except V2ClassMasteryBundleError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_invalid", "message": str(exc)}), 422
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_class_mastery_bundle", "debug_summary": repository.debug_summary()})


@experimental_bp.route("/v2/classes/<path:class_id>", methods=["GET"])
def v2_class_detail(class_id: str):
    """Return one v2 class record by canonical ID."""

    try:
        repository = _load_v2_class_mastery_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_missing", "message": str(exc)}), 404
    except V2ClassMasteryBundleError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_class(class_id)
    if record is None:
        return jsonify({"success": False, "error": "class_not_found", "message": f"v2 class not found: {class_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_class_mastery_bundle", "source_path": str(repository.bundle_path), "record": record, "masteries": repository.get_masteries_by_class(class_id)})


@experimental_bp.route("/v2/masteries", methods=["GET"])
def v2_masteries():
    """Query the read-only v2 mastery records."""

    parsed = _parse_v2_class_mastery_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_class_mastery_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_missing", "message": str(exc)}), 404
    except V2ClassMasteryBundleError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_invalid", "message": str(exc)}), 422
    records = repository.filter_masteries(query=parsed["q"], class_id=parsed["class_id"], limit=parsed["limit"], offset=parsed["offset"])
    return jsonify(_v2_class_mastery_response(repository, records, parsed, data_source="v2_class_mastery_bundle", record_kind="masteries"))


@experimental_bp.route("/v2/masteries/<path:mastery_id>", methods=["GET"])
def v2_mastery_detail(mastery_id: str):
    """Return one v2 mastery record by canonical ID."""

    try:
        repository = _load_v2_class_mastery_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_missing", "message": str(exc)}), 404
    except V2ClassMasteryBundleError as exc:
        return jsonify({"success": False, "error": "v2_class_mastery_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_mastery(mastery_id)
    if record is None:
        return jsonify({"success": False, "error": "mastery_not_found", "message": f"v2 mastery not found: {mastery_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_class_mastery_bundle", "source_path": str(repository.bundle_path), "record": record})


@experimental_bp.route("/v2/passives", methods=["GET"])
def v2_passives():
    """Query the read-only v2 passive tree bundle."""

    parsed = _parse_v2_passive_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_passive_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_missing", "message": str(exc)}), 404
    except V2PassiveBundleError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_invalid", "message": str(exc)}), 422
    records = repository.filter_trees(
        query=parsed["q"],
        class_id=parsed["class_id"],
        mastery_id=parsed["mastery_id"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    return jsonify(_v2_passive_response(repository, records, parsed))


@experimental_bp.route("/v2/passives/debug", methods=["GET"])
def v2_passive_debug():
    """Return a debug summary for read-only v2 passive tree bundle."""

    try:
        repository = _load_v2_passive_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_missing", "message": str(exc)}), 404
    except V2PassiveBundleError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_invalid", "message": str(exc)}), 422
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_passive_tree_bundle", "debug_summary": repository.debug_summary()})


@experimental_bp.route("/v2/passives/<path:tree_id>", methods=["GET"])
def v2_passive_detail(tree_id: str):
    """Return one v2 passive tree with its nodes."""

    parsed = _parse_v2_passive_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_passive_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_missing", "message": str(exc)}), 404
    except V2PassiveBundleError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_tree(tree_id)
    if record is None:
        return jsonify({"success": False, "error": "passive_tree_not_found", "message": f"v2 passive tree not found: {tree_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_passive_tree_bundle", "source_path": str(repository.bundle_path), "record": record, "nodes": repository.get_nodes_by_tree(tree_id, limit=parsed["limit"], offset=parsed["offset"])})


@experimental_bp.route("/v2/passives/<path:tree_id>/nodes/<path:node_id>", methods=["GET"])
def v2_passive_node_detail(tree_id: str, node_id: str):
    """Return one v2 passive node by canonical ID."""

    try:
        repository = _load_v2_passive_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_missing", "message": str(exc)}), 404
    except V2PassiveBundleError as exc:
        return jsonify({"success": False, "error": "v2_passive_tree_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_node(node_id)
    if record is None or record.get("tree_id") != tree_id:
        return jsonify({"success": False, "error": "passive_node_not_found", "message": f"v2 passive node not found: {node_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_passive_tree_bundle", "source_path": str(repository.bundle_path), "record": record})


@experimental_bp.route("/v2/skills", methods=["GET"])
def v2_skills():
    """Query the read-only v2 skill bundle."""

    parsed = _parse_v2_skill_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_skill_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_missing", "message": str(exc)}), 404
    except V2SkillBundleError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_invalid", "message": str(exc)}), 422
    records = repository.filter_skills(
        query=parsed["q"],
        class_id=parsed["class_id"],
        mastery_id=parsed["mastery_id"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    return jsonify(_v2_skill_response(repository, records, parsed))


@experimental_bp.route("/v2/skills/debug", methods=["GET"])
def v2_skill_debug():
    """Return a debug summary for read-only v2 skill bundles."""

    try:
        repository = _load_v2_skill_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_missing", "message": str(exc)}), 404
    except V2SkillBundleError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_invalid", "message": str(exc)}), 422
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_skill_bundle", "debug_summary": repository.debug_summary()})


@experimental_bp.route("/v2/skills/trees/<path:tree_id>", methods=["GET"])
def v2_skill_tree_detail(tree_id: str):
    """Return one v2 skill tree with nodes."""

    parsed = _parse_v2_skill_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_skill_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_missing", "message": str(exc)}), 404
    except V2SkillBundleError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_tree(tree_id)
    if record is None:
        return jsonify({"success": False, "error": "skill_tree_not_found", "message": f"v2 skill tree not found: {tree_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_skill_tree_bundle", "source_path": str(repository.skill_tree_bundle_path), "record": record, "nodes": repository.get_nodes_by_tree(tree_id, limit=parsed["limit"], offset=parsed["offset"])})


@experimental_bp.route("/v2/skills/trees/<path:tree_id>/nodes/<path:node_id>", methods=["GET"])
def v2_skill_node_detail(tree_id: str, node_id: str):
    """Return one v2 skill tree node by canonical ID."""

    try:
        repository = _load_v2_skill_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_missing", "message": str(exc)}), 404
    except V2SkillBundleError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_node(node_id)
    if record is None or record.get("skill_tree_id") != tree_id:
        return jsonify({"success": False, "error": "skill_node_not_found", "message": f"v2 skill node not found: {node_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_skill_tree_bundle", "source_path": str(repository.skill_tree_bundle_path), "record": record})


@experimental_bp.route("/v2/skills/<path:skill_id>/tree", methods=["GET"])
def v2_skill_tree_by_skill(skill_id: str):
    """Return the v2 skill tree for a skill canonical ID."""

    parsed = _parse_v2_skill_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        repository = _load_v2_skill_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_missing", "message": str(exc)}), 404
    except V2SkillBundleError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_tree_by_skill(skill_id)
    if record is None:
        return jsonify({"success": False, "error": "skill_tree_not_found", "message": f"v2 skill tree not found for skill: {skill_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_skill_tree_bundle", "source_path": str(repository.skill_tree_bundle_path), "record": record, "nodes": repository.get_nodes_by_tree(record["canonical_id"], limit=parsed["limit"], offset=parsed["offset"])})


@experimental_bp.route("/v2/skills/<path:skill_id>", methods=["GET"])
def v2_skill_detail(skill_id: str):
    """Return one v2 skill record by canonical ID."""

    try:
        repository = _load_v2_skill_repository()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_missing", "message": str(exc)}), 404
    except V2SkillBundleError as exc:
        return jsonify({"success": False, "error": "v2_skill_bundle_invalid", "message": str(exc)}), 422
    record = repository.get_skill(skill_id)
    if record is None:
        return jsonify({"success": False, "error": "skill_not_found", "message": f"v2 skill not found: {skill_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_skill_bundle", "source_path": str(repository.skill_bundle_path), "record": record})


@experimental_bp.route("/v2/stats", methods=["GET"])
def v2_stats():
    """Return v2 normalized stat registry records."""

    parsed = _parse_v2_modifier_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        registry = _load_v2_stat_registry()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_stat_registry_missing", "message": str(exc)}), 404
    except V2StatRegistryError as exc:
        return jsonify({"success": False, "error": "v2_stat_registry_invalid", "message": str(exc)}), 422
    records = registry.list_stats(limit=parsed["limit"], offset=parsed["offset"])
    if parsed["q"]:
        needle = parsed["q"].strip().lower()
        records = [
            record for record in records
            if needle in record["canonical_stat_id"].lower()
            or needle in str(record.get("display_name", "")).lower()
        ]
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_stat_registry", "source_path": str(registry.registry_path), "count": len(records), "records": records})


@experimental_bp.route("/v2/stats/<path:stat_id>", methods=["GET"])
def v2_stat_detail(stat_id: str):
    """Return one v2 normalized stat record."""

    try:
        registry = _load_v2_stat_registry()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_stat_registry_missing", "message": str(exc)}), 404
    except V2StatRegistryError as exc:
        return jsonify({"success": False, "error": "v2_stat_registry_invalid", "message": str(exc)}), 422
    record = registry.get_stat(stat_id)
    if record is None:
        return jsonify({"success": False, "error": "stat_not_found", "message": f"v2 stat not found: {stat_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_stat_registry", "source_path": str(registry.registry_path), "record": record})


@experimental_bp.route("/v2/modifiers", methods=["GET"])
def v2_modifiers():
    """Return v2 normalized modifier registry records."""

    parsed = _parse_v2_modifier_query_args()
    if parsed["errors"]:
        return jsonify({"success": False, "error": "invalid_query", "message": "; ".join(parsed["errors"])}), 400
    try:
        registry = _load_v2_modifier_registry()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_modifier_registry_missing", "message": str(exc)}), 404
    except V2ModifierRegistryError as exc:
        return jsonify({"success": False, "error": "v2_modifier_registry_invalid", "message": str(exc)}), 422
    stable = None
    if request.args.get("stable_calculable") not in (None, ""):
        stable = _parse_bool(request.args.get("stable_calculable"))
    records = registry.list_modifiers(
        source_type=parsed["source_type"],
        stat_id=parsed["stat_id"],
        stable_calculable=stable,
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    if parsed["q"]:
        needle = parsed["q"].strip().lower()
        records = [
            record for record in records
            if needle in record["canonical_modifier_id"].lower()
            or needle in str(record.get("source_display_name", "")).lower()
            or needle in str(record.get("stat_id", "")).lower()
        ]
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_modifier_registry", "source_path": str(registry.registry_path), "count": len(records), "records": records})


@experimental_bp.route("/v2/modifiers/debug", methods=["GET"])
def v2_modifier_debug():
    """Return debug summaries for v2 stat and modifier registries."""

    try:
        modifier_registry = _load_v2_modifier_registry()
        stat_registry = _load_v2_stat_registry()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_modifier_registry_missing", "message": str(exc)}), 404
    except (V2ModifierRegistryError, V2StatRegistryError) as exc:
        return jsonify({"success": False, "error": "v2_modifier_registry_invalid", "message": str(exc)}), 422
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_modifier_registries", "debug_summary": {"modifiers": modifier_registry.debug_summary(), "stats": stat_registry.debug_summary()}})


@experimental_bp.route("/v2/modifiers/<path:modifier_id>", methods=["GET"])
def v2_modifier_detail(modifier_id: str):
    """Return one v2 normalized modifier record."""

    try:
        registry = _load_v2_modifier_registry()
    except FileNotFoundError as exc:
        return jsonify({"success": False, "error": "v2_modifier_registry_missing", "message": str(exc)}), 404
    except V2ModifierRegistryError as exc:
        return jsonify({"success": False, "error": "v2_modifier_registry_invalid", "message": str(exc)}), 422
    record = registry.get_modifier(modifier_id)
    if record is None:
        return jsonify({"success": False, "error": "modifier_not_found", "message": f"v2 modifier not found: {modifier_id}"}), 404
    return jsonify({"success": True, "experimental": True, "read_only": True, "production_consumer": False, "data_source": "v2_modifier_registry", "source_path": str(registry.registry_path), "record": record})


def _forge_safe_canonical_affix_catalog(parsed: dict[str, Any], *, detail: bool = False):
    source_path = _configured_export_path()
    if not source_path:
        return jsonify({
            "success": False,
            "error": "missing_export_path",
            "message": "FORGE_SAFE_AFFIX_EXPORT_PATH is not configured.",
        }), 503

    try:
        repository = ForgeSafeAffixRepository(source_path).load()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "export_file_missing",
            "message": str(exc),
        }), 404
    except (ForgeSafeAffixLoaderError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": "export_validation_failed",
            "message": str(exc),
        }), 422

    records = _query_canonical_records(
        repository,
        affix_id=parsed["affix_id"],
        query=parsed["q"],
        source_type=parsed["source_type"],
        item_type=parsed["item_type"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    summary = repository.get_summary()
    if detail and not records:
        return jsonify({
            "success": False,
            "error": "affix_not_found",
            "message": f"Forge-safe affix not found: {parsed['affix_id']}",
        }), 404
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "forge_safe_canonical_affixes",
        "source_path": summary["source_path"],
        "result_count": len(records),
        "total_loaded_count": repository.count(),
        "total_affixes": repository.count(),
        "total_modifiers": None,
        "query": {
            "limit": parsed["limit"],
            "offset": parsed["offset"],
            "q": parsed["q"],
            "affix_id": parsed["affix_id"],
            "source_type": parsed["source_type"],
            "item_type": parsed["item_type"],
            "include_modifiers": parsed["include_modifiers"],
        },
        "warning_count": summary["warning_count"],
        "warnings": summary["warnings"],
        "export_policy": summary["export_policy"],
        "export_status": summary["export_status"],
        "total_affix_records_seen": summary["total_affix_records_seen"],
        "excluded_affix_records": summary["excluded_affix_records"],
        "summary": summary["summary"],
        "records": records,
    })


def _forge_safe_affix_bundle_catalog(parsed: dict[str, Any], *, detail: bool = False):
    bundle_path = _configured_bundle_path()
    if not bundle_path:
        return jsonify({
            "success": False,
            "error": "missing_bundle_path",
            "message": "FORGE_SAFE_AFFIX_BUNDLE_PATH is not configured.",
        }), 503

    try:
        repository = ForgeSafeAffixBundleRepository(bundle_path).load()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "bundle_file_missing",
            "message": str(exc),
        }), 404
    except (ForgeSafeAffixBundleLoaderError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": "bundle_validation_failed",
            "message": str(exc),
        }), 422

    records = _query_bundle_records(
        repository,
        affix_id=parsed["affix_id"],
        query=parsed["q"],
        source_type=parsed["source_type"],
        item_type=parsed["item_type"],
        limit=parsed["limit"],
        offset=parsed["offset"],
        include_modifiers=parsed["include_modifiers"],
    )
    summary = repository.get_summary()
    if detail and not records:
        return jsonify({
            "success": False,
            "error": "affix_not_found",
            "message": f"Forge-safe affix not found: {parsed['affix_id']}",
        }), 404
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "forge_safe_affix_bundle",
        "source_path": summary["source_path"],
        "result_count": len(records),
        "total_loaded_count": repository.count_affixes(),
        "total_affixes": repository.count_affixes(),
        "total_modifiers": repository.count_modifiers(),
        "query": {
            "limit": parsed["limit"],
            "offset": parsed["offset"],
            "q": parsed["q"],
            "affix_id": parsed["affix_id"],
            "source_type": parsed["source_type"],
            "item_type": parsed["item_type"],
            "include_modifiers": parsed["include_modifiers"],
        },
        "warning_count": summary["warning_count"],
        "warnings": summary["warnings"],
        "export_policy": summary["export_policy"],
        "export_status": summary["export_status"],
        "total_affix_records_seen": summary["total_affix_records_seen"],
        "excluded_affix_records": summary["excluded_affix_records"],
        "bundle_summary": summary["summary"],
        "cross_reference_validation": summary["cross_reference_validation"],
        "records": records,
    })


def _configured_export_path() -> Path | None:
    configured = current_app.config.get("FORGE_SAFE_AFFIX_EXPORT_PATH")
    if not configured:
        return None
    return Path(configured)


def _configured_bundle_path() -> Path | None:
    configured = current_app.config.get("FORGE_SAFE_AFFIX_BUNDLE_PATH")
    if not configured:
        return None
    return Path(configured)


def _bundle_catalog_enabled() -> bool:
    return current_app.config.get("FORGE_SAFE_AFFIX_BUNDLE_ENABLED", False)


def _configured_v2_affix_bundle_path() -> Path:
    configured = current_app.config.get("V2_AFFIX_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_AFFIX_BUNDLE_PATH


def _configured_v2_item_base_bundle_path() -> Path:
    configured = current_app.config.get("V2_ITEM_BASE_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_ITEM_BASE_BUNDLE_PATH


def _configured_v2_item_implicit_bundle_path() -> Path:
    configured = current_app.config.get("V2_ITEM_IMPLICIT_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_ITEM_IMPLICIT_BUNDLE_PATH


def _configured_v2_unique_bundle_path() -> Path:
    configured = current_app.config.get("V2_UNIQUE_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_UNIQUE_BUNDLE_PATH


def _configured_v2_set_bundle_path() -> Path:
    configured = current_app.config.get("V2_SET_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_SET_BUNDLE_PATH


def _configured_v2_idol_bundle_path() -> Path:
    configured = current_app.config.get("V2_IDOL_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_IDOL_BUNDLE_PATH


def _configured_v2_idol_affix_bundle_path() -> Path:
    configured = current_app.config.get("V2_IDOL_AFFIX_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_IDOL_AFFIX_BUNDLE_PATH


def _configured_v2_class_mastery_bundle_path() -> Path:
    configured = current_app.config.get("V2_CLASS_MASTERY_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_CLASS_MASTERY_BUNDLE_PATH


def _configured_v2_passive_tree_bundle_path() -> Path:
    configured = current_app.config.get("V2_PASSIVE_TREE_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_PASSIVE_TREE_BUNDLE_PATH


def _configured_v2_skill_bundle_path() -> Path:
    configured = current_app.config.get("V2_SKILL_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_SKILL_BUNDLE_PATH


def _configured_v2_skill_tree_bundle_path() -> Path:
    configured = current_app.config.get("V2_SKILL_TREE_BUNDLE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_SKILL_TREE_BUNDLE_PATH


def _configured_v2_stat_registry_path() -> Path:
    configured = current_app.config.get("V2_STAT_REGISTRY_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_STAT_REGISTRY_PATH


def _configured_v2_modifier_registry_path() -> Path:
    configured = current_app.config.get("V2_MODIFIER_REGISTRY_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_V2_MODIFIER_REGISTRY_PATH


def _load_v2_affix_repository() -> V2AffixRepository:
    return V2AffixRepository(_configured_v2_affix_bundle_path()).load()


def _load_v2_item_repository() -> V2ItemRepository:
    return V2ItemRepository(
        _configured_v2_item_base_bundle_path(),
        _configured_v2_item_implicit_bundle_path(),
    ).load()


def _load_v2_unique_set_repository() -> V2UniqueSetRepository:
    return V2UniqueSetRepository(
        _configured_v2_unique_bundle_path(),
        _configured_v2_set_bundle_path(),
    ).load()


def _load_v2_idol_repository() -> V2IdolRepository:
    return V2IdolRepository(
        _configured_v2_idol_bundle_path(),
        _configured_v2_idol_affix_bundle_path(),
    ).load()


def _load_v2_class_mastery_repository() -> V2ClassMasteryRepository:
    return V2ClassMasteryRepository(_configured_v2_class_mastery_bundle_path()).load()


def _load_v2_passive_repository() -> V2PassiveRepository:
    return V2PassiveRepository(_configured_v2_passive_tree_bundle_path()).load()


def _load_v2_skill_repository() -> V2SkillRepository:
    return V2SkillRepository(
        _configured_v2_skill_bundle_path(),
        _configured_v2_skill_tree_bundle_path(),
    ).load()


def _load_v2_stat_registry() -> V2StatRegistry:
    return V2StatRegistry(_configured_v2_stat_registry_path()).load()


def _load_v2_modifier_registry() -> V2ModifierRegistry:
    return V2ModifierRegistry(_configured_v2_modifier_registry_path()).load()


def _parse_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "affix_id": request.args.get("affix_id") or "",
        "source_type": request.args.get("source_type") or "",
        "item_type": request.args.get("item_type") or "",
        "include_modifiers": _parse_bool(request.args.get("include_modifiers")),
        "errors": errors,
    }


def _parse_v2_affix_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "affix_id": request.args.get("affix_id") or "",
        "slot": request.args.get("slot") or "",
        "item_type": request.args.get("item_type") or "",
        "class_id": request.args.get("class_id") or "",
        "support_status": request.args.get("support_status") or "",
        "errors": errors,
    }


def _parse_v2_item_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "slot": request.args.get("slot") or "",
        "item_type": request.args.get("item_type") or "",
        "class_id": request.args.get("class_id") or "",
        "base_id": request.args.get("base_id") or request.args.get("item_base_id") or "",
        "errors": errors,
    }


def _parse_v2_idol_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "shape": request.args.get("shape") or "",
        "idol_type": request.args.get("idol_type") or request.args.get("item_type") or "",
        "class_id": request.args.get("class_id") or "",
        "mastery": request.args.get("mastery") or "",
        "errors": errors,
    }


def _parse_v2_class_mastery_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "class_id": request.args.get("class_id") or "",
        "errors": errors,
    }


def _parse_v2_passive_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "class_id": request.args.get("class_id") or "",
        "mastery_id": request.args.get("mastery_id") or "",
        "errors": errors,
    }


def _parse_v2_skill_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "class_id": request.args.get("class_id") or "",
        "mastery_id": request.args.get("mastery_id") or "",
        "errors": errors,
    }


def _parse_v2_modifier_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "source_type": request.args.get("source_type") or "",
        "stat_id": request.args.get("stat_id") or "",
        "errors": errors,
    }


def _parse_compare_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "include_details": _parse_bool(request.args.get("include_details")),
        "errors": errors,
    }


def _parse_non_negative_int(
    name: str,
    raw: str | None,
    default: int,
    errors: list[str],
) -> int:
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except ValueError:
        errors.append(f"{name} must be an integer")
        return default
    if value < 0:
        errors.append(f"{name} must be non-negative")
        return default
    return value


def _parse_bool(raw: str | None) -> bool:
    if raw is None:
        return False
    return raw.lower() in {"1", "true", "yes", "on"}


def _query_canonical_records(
    repository: ForgeSafeAffixRepository,
    *,
    affix_id: str,
    query: str,
    source_type: str,
    item_type: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    if affix_id:
        record = repository.get_by_affix_id(affix_id)
        records = [record] if record is not None else []
    elif query:
        records = repository.search(query, limit=repository.count())
    elif source_type:
        records = repository.filter_by_source_type(source_type, limit=repository.count())
    elif item_type:
        records = repository.filter_by_item_type(item_type, limit=repository.count())
    else:
        records = repository.list_affixes()

    if source_type and (affix_id or query or item_type):
        expected_source = source_type.lower()
        records = [
            record for record in records
            if str(record.get("source_type", "")).lower() == expected_source
        ]
    if item_type and (affix_id or query or source_type):
        expected_item = item_type.lower()
        records = [
            record for record in records
            if _record_matches_item_type(record, expected_item)
        ]
    return records[offset : offset + limit]


def _query_bundle_records(
    repository: ForgeSafeAffixBundleRepository,
    *,
    affix_id: str,
    query: str,
    source_type: str,
    item_type: str,
    limit: int,
    offset: int,
    include_modifiers: bool,
) -> list[dict[str, Any]]:
    if affix_id:
        if include_modifiers:
            bundle_record = repository.get_affix_with_modifiers(affix_id)
            records = [_format_bundle_record(bundle_record, include_modifiers=True)] if bundle_record else []
        else:
            record = repository.get_affix(affix_id)
            records = [_format_bundle_record({"affix": record}, include_modifiers=False)] if record else []
    elif query:
        records = repository.search_affixes(query, limit=repository.count_affixes())
    elif source_type:
        records = repository.filter_by_source_type(source_type, limit=repository.count_affixes())
    elif item_type:
        records = repository.filter_by_item_type(item_type, limit=repository.count_affixes())
    else:
        records = repository.list_affixes()

    if source_type and (affix_id or query or item_type):
        expected_source = source_type.lower()
        records = [
            record for record in records
            if str(record.get("source_type", "")).lower() == expected_source
        ]
    if item_type and (affix_id or query or source_type):
        expected_item = item_type.lower()
        records = [
            record for record in records
            if _record_matches_item_type(record, expected_item)
        ]

    page = records[offset : offset + limit]
    return [
        _format_bundle_affix(repository, record, include_modifiers=include_modifiers)
        for record in page
    ]


def _format_bundle_affix(
    repository: ForgeSafeAffixBundleRepository,
    affix: dict[str, Any],
    *,
    include_modifiers: bool,
) -> dict[str, Any]:
    identity = _source_affix_identity(affix)
    modifiers = repository.get_modifiers_for_affix(identity)
    record = dict(affix)
    record["modifier_count"] = len(modifiers)
    if include_modifiers:
        record["modifiers"] = modifiers
    return record


def _format_bundle_record(
    bundle_record: dict[str, Any] | None,
    *,
    include_modifiers: bool,
) -> dict[str, Any]:
    if not bundle_record or bundle_record.get("affix") is None:
        return {}
    record = dict(bundle_record["affix"])
    modifiers = bundle_record.get("modifiers") or []
    record["modifier_count"] = bundle_record.get("modifier_count", len(modifiers))
    if include_modifiers:
        record["modifiers"] = modifiers
    return record


def _record_matches_item_type(record: dict[str, Any], expected: str) -> bool:
    if str(record.get("item_type", "")).lower() == expected:
        return True
    return any(
        str(value).lower() == expected
        for value in (record.get("eligible_item_types") or [])
    )


def _source_affix_identity(record: dict[str, Any]) -> str:
    provenance = record.get("provenance")
    if isinstance(provenance, dict) and provenance.get("source_affix_identity"):
        return str(provenance["source_affix_identity"])
    return ""


def _v2_affix_response(
    repository: V2AffixRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_affix_bundle",
        "source_path": str(repository.bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count(),
        "total_affixes": repository.count(),
        "total_modifiers": summary["summary"].get("source_modifier_count"),
        "query": {
            "limit": parsed["limit"],
            "offset": parsed["offset"],
            "q": parsed["q"],
            "affix_id": parsed["affix_id"],
            "slot": parsed["slot"],
            "item_type": parsed["item_type"],
            "class_id": parsed["class_id"],
            "support_status": parsed["support_status"],
        },
        "warning_count": summary["summary"].get("records_with_warnings_count", 0),
        "warnings": [],
        "export_policy": "v2_affix_bundle",
        "export_status": "pass" if summary["summary"].get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary,
        "records": records,
    }


def _v2_item_base_response(
    repository: V2ItemRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_item_base_bundle",
        "source_path": str(repository.base_bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_bases(),
        "total_item_bases": repository.count_bases(),
        "total_implicits": repository.count_implicits(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_item_base_bundle",
        "export_status": "pass" if summary["base_summary"].get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary["base_summary"],
        "records": records,
    }


def _v2_item_implicit_response(
    repository: V2ItemRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_item_implicit_bundle",
        "source_path": str(repository.implicit_bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_implicits(),
        "total_item_bases": repository.count_bases(),
        "total_implicits": repository.count_implicits(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_item_implicit_bundle",
        "export_status": "pass" if summary["implicit_summary"].get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary["implicit_summary"],
        "records": records,
    }


def _v2_unique_response(
    repository: V2UniqueSetRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_unique_bundle",
        "source_path": str(repository.unique_bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_uniques(),
        "total_uniques": repository.count_uniques(),
        "total_sets": repository.count_sets(),
        "total_set_items": repository.count_set_items(),
        "total_set_bonuses": repository.count_set_bonuses(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_unique_bundle",
        "export_status": "pass" if summary["unique_summary"].get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary["unique_summary"],
        "records": records,
    }


def _v2_set_response(
    repository: V2UniqueSetRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_set_bundle",
        "source_path": str(repository.set_bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_sets(),
        "total_uniques": repository.count_uniques(),
        "total_sets": repository.count_sets(),
        "total_set_items": repository.count_set_items(),
        "total_set_bonuses": repository.count_set_bonuses(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_set_bundle",
        "export_status": "pass" if summary["set_summary"].get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary["set_summary"],
        "records": records,
    }


def _v2_unique_set_debug(data_source: str):
    try:
        repository = _load_v2_unique_set_repository()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_missing",
            "message": str(exc),
        }), 404
    except V2UniqueSetBundleError as exc:
        return jsonify({
            "success": False,
            "error": "v2_unique_set_bundle_invalid",
            "message": str(exc),
        }), 422
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": data_source,
        "debug_summary": repository.debug_summary(),
    })


def _v2_idol_response(
    repository: V2IdolRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
    *,
    data_source: str,
) -> dict[str, Any]:
    summary = repository.debug_summary()
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": data_source,
        "source_path": str(repository.idol_bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_idols(),
        "total_idols": repository.count_idols(),
        "total_idol_affixes": repository.count_affixes(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_idol_bundle",
        "export_status": "pass" if summary["idol_summary"].get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary["idol_summary"],
        "records": records,
    }


def _v2_idol_affix_response(
    repository: V2IdolRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_idol_affix_bundle",
        "source_path": str(repository.idol_affix_bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_affixes(),
        "total_idols": repository.count_idols(),
        "total_idol_affixes": repository.count_affixes(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_idol_affix_bundle",
        "export_status": "pass" if summary["idol_affix_summary"].get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary["idol_affix_summary"],
        "records": records,
    }


def _v2_class_mastery_response(
    repository: V2ClassMasteryRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
    *,
    data_source: str,
    record_kind: str,
) -> dict[str, Any]:
    summary = repository.debug_summary()["summary"]
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": data_source,
        "source_path": str(repository.bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_classes() if record_kind == "classes" else repository.count_masteries(),
        "total_classes": repository.count_classes(),
        "total_masteries": repository.count_masteries(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_class_mastery_bundle",
        "export_status": "pass" if summary.get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary,
        "records": records,
    }


def _v2_passive_response(
    repository: V2PassiveRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()["summary"]
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_passive_tree_bundle",
        "source_path": str(repository.bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_trees(),
        "total_passive_trees": repository.count_trees(),
        "total_passive_nodes": repository.count_nodes(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_passive_tree_bundle",
        "export_status": "pass" if summary.get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary,
        "records": records,
    }


def _v2_skill_response(
    repository: V2SkillRepository,
    records: list[dict[str, Any]],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    summary = repository.debug_summary()["skill_summary"]
    return {
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "v2_skill_bundle",
        "source_path": str(repository.skill_bundle_path),
        "result_count": len(records),
        "total_loaded_count": repository.count_skills(),
        "total_skills": repository.count_skills(),
        "total_skill_trees": repository.count_trees(),
        "total_skill_nodes": repository.count_nodes(),
        "query": parsed,
        "warning_count": 0,
        "warnings": [],
        "export_policy": "v2_skill_bundle",
        "export_status": "pass" if summary.get("validation_error_count", 0) == 0 else "blocked",
        "summary": summary,
        "records": records,
    }
