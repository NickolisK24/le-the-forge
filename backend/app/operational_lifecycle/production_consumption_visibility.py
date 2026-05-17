"""Fail-visible controlled production consumption governance visibility helpers."""

from __future__ import annotations

from .production_consumption_models import (
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION,
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS,
    PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED,
    PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED,
    PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED,
    PRODUCTION_CONSUMPTION_GATE_TYPES,
    PRODUCTION_CONSUMPTION_GATE_STATES,
    PRODUCTION_CONSUMPTION_SEVERITIES,
    PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL,
    PRODUCTION_CONSUMPTION_SEVERITY_WARNING,
    ProductionConsumptionGate,
    ProductionConsumptionGovernanceReport,
)


def count_production_consumption_gate_types(
    gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate],
) -> dict[str, int]:
    counts = {gate_type: 0 for gate_type in PRODUCTION_CONSUMPTION_GATE_TYPES}
    counts["invalid"] = 0
    for gate in gates:
        if gate.gate_type in counts:
            counts[gate.gate_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_production_consumption_gate_states(
    gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate],
) -> dict[str, int]:
    counts = {gate_state: 0 for gate_state in PRODUCTION_CONSUMPTION_GATE_STATES}
    counts["invalid"] = 0
    for gate in gates:
        if gate.gate_state in counts:
            counts[gate.gate_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_production_consumption_severities(
    gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate],
) -> dict[str, int]:
    counts = {severity: 0 for severity in PRODUCTION_CONSUMPTION_SEVERITIES}
    counts["invalid"] = 0
    for gate in gates:
        if gate.severity in counts:
            counts[gate.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def satisfied_gate_count(gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate]) -> int:
    return sum(1 for gate in gates if gate.gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED)


def blocked_gate_count(gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate]) -> int:
    return sum(1 for gate in gates if gate.gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED)


def unsupported_gate_count(gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate]) -> int:
    return sum(1 for gate in gates if gate.gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED)


def prohibited_gate_count(gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate]) -> int:
    return sum(1 for gate in gates if gate.gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED)


def unknown_gate_count(gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate]) -> int:
    return sum(1 for gate in gates if gate.gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN)


def warning_gate_count(gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate]) -> int:
    return sum(1 for gate in gates if gate.severity == PRODUCTION_CONSUMPTION_SEVERITY_WARNING)


def critical_gate_count(gates: tuple[ProductionConsumptionGate, ...] | list[ProductionConsumptionGate]) -> int:
    return sum(1 for gate in gates if gate.severity == PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL)


def build_production_consumption_visibility(report: ProductionConsumptionGovernanceReport) -> dict[str, object]:
    gates = report.gates
    gate_type_counts = count_production_consumption_gate_types(gates)
    return {
        "gate_type_counts": gate_type_counts,
        "gate_state_counts": count_production_consumption_gate_states(gates),
        "severity_counts": count_production_consumption_severities(gates),
        "satisfied_gate_count": report.satisfied_gate_count,
        "blocked_gate_count": report.blocked_gate_count,
        "unsupported_gate_count": report.unsupported_gate_count,
        "prohibited_gate_count": report.prohibited_gate_count,
        "unknown_gate_count": report.unknown_gate_count,
        "warning_count": report.warning_count,
        "critical_count": report.critical_count,
        "production_consumption_authorized": report.production_consumption_authorized,
        "production_consumption_enabled": report.production_consumption_enabled,
        "production_consumption_prohibition_visible": (
            gate_type_counts[PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION] > 0
        ),
        "production_consumption_readiness_visible": (
            gate_type_counts[PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS] > 0
        ),
        "visibility_is_descriptive_only": all(gate.descriptive_only for gate in gates),
        "approval_enabled": any(gate.approval_enabled for gate in gates),
        "authorization_enabled": any(gate.authorization_enabled for gate in gates),
        "production_gate_authorized": any(gate.production_consumption_authorized for gate in gates),
        "production_gate_enabled": any(gate.production_consumption_enabled for gate in gates),
        "production_bundle_consumption_enabled": any(gate.production_bundle_consumption_enabled for gate in gates),
        "planner_integration_enabled": any(gate.planner_integration_enabled for gate in gates),
        "planner_behavior_changed": any(gate.planner_behavior_changed for gate in gates),
        "remediation_enabled": any(gate.remediation_enabled for gate in gates),
        "execution_enabled": any(gate.execution_enabled for gate in gates),
        "orchestration_execution_enabled": any(gate.orchestration_execution_enabled for gate in gates),
        "runtime_mutation_enabled": any(gate.runtime_mutation_enabled for gate in gates),
        "hidden_gate_count": sum(1 for gate in gates if gate.hidden),
    }


def validate_production_consumption_visibility(report: ProductionConsumptionGovernanceReport) -> dict[str, object]:
    visibility = build_production_consumption_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.approval_enabled,
            report.authorization_enabled,
            report.deployment_enabled,
            report.remediation_enabled,
            report.execution_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.orchestration_execution_enabled,
            report.runtime_mutation_enabled,
            report.production_consumption_authorized,
            report.production_consumption_enabled,
            report.production_bundle_consumption_enabled,
            report.planner_integration_enabled,
            report.planner_behavior_changed,
            visibility["approval_enabled"],
            visibility["authorization_enabled"],
            visibility["production_gate_authorized"],
            visibility["production_gate_enabled"],
            visibility["production_bundle_consumption_enabled"],
            visibility["planner_integration_enabled"],
            visibility["planner_behavior_changed"],
            visibility["remediation_enabled"],
            visibility["execution_enabled"],
            visibility["orchestration_execution_enabled"],
            visibility["runtime_mutation_enabled"],
        )
        if enabled
    )
    return {
        **visibility,
        "capability_enabled_count": capability_enabled_count,
        "valid": (
            report.descriptive_only
            and report.replay_safe
            and report.rollback_safe
            and report.provenance_safe
            and report.lineage_safe
            and not report.production_consumption_authorized
            and not report.production_consumption_enabled
            and not report.planner_integration_enabled
            and not report.planner_behavior_changed
            and visibility["visibility_is_descriptive_only"]
            and visibility["production_consumption_prohibition_visible"]
            and visibility["production_consumption_readiness_visible"]
            and visibility["hidden_gate_count"] == 0
            and capability_enabled_count == 0
        ),
    }
