"""Stable hashing for trusted bundle governance evidence."""

from __future__ import annotations

from typing import Any

from .bundle_governance_models import TrustedBundleGovernanceFinding, TrustedBundleGovernanceReport
from .bundle_governance_serialization import (
    export_trusted_bundle_governance_finding,
    export_trusted_bundle_governance_report_for_hash,
)
from .lifecycle_hashing import deterministic_lifecycle_hash


def deterministic_bundle_governance_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_trusted_bundle_governance_finding(finding: TrustedBundleGovernanceFinding) -> str:
    return deterministic_bundle_governance_hash(export_trusted_bundle_governance_finding(finding))


def hash_trusted_bundle_governance_report(report: TrustedBundleGovernanceReport) -> str:
    return deterministic_bundle_governance_hash(export_trusted_bundle_governance_report_for_hash(report))
