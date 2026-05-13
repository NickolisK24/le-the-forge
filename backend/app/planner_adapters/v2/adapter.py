"""Read-only v2 planner-safe adapter boundary."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from app.normalization.v2 import V2ModifierRegistry
from app.repositories.v2.paths import artifact_path

from .contracts import PLANNER_ADAPTER_SAFETY_GATES, PlannerAdapterDomainSummary
from .eligibility import evaluate_modifier_record


class V2PlannerSafeAdapter:
    """Inspect v2 normalized modifier rows without enabling planner consumption."""

    def __init__(self, *, root: str | Path | None = None, modifier_registry: V2ModifierRegistry | None = None) -> None:
        self.root = Path(root) if root is not None else None
        self._modifier_registry = modifier_registry

    def load_modifier_registry(self) -> V2ModifierRegistry:
        if self._modifier_registry is not None:
            return self._modifier_registry
        return V2ModifierRegistry(artifact_path("modifier_registry", root=self.root)).load()

    def list_domains(self) -> list[str]:
        registry = self.load_modifier_registry()
        return sorted({str(record.get("source_type") or "unknown") for record in registry.list_modifiers()})

    def summarize_eligibility(self, *, sample_limit: int = 10) -> dict[str, Any]:
        registry = self.load_modifier_registry()
        domain_summaries: dict[str, PlannerAdapterDomainSummary] = {}
        global_reason_counts: Counter[str] = Counter()
        eligible_samples: list[dict[str, Any]] = []
        blocked_samples: list[dict[str, Any]] = []
        total = 0
        eligible = 0
        stable = 0

        for record in registry.list_modifiers():
            total += 1
            result = evaluate_modifier_record(record)
            domain = result.source_type
            domain_summary = domain_summaries.setdefault(domain, PlannerAdapterDomainSummary(domain=domain))
            domain_summary.add(result)
            global_reason_counts.update(result.blocked_reasons)
            if result.eligible:
                eligible += 1
                if len(eligible_samples) < sample_limit:
                    eligible_samples.append(result.to_dict())
            elif len(blocked_samples) < sample_limit:
                blocked_samples.append(result.to_dict())
            if result.stable_calculable:
                stable += 1

        return {
            "summary": {
                "domain_count": len(domain_summaries),
                "inspected_modifier_count": total,
                "eligible_planner_calculable_count": eligible,
                "blocked_modifier_count": total - eligible,
                "stable_calculable_count": stable,
                "production_consumed": False,
            },
            "domains": [summary.to_dict() for summary in sorted(domain_summaries.values(), key=lambda item: item.domain)],
            "blocked_reason_counts": dict(sorted(global_reason_counts.items())),
            "eligible_samples": eligible_samples,
            "blocked_samples": blocked_samples,
            "safety_gates": list(PLANNER_ADAPTER_SAFETY_GATES),
            "policy": {
                "read_only": True,
                "experimental": True,
                "production_consumed": False,
                "planner_consumed": False,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
        }
