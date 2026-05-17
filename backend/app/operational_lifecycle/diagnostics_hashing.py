"""Stable hashing for operational diagnostics."""

from __future__ import annotations

from typing import Any

from .diagnostics_models import OperationalDiagnosticEntry, OperationalDiagnosticsReport
from .diagnostics_serialization import (
    export_operational_diagnostic_entry,
    export_operational_diagnostics_report_for_hash,
)
from .lifecycle_hashing import deterministic_lifecycle_hash


def deterministic_operational_diagnostics_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_operational_diagnostic_entry(entry: OperationalDiagnosticEntry) -> str:
    return deterministic_operational_diagnostics_hash(export_operational_diagnostic_entry(entry))


def hash_operational_diagnostics_report(report: OperationalDiagnosticsReport) -> str:
    return deterministic_operational_diagnostics_hash(export_operational_diagnostics_report_for_hash(report))
