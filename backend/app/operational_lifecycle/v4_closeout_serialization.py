"""Deterministic serialization for v4.0 closeout certification."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .lifecycle_serialization import stable_serialize
from .v4_closeout_models import V4CloseoutFinding, V4CloseoutReport


def export_v4_closeout_finding(finding: V4CloseoutFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["execution_authorized"] = False
    data["remediation_authorized"] = False
    data["production_consumption_enabled"] = False
    data["orchestration_enabled"] = False
    data["planner_integration_enabled"] = False
    data["approval_enabled"] = False
    data["authorization_enabled"] = False
    data["execution_enabled"] = False
    return data


def sorted_v4_closeout_findings(
    findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding],
) -> list[V4CloseoutFinding]:
    return sorted(findings, key=lambda item: item.deterministic_key)


def export_v4_closeout_report(report: V4CloseoutReport) -> dict[str, Any]:
    data = asdict(report)
    data["findings"] = [export_v4_closeout_finding(finding) for finding in sorted_v4_closeout_findings(report.findings)]
    data["execution_authorized"] = False
    data["remediation_authorized"] = False
    data["production_consumption_enabled"] = False
    data["orchestration_enabled"] = False
    data["planner_integration_enabled"] = False
    data["approval_enabled"] = False
    data["authorization_enabled"] = False
    data["remediation_enabled"] = False
    data["repair_enabled"] = False
    data["execution_enabled"] = False
    return data


def export_v4_closeout_report_for_hash(report: V4CloseoutReport) -> dict[str, Any]:
    data = export_v4_closeout_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_v4_closeout_finding(finding: V4CloseoutFinding) -> str:
    return stable_serialize(export_v4_closeout_finding(finding))


def serialize_v4_closeout_report(report: V4CloseoutReport) -> str:
    return stable_serialize(export_v4_closeout_report(report))
