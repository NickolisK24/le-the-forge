"""Developer-only audit for affix stat/modifier reference evidence.

This module consumes generated diagnostic artifacts only. It does not read
production bundle families as authority, source exports directly, production
loaders, importers, routes, frontend code, crafting logic, simulation code,
build math, or gameplay output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.game_data.affix_diagnostic_consumer import (
    DEFAULT_DIAGNOSTICS_DIR,
    FORBIDDEN_PRODUCTION_USAGE,
    PHASE_ARTIFACTS,
    REPO_ROOT,
    validate_affix_diagnostic_output_path,
)


DIAGNOSTIC_NAME = "affix_stat_modifier_reference_audit"
DEFAULT_PER_AFFIX_ARTIFACT = (
    REPO_ROOT / "docs" / "generated" / "controlled_affix_per_affix_diagnostic_records.json"
)


class AffixStatModifierReferenceAuditError(RuntimeError):
    """Raised when stat/modifier reference diagnostics cannot be audited safely."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report


def audit_affix_stat_modifier_references(
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
    per_affix_artifact_path: str | Path = DEFAULT_PER_AFFIX_ARTIFACT,
) -> dict[str, Any]:
    """Audit current stat/modifier reference evidence from generated diagnostics."""

    phase_artifacts = _load_phase_artifacts(Path(diagnostics_dir))
    per_affix = _load_json(Path(per_affix_artifact_path))
    report = build_affix_stat_modifier_reference_audit(
        phase_artifacts,
        per_affix,
        diagnostics_dir=diagnostics_dir,
        per_affix_artifact_path=per_affix_artifact_path,
    )
    if any(error.get("severity") == "error" for error in report["findings"]):
        raise AffixStatModifierReferenceAuditError(
            "Affix stat/modifier reference audit found blocking diagnostic errors.",
            report=report,
        )
    return report


def build_affix_stat_modifier_reference_audit(
    phase_artifacts: dict[str, dict[str, Any]],
    per_affix_artifact: dict[str, Any],
    *,
    diagnostics_dir: str | Path,
    per_affix_artifact_path: str | Path,
) -> dict[str, Any]:
    """Build a serializable stat/modifier reference audit from loaded artifacts."""

    _require_phases(phase_artifacts)
    phase1 = phase_artifacts["phase_1_source_shape"]
    phase2 = phase_artifacts["phase_2_identity_provenance"]
    phase3 = phase_artifacts["phase_3_eligibility"]
    phase4 = phase_artifacts["phase_4_tag_category"]
    phase5 = phase_artifacts["phase_5_saved_vs_fresh"]
    records = per_affix_artifact.get("records") or []

    total_refs = int(_summary_value(phase1, "total_embedded_tiers"))
    unresolved_refs = int(_summary_value(phase1, "missing_stat_modifier_references"))
    malformed_refs = int(_summary_value(phase1, "malformed_tier_ranges"))
    unsupported_structures = int(_summary_value(phase1, "unsupported_or_unresolved_fields"))
    duplicate_refs = _duplicate_reference_count(phase1, records)
    ambiguous_refs = _ambiguous_reference_count(phase1)
    unsafe_identity = _unsafe_identity_count(phase2, phase3, phase4)
    missing_provenance = _missing_provenance_count(records)
    resolved_refs = max(total_refs - unresolved_refs, 0)
    deterministic_stable = _deterministic_output_stable(per_affix_artifact, phase5)

    findings = _findings(
        phase_artifacts,
        per_affix_artifact,
        unresolved_refs=unresolved_refs,
        duplicate_refs=duplicate_refs,
        ambiguous_refs=ambiguous_refs,
        malformed_refs=malformed_refs,
        unsupported_structures=unsupported_structures,
        missing_provenance=missing_provenance,
        unsafe_identity=unsafe_identity,
    )
    validation_status = _validation_status(findings)
    safe_categories, unsafe_categories = _category_disposition(
        total_refs=total_refs,
        resolved_refs=resolved_refs,
        unresolved_refs=unresolved_refs,
        malformed_refs=malformed_refs,
        unsupported_structures=unsupported_structures,
        missing_provenance=missing_provenance,
        unsafe_identity=unsafe_identity,
    )

    return {
        "diagnostic": DIAGNOSTIC_NAME,
        "production_safe": False,
        "diagnostic_only": True,
        "scope": "non_production_read_only_stat_modifier_reference_audit",
        "diagnostics_dir": str(Path(diagnostics_dir)),
        "per_affix_artifact_path": str(Path(per_affix_artifact_path)),
        "validation_status": validation_status,
        "summary": {
            "total_affixes": _summary_value(phase1, "total_affixes"),
            "equipment_affixes": _summary_value(phase1, "equipment_affixes"),
            "idol_affixes": _summary_value(phase1, "idol_affixes"),
            "total_affix_stat_modifier_references": total_refs,
            "resolved_references": resolved_refs,
            "unresolved_references": unresolved_refs,
            "duplicate_references": duplicate_refs,
            "ambiguous_references": ambiguous_refs,
            "unsupported_modifier_structures": unsupported_structures,
            "malformed_modifier_structures": malformed_refs,
            "missing_provenance_source_references": missing_provenance,
            "unsafe_identity_assumption_references": unsafe_identity,
            "deterministic_inspection_output_stable": deterministic_stable,
            "production_safe": False,
        },
        "modifier_families": _modifier_families(phase1, phase4, per_affix_artifact),
        "structurally_safe_categories": safe_categories,
        "unsafe_categories": unsafe_categories,
        "minimum_guarantees_before_modifier_resolver": _minimum_guarantees(),
        "findings": findings,
        "warnings": _warning_messages(findings),
        "errors": _error_messages(findings),
        "forbidden_production_usage": list(FORBIDDEN_PRODUCTION_USAGE)
        + [
            "Do not use this audit as a gameplay modifier resolver.",
            "Do not treat structurally present references as gameplay-correct modifiers.",
        ],
        "notes": [
            "Resolved means structurally present in diagnostic evidence, not gameplay-ready.",
            "This audit does not interpret tooltip prose or modifier formulas.",
            "This audit does not create an affix modifier resolver.",
            "production_safe remains false.",
        ],
    }


def render_affix_stat_modifier_reference_audit(report: dict[str, Any]) -> str:
    """Render the audit report as markdown."""

    lines = [
        "# Affix Stat/Modifier Reference Audit",
        "",
        f"- diagnostic: {DIAGNOSTIC_NAME}",
        "- scope: non_production_read_only_stat_modifier_reference_audit",
        "- diagnostic_only: true",
        "- production_safe: false",
        f"- validation_status: {report['validation_status']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Modifier Families / Categories", ""])
    lines.extend(_format_bullets(report["modifier_families"]))
    lines.extend(["", "## Structurally Safe Categories", ""])
    lines.extend(_format_bullets(report["structurally_safe_categories"]))
    lines.extend(["", "## Unsafe / Blocked Categories", ""])
    lines.extend(_format_bullets(report["unsafe_categories"]))
    lines.extend(["", "## Minimum Guarantees Before Modifier Resolver", ""])
    lines.extend(_format_bullets(report["minimum_guarantees_before_modifier_resolver"]))
    lines.extend(["", "## Findings", ""])
    lines.extend(_format_bullets(report["findings"]))
    lines.extend(["", "## Errors", ""])
    lines.extend(_format_bullets(report["errors"]))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_format_bullets(report["warnings"]))
    lines.extend(["", "## Forbidden Production Usage", ""])
    lines.extend(_format_bullets(report["forbidden_production_usage"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- Diagnostic-only and non-production.",
            "- Read-only over generated diagnostic artifacts.",
            "- Does not modify source data or generated production output.",
            "- Does not modify importers, loaders, runtime behavior, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "- Does not create a gameplay modifier resolver.",
            "- Does not claim gameplay correctness or production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def affix_stat_modifier_reference_audit_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_affix_stat_modifier_reference_audit_output_path(path: Path) -> None:
    validate_affix_diagnostic_output_path(path)


def _load_phase_artifacts(diagnostics_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        phase: _load_json(diagnostics_dir / filename)
        for phase, filename in PHASE_ARTIFACTS.items()
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing affix stat/modifier audit input: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Affix stat/modifier audit input must be a JSON object: {path}")
    return data


def _require_phases(artifacts: dict[str, dict[str, Any]]) -> None:
    missing = sorted(set(PHASE_ARTIFACTS) - set(artifacts))
    if missing:
        raise ValueError(f"Missing affix diagnostic phases: {', '.join(missing)}")


def _summary_value(data: dict[str, Any], key: str) -> Any:
    return (data.get("summary") or {}).get(key, 0)


def _duplicate_reference_count(phase1: dict[str, Any], records: list[dict[str, Any]]) -> int:
    summary_value = int(_summary_value(phase1, "duplicate_stat_modifier_references") or 0)
    warning_count = sum(
        1
        for warning in phase1.get("warnings") or []
        if isinstance(warning, dict)
        and "duplicate" in str(warning.get("code", "")).lower()
        and ("modifier" in str(warning.get("code", "")).lower() or "stat" in str(warning.get("code", "")).lower())
    )
    record_count = sum(
        1
        for record in records
        for warning in record.get("warnings") or []
        if isinstance(warning, dict)
        and "duplicate" in str(warning.get("code", "")).lower()
        and ("modifier" in str(warning.get("code", "")).lower() or "stat" in str(warning.get("code", "")).lower())
    )
    return max(summary_value, warning_count, record_count)


def _ambiguous_reference_count(phase1: dict[str, Any]) -> int:
    explicit = int(_summary_value(phase1, "ambiguous_stat_modifier_references") or 0)
    if explicit:
        return explicit
    return sum(
        1
        for warning in phase1.get("warnings") or []
        if isinstance(warning, dict)
        and "ambiguous" in str(warning.get("code", "")).lower()
        and ("modifier" in str(warning.get("code", "")).lower() or "stat" in str(warning.get("code", "")).lower())
    )


def _unsafe_identity_count(phase2: dict[str, Any], phase3: dict[str, Any], phase4: dict[str, Any]) -> int:
    keys = (
        (phase2, "affixes_relying_on_name_only_identity"),
        (phase2, "affixes_relying_on_subtype_id_only_identity"),
        (phase3, "eligibility_records_using_name_only_matching"),
        (phase3, "eligibility_records_using_subtype_id_only_identity"),
        (phase4, "tag_category_records_using_name_only_matching"),
        (phase4, "tag_category_records_using_subtype_id_only_identity"),
    )
    return sum(int(_summary_value(data, key) or 0) for data, key in keys)


def _missing_provenance_count(records: list[dict[str, Any]]) -> int:
    count = 0
    for record in records:
        provenance = record.get("provenance") or {}
        if not provenance.get("source_artifacts") or not provenance.get("source_record_identity"):
            count += 1
    return count


def _deterministic_output_stable(per_affix_artifact: dict[str, Any], phase5: dict[str, Any]) -> bool:
    if per_affix_artifact.get("production_safe") is not False:
        return False
    if per_affix_artifact.get("diagnostic_only") is not True:
        return False
    phase5_summary = phase5.get("summary") or {}
    drift_keys = (
        "phases_with_count_deltas",
        "phases_with_warning_deltas",
        "phases_with_error_deltas",
    )
    return all(int(phase5_summary.get(key) or 0) == 0 for key in drift_keys)


def _findings(
    phase_artifacts: dict[str, dict[str, Any]],
    per_affix_artifact: dict[str, Any],
    *,
    unresolved_refs: int,
    duplicate_refs: int,
    ambiguous_refs: int,
    malformed_refs: int,
    unsupported_structures: int,
    missing_provenance: int,
    unsafe_identity: int,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for phase, artifact in phase_artifacts.items():
        if artifact.get("production_safe") is not False:
            findings.append(_finding("production_safe_violation", "error", phase, "Phase artifact production_safe must be false."))
    if per_affix_artifact.get("production_safe") is not False:
        findings.append(_finding("production_safe_violation", "error", "per_affix_artifact", "Per-affix artifact production_safe must be false."))
    if per_affix_artifact.get("diagnostic_only") is not True:
        findings.append(_finding("diagnostic_only_violation", "error", "per_affix_artifact", "Per-affix artifact diagnostic_only must be true."))
    if unsafe_identity:
        findings.append(_finding("unsafe_identity_assumptions", "error", "phase_diagnostics", f"{unsafe_identity} references rely on unsafe identity assumptions."))
    if unresolved_refs:
        findings.append(_finding("unresolved_stat_modifier_references", "warning", "phase_1_source_shape", f"{unresolved_refs} stat/modifier references are unresolved."))
    if duplicate_refs:
        findings.append(_finding("duplicate_stat_modifier_references", "warning", "phase_1_source_shape", f"{duplicate_refs} duplicate stat/modifier references are present."))
    if ambiguous_refs:
        findings.append(_finding("ambiguous_stat_modifier_references", "warning", "phase_1_source_shape", f"{ambiguous_refs} ambiguous stat/modifier references are present."))
    if malformed_refs:
        findings.append(_finding("malformed_modifier_structures", "warning", "phase_1_source_shape", f"{malformed_refs} modifier/tier structures are malformed or semantically unresolved."))
    if unsupported_structures:
        findings.append(_finding("unsupported_modifier_structures", "warning", "phase_1_source_shape", f"{unsupported_structures} records contain unsupported or unresolved modifier structures."))
    if missing_provenance:
        findings.append(_finding("missing_provenance_source_references", "warning", "per_affix_artifact", f"{missing_provenance} per-affix records are missing provenance/source references."))
    if not findings:
        findings.append(_finding("no_blocking_findings", "info", "audit", "No stat/modifier reference safety issues were found in diagnostic evidence."))
    return sorted(findings, key=lambda item: (item["severity"], item["code"], item["source"]))


def _finding(code: str, severity: str, source: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "source": source, "message": message}


def _validation_status(findings: list[dict[str, Any]]) -> str:
    if any(finding.get("severity") == "error" for finding in findings):
        return "error"
    if any(finding.get("severity") == "warning" for finding in findings):
        return "warning"
    return "pass"


def _category_disposition(
    *,
    total_refs: int,
    resolved_refs: int,
    unresolved_refs: int,
    malformed_refs: int,
    unsupported_structures: int,
    missing_provenance: int,
    unsafe_identity: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    safe = [
        {
            "category": "diagnostic_embedded_tier_reference_slots",
            "count": total_refs,
            "status": "structurally_present_only",
            "notes": "Tier/reference slots are countable and deterministic, but not gameplay-ready.",
        },
        {
            "category": "references_with_structural_evidence",
            "count": resolved_refs,
            "status": "inspection_safe",
            "notes": "These references are present in diagnostics; formulas and gameplay semantics remain unaudited.",
        },
    ]
    unsafe = []
    if unresolved_refs:
        unsafe.append({"category": "unresolved_references", "count": unresolved_refs, "status": "unsafe_for_modifier_resolver"})
    if malformed_refs:
        unsafe.append({"category": "malformed_modifier_structures", "count": malformed_refs, "status": "unsafe_until_semantics_audited"})
    if unsupported_structures:
        unsafe.append({"category": "unsupported_modifier_structures", "count": unsupported_structures, "status": "unsafe_until_modeled"})
    if missing_provenance:
        unsafe.append({"category": "missing_provenance", "count": missing_provenance, "status": "unsafe_until_source_traceable"})
    if unsafe_identity:
        unsafe.append({"category": "unsafe_identity_assumptions", "count": unsafe_identity, "status": "blocking"})
    return safe, unsafe


def _modifier_families(
    phase1: dict[str, Any],
    phase4: dict[str, Any],
    per_affix_artifact: dict[str, Any],
) -> list[dict[str, Any]]:
    summary = per_affix_artifact.get("summary") or {}
    return [
        {
            "family": "equipment_affix_modifier_evidence",
            "count": summary.get("equipment_records") or _summary_value(phase1, "equipment_affixes"),
            "status": "diagnostic_only",
        },
        {
            "family": "idol_affix_modifier_evidence",
            "count": summary.get("idol_records") or _summary_value(phase1, "idol_affixes"),
            "status": "diagnostic_only",
        },
        {
            "family": "embedded_tier_modifier_slots",
            "count": summary.get("embedded_tier_count") or _summary_value(phase1, "total_embedded_tiers"),
            "status": "structurally_present_only",
        },
        {
            "family": "tag_category_modifier_context",
            "count": _summary_value(phase4, "known_tag_category_families"),
            "status": "warning_metadata_only",
        },
    ]


def _minimum_guarantees() -> list[str]:
    return [
        "Every modifier reference must have stable source identity and provenance.",
        "No modifier may rely on display-name-only identity.",
        "No modifier may rely on subtype_id-only identity.",
        "Unresolved stat/modifier references must be zero or explicitly policy-classified as warning-only.",
        "Malformed tier/modifier structures need a documented semantic policy before resolution.",
        "Unsupported TypeTree or extra fields must be modeled or explicitly excluded.",
        "Diagnostic output must remain deterministic with saved-vs-fresh comparison coverage.",
        "A future modifier resolver must stay non-production until a separate production readiness review.",
    ]


def _warning_messages(findings: list[dict[str, Any]]) -> list[str]:
    return [finding["message"] for finding in findings if finding.get("severity") == "warning"]


def _error_messages(findings: list[dict[str, Any]]) -> list[str]:
    return [finding["message"] for finding in findings if finding.get("severity") == "error"]


def _format_bullets(items: list[Any]) -> list[str]:
    if not items:
        return ["- none"]
    lines = []
    for item in items:
        if isinstance(item, dict):
            rendered = ", ".join(f"{key}={value}" for key, value in item.items())
            lines.append(f"- {rendered}")
        else:
            lines.append(f"- {item}")
    return lines
