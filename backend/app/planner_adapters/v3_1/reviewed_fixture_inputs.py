"""Reviewed fixture input discovery and normalization.

This module is pure governance infrastructure. It reads candidate payloads
provided by callers, normalizes deterministic fixture input records, and never
integrates with production planner/runtime behavior.
"""

from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


REVIEWED_FIXTURE_INPUT_STATUSES = (
    "reviewed",
    "missing_source",
    "malformed",
    "duplicate",
    "unsupported",
)
STABLE_REVIEWED_INPUT_GENERATION_TOKEN = "v3_1_phase_6_reviewed_fixture_inputs_token"
SUPPORTED_SOURCE_TYPES = frozenset({"baseline_fixture_workflows", "persisted_fixture_sets"})


def discover_default_reviewed_fixture_input_sources(repo_root: Path | None = None) -> list[dict[str, Any]]:
    root = repo_root or Path(__file__).resolve().parents[4]
    generated = root / "docs" / "generated"
    return [
        {
            "source_id": "v3_1_baseline_fixture_workflows_report",
            "source_type": "baseline_fixture_workflows",
            "path": str(generated / "v3_1_baseline_fixture_workflows_report.json"),
        },
        {
            "source_id": "v3_1_persisted_fixture_sets_report",
            "source_type": "persisted_fixture_sets",
            "path": str(generated / "v3_1_persisted_fixture_sets_report.json"),
        },
    ]


def load_reviewed_fixture_input_sources(source_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    loaded: list[dict[str, Any]] = []
    for spec in sorted(source_specs, key=lambda row: str(row.get("source_id") or row.get("path") or "")):
        path = Path(str(spec.get("path") or ""))
        if not path.exists():
            loaded.append(_missing_source_record(spec, f"source path not found: {path}"))
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            loaded.append(_missing_source_record(spec, f"invalid source JSON: {exc}"))
            continue
        loaded.append(
            {
                "source_id": str(spec.get("source_id") or path.name),
                "source_type": str(spec.get("source_type") or "unknown"),
                "source_path": str(path),
                "payload": payload,
                "source_available": True,
            }
        )
    return loaded


def build_reviewed_fixture_input_report(source_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = normalize_reviewed_fixture_inputs(source_payloads)
    counts = Counter(record["status"] for record in normalized)
    report = {
        "schema_version": "v3_1.reviewed_fixture_inputs.1",
        "source_count": len(source_payloads),
        "discovered_input_source_count": len(source_payloads),
        "normalized_fixture_count": len(normalized),
        "duplicate_count": counts["duplicate"],
        "malformed_count": counts["malformed"],
        "unsupported_count": counts["unsupported"],
        "missing_source_count": counts["missing_source"],
        "reviewed_candidate_count": counts["reviewed"],
        "status_counts": {
            status: counts[status]
            for status in REVIEWED_FIXTURE_INPUT_STATUSES
        },
        "normalized_fixture_inputs": normalized,
        "safety_confirmations": {
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "legacy_planner_ownership_preserved": True,
            "runtime_state_mutated": False,
            "reviewed_inputs_authorize_production_routing": False,
        },
        "metadata": {
            "source": "v3_1_reviewed_fixture_inputs",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_REVIEWED_INPUT_GENERATION_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    report["deterministic_hash"] = deterministic_hash(report)
    return report


def normalize_reviewed_fixture_inputs(source_payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_records: list[dict[str, Any]] = []
    for source in sorted(source_payloads, key=lambda row: str(row.get("source_id") or "")):
        raw_records.extend(_records_from_source(source))

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for record in sorted(raw_records, key=lambda row: (str(row.get("input_id") or ""), str(row.get("source_id") or ""))):
        item = _normalize_record(record)
        if item["status"] == "reviewed" and item["normalized_fixture_id"] in seen:
            item["status"] = "duplicate"
            item["reason_codes"] = ["duplicate_fixture_identifier"]
        elif item["status"] == "reviewed":
            seen.add(item["normalized_fixture_id"])
        normalized.append(item)
    return normalized


def _records_from_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    if not source.get("source_available", True):
        return [
            {
                "source_id": source.get("source_id"),
                "source_type": source.get("source_type"),
                "source_path": source.get("source_path"),
                "input_id": source.get("source_id"),
                "status_hint": "missing_source",
                "reason_codes": [source.get("error") or "source_unavailable"],
            }
        ]
    source_type = str(source.get("source_type") or "")
    if source_type not in SUPPORTED_SOURCE_TYPES:
        return [
            {
                "source_id": source.get("source_id"),
                "source_type": source_type,
                "source_path": source.get("source_path"),
                "input_id": source.get("source_id"),
                "status_hint": "unsupported",
                "reason_codes": ["unsupported_source_type"],
            }
        ]
    payload = source.get("payload") or {}
    if source_type == "baseline_fixture_workflows":
        fixtures = (((payload.get("baseline_fixture_workflows") or {}).get("fixtures")) or [])
        if not isinstance(fixtures, list):
            return [_malformed_source(source, "baseline_fixture_workflows.fixtures_not_list")]
        return [
            {
                "source_id": source.get("source_id"),
                "source_type": source_type,
                "source_path": source.get("source_path"),
                "input_id": fixture.get("fixture_id") if isinstance(fixture, dict) else None,
                "status_hint": _status_from_fixture(fixture),
                "reason_codes": _reasons_from_fixture(fixture),
                "payload_digest": deterministic_hash({"fixture": fixture}),
            }
            for fixture in fixtures
        ]
    fixture_sets = (((payload.get("persisted_fixture_sets") or {}).get("fixture_sets")) or [])
    if not isinstance(fixture_sets, list):
        return [_malformed_source(source, "persisted_fixture_sets.fixture_sets_not_list")]
    return [
        {
            "source_id": source.get("source_id"),
            "source_type": source_type,
            "source_path": source.get("source_path"),
            "input_id": fixture_set.get("fixture_set_id") if isinstance(fixture_set, dict) else None,
            "status_hint": _status_from_fixture_set(fixture_set),
            "reason_codes": _reasons_from_fixture_set(fixture_set),
            "payload_digest": deterministic_hash({"fixture_set": fixture_set}),
        }
        for fixture_set in fixture_sets
    ]


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    input_id = record.get("input_id")
    status = str(record.get("status_hint") or "reviewed")
    reason_codes = [str(reason) for reason in record.get("reason_codes") or []]
    if not input_id:
        status = "malformed"
        reason_codes = reason_codes or ["missing_fixture_identifier"]
        normalized_id = f"malformed:{record.get('source_id')}"
    else:
        normalized_id = _normalize_identifier(str(input_id))
    if status not in REVIEWED_FIXTURE_INPUT_STATUSES:
        status = "malformed"
        reason_codes = reason_codes or ["unknown_input_status"]
    return {
        "normalized_fixture_id": normalized_id,
        "source_fixture_id": str(input_id) if input_id is not None else None,
        "source_id": str(record.get("source_id") or ""),
        "source_type": str(record.get("source_type") or ""),
        "source_path": str(record.get("source_path") or ""),
        "status": status,
        "reason_codes": sorted(set(reason_codes or [f"{status}_fixture_input"])),
        "payload_digest": record.get("payload_digest"),
        "production_output_affected": False,
        "production_routing_authorized": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _normalize_identifier(value: str) -> str:
    return "_".join(value.strip().lower().replace("\\", "/").replace(":", "_").split())


def _status_from_fixture(fixture: Any) -> str:
    if not isinstance(fixture, dict):
        return "malformed"
    state = str(fixture.get("approval_state") or "")
    if fixture.get("unsupported") or state in {"unsupported", "blocked", "insufficient_data"}:
        return "unsupported"
    return "reviewed"


def _reasons_from_fixture(fixture: Any) -> list[str]:
    if not isinstance(fixture, dict):
        return ["fixture_record_not_object"]
    if not fixture.get("fixture_id"):
        return ["missing_fixture_identifier"]
    state = str(fixture.get("approval_state") or "")
    if fixture.get("unsupported"):
        return ["unsupported_fixture_visible"]
    if fixture.get("blocked") or state == "blocked":
        return ["blocked_fixture_visible"]
    if state == "insufficient_data":
        return ["insufficient_data_fixture_visible"]
    return [f"approval_state_{state or 'unknown'}"]


def _status_from_fixture_set(fixture_set: Any) -> str:
    if not isinstance(fixture_set, dict):
        return "malformed"
    state = str(fixture_set.get("lifecycle_state") or "")
    if fixture_set.get("unsupported") or fixture_set.get("blocked") or state in {"unsupported", "blocked", "insufficient_data"}:
        return "unsupported"
    return "reviewed"


def _reasons_from_fixture_set(fixture_set: Any) -> list[str]:
    if not isinstance(fixture_set, dict):
        return ["fixture_set_record_not_object"]
    if not fixture_set.get("fixture_set_id"):
        return ["missing_fixture_set_identifier"]
    state = str(fixture_set.get("lifecycle_state") or "")
    if fixture_set.get("unsupported") or state == "unsupported":
        return ["unsupported_fixture_set_visible"]
    if fixture_set.get("blocked") or state == "blocked":
        return ["blocked_fixture_set_visible"]
    if state == "insufficient_data":
        return ["insufficient_data_fixture_set_visible"]
    return [f"lifecycle_state_{state or 'unknown'}"]


def _missing_source_record(spec: dict[str, Any], error: str) -> dict[str, Any]:
    return {
        "source_id": str(spec.get("source_id") or spec.get("path") or "missing_source"),
        "source_type": str(spec.get("source_type") or "unknown"),
        "source_path": str(spec.get("path") or ""),
        "source_available": False,
        "error": error,
    }


def _malformed_source(source: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "source_id": source.get("source_id"),
        "source_type": source.get("source_type"),
        "source_path": source.get("source_path"),
        "input_id": source.get("source_id"),
        "status_hint": "malformed",
        "reason_codes": [reason],
    }
