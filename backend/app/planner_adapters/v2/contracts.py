"""Contracts for the v2 planner-safe adapter boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


PLANNER_ADAPTER_SAFETY_GATES = (
    "trusted_or_explicitly_supported_support_status",
    "known_canonical_id",
    "valid_provenance",
    "non_unsupported_mechanics",
    "non_text_only_behavior",
    "non_scripted_behavior",
    "planner_normalized_value_scale",
    "resolved_stat_identity",
    "resolved_source_identity",
    "backend_policy_stable_calculable",
)


BLOCKED_REASON_CODES = (
    "unstable_support_status",
    "missing_canonical_id",
    "missing_provenance",
    "unsupported_behavior",
    "text_only_behavior",
    "scripted_behavior",
    "unknown_behavior",
    "unknown_value_scale",
    "source_units_value_scale",
    "unresolved_stat_identity",
    "unknown_operation",
    "unresolved_skill_identity",
    "not_stable_calculable",
)


@dataclass(frozen=True)
class PlannerAdapterRecordEligibility:
    canonical_id: str
    source_type: str
    source_id: str
    eligible: bool
    stable_calculable: bool
    blocked_reasons: tuple[str, ...]
    support_status: str
    trust_level: str
    value_scale_status: str
    operation: str
    stat_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_id": self.canonical_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "eligible": self.eligible,
            "stable_calculable": self.stable_calculable,
            "blocked_reasons": list(self.blocked_reasons),
            "support_status": self.support_status,
            "trust_level": self.trust_level,
            "value_scale_status": self.value_scale_status,
            "operation": self.operation,
            "stat_id": self.stat_id,
        }


@dataclass
class PlannerAdapterDomainSummary:
    domain: str
    inspected_count: int = 0
    eligible_count: int = 0
    blocked_count: int = 0
    stable_calculable_count: int = 0
    blocked_reason_counts: dict[str, int] = field(default_factory=dict)

    def add(self, eligibility: PlannerAdapterRecordEligibility) -> None:
        self.inspected_count += 1
        if eligibility.eligible:
            self.eligible_count += 1
        else:
            self.blocked_count += 1
        if eligibility.stable_calculable:
            self.stable_calculable_count += 1
        for reason in eligibility.blocked_reasons:
            self.blocked_reason_counts[reason] = self.blocked_reason_counts.get(reason, 0) + 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "inspected_count": self.inspected_count,
            "eligible_count": self.eligible_count,
            "blocked_count": self.blocked_count,
            "stable_calculable_count": self.stable_calculable_count,
            "blocked_reason_counts": dict(sorted(self.blocked_reason_counts.items())),
        }
