"""Deterministic serialization for operational continuity certification."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .continuity_certification_models import (
    OperationalContinuityCertificationReport,
    OperationalContinuityFinding,
)
from .lifecycle_serialization import stable_serialize


def export_operational_continuity_finding(finding: OperationalContinuityFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["execution_authorized"] = False
    data["remediation_authorized"] = False
    data["production_consumption_enabled"] = False
    data["approval_enabled"] = False
    data["authorization_enabled"] = False
    data["execution_enabled"] = False
    data["orchestration_execution_enabled"] = False
    return data


def sorted_operational_continuity_findings(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> list[OperationalContinuityFinding]:
    return sorted(findings, key=lambda item: item.deterministic_key)


def export_operational_continuity_certification_report(
    report: OperationalContinuityCertificationReport,
) -> dict[str, Any]:
    data = asdict(report)
    data["findings"] = [
        export_operational_continuity_finding(finding)
        for finding in sorted_operational_continuity_findings(report.findings)
    ]
    data["execution_authorized"] = False
    data["remediation_authorized"] = False
    data["production_consumption_enabled"] = False
    data["approval_enabled"] = False
    data["authorization_enabled"] = False
    data["remediation_enabled"] = False
    data["repair_enabled"] = False
    data["execution_enabled"] = False
    data["orchestration_execution_enabled"] = False
    return data


def export_operational_continuity_certification_report_for_hash(
    report: OperationalContinuityCertificationReport,
) -> dict[str, Any]:
    data = export_operational_continuity_certification_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_operational_continuity_finding(finding: OperationalContinuityFinding) -> str:
    return stable_serialize(export_operational_continuity_finding(finding))


def serialize_operational_continuity_certification_report(
    report: OperationalContinuityCertificationReport,
) -> str:
    return stable_serialize(export_operational_continuity_certification_report(report))
