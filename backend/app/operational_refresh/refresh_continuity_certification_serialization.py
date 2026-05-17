"""Stable serialization helpers for v4.1 refresh continuity certification."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from typing import Any

from .refresh_continuity_certification_models import (
    RefreshContinuityCertification,
    RefreshContinuityCertificationIdentity,
)


def _stable_value(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _stable_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple | list):
        return [_stable_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _stable_value(value[key]) for key in sorted(value)}
    return value


def _sorted_certifications(payload: RefreshContinuityCertification) -> RefreshContinuityCertification:
    ordered = tuple(
        sorted(
            payload.certifications,
            key=lambda certification: (certification.deterministic_order, certification.certification_id),
        )
    )
    if ordered == payload.certifications:
        return payload
    return RefreshContinuityCertification(
        identity=payload.identity,
        certifications=ordered,
        cross_layer_aggregation=payload.cross_layer_aggregation,
        continuity_metadata=payload.continuity_metadata,
        diagnostics=payload.diagnostics,
        explainability=payload.explainability,
        integrity_boundary=payload.integrity_boundary,
        governance=payload.governance,
        non_executable=payload.non_executable,
        descriptive_only=payload.descriptive_only,
        remediation_enabled=payload.remediation_enabled,
        automatic_correction_enabled=payload.automatic_correction_enabled,
        automatic_repair_enabled=payload.automatic_repair_enabled,
        refresh_execution_enabled=payload.refresh_execution_enabled,
        orchestration_enabled=payload.orchestration_enabled,
        automatic_sequencing_enabled=payload.automatic_sequencing_enabled,
        dependency_resolution_enabled=payload.dependency_resolution_enabled,
        schema_migration_execution_enabled=payload.schema_migration_execution_enabled,
        automatic_migration_enabled=payload.automatic_migration_enabled,
        rollback_execution_enabled=payload.rollback_execution_enabled,
        recovery_execution_enabled=payload.recovery_execution_enabled,
        planner_integration_enabled=payload.planner_integration_enabled,
        production_consumption_enabled=payload.production_consumption_enabled,
        recommendation_enabled=payload.recommendation_enabled,
        ranking_enabled=payload.ranking_enabled,
        scoring_enabled=payload.scoring_enabled,
        selection_enabled=payload.selection_enabled,
        optimization_enabled=payload.optimization_enabled,
        authorization_enabled=payload.authorization_enabled,
        approval_enabled=payload.approval_enabled,
        runtime_mutation_enabled=payload.runtime_mutation_enabled,
        hidden_remediation_behavior_enabled=payload.hidden_remediation_behavior_enabled,
        hidden_orchestration_behavior_enabled=payload.hidden_orchestration_behavior_enabled,
        implicit_execution_pathway_enabled=payload.implicit_execution_pathway_enabled,
    )


def stable_serialize(value: Any) -> str:
    return json.dumps(_stable_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def export_continuity_certification_identity(identity: RefreshContinuityCertificationIdentity) -> dict[str, Any]:
    return _stable_value(identity)


def serialize_continuity_certification_identity(identity: RefreshContinuityCertificationIdentity) -> str:
    return stable_serialize(identity)


def export_refresh_continuity_certification(payload: RefreshContinuityCertification) -> dict[str, Any]:
    return _stable_value(_sorted_certifications(payload))


def serialize_refresh_continuity_certification(payload: RefreshContinuityCertification) -> str:
    return stable_serialize(export_refresh_continuity_certification(payload))
