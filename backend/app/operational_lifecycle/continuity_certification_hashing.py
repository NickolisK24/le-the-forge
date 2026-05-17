"""Stable hashing for operational continuity certification evidence."""

from __future__ import annotations

from typing import Any

from .continuity_certification_models import (
    OperationalContinuityCertificationReport,
    OperationalContinuityFinding,
)
from .continuity_certification_serialization import (
    export_operational_continuity_certification_report_for_hash,
    export_operational_continuity_finding,
)
from .lifecycle_hashing import deterministic_lifecycle_hash


def deterministic_operational_continuity_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_operational_continuity_finding(finding: OperationalContinuityFinding) -> str:
    return deterministic_operational_continuity_hash(export_operational_continuity_finding(finding))


def hash_operational_continuity_certification_report(
    report: OperationalContinuityCertificationReport,
) -> str:
    return deterministic_operational_continuity_hash(
        export_operational_continuity_certification_report_for_hash(report)
    )
