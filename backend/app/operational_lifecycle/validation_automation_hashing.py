"""Stable hashing for operational validation automation evidence."""

from __future__ import annotations

from typing import Any

from .lifecycle_hashing import deterministic_lifecycle_hash
from .validation_automation_models import OperationalValidationFinding, OperationalValidationReport
from .validation_automation_serialization import (
    export_operational_validation_finding,
    export_operational_validation_report_for_hash,
)


def deterministic_operational_validation_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_operational_validation_finding(finding: OperationalValidationFinding) -> str:
    return deterministic_operational_validation_hash(export_operational_validation_finding(finding))


def hash_operational_validation_report(report: OperationalValidationReport) -> str:
    return deterministic_operational_validation_hash(export_operational_validation_report_for_hash(report))
