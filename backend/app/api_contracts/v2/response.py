"""Standard response envelope helpers for experimental v2 APIs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SUPPORT_STATUSES = ("trusted", "partial", "text_only", "unsupported", "experimental", "unknown")


def standardize_v2_payload(payload: dict[str, Any], *, path: str, status_code: int) -> dict[str, Any]:
    """Return a v2 API envelope while preserving existing route-specific keys."""

    if not isinstance(payload, dict):
        return payload

    normalized = deepcopy(payload)
    domain = _domain_from_path(path)
    if _is_error_payload(normalized, status_code):
        return _standardize_error_payload(normalized, domain=domain, path=path, status_code=status_code)

    normalized.setdefault("data", _extract_data(normalized))
    normalized.setdefault("meta", _build_meta(normalized, domain=domain, path=path, status_code=status_code))
    normalized.setdefault("support_summary", _build_support_summary(normalized))
    normalized.setdefault("warnings", _extract_warnings(normalized))
    normalized.setdefault("provenance", _build_provenance(normalized))
    normalized.setdefault("debug", _build_debug(normalized, path=path))
    return normalized


def _standardize_error_payload(payload: dict[str, Any], *, domain: str, path: str, status_code: int) -> dict[str, Any]:
    legacy_code = str(payload.get("error") or "v2_api_error")
    message = str(payload.get("message") or legacy_code)
    details = payload.get("details") if isinstance(payload.get("details"), dict) else {}
    return {
        **payload,
        "error": {
            "code": legacy_code,
            "message": message,
            "details": details,
        },
        "meta": _build_meta(payload, domain=domain, path=path, status_code=status_code),
        "debug": {
            "route": path,
            "legacy_error_code": legacy_code,
            "read_only": True,
            "production_consumer": False,
        },
    }


def _is_error_payload(payload: dict[str, Any], status_code: int) -> bool:
    return status_code >= 400 or payload.get("success") is False


def _extract_data(payload: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key in ("record", "records", "debug_summary", "implicits", "masteries", "nodes", "comparison"):
        if key in payload:
            data[key] = deepcopy(payload[key])
    if "count" in payload:
        data["count"] = payload["count"]
    if "result_count" in payload:
        data["result_count"] = payload["result_count"]
    return data


def _build_meta(payload: dict[str, Any], *, domain: str, path: str, status_code: int) -> dict[str, Any]:
    summary = _summary_from_payload(payload)
    total_records = (
        payload.get("result_count")
        if payload.get("result_count") is not None
        else payload.get("count")
        if payload.get("count") is not None
        else _summary_total(summary)
    )
    meta = {
        "domain": domain,
        "route": path,
        "route_version": "v2",
        "status_code": status_code,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": payload.get("data_source"),
        "total_records": total_records,
        "schema_version": "v2.experimental",
    }
    if summary.get("generated_at"):
        meta["generated_at"] = summary["generated_at"]
    return meta


def _build_support_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _summary_from_payload(payload)
    counts = {status: 0 for status in SUPPORT_STATUSES}
    counts.update({str(key): int(value) for key, value in (summary.get("support_status_counts") or {}).items()})
    for record in _iter_records(payload):
        status = str(record.get("support_status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return {
        **counts,
        "stable_calculable": int(summary.get("stable_calculable_count") or 0),
        "audit_only": _audit_only_count(payload, summary),
        "unresolved": _unresolved_count(summary),
    }


def _build_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    provenance = {
        "data_source": payload.get("data_source"),
        "source_path": payload.get("source_path"),
        "production_consumed": False,
    }
    record = payload.get("record")
    if isinstance(record, dict) and isinstance(record.get("provenance"), dict):
        provenance["record_provenance"] = deepcopy(record["provenance"])
    return provenance


def _build_debug(payload: dict[str, Any], *, path: str) -> dict[str, Any]:
    debug_summary = payload.get("debug_summary") if isinstance(payload.get("debug_summary"), dict) else {}
    summary = _summary_from_payload(payload)
    return {
        "route": path,
        "repository_debug_summary": deepcopy(debug_summary),
        "validation_error_count": int(summary.get("validation_error_count") or 0),
        "validation_warning_count": int(summary.get("validation_warning_count") or 0),
        "read_only": True,
        "production_consumer": False,
        "value_policy_audit_only": "value" in str(payload.get("data_source") or "").lower(),
        "unresolved_skill_identity_count": _unresolved_count(summary),
    }


def _extract_warnings(payload: dict[str, Any]) -> list[Any]:
    warnings = payload.get("warnings")
    if isinstance(warnings, list):
        return deepcopy(warnings)
    record = payload.get("record")
    if isinstance(record, dict) and isinstance(record.get("warnings"), list):
        return deepcopy(record["warnings"])
    return []


def _summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    debug_summary = payload.get("debug_summary")
    if isinstance(debug_summary, dict):
        if isinstance(debug_summary.get("summary"), dict):
            return debug_summary["summary"]
        if isinstance(debug_summary.get("skill_summary"), dict):
            return debug_summary["skill_summary"]
        if isinstance(debug_summary.get("base_summary"), dict):
            return debug_summary["base_summary"]
        if isinstance(debug_summary.get("unique_summary"), dict):
            return debug_summary["unique_summary"]
    return payload.get("summary") if isinstance(payload.get("summary"), dict) else {}


def _iter_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("records")
    if isinstance(records, list):
        return [record for record in records if isinstance(record, dict)]
    record = payload.get("record")
    if isinstance(record, dict):
        return [record]
    return []


def _summary_total(summary: dict[str, Any]) -> int | None:
    for key in (
        "affix_count",
        "item_base_count",
        "implicit_count",
        "unique_count",
        "set_group_count",
        "idol_count",
        "idol_affix_count",
        "class_count",
        "mastery_count",
        "passive_tree_count",
        "skill_count",
        "stat_count",
        "modifier_count",
    ):
        if key in summary:
            return int(summary[key])
    return None


def _audit_only_count(payload: dict[str, Any], summary: dict[str, Any]) -> int:
    if "value" in str(payload.get("data_source") or "").lower():
        return int(summary.get("candidate_family_count") or summary.get("modifier_count") or 0)
    return 0


def _unresolved_count(summary: dict[str, Any]) -> int:
    for key in (
        "unresolved_reference_count",
        "class_mastery_unresolved_skill_link_count",
        "unresolved_skill_link_count",
        "source_identity_gap_count",
    ):
        if key in summary:
            return int(summary[key] or 0)
    return 0


def _domain_from_path(path: str) -> str:
    parts = [part for part in path.strip("/").split("/") if part]
    if parts and parts[0] == "api":
        parts = parts[1:]
    if len(parts) < 3 or parts[0] != "experimental" or parts[1] != "v2":
        return "unknown"
    domain = parts[2]
    if domain == "items":
        return "items"
    if domain == "idols":
        return "idols"
    if domain == "classes" or domain == "masteries":
        return "classes_masteries"
    if domain == "uniques" or domain == "sets":
        return "unique_sets"
    return domain
