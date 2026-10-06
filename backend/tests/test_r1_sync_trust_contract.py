"""AUDIT-R1.13: the Forge sync carries upstream trust states through unchanged."""
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def sync(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("sync_game_data_r1", REPO / "scripts" / "sync_game_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = tmp_path / "led" / "exports_json"
    src.mkdir(parents=True)
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(mod, "SRC_DIR", src)
    monkeypatch.setattr(mod, "DATA_DIR", data)
    return mod, src, data


def _manifest(src: Path, families):
    canon = src.parent / "exports_canonical"
    canon.mkdir(exist_ok=True)
    (canon / "TRUST_MANIFEST.json").write_text(json.dumps(
        {"trust_schema": "r1_trust_manifest/1", "report_hash": "h", "patch": {"patch": "1.4.6"},
         "families": families}))


def test_absent_manifest_is_reported_not_invented(sync):
    mod, src, data = sync
    mod._write_version_stamp([])
    stamp = json.loads((data / "version.json").read_text())
    assert stamp["upstream_trust"]["status"] == "ABSENT"
    assert not (data / "upstream_trust_manifest.json").exists()


def test_states_and_reasons_carried_unchanged(sync):
    mod, src, data = sync
    fams = [{"family": "exports_json/affixes.json", "consumer_state": "QUARANTINED",
             "trusted_calculation_eligible": False, "reasons": ["upstream data_bundle action BLOCK"]},
            {"family": "exports_canonical/affixes.json", "consumer_state": "QUARANTINED", "reasons": ["x"]}]
    _manifest(src, fams)
    mod._write_version_stamp(["data/items/affixes.json"])
    stamp = json.loads((data / "version.json").read_text())
    t = stamp["upstream_trust"]
    assert t["status"] == "PRESENT" and t["manifest_hash"] == "h"
    assert t["exports"] == {"affixes.json": {"consumer_state": "QUARANTINED",
                                             "trusted_calculation_eligible": False,
                                             "reasons": ["upstream data_bundle action BLOCK"]}}
    copy = json.loads((data / "upstream_trust_manifest.json").read_text())
    assert copy["families"] == fams
