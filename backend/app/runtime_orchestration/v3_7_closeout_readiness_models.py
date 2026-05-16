"""Deterministic v3.7 closeout and v3.8 planning-readiness models.

The closeout models are audit evidence only. They do not authorize runtime
orchestration, route work, schedule work, dispatch work, traverse graphs,
optimize execution, recommend execution, or create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


V3_7_CLOSEOUT_PHASE_ID = "v3_7_closeout_and_v3_8_readiness"
V3_7_CLOSED_OUT_READY_FOR_V3_8_PLANNING = "v3_7_closed_out_ready_for_v3_8_planning"
V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING = "v3_7_closeout_blocked_for_v3_8_planning"

V37_CLOSEOUT_FINDING_CLOSEOUT_READY = "closeout_ready"
V37_CLOSEOUT_FINDING_CLOSEOUT_BLOCKED = "closeout_blocked"
V37_CLOSEOUT_FINDING_READINESS_CERTIFIED = "readiness_certified"
V37_CLOSEOUT_FINDING_READINESS_BLOCKED = "readiness_blocked"
V37_CLOSEOUT_FINDING_CONTINUITY_PRESERVED = "continuity_preserved"
V37_CLOSEOUT_FINDING_CONTINUITY_BROKEN = "continuity_broken"
V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_PRESERVED = "execution_boundary_preserved"
V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_BROKEN = "execution_boundary_broken"
V37_CLOSEOUT_FINDING_REPLAY_SAFE = "replay_safe"
V37_CLOSEOUT_FINDING_ROLLBACK_SAFE = "rollback_safe"
V37_CLOSEOUT_FINDING_PROVENANCE_SAFE = "provenance_safe"
V37_CLOSEOUT_FINDING_EXPLAINABILITY_SAFE = "explainability_safe"
V37_CLOSEOUT_FINDING_DETERMINISTIC = "deterministic"
V37_CLOSEOUT_FINDING_NON_EXECUTABLE = "non_executable"
V37_CLOSEOUT_FINDING_HIDDEN_RISK_DETECTED = "hidden_risk_detected"
V37_CLOSEOUT_FINDING_CLASSIFICATIONS: tuple[str, ...] = (
    V37_CLOSEOUT_FINDING_CLOSEOUT_READY,
    V37_CLOSEOUT_FINDING_CLOSEOUT_BLOCKED,
    V37_CLOSEOUT_FINDING_READINESS_CERTIFIED,
    V37_CLOSEOUT_FINDING_READINESS_BLOCKED,
    V37_CLOSEOUT_FINDING_CONTINUITY_PRESERVED,
    V37_CLOSEOUT_FINDING_CONTINUITY_BROKEN,
    V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_PRESERVED,
    V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_BROKEN,
    V37_CLOSEOUT_FINDING_REPLAY_SAFE,
    V37_CLOSEOUT_FINDING_ROLLBACK_SAFE,
    V37_CLOSEOUT_FINDING_PROVENANCE_SAFE,
    V37_CLOSEOUT_FINDING_EXPLAINABILITY_SAFE,
    V37_CLOSEOUT_FINDING_DETERMINISTIC,
    V37_CLOSEOUT_FINDING_NON_EXECUTABLE,
    V37_CLOSEOUT_FINDING_HIDDEN_RISK_DETECTED,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37CloseoutReadinessInput:
    certification: object | None = None
    omitted_phase_ids: tuple[str, ...] = ()
    manual_blocker_reasons: tuple[str, ...] = ()
    force_hidden_risk_detected: bool = False
    force_execution_boundary_violation: bool = False
    force_missing_replay_evidence: bool = False
    force_missing_rollback_evidence: bool = False

    def __post_init__(self) -> None:
        for field_name in ("omitted_phase_ids", "manual_blocker_reasons"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37CloseoutPhaseEvidence:
    phase_order: int
    phase_id: str
    phase_name: str
    reference_type: str
    evidence_reference_id: str
    artifact_id: str
    artifact_hash: str
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    replay_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    explainability_safe: bool = True
    deterministic_hash_present: bool = True
    non_executable_evidence: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_references",
            "explainability_references",
            "continuity_hashes",
            "replay_references",
            "rollback_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37CloseoutReadinessFinding:
    finding_id: str
    finding_classification: str
    subject_type: str
    subject_id: str
    severity: str
    summary: str
    evidence_references: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False
    active: bool = True
    active_violation: bool = False
    blocks_closeout: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class V37CloseoutReadinessResult:
    closeout_status: str
    v3_8_readiness_classification: str
    phase_id: str
    total_phases_audited: int
    phase_evidence: tuple[V37CloseoutPhaseEvidence, ...]
    findings: tuple[V37CloseoutReadinessFinding, ...]
    validation_totals: Mapping[str, int | bool | str]
    continuity_validation_totals: Mapping[str, int | bool | str]
    execution_boundary_audit_totals: Mapping[str, int | bool | str]
    replay_rollback_totals: Mapping[str, int | bool | str]
    provenance_explainability_totals: Mapping[str, int | bool | str]
    deterministic_guarantees: Mapping[str, int | bool | str]
    hidden_risk_totals: Mapping[str, int | bool | str]
    explanation_summary: tuple[str, ...]
    v3_8_allowed_expansion_summary: tuple[str, ...]
    v3_8_prohibited_expansion_summary: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    replay_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    deterministic_closeout_hash: str = ""
    closeout_is_non_executable: bool = True
    closeout_certifies_planning_intelligence_continuity_only: bool = True
    readiness_for_v3_8_planning: bool = True
    runtime_execution_readiness_certified: bool = False
    execution_authorization_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    traversal_enabled: bool = False
    runtime_path_selection_enabled: bool = False
    scenario_execution_selection_enabled: bool = False
    execution_recommendation_enabled: bool = False
    optimization_for_execution_enabled: bool = False
    callable_execution_flow_enabled: bool = False
    runtime_orchestration_engine_enabled: bool = False
    runtime_mutation_enabled: bool = False
    persistent_runtime_writes_enabled: bool = False
    autonomous_orchestration_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "phase_evidence",
            "findings",
            "explanation_summary",
            "v3_8_allowed_expansion_summary",
            "v3_8_prohibited_expansion_summary",
            "provenance_references",
            "explainability_references",
            "replay_references",
            "rollback_references",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_closeout_phase_evidence(evidence: V37CloseoutPhaseEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "provenance_references",
        "explainability_references",
        "continuity_hashes",
        "replay_references",
        "rollback_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_closeout_readiness_finding(finding: V37CloseoutReadinessFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_closeout_readiness_result(result: V37CloseoutReadinessResult) -> dict[str, Any]:
    data = asdict(result)
    data["phase_evidence"] = [
        export_v3_7_closeout_phase_evidence(evidence)
        for evidence in sorted(result.phase_evidence, key=lambda item: item.phase_order)
    ]
    data["findings"] = [
        export_v3_7_closeout_readiness_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    for field_name in (
        "validation_totals",
        "continuity_validation_totals",
        "execution_boundary_audit_totals",
        "replay_rollback_totals",
        "provenance_explainability_totals",
        "deterministic_guarantees",
        "hidden_risk_totals",
    ):
        data[field_name] = dict(sorted(data[field_name].items()))
    for field_name in (
        "explanation_summary",
        "v3_8_allowed_expansion_summary",
        "v3_8_prohibited_expansion_summary",
        "provenance_references",
        "explainability_references",
        "replay_references",
        "rollback_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def serialize_v3_7_closeout_readiness_result(result: V37CloseoutReadinessResult) -> str:
    return stable_serialize(export_v3_7_closeout_readiness_result(result))


def hash_v3_7_closeout_readiness_result(result: V37CloseoutReadinessResult) -> str:
    data = export_v3_7_closeout_readiness_result(result)
    data.pop("deterministic_closeout_hash", None)
    return deterministic_hash(data)


def validate_v3_7_closeout_serialization_stability(result: V37CloseoutReadinessResult) -> dict[str, Any]:
    first = serialize_v3_7_closeout_readiness_result(result)
    second = serialize_v3_7_closeout_readiness_result(result)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_7_closeout_readiness",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_closeout_hash_stability(result: V37CloseoutReadinessResult) -> dict[str, Any]:
    first = hash_v3_7_closeout_readiness_result(result)
    second = hash_v3_7_closeout_readiness_result(result)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_7_closeout_readiness",
    }
