"""Stable serialization helpers for v4.1 closeout readiness."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass, replace
from typing import Any

from .v4_1_closeout_readiness_models import V41CloseoutIdentity, V41CloseoutReadiness


def _stable_value(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _stable_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple | list):
        return [_stable_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _stable_value(value[key]) for key in sorted(value)}
    return value


def _sorted_closeout(payload: V41CloseoutReadiness) -> V41CloseoutReadiness:
    return replace(
        payload,
        phase_coverage=tuple(
            sorted(payload.phase_coverage, key=lambda phase: (phase.deterministic_order, phase.phase_id))
        ),
        report_coverage=tuple(
            sorted(payload.report_coverage, key=lambda report: (report.deterministic_order, report.report_name))
        ),
        warnings=tuple(sorted(payload.warnings, key=lambda warning: (warning.deterministic_order, warning.warning_id))),
    )


def stable_serialize(value: Any) -> str:
    return json.dumps(_stable_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def export_v4_1_closeout_identity(identity: V41CloseoutIdentity) -> dict[str, Any]:
    return _stable_value(identity)


def serialize_v4_1_closeout_identity(identity: V41CloseoutIdentity) -> str:
    return stable_serialize(identity)


def export_v4_1_closeout_readiness(payload: V41CloseoutReadiness) -> dict[str, Any]:
    return _stable_value(_sorted_closeout(payload))


def serialize_v4_1_closeout_readiness(payload: V41CloseoutReadiness) -> str:
    return stable_serialize(export_v4_1_closeout_readiness(payload))
