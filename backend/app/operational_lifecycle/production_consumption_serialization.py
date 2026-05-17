"""Deterministic serialization for controlled production consumption governance."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .lifecycle_serialization import stable_serialize
from .production_consumption_models import ProductionConsumptionGate, ProductionConsumptionGovernanceReport


def export_production_consumption_gate(gate: ProductionConsumptionGate) -> dict[str, Any]:
    data = asdict(gate)
    data["production_consumption_authorized"] = False
    data["production_consumption_enabled"] = False
    data["production_bundle_consumption_enabled"] = False
    data["planner_integration_enabled"] = False
    data["planner_behavior_changed"] = False
    return data


def sorted_production_consumption_gates(
    gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate],
) -> list[ProductionConsumptionGate]:
    return sorted(gates, key=lambda item: item.deterministic_key)


def export_production_consumption_governance_report(
    report: ProductionConsumptionGovernanceReport,
) -> dict[str, Any]:
    data = asdict(report)
    data["gates"] = [
        export_production_consumption_gate(gate)
        for gate in sorted_production_consumption_gates(report.gates)
    ]
    data["production_consumption_authorized"] = False
    data["production_consumption_enabled"] = False
    data["production_bundle_consumption_enabled"] = False
    data["planner_integration_enabled"] = False
    data["planner_behavior_changed"] = False
    return data


def export_production_consumption_governance_report_for_hash(
    report: ProductionConsumptionGovernanceReport,
) -> dict[str, Any]:
    data = export_production_consumption_governance_report(report)
    data.pop("deterministic_report_hash", None)
    return data


def serialize_production_consumption_gate(gate: ProductionConsumptionGate) -> str:
    return stable_serialize(export_production_consumption_gate(gate))


def serialize_production_consumption_governance_report(
    report: ProductionConsumptionGovernanceReport,
) -> str:
    return stable_serialize(export_production_consumption_governance_report(report))
