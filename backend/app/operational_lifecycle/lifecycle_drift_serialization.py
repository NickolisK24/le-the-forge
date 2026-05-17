"""Deterministic serialization for v4.0 lifecycle drift reports."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .lifecycle_drift_models import LifecycleDriftFinding, LifecycleDriftReport
from .lifecycle_serialization import stable_serialize


def export_lifecycle_drift_finding(finding: LifecycleDriftFinding) -> dict[str, Any]:
    return asdict(finding)


def sorted_lifecycle_drift_findings(
    findings: tuple[LifecycleDriftFinding, ...] | list[LifecycleDriftFinding],
) -> list[LifecycleDriftFinding]:
    return sorted(findings, key=lambda item: item.deterministic_key)


def export_lifecycle_drift_report(report: LifecycleDriftReport) -> dict[str, Any]:
    data = asdict(report)
    data["findings"] = [
        export_lifecycle_drift_finding(finding) for finding in sorted_lifecycle_drift_findings(report.findings)
    ]
    return data


def export_lifecycle_drift_report_for_hash(report: LifecycleDriftReport) -> dict[str, Any]:
    data = export_lifecycle_drift_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_lifecycle_drift_finding(finding: LifecycleDriftFinding) -> str:
    return stable_serialize(export_lifecycle_drift_finding(finding))


def serialize_lifecycle_drift_report(report: LifecycleDriftReport) -> str:
    return stable_serialize(export_lifecycle_drift_report(report))
