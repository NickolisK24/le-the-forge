"""AUDIT-R2 P16: dangerous-fallback registry and ratchet gate.

The first test runs the real gate over the repository, so the backend suite
fails on a new unclassified fallback even before the dedicated CI job runs.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "fallback_gate"))

import gate  # noqa: E402
import scanner  # noqa: E402

# Measured by the R2 census (R2_FALLBACK_AUDIT.md). The ratchet may only go down from here;
# raising any of these is a reviewed change to this file.
CENSUS_DANGEROUS = 744
CENSUS_RUNTIME = 575
CENSUS_BY_OWNER = {
    "R2-P05": 111, "R2-P06": 56, "R2-P07": 23, "R2-P08": 139, "R2-P09": 8, "R2-P11": 116, "R2-P13": 43,
    "R2-P16": 6, "R2-P19": 10, "R6": 69, "archived (R2-P18)": 7, "deleted with its module (R2-P18)": 156,
}


# --- the real repository ----------------------------------------------------------------------

def test_repository_passes_the_gate():
    assert gate.check() == []


def test_registry_is_valid_and_machine_readable():
    entries = gate.load_registry()
    assert gate.validate_registry(entries) == []
    for e in entries:
        if e["classification"] == gate.DANGEROUS:
            assert {"file", "line", "symbol", "pattern", "family", "owner", "reason", "replacement",
                    "status"} <= set(e)


def test_baseline_never_exceeds_the_census():
    base = json.loads(gate.BASELINE.read_text())["dangerous_open_by_owner"]
    for owner, n in base.items():
        assert n <= CENSUS_BY_OWNER.get(owner, 0), owner
    entries = gate.load_registry()
    s = gate.summary(entries, gate.evaluate(gate.ROOT, entries))
    assert s["dangerous_open_total"] <= CENSUS_DANGEROUS
    assert s["dangerous_open_runtime"] <= CENSUS_RUNTIME
    assert s["new_unclassified"] == 0


def test_every_census_record_is_in_the_registry():
    census = REPO / "docs/audits/2026-10-system-deep-audit/r2/R2_FALLBACK_CENSUS.jsonl"
    ids = {json.loads(line)["id"] for line in census.read_text().splitlines() if line.strip()}
    reg = {e.get("census_id") for e in gate.load_registry()}
    assert ids <= reg


def test_cutover_check_counts_r2_owned_only():
    open_r2 = gate.cutover_check()
    entries = gate.load_registry()
    expected = sum(1 for e in entries if e["classification"] == gate.DANGEROUS and e["status"] == "OPEN"
                   and gate.is_r2_owned(e["owner"]))
    assert len(open_r2) == expected > 0          # cutover (R2-P20) is correctly blocked today
    assert not any("owner=R6" in x for x in open_r2)


def test_new_canonical_data_code_has_no_dangerous_entries():
    for e in gate.load_registry():
        if "app/canonical_data/" in e["file"]:
            assert e["classification"] == "NOT_A_FALLBACK", e


# --- synthetic repositories -------------------------------------------------------------------

def _repo(tmp_path: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def _classify(root: Path, cls: str = gate.DANGEROUS, owner: str = "R2-P05") -> list[dict]:
    out = []
    for c in scanner.scan(root):
        e = {"fp": c.key, "file": c.file, "line": c.line, "symbol": c.symbol, "pattern": c.pattern,
             "snippet": c.snippet, "classification": cls, "reason": "test", "family": "affixes"}
        if cls == gate.DANGEROUS:
            e.update(owner=owner, replacement="raise", status="OPEN")
        out.append(e)
    return out


def _baseline(entries) -> dict:
    return {"dangerous_open_by_owner": dict(collections.Counter(
        e["owner"] for e in entries if e["classification"] == gate.DANGEROUS and e["status"] == "OPEN"))}


PY = '''def tier(rec):
    return rec.get("tier", 0)
'''


def test_new_dangerous_pattern_is_unclassified(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    (root / "backend/app/m.py").write_text(PY + 'def name(r):\n    return r.get("name", "Unknown")\n')
    errs = gate.check(root, entries, _baseline(entries))
    assert len(errs) == 1 and "unclassified" in errs[0] and "get_default_unknown" in errs[0]


@pytest.mark.parametrize("text,pattern", [
    ("x = d.get('k', [])\n", "get_default_empty_list"),
    ("x = d.get('k') or 0\n", "or_0"),
    ("x = next(iter(things))\n", "next_iter"),
    ("x = matches[0]\n", "first_index_pick"),
    ("try:\n    f()\nexcept Exception:\n    pass\n", "except_pass"),
    ("for a in b:\n    try:\n        f()\n    except KeyError:\n        continue\n", "except_continue"),
    ("def g():\n    try:\n        return f()\n    except Exception:\n        return []\n", "except_return_empty"),
])
def test_backend_patterns_detected(tmp_path, text, pattern):
    root = _repo(tmp_path, {"backend/app/m.py": text})
    assert pattern in {c.pattern for c in scanner.scan(root)}


@pytest.mark.parametrize("text,pattern", [
    ("const a = x ?? 0;\n", "nullish_0"),
    ("const a = x || [];\n", "or_empty_list"),
    ("const a = list.find(f);\n", "find_result"),
    ("const c = cls ?? 'Sentinel';\n", "nullish_game_identity"),
    ("try { f(); } catch (e) {\n  return [];\n}\n", "catch_fallback"),
])
def test_frontend_patterns_detected(tmp_path, text, pattern):
    root = _repo(tmp_path, {"frontend/src/a.ts": text})
    assert pattern in {c.pattern for c in scanner.scan(root)}


def test_reraise_and_tests_are_not_candidates(tmp_path):
    root = _repo(tmp_path, {
        "backend/app/m.py": "try:\n    f()\nexcept KeyError:\n    raise\n",
        "backend/app/tests/t.py": "x = d.get('k', 0)\n",
        "frontend/src/a.test.ts": "const a = x ?? 0;\n",
        "frontend/src/b.ts": "try { f(); } catch (e) {\n  throw e;\n}\n",
    })
    assert scanner.scan(root) == []


def test_fingerprint_survives_moved_lines(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    (root / "backend/app/m.py").write_text("import os\n\n\n" + PY)
    assert gate.check(root, entries, _baseline(entries)) == []


def test_inline_annotation_classifies_but_not_as_dangerous(tmp_path):
    text = 'def label(r):\n    # fallback: SAFE_PRESENTATION — icon is cosmetic\n    return r.get("icon", "")\n'
    root = _repo(tmp_path, {"backend/app/m.py": text})
    assert gate.check(root, [], {"dangerous_open_by_owner": {}}) == []
    bare = text.replace("# fallback: SAFE_PRESENTATION — icon is cosmetic", "# icon")
    (root / "backend/app/m.py").write_text(bare)
    assert len(gate.check(root, [], {"dangerous_open_by_owner": {}})) == 1
    dangerous = text.replace("SAFE_PRESENTATION", "DANGEROUS_SILENT_FALLBACK")
    (root / "backend/app/m.py").write_text(dangerous)
    assert len(gate.check(root, [], {"dangerous_open_by_owner": {}})) == 1


def test_annotation_without_reason_does_not_count(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": 'x = d.get("icon", "")  # fallback: SAFE_PRESENTATION\n'})
    assert len(gate.check(root, [], {"dangerous_open_by_owner": {}})) == 1


def test_count_increase_fails_the_ratchet(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    base = _baseline(entries)
    (root / "backend/app/m.py").write_text(PY + 'def other(r):\n    return r.get("level", 0)\n')
    entries = _classify(root)           # someone registers the new one as OPEN debt
    errs = gate.check(root, entries, base)
    assert any("rose" in e for e in errs)


def test_debt_reassigned_to_another_owner_fails(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root, owner="R2-P05")
    errs = gate.check(root, _classify(root, owner="R6"), _baseline(entries))
    assert any("'R6'" in e and "rose" in e for e in errs)


def test_removed_dangerous_code_must_be_recorded_then_locked_in(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    base = _baseline(entries)
    (root / "backend/app/m.py").write_text('def tier(rec):\n    return rec["tier"]\n')
    errs = gate.check(root, entries, base)
    assert any("no longer matches the code" in e for e in errs)
    entries[0]["status"] = "REMOVED"
    errs = gate.check(root, entries, base)
    assert len(errs) == 1 and "fell" in errs[0]           # ratchet: lower the baseline
    assert gate.check(root, entries, _baseline(entries)) == []


def test_marked_removed_but_still_present_fails(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    entries[0]["status"] = "REPLACED_WITH_EXPLICIT_UNSUPPORTED"
    errs = gate.check(root, entries, _baseline(entries))
    assert any("still in the code" in e for e in errs)


def test_proven_safe_stays_present_and_needs_proof(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    entries[0]["status"] = "PROVEN_SAFE"
    assert any("needs a proof" in e for e in gate.check(root, entries, _baseline(entries)))
    entries[0]["proof"] = "tier is required by the canonical schema; absence is rejected at load"
    assert gate.check(root, entries, _baseline(entries)) == []


@pytest.mark.parametrize("field", ["owner", "replacement", "family", "symbol"])
def test_dangerous_entry_must_be_complete(tmp_path, field):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    del entries[0][field]
    assert any(f"without {field}" in e for e in gate.validate_registry(entries))


def test_unknown_status_and_classification_rejected(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": PY})
    entries = _classify(root)
    entries[0]["status"] = "FIXED"
    assert gate.validate_registry(entries)
    entries = _classify(root, cls="SAFE_PRESENTATION_FALLBACK")
    entries[0]["status"] = "OPEN"
    assert any("only dangerous" in e for e in gate.validate_registry(entries))
    entries = _classify(root, cls="FINE")
    assert any("unknown classification" in e for e in gate.validate_registry(entries))


def test_duplicate_lines_are_counted_as_a_multiset(tmp_path):
    two = PY + 'def tier2(rec):\n    return rec.get("tier", 0)\n'
    root = _repo(tmp_path, {"backend/app/m.py": two})
    entries = _classify(root)
    assert len(entries) == 2 and entries[0]["fp"] == entries[1]["fp"]
    (root / "backend/app/m.py").write_text(two + 'def tier3(rec):\n    return rec.get("tier", 0)\n')
    errs = gate.check(root, entries, _baseline(entries))
    assert len(errs) == 1 and "unclassified" in errs[0]


def test_manual_entries_tracked_by_source_line(tmp_path):
    root = _repo(tmp_path, {"backend/app/m.py": 'cls = "Sentinel"\n'})
    e = {"fp": None, "manual": True, "file": "backend/app/m.py", "line": 1, "symbol": None,
         "pattern": "literal_default_identity", "snippet": 'cls = "Sentinel"', "classification": gate.DANGEROUS,
         "reason": "default class", "family": "classes", "owner": "R2-P05", "replacement": "400", "status": "OPEN"}
    assert gate.check(root, [e], _baseline([e])) == []
    (root / "backend/app/m.py").write_text("cls = request_class\n")
    assert any("no longer matches" in x for x in gate.check(root, [e], _baseline([e])))


def test_cli(capsys):
    assert gate.main(["check"]) == 0
    assert "PASS" in capsys.readouterr().out
    assert gate.main(["report"]) == 0
    assert json.loads(capsys.readouterr().out)["new_unclassified"] == 0
    assert gate.main(["cutover-check"]) == 1
