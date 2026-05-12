from pathlib import Path

import pytest

from app.data_contracts import (
    CanonicalAffix,
    SourceProvenance,
    SupportStatus,
    TrustLevel,
    assert_stable_planner_eligible,
    is_stable_calculable,
    validate_canonical_id,
)
from app.data_contracts.trust_level import coerce_trust_level
from app.data_contracts.trust_status import coerce_support_status


ROOT = Path(__file__).resolve().parents[2]


def test_support_status_enum_validation():
    assert coerce_support_status("trusted") == SupportStatus.TRUSTED
    assert {status.value for status in SupportStatus} == {
        "trusted",
        "partial",
        "text_only",
        "unsupported",
        "experimental",
        "unknown",
    }
    with pytest.raises(ValueError):
        coerce_support_status("calculated")


def test_trust_level_enum_validation():
    assert coerce_trust_level("game_extracted") == TrustLevel.GAME_EXTRACTED
    assert {level.value for level in TrustLevel} == {
        "game_extracted",
        "generated_from_game_data",
        "manual_bridge",
        "inferred",
        "placeholder",
        "deprecated",
    }
    with pytest.raises(ValueError):
        coerce_trust_level("trusted_by_name")


def test_generated_record_requires_provenance():
    with pytest.raises(ValueError, match="provenance is required"):
        CanonicalAffix(
            canonical_id="affix:test",
            display_name="Test Affix",
            support_status=SupportStatus.TRUSTED,
            trust_level=TrustLevel.GENERATED_FROM_GAME_DATA,
            provenance=None,  # type: ignore[arg-type]
        )


def test_unknown_unsupported_and_text_only_are_not_stable_calculable():
    for status in [
        SupportStatus.UNKNOWN,
        SupportStatus.UNSUPPORTED,
        SupportStatus.TEXT_ONLY,
        SupportStatus.EXPERIMENTAL,
    ]:
        assert is_stable_calculable(status, TrustLevel.GAME_EXTRACTED) is False


def test_placeholder_record_is_blocked_from_stable_planner_eligibility():
    record = _record(
        support_status=SupportStatus.TRUSTED,
        trust_level=TrustLevel.PLACEHOLDER,
    )

    with pytest.raises(ValueError, match="placeholder"):
        assert_stable_planner_eligible(record)


def test_canonical_id_validation():
    assert validate_canonical_id("affix:health_pct") == "affix:health_pct"
    with pytest.raises(ValueError):
        validate_canonical_id("Health Percent")
    with pytest.raises(ValueError):
        validate_canonical_id("")


def test_frontend_backend_status_values_are_aligned():
    trust_status_text = (ROOT / "frontend" / "src" / "types" / "trustStatus.ts").read_text(
        encoding="utf-8"
    )
    for status in SupportStatus:
        assert f'"{status.value}"' in trust_status_text
    for level in TrustLevel:
        assert f'"{level.value}"' in trust_status_text


def test_trusted_extracted_record_is_stable_eligible():
    record = _record(
        support_status=SupportStatus.TRUSTED,
        trust_level=TrustLevel.GAME_EXTRACTED,
    )

    assert_stable_planner_eligible(record)


def _record(*, support_status: SupportStatus, trust_level: TrustLevel) -> CanonicalAffix:
    return CanonicalAffix(
        canonical_id="affix:test",
        display_name="Test Affix",
        support_status=support_status,
        trust_level=trust_level,
        provenance=SourceProvenance(
            source_path="data/items/affixes.json",
            source_type="json",
            extraction_method="test_fixture",
            patch_version="1.4.3",
            source_id="1",
        ),
    )
