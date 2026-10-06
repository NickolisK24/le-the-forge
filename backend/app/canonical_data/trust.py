"""Trust states and the consumption policy (AUDIT-R2 contract, B2).

Vocabulary is R1's (``tools/scripts/r1_trust.py`` in last-epoch-data),
carried unchanged. The Forge may narrow trust, never widen it.

Locked default (B2): UNCERTIFIED REQUIRED DATA DOES NOT ENTER TRUSTED
CALCULATIONS. There is no advisory-calculation mode. ADVISORY_DISPLAY exists
for labelled reference display only; adding an advisory calculation mode is a
product decision and requires changing this module and its tests.
"""
from __future__ import annotations

from enum import Enum

from .errors import CoverageInsufficient, ManifestInvalid, RelationshipIntegrityFailure, UntrustedFamily


class TrustState(str, Enum):
    CERTIFIED = "CERTIFIED"
    QUARANTINED = "QUARANTINED"
    PRESERVED_ONLY = "PRESERVED_ONLY"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class CoverageState(str, Enum):
    FIELDS_CLASSIFIED = "FIELDS_CLASSIFIED"
    FIELDS_UNKNOWN = "FIELDS_UNKNOWN"
    FIELDS_UNMEASURED = "FIELDS_UNMEASURED"


class RelationshipState(str, Enum):
    NONE_DISCOVERED = "NONE_DISCOVERED"
    RESOLVED_OR_ALLOWLISTED = "RESOLVED_OR_ALLOWLISTED"
    DANGLING = "DANGLING"


class ConsumptionMode(str, Enum):
    TRUSTED_CALCULATION = "TRUSTED_CALCULATION"
    ADVISORY_DISPLAY = "ADVISORY_DISPLAY"


# Which trust states each mode admits. Nothing else is ever admitted.
ADMITTED: dict[ConsumptionMode, frozenset[TrustState]] = {
    ConsumptionMode.TRUSTED_CALCULATION: frozenset({TrustState.CERTIFIED}),
    ConsumptionMode.ADVISORY_DISPLAY: frozenset({TrustState.CERTIFIED, TrustState.QUARANTINED}),
}

# B2 lock, asserted by tests: no mode lets uncertified data into a calculation.
ADVISORY_CALCULATION_ENABLED = False


def parse_enum(enum_cls, value, field: str):
    try:
        return enum_cls(value)
    except ValueError as e:
        raise ManifestInvalid(f"{field}: {value!r} is not a valid {enum_cls.__name__}",
                              field=field, value=value) from e


def check_admitted(family_id: str, mode: ConsumptionMode, trust: TrustState, reasons: tuple[str, ...],
                   coverage: CoverageState, relationships: RelationshipState) -> None:
    """Raise unless ``family_id`` may be consumed in ``mode``."""
    if trust not in ADMITTED[mode]:
        raise UntrustedFamily(f"family {family_id!r} is {trust.value}; {mode.value} admits "
                              f"{sorted(s.value for s in ADMITTED[mode])}",
                              family=family_id, trust=trust.value, mode=mode.value, reasons=list(reasons))
    if mode is ConsumptionMode.TRUSTED_CALCULATION:
        if coverage is not CoverageState.FIELDS_CLASSIFIED:
            raise CoverageInsufficient(f"family {family_id!r} field coverage is {coverage.value}",
                                       family=family_id, coverage=coverage.value)
        if relationships is RelationshipState.DANGLING:
            raise RelationshipIntegrityFailure(f"family {family_id!r} has dangling relationships",
                                               family=family_id)
