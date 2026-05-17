"""Stable hashing for v4.0 closeout certification evidence."""

from __future__ import annotations

from typing import Any

from .lifecycle_hashing import deterministic_lifecycle_hash
from .v4_closeout_models import V4CloseoutFinding, V4CloseoutReport
from .v4_closeout_serialization import export_v4_closeout_finding, export_v4_closeout_report_for_hash


def deterministic_v4_closeout_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_v4_closeout_finding(finding: V4CloseoutFinding) -> str:
    return deterministic_v4_closeout_hash(export_v4_closeout_finding(finding))


def hash_v4_closeout_report(report: V4CloseoutReport) -> str:
    return deterministic_v4_closeout_hash(export_v4_closeout_report_for_hash(report))
