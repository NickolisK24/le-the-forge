"""Deterministic serialization for operational diagnostics."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .diagnostics_models import OperationalDiagnosticEntry, OperationalDiagnosticsReport
from .lifecycle_serialization import stable_serialize


def export_operational_diagnostic_entry(entry: OperationalDiagnosticEntry) -> dict[str, Any]:
    data = asdict(entry)
    data["recommendations_present"] = False
    data["execution_authorized"] = False
    return data


def sorted_operational_diagnostic_entries(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> list[OperationalDiagnosticEntry]:
    return sorted(entries, key=lambda item: item.deterministic_key)


def export_operational_diagnostics_report(report: OperationalDiagnosticsReport) -> dict[str, Any]:
    data = asdict(report)
    data["entries"] = [
        export_operational_diagnostic_entry(entry)
        for entry in sorted_operational_diagnostic_entries(report.entries)
    ]
    data["category_counts"] = dict(sorted(report.category_counts.items()))
    data["severity_counts"] = dict(sorted(report.severity_counts.items()))
    data["recommendations_present"] = False
    data["execution_authorized"] = False
    return data


def export_operational_diagnostics_report_for_hash(report: OperationalDiagnosticsReport) -> dict[str, Any]:
    data = export_operational_diagnostics_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_operational_diagnostic_entry(entry: OperationalDiagnosticEntry) -> str:
    return stable_serialize(export_operational_diagnostic_entry(entry))


def serialize_operational_diagnostics_report(report: OperationalDiagnosticsReport) -> str:
    return stable_serialize(export_operational_diagnostics_report(report))
