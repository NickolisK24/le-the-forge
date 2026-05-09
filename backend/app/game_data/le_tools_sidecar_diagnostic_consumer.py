"""Developer-only consumer for saved LE Tools import context sidecars."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from app.game_data.bundle_item_type_dry_run_resolver import (
    STATUS_DEFERRED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
)
from app.game_data.le_tools_import_context_sidecar_validator import (
    load_sidecar,
    validate_sidecar_artifact,
)


BLOCKED_STATUSES = {STATUS_NEEDS_CONTEXT, STATUS_NEEDS_REVIEW, STATUS_DEFERRED, STATUS_UNRESOLVED}


class SidecarDiagnosticConsumerError(RuntimeError):
    """Raised when a saved sidecar cannot be consumed safely."""

    def __init__(self, message: str, validation_result: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.validation_result = validation_result


def consume_sidecar_diagnostic(sidecar_path: str | Path) -> dict[str, Any]:
    """Validate and summarize a saved sidecar diagnostic artifact.

    This function reads a saved diagnostic sidecar only. It does not call the
    importer, mutate the sidecar, or activate production item resolution.
    """

    path = Path(sidecar_path)
    sidecar = load_sidecar(path)
    original = deepcopy(sidecar)
    validation = validate_sidecar_artifact(sidecar)
    if validation.get("status") == "failed" or validation.get("errors"):
        raise SidecarDiagnosticConsumerError(
            "Sidecar validation failed; refusing to consume diagnostic artifact.",
            validation_result=validation,
        )
    if sidecar != original:
        raise SidecarDiagnosticConsumerError("Sidecar validator mutated the input artifact.")

    records = [_record_from_item(item) for item in sidecar.get("items", [])]
    blocked = [record for record in records if record["resolver_status"] in BLOCKED_STATUSES]
    report = {
        "production_safe": False,
        "sidecar_path": str(path),
        "validation_status": validation["status"],
        "errors": validation["errors"],
        "warnings": validation["warnings"],
        "summary": validation["summary"],
        "records": records,
        "blocked_records": blocked,
        "resolved_records": [record for record in records if record["resolver_status"] == STATUS_RESOLVED],
        "records_requiring_base_type_id": [
            record for record in records if record["resolver_status"] == STATUS_NEEDS_CONTEXT
        ],
        "manual_review_records": [
            record for record in records if record["resolver_status"] == STATUS_NEEDS_REVIEW
        ],
        "unresolved_records": [
            record for record in records if record["resolver_status"] == STATUS_UNRESOLVED
        ],
        "subtype_only_blocked_records": [
            record for record in records if record["context"].get("subtype_only")
        ],
        "name_only_blocked_records": [
            record
            for record in records
            if not record["context"].get("has_raw_item_type_signal")
            and record["resolver_status"] != STATUS_RESOLVED
        ],
        "recommendations": _recommendations(validation, blocked),
    }
    return report


def render_consumer_report(report: dict[str, Any]) -> str:
    lines = [
        "# LE Tools Sidecar Diagnostic Consumer Report",
        "",
        f"- sidecar_path: {report['sidecar_path']}",
        f"- validation_status: {report['validation_status']}",
        "- production_safe: false",
        "",
        "## Validation",
        "",
        "### Errors",
        "",
    ]
    lines.extend(_format_messages(report["errors"]))
    lines.extend(["", "### Warnings", ""])
    lines.extend(_format_messages(report["warnings"]))
    lines.extend(["", "## Summary", ""])
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Resolved Records", ""])
    resolved = report["resolved_records"]
    if not resolved:
        lines.append("- none")
    for record in resolved:
        lines.append(
            "- index={index} slot={slot} raw_type={raw_type} bundle={bundle} match={match}".format(
                index=record["index"],
                slot=record["slot"] or "null",
                raw_type=record["raw_item_type"] or "null",
                bundle=record["bundle_item_type_id"] or "null",
                match=record["match_source"] or "none",
            )
        )

    lines.extend(["", "## Blocked Records", ""])
    blocked = report["blocked_records"]
    if not blocked:
        lines.append("- none")
    for record in blocked:
        lines.append(
            "- index={index} slot={slot} raw_type={raw_type} status={status} raw_base={raw_base} "
            "mapped_base={mapped_base} bundle={bundle}".format(
                index=record["index"],
                slot=record["slot"] or "null",
                raw_type=record["raw_item_type"] or "null",
                status=record["resolver_status"],
                raw_base=record["raw_base_type_id"],
                mapped_base=record["mapped_base_type_id"],
                bundle=record["bundle_item_type_id"] or "null",
            )
        )
        for warning in record["warnings"]:
            lines.append(f"  - warning: {warning}")
        for note in record["notes"]:
            lines.append(f"  - note: {note}")

    lines.extend(["", "## Context Gaps", ""])
    lines.append(f"- records_requiring_base_type_id: {len(report['records_requiring_base_type_id'])}")
    lines.append(f"- manual_review_records: {len(report['manual_review_records'])}")
    lines.append(f"- unresolved_records: {len(report['unresolved_records'])}")
    lines.append(f"- subtype_only_blocked_records: {len(report['subtype_only_blocked_records'])}")
    lines.append(f"- name_only_blocked_records: {len(report['name_only_blocked_records'])}")

    lines.extend(["", "## Recommendations", ""])
    lines.extend(_format_messages(report["recommendations"]))
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- This report is developer-only and reads a saved sidecar artifact.",
            "- It does not call the LET importer, API routes, frontend code, or production loaders.",
            "- production_safe remains false globally and per record.",
            "- Warning-only validation is allowed only with visible warnings.",
            "",
            "## What This Proves",
            "",
            "- A saved sidecar artifact can be validated and consumed by diagnostic tooling.",
            "- Resolver statuses can be reported without activating production migration.",
            "",
            "## What This Does Not Prove",
            "",
            "- Live LET payload shape.",
            "- Production importer migration.",
            "- Production bundle consumption.",
            "- Base item production migration.",
            "",
        ]
    )
    return "\n".join(lines)


def consumer_report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def _record_from_item(item: dict[str, Any]) -> dict[str, Any]:
    raw = item.get("raw") or {}
    mapped = item.get("mapped") or {}
    resolver = item.get("resolver") or {}
    context = item.get("context") or {}
    return {
        "index": item.get("index"),
        "slot": item.get("slot"),
        "raw_item_type": raw.get("item_type"),
        "raw_base_type_id": raw.get("base_type_id"),
        "mapped_base_type_id": mapped.get("base_type_id"),
        "resolver_status": resolver.get("status"),
        "bundle_item_type_id": resolver.get("bundle_item_type_id"),
        "match_source": resolver.get("match_source"),
        "production_safe": False,
        "warnings": list(resolver.get("warnings") or []),
        "notes": list(resolver.get("notes") or []),
        "context": {
            "has_base_type_id": bool(context.get("has_base_type_id")),
            "has_subtype_id": bool(context.get("has_subtype_id")),
            "subtype_only": bool(context.get("subtype_only")),
            "has_raw_item_type_signal": bool(context.get("has_raw_item_type_signal")),
            "requires_test_pairing": bool(context.get("requires_test_pairing")),
        },
    }


def _recommendations(validation: dict[str, Any], blocked_records: list[dict[str, Any]]) -> list[str]:
    recommendations = [
        "Keep this consumer developer-only until a separate non-production migration review is complete.",
        "Do not consume bundle item type IDs in production from this report.",
    ]
    if validation.get("status") == "warning":
        recommendations.append("Review validation warnings before using this report as a diagnostic baseline.")
    if any(record["resolver_status"] == STATUS_NEEDS_CONTEXT for record in blocked_records):
        recommendations.append("Thread base_type_id context for needs_context records before resolution.")
    if any(record["resolver_status"] == STATUS_NEEDS_REVIEW for record in blocked_records):
        recommendations.append("Manually review needs_review records before adding adapter coverage.")
    if any(record["resolver_status"] == STATUS_UNRESOLVED for record in blocked_records):
        recommendations.append("Keep unresolved records blocked; do not fall back to name-only matching.")
    return recommendations


def _format_messages(messages: list[str]) -> list[str]:
    if not messages:
        return ["- none"]
    return [f"- {message}" for message in messages]
