import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inspect_forge_safe_affixes.py"
BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_cli_succeeds_on_valid_small_fixture(tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(1), _record(2)]))

    result = _run_cli("--input", str(path))

    assert result.returncode == 0
    assert "loaded_record_count: 2" in result.stdout
    assert "export_policy: deterministic_affix_only" in result.stdout
    assert "affix_id=1" in result.stdout
    assert result.stderr == ""


def test_cli_returns_nonzero_on_invalid_fixture(tmp_path):
    path = tmp_path / "bad.json"
    _write_json(path, _payload(records=[_record(1, forge_safe=False)]))

    result = _run_cli("--input", str(path))

    assert result.returncode == 1
    assert "forge_safe=true" in result.stderr


def test_cli_json_output_parses_successfully(tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(7)]))

    result = _run_cli("--input", str(path), "--json")

    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
    assert parsed["count"] == 1
    assert parsed["warning_count"] == 0
    assert parsed["sample_records"][0]["affix_id"] == 7


def test_cli_respects_limit(tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(1), _record(2), _record(3)]))

    result = _run_cli("--input", str(path), "--json", "--limit", "2")

    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert [record["affix_id"] for record in parsed["sample_records"]] == [1, 2]


def test_cli_uses_existing_loader_behavior_for_summary_warnings(tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    payload = _payload(records=[_record(1)])
    payload["summary"]["exported_affix_records"] = 3
    _write_json(path, payload)

    result = _run_cli("--input", str(path), "--json")

    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["warning_count"] == 1
    assert "summary.exported_affix_records=3" in parsed["warnings"][0]


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=BACKEND_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _payload(records):
    return {
        "artifact": "forge_safe_canonical_affixes",
        "export_policy": "deterministic_affix_only",
        "production_safe": False,
        "records": records,
        "summary": {
            "export_status": "warning",
            "exported_affix_records": len(records),
            "forge_safe_records_only": True,
            "production_safe": False,
        },
    }


def _record(affix_id, *, forge_safe=True):
    return {
        "affix_id": affix_id,
        "affix_name": f"Affix {affix_id}",
        "source_type": "equipment",
        "item_type": "Equipment",
        "eligible_item_types": ["AMULET"],
        "safety": {
            "export_policy": "deterministic_affix_only",
            "forge_safe": forge_safe,
            "production_safe": False,
        },
    }


def _write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
