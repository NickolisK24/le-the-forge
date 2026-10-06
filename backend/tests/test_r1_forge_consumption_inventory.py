"""AUDIT-R1: the Forge consumption inventory feeding the extraction denominator."""
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "r1_forge_consumption_inventory.py"


@pytest.fixture(scope="module")
def inv():
    spec = importlib.util.spec_from_file_location("r1_forge_consumption_inventory", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def snapshot(inv):
    return inv.build_snapshot(REPO, forge_commit="test")


def test_snapshot_is_deterministic(inv, snapshot):
    again = inv.build_snapshot(REPO, forge_commit="test")
    assert json.dumps(again, sort_keys=True) == json.dumps(snapshot, sort_keys=True)
    assert "generated_at" not in json.dumps(snapshot)


def test_every_synced_export_is_listed(snapshot):
    for name in ("affixes.json", "items.json", "uniques.json", "passive_trees.json", "ailments.json",
                 "quests.json", "timelines.json", "monster_mods.json", "zones.json", "localization"):
        assert name in snapshot["exports"], name


def test_affix_sync_written_by_main_is_resolved(snapshot):
    # sync_affixes returns data; main() writes items/affixes.json.
    assert snapshot["exports"]["affixes.json"]["data_files"] == ["items/affixes.json"]
    consumers = snapshot["exports"]["affixes.json"]["runtime_consumers"]
    assert "backend/app/game_data/pipeline.py" in consumers


@pytest.mark.parametrize("export", ["ailments.json", "quests.json", "timelines.json", "zones.json",
                                    "loot_tables.json", "monster_mods.json", "actors.json"])
def test_synced_but_unconsumed_exports(snapshot, export):
    # Audit EXT-9: synced into data/ but not read by production code.
    assert snapshot["exports"][export]["runtime_consumers"] == []


def test_directory_mkdir_is_not_a_consumer_signal(snapshot):
    for name, e in snapshot["exports"].items():
        if name != "localization":
            assert not any(df.endswith("/*") for df in e["data_files"]), name


def test_tests_are_not_consumers(snapshot):
    for e in snapshot["exports"].values():
        for c in e["runtime_consumers"] + e["report_only_references"]:
            assert "/tests/" not in c and "__tests__" not in c


def test_hand_authored_runtime_inputs_listed(snapshot):
    inputs = set(snapshot["non_extracted_runtime_inputs"])
    assert {"items/base_items.json", "progression/weaver_tree.json", "entities/enemy_profiles.json"} <= inputs
    assert "backend/app/game_data/skills.json" in snapshot["hand_authored_backend_inputs"]
