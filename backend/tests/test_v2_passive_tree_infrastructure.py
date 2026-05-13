import json
from pathlib import Path

import pytest

from app.repositories.v2.passive_repository import V2PassiveBundleError, V2PassiveRepository
from scripts.report_v2_passive_tree_bundle import build_v2_passive_tree_bundle, validate_v2_passive_tree_records


def test_v2_passive_tree_bundle_generation(tmp_path):
    source, layout, classes = _write_sources(tmp_path)

    bundle, validation, unsupported = build_v2_passive_tree_bundle(source, layout, classes)

    assert bundle["summary"]["passive_tree_count"] == 1
    assert bundle["summary"]["passive_node_count"] == 2
    assert bundle["summary"]["layout_matched_node_count"] == 2
    assert bundle["summary"]["class_mastery_resolved_passive_tree_link_count"] == 1
    assert validation["summary"]["error_count"] == 0
    assert unsupported["summary"]["unsupported_or_text_only_count"] == 1
    tree = bundle["records"]["passive_trees"][0]
    nodes = bundle["records"]["passive_nodes"]
    assert tree["canonical_id"] == "passive_tree:mg_1"
    assert tree["owner_class_id"] == "class:mage"
    assert nodes[0]["canonical_id"] == "passive_node:mg_1:1"
    assert nodes[0]["position"] == {"x": 10.0, "y": 20.0}
    assert nodes[0]["special_behavior_classification"] == "partial_modifier"
    assert nodes[1]["special_behavior_classification"] == "unsupported_special_behavior"
    assert nodes[0]["stable_calculable"] is False


def test_v2_passive_validation_detects_duplicate_ids(tmp_path):
    bundle, _validation, _unsupported = _bundle(tmp_path)
    trees = bundle["records"]["passive_trees"]
    nodes = bundle["records"]["passive_nodes"]
    trees.append(dict(trees[0]))
    nodes.append(dict(nodes[0]))

    report = validate_v2_passive_tree_records(trees, nodes, _class_mastery_bundle())

    assert report["summary"]["duplicate_passive_tree_id_count"] == 1
    assert report["summary"]["duplicate_passive_node_id_count"] == 1
    with pytest.raises(V2PassiveBundleError, match="Duplicate canonical_id"):
        V2PassiveRepository("<bundle>").load_payload(bundle)


def test_v2_passive_validation_detects_missing_tree_and_class_link(tmp_path):
    bundle, _validation, _unsupported = _bundle(tmp_path)
    bundle["records"]["passive_trees"][0]["owner_class_id"] = "class:missing"
    bundle["records"]["passive_nodes"][0]["tree_id"] = "passive_tree:missing"

    report = validate_v2_passive_tree_records(bundle["records"]["passive_trees"], bundle["records"]["passive_nodes"], _class_mastery_bundle())

    assert report["summary"]["passive_tree_missing_class_link_count"] == 1
    assert report["summary"]["passive_node_missing_tree_link_count"] == 1
    with pytest.raises(V2PassiveBundleError, match="links missing tree"):
        V2PassiveRepository("<bundle>").load_payload(bundle)


def test_v2_passive_validation_requires_provenance_and_support_status(tmp_path):
    bundle, _validation, _unsupported = _bundle(tmp_path)
    bundle["records"]["passive_trees"][0]["provenance"] = {}
    bundle["records"]["passive_nodes"][0].pop("support_status")

    report = validate_v2_passive_tree_records(bundle["records"]["passive_trees"], bundle["records"]["passive_nodes"], _class_mastery_bundle())

    assert report["summary"]["missing_provenance_count"] == 1
    assert report["summary"]["missing_support_status_count"] == 1
    with pytest.raises(V2PassiveBundleError, match="missing provenance"):
        V2PassiveRepository("<bundle>").load_payload(bundle)


def test_v2_passive_repository_lookup_and_debug(tmp_path):
    bundle, _validation, _unsupported = _bundle(tmp_path)
    repository = V2PassiveRepository("<bundle>").load_payload(bundle)

    assert repository.count_trees() == 1
    assert repository.count_nodes() == 2
    assert repository.get_tree("passive_tree:mg_1")["display_name"] == "Mage Passive Tree"
    assert repository.get_node("passive_node:mg_1:1")["display_name"] == "Knowledge"
    assert repository.get_nodes_by_tree("passive_tree:mg_1")[0]["canonical_id"] == "passive_node:mg_1:1"
    assert repository.filter_trees(class_id="class:mage")[0]["canonical_id"] == "passive_tree:mg_1"
    assert repository.debug_summary()["production_consumer"] is False


def test_v2_passive_routes(app, tmp_path):
    bundle, _validation, _unsupported = _bundle(tmp_path)
    path = tmp_path / "v2_passive_tree_bundle.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")
    app.config["V2_PASSIVE_TREE_BUNDLE_PATH"] = str(path)
    client = app.test_client()

    trees = client.get("/experimental/v2/passives?class_id=class:mage")
    assert trees.status_code == 200
    assert trees.get_json()["records"][0]["canonical_id"] == "passive_tree:mg_1"

    detail = client.get("/experimental/v2/passives/passive_tree:mg_1")
    assert detail.status_code == 200
    assert detail.get_json()["nodes"][0]["canonical_id"] == "passive_node:mg_1:1"

    node = client.get("/experimental/v2/passives/passive_tree:mg_1/nodes/passive_node:mg_1:2")
    assert node.status_code == 200
    assert node.get_json()["record"]["special_behavior_classification"] == "unsupported_special_behavior"

    debug = client.get("/experimental/v2/passives/debug")
    assert debug.status_code == 200
    assert debug.get_json()["debug_summary"]["production_safe"] is False


def test_v2_passive_bundle_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "repositories" / "v2" / "passive_repository.py",
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "app" / "repositories" / "v2" / "paths.py",
        root / "backend" / "app" / "repositories" / "v2" / "registry.py",
        root / "backend" / "scripts" / "report_v2_passive_tree_bundle.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_passive_tree_bundle.json", "V2PassiveRepository")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _bundle(tmp_path: Path) -> tuple[dict, dict, dict]:
    source, layout, classes = _write_sources(tmp_path)
    return build_v2_passive_tree_bundle(source, layout, classes)


def _write_sources(tmp_path: Path) -> tuple[Path, Path, Path]:
    source = tmp_path / "passive_trees.json"
    layout = tmp_path / "passives.json"
    classes = tmp_path / "v2_class_mastery_bundle.json"
    source.write_text(json.dumps(_source_passives()), encoding="utf-8")
    layout.write_text(json.dumps(_layout_passives()), encoding="utf-8")
    classes.write_text(json.dumps(_class_mastery_bundle()), encoding="utf-8")
    return source, layout, classes


def _source_passives() -> dict:
    return {
        "meta": {"source": "test"},
        "passiveTrees": [
            {
                "class": "Mage",
                "treeId": "mg-1",
                "masteryNames": ["Mage", "Runemaster"],
                "nodes": [
                    {
                        "id": 1,
                        "name": "Knowledge",
                        "nodeDescription": "Grants [1] intelligence",
                        "maxPoints": 5,
                        "mastery": 0,
                        "masteryName": "Mage",
                        "masteryRequirement": 0,
                        "requirements": [],
                        "effectHints": [{"classification": "stat_modifier_serialized", "statName": "Intelligence", "value": "+1"}],
                    },
                    {
                        "id": 2,
                        "name": "Special Case",
                        "nodeDescription": "Special text",
                        "maxPoints": 1,
                        "mastery": 1,
                        "masteryName": "Runemaster",
                        "masteryRequirement": 20,
                        "requirements": [{"nodeId": 1, "requirement": 1}],
                        "effectHints": [{"classification": "unsafe_to_infer", "statName": "Special", "value": "+1"}],
                    },
                ],
            }
        ],
    }


def _layout_passives() -> list[dict]:
    return [
        {"id": "mg_1", "raw_node_id": 1, "character_class": "Mage", "x": 10, "y": 20, "connections": ["mg_2"], "node_type": "core"},
        {"id": "mg_2", "raw_node_id": 2, "character_class": "Mage", "x": 30, "y": 40, "connections": ["mg_1"], "node_type": "notable"},
    ]


def _class_mastery_bundle() -> dict:
    return {
        "records": {
            "classes": [
                {
                    "canonical_id": "class:mage",
                    "display_name": "Mage",
                    "passive_tree_ids": ["passive_tree:mg_1"],
                }
            ],
            "masteries": [
                {
                    "canonical_id": "mastery:mage:runemaster",
                    "display_name": "Runemaster",
                    "class_id": "class:mage",
                    "passive_tree_ids": [],
                }
            ],
        }
    }
