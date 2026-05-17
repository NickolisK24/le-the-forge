"""Stable hashing for operational integrity enforcement evidence."""

from __future__ import annotations

from typing import Any

from .integrity_enforcement_models import OperationalIntegrityFinding, OperationalIntegrityReport
from .integrity_enforcement_serialization import (
    export_operational_integrity_finding,
    export_operational_integrity_report_for_hash,
)
from .lifecycle_hashing import deterministic_lifecycle_hash


def deterministic_operational_integrity_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_operational_integrity_finding(finding: OperationalIntegrityFinding) -> str:
    return deterministic_operational_integrity_hash(export_operational_integrity_finding(finding))


def hash_operational_integrity_report(report: OperationalIntegrityReport) -> str:
    return deterministic_operational_integrity_hash(export_operational_integrity_report_for_hash(report))
