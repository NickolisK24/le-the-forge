"""Deterministic serialization for operational integrity enforcement."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .integrity_enforcement_models import OperationalIntegrityFinding, OperationalIntegrityReport
from .lifecycle_serialization import stable_serialize


def export_operational_integrity_finding(finding: OperationalIntegrityFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["remediation_enabled"] = False
    data["correction_enabled"] = False
    data["repair_enabled"] = False
    data["approval_enabled"] = False
    data["authorization_enabled"] = False
    data["execution_enabled"] = False
    data["orchestration_execution_enabled"] = False
    return data


def sorted_operational_integrity_findings(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> list[OperationalIntegrityFinding]:
    return sorted(findings, key=lambda item: item.deterministic_key)


def export_operational_integrity_report(report: OperationalIntegrityReport) -> dict[str, Any]:
    data = asdict(report)
    data["findings"] = [
        export_operational_integrity_finding(finding)
        for finding in sorted_operational_integrity_findings(report.findings)
    ]
    data["integrity_enforcement_performed"] = True
    data["correction_enabled"] = False
    data["remediation_enabled"] = False
    data["repair_enabled"] = False
    data["approval_enabled"] = False
    data["authorization_enabled"] = False
    data["execution_enabled"] = False
    data["orchestration_execution_enabled"] = False
    return data


def export_operational_integrity_report_for_hash(report: OperationalIntegrityReport) -> dict[str, Any]:
    data = export_operational_integrity_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_operational_integrity_finding(finding: OperationalIntegrityFinding) -> str:
    return stable_serialize(export_operational_integrity_finding(finding))


def serialize_operational_integrity_report(report: OperationalIntegrityReport) -> str:
    return stable_serialize(export_operational_integrity_report(report))
