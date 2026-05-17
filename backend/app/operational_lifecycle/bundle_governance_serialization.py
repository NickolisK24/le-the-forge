"""Deterministic serialization for trusted bundle governance evidence."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .bundle_governance_models import (
    TrustedBundleGovernanceFinding,
    TrustedBundleGovernanceReport,
    TrustedBundleIdentity,
    TrustedBundleStatus,
    TrustedBundleSupportStatus,
    TrustedBundleValidationStatus,
)
from .lifecycle_serialization import sorted_entries, stable_serialize


def export_trusted_bundle_identity(identity: TrustedBundleIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_trusted_bundle_status(status: TrustedBundleStatus) -> dict[str, Any]:
    return asdict(status)


def export_trusted_bundle_validation_status(status: TrustedBundleValidationStatus) -> dict[str, Any]:
    return asdict(status)


def export_trusted_bundle_support_status(status: TrustedBundleSupportStatus) -> dict[str, Any]:
    return asdict(status)


def export_trusted_bundle_governance_finding(finding: TrustedBundleGovernanceFinding) -> dict[str, Any]:
    return asdict(finding)


def sorted_trusted_bundle_governance_findings(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> list[TrustedBundleGovernanceFinding]:
    return sorted(findings, key=lambda item: item.deterministic_key)


def export_trusted_bundle_governance_report(report: TrustedBundleGovernanceReport) -> dict[str, Any]:
    data = asdict(report)
    data["bundle_identity"] = export_trusted_bundle_identity(report.bundle_identity)
    data["blocked_domains"] = sorted_entries(report.blocked_domains)
    data["findings"] = [
        export_trusted_bundle_governance_finding(finding)
        for finding in sorted_trusted_bundle_governance_findings(report.findings)
    ]
    data["production_consumption_authorized"] = False
    return data


def export_trusted_bundle_governance_report_for_hash(report: TrustedBundleGovernanceReport) -> dict[str, Any]:
    data = export_trusted_bundle_governance_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_trusted_bundle_governance_finding(finding: TrustedBundleGovernanceFinding) -> str:
    return stable_serialize(export_trusted_bundle_governance_finding(finding))


def serialize_trusted_bundle_governance_report(report: TrustedBundleGovernanceReport) -> str:
    return stable_serialize(export_trusted_bundle_governance_report(report))
