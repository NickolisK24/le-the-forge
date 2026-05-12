"""Validation helpers for canonical v2 contracts."""

from __future__ import annotations

from .canonical_base import CanonicalRecord
from .canonical_id import validate_canonical_id
from .trust_level import STABLE_TRUST_LEVELS, TrustLevel, coerce_trust_level
from .trust_status import STABLE_CALCULABLE_STATUSES, SupportStatus, coerce_support_status


def validate_support_status(value: str | SupportStatus) -> SupportStatus:
    return coerce_support_status(value)


def validate_trust_level(value: str | TrustLevel) -> TrustLevel:
    return coerce_trust_level(value)


def is_stable_calculable(
    support_status: str | SupportStatus,
    trust_level: str | TrustLevel,
    *,
    allow_partial: bool = False,
) -> bool:
    status = coerce_support_status(support_status)
    level = coerce_trust_level(trust_level)
    allowed_statuses = set(STABLE_CALCULABLE_STATUSES)
    if allow_partial:
        allowed_statuses.add(SupportStatus.PARTIAL)
    return status in allowed_statuses and level in STABLE_TRUST_LEVELS


def assert_generated_record_provenance(record: CanonicalRecord) -> None:
    if record.provenance is None:
        raise ValueError("canonical record provenance is required")
    if record.trust_level == TrustLevel.GENERATED_FROM_GAME_DATA:
        if not record.provenance.source_path or not record.provenance.extraction_method:
            raise ValueError("generated records require source path and extraction method")


def assert_stable_planner_eligible(record: CanonicalRecord, *, allow_partial: bool = False) -> None:
    assert_generated_record_provenance(record)
    validate_canonical_id(record.canonical_id)
    if record.trust_level == TrustLevel.PLACEHOLDER:
        raise ValueError("placeholder records are not stable planner eligible")
    if not is_stable_calculable(
        record.support_status,
        record.trust_level,
        allow_partial=allow_partial,
    ):
        raise ValueError(
            f"{record.canonical_id} is not stable planner eligible "
            f"({record.support_status.value}, {record.trust_level.value})"
        )
