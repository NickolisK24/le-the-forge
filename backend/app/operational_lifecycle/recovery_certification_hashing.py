"""Stable hashing for rollback and recovery certification evidence."""

from __future__ import annotations

from typing import Any

from .lifecycle_hashing import deterministic_lifecycle_hash
from .recovery_certification_models import RecoveryCertificationFinding, RecoveryCertificationReport
from .recovery_certification_serialization import (
    export_recovery_certification_finding,
    export_recovery_certification_report_for_hash,
)


def deterministic_recovery_certification_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_recovery_certification_finding(finding: RecoveryCertificationFinding) -> str:
    return deterministic_recovery_certification_hash(export_recovery_certification_finding(finding))


def hash_recovery_certification_report(report: RecoveryCertificationReport) -> str:
    return deterministic_recovery_certification_hash(export_recovery_certification_report_for_hash(report))
