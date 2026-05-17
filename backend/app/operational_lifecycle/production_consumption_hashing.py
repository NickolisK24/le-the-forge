"""Stable hashing for controlled production consumption governance."""

from __future__ import annotations

from typing import Any

from .lifecycle_hashing import deterministic_lifecycle_hash
from .production_consumption_models import ProductionConsumptionGate, ProductionConsumptionGovernanceReport
from .production_consumption_serialization import (
    export_production_consumption_gate,
    export_production_consumption_governance_report_for_hash,
)


def deterministic_production_consumption_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_production_consumption_gate(gate: ProductionConsumptionGate) -> str:
    return deterministic_production_consumption_hash(export_production_consumption_gate(gate))


def hash_production_consumption_governance_report(
    report: ProductionConsumptionGovernanceReport,
) -> str:
    return deterministic_production_consumption_hash(
        export_production_consumption_governance_report_for_hash(report)
    )
