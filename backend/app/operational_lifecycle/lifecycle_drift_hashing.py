"""Stable hashing for v4.0 patch lifecycle drift evidence."""

from __future__ import annotations

from typing import Any

from .lifecycle_drift_models import LifecycleDriftFinding, LifecycleDriftReport
from .lifecycle_drift_serialization import (
    export_lifecycle_drift_finding,
    export_lifecycle_drift_report_for_hash,
)
from .lifecycle_hashing import deterministic_lifecycle_hash


def deterministic_lifecycle_drift_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_lifecycle_drift_finding(finding: LifecycleDriftFinding) -> str:
    return deterministic_lifecycle_drift_hash(export_lifecycle_drift_finding(finding))


def hash_lifecycle_drift_report(report: LifecycleDriftReport) -> str:
    return deterministic_lifecycle_drift_hash(export_lifecycle_drift_report_for_hash(report))
