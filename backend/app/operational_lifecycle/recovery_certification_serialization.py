"""Deterministic serialization for rollback and recovery certification."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .lifecycle_serialization import stable_serialize
from .recovery_certification_models import RecoveryCertificationFinding, RecoveryCertificationReport


def export_recovery_certification_finding(finding: RecoveryCertificationFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["recovery_execution_authorized"] = False
    data["rollback_execution_authorized"] = False
    data["recovery_execution_enabled"] = False
    data["rollback_execution_enabled"] = False
    return data


def sorted_recovery_certification_findings(
    findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding],
) -> list[RecoveryCertificationFinding]:
    return sorted(findings, key=lambda item: item.deterministic_key)


def export_recovery_certification_report(report: RecoveryCertificationReport) -> dict[str, Any]:
    data = asdict(report)
    data["findings"] = [
        export_recovery_certification_finding(finding)
        for finding in sorted_recovery_certification_findings(report.findings)
    ]
    data["recovery_execution_authorized"] = False
    data["rollback_execution_authorized"] = False
    data["recovery_execution_enabled"] = False
    data["rollback_execution_enabled"] = False
    data["production_consumption_authorized"] = False
    return data


def export_recovery_certification_report_for_hash(report: RecoveryCertificationReport) -> dict[str, Any]:
    data = export_recovery_certification_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_recovery_certification_finding(finding: RecoveryCertificationFinding) -> str:
    return stable_serialize(export_recovery_certification_finding(finding))


def serialize_recovery_certification_report(report: RecoveryCertificationReport) -> str:
    return stable_serialize(export_recovery_certification_report(report))
