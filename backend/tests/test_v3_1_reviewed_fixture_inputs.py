import json

from app.planner_adapters.v3_1.reviewed_fixture_inputs import (
    build_reviewed_fixture_input_report,
    load_reviewed_fixture_input_sources,
    normalize_reviewed_fixture_inputs,
)
from scripts.report_v3_1_reviewed_fixture_inputs import (
    build_v3_1_reviewed_fixture_inputs_report,
    write_report,
)


def test_deterministic_normalization():
    sources = [_source("workflows", "baseline_fixture_workflows", [_fixture("fixture_b"), _fixture("fixture_a")])]

    first = normalize_reviewed_fixture_inputs(sources)
    second = normalize_reviewed_fixture_inputs(list(reversed(sources)))

    assert first == second
    assert [row["normalized_fixture_id"] for row in first] == ["fixture_a", "fixture_b"]


def test_duplicate_handling():
    sources = [
        _source("a", "baseline_fixture_workflows", [_fixture("fixture_a")]),
        _source("b", "baseline_fixture_workflows", [_fixture("fixture_a")]),
    ]
    report = build_reviewed_fixture_input_report(sources)

    assert report["duplicate_count"] == 1
    assert [row["status"] for row in report["normalized_fixture_inputs"]] == ["reviewed", "duplicate"]


def test_malformed_input_handling():
    sources = [_source("workflows", "baseline_fixture_workflows", [{"approval_state": "pending_review"}])]
    report = build_reviewed_fixture_input_report(sources)

    assert report["malformed_count"] == 1
    row = report["normalized_fixture_inputs"][0]
    assert row["status"] == "malformed"
    assert "missing_fixture_identifier" in row["reason_codes"]


def test_unsupported_input_handling():
    sources = [_source("workflows", "baseline_fixture_workflows", [_fixture("fixture_u", unsupported=True)])]
    report = build_reviewed_fixture_input_report(sources)

    assert report["unsupported_count"] == 1
    row = report["normalized_fixture_inputs"][0]
    assert row["status"] == "unsupported"
    assert "unsupported_fixture_visible" in row["reason_codes"]


def test_missing_source_is_visible(tmp_path):
    missing = tmp_path / "missing.json"
    loaded = load_reviewed_fixture_input_sources(
        [{"source_id": "missing", "source_type": "baseline_fixture_workflows", "path": str(missing)}]
    )
    report = build_reviewed_fixture_input_report(loaded)

    assert report["missing_source_count"] == 1
    assert report["normalized_fixture_inputs"][0]["status"] == "missing_source"


def test_no_production_routing_enablement():
    report = build_reviewed_fixture_input_report([_source("workflows", "baseline_fixture_workflows", [_fixture("fixture_a")])])

    assert report["safety_confirmations"]["production_output_affected"] is False
    assert report["safety_confirmations"]["reviewed_inputs_authorize_production_routing"] is False
    assert report["metadata"]["production_default_routing_authorized"] is False
    assert all(row["production_routing_authorized"] is False for row in report["normalized_fixture_inputs"])


def test_no_live_runtime_planner_dependency():
    report = build_reviewed_fixture_input_report([_source("sets", "persisted_fixture_sets", [_fixture_set("set_a")])])

    assert report["normalized_fixture_count"] == 1
    assert report["metadata"]["planner_remap_performed"] is False


def test_report_generation_stability(tmp_path):
    first = build_v3_1_reviewed_fixture_inputs_report()
    second = build_v3_1_reviewed_fixture_inputs_report()

    assert first["reviewed_fixture_inputs"]["deterministic_hash"] == second["reviewed_fixture_inputs"]["deterministic_hash"]
    assert first["summary"] == second["summary"]

    output = tmp_path / "reviewed_inputs.json"
    write_report(first, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v3_1.reviewed_fixture_inputs_report.1"
    assert loaded["production_default_routing_authorized"] is False


def _source(source_id, source_type, records):
    if source_type == "baseline_fixture_workflows":
        payload = {"baseline_fixture_workflows": {"fixtures": records}}
    else:
        payload = {"persisted_fixture_sets": {"fixture_sets": records}}
    return {
        "source_id": source_id,
        "source_type": source_type,
        "source_path": f"fixture:{source_id}",
        "source_available": True,
        "payload": payload,
    }


def _fixture(fixture_id, unsupported=False):
    return {
        "fixture_id": fixture_id,
        "approval_state": "unsupported" if unsupported else "pending_review",
        "unsupported": unsupported,
        "blocked": False,
        "production_output_affected": False,
    }


def _fixture_set(fixture_set_id):
    return {
        "fixture_set_id": fixture_set_id,
        "lifecycle_state": "review_ready",
        "unsupported": False,
        "blocked": False,
        "production_output_affected": False,
    }
