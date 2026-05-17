"""Deterministic serialization for operational validation automation evidence."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .lifecycle_serialization import stable_serialize
from .validation_automation_models import OperationalValidationFinding, OperationalValidationReport


def export_operational_validation_finding(finding: OperationalValidationFinding) -> dict[str, Any]:
    return asdict(finding)


def sorted_operational_validation_findings(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> list[OperationalValidationFinding]:
    return sorted(findings, key=lambda item: item.deterministic_key)


def export_operational_validation_report(report: OperationalValidationReport) -> dict[str, Any]:
    data = asdict(report)
    data["findings"] = [
        export_operational_validation_finding(finding)
        for finding in sorted_operational_validation_findings(report.findings)
    ]
    data["operational_execution_authorized"] = False
    data["production_consumption_authorized"] = False
    return data


def export_operational_validation_report_for_hash(report: OperationalValidationReport) -> dict[str, Any]:
    data = export_operational_validation_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_operational_validation_finding(finding: OperationalValidationFinding) -> str:
    return stable_serialize(export_operational_validation_finding(finding))


def serialize_operational_validation_report(report: OperationalValidationReport) -> str:
    return stable_serialize(export_operational_validation_report(report))
