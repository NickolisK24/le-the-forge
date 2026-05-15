import json
from pathlib import Path

from app.planner_adapters.v3_1.trusted_shadow_consumption import (
    TrustedRepositoryProbe,
    V31TrustedProductionShadowConsumption,
)
from scripts.report_v3_1_trusted_shadow_consumption import (
    build_v3_1_trusted_shadow_consumption_report,
    write_report,
)


def test_shadow_gate_defaults_disabled(app):
    assert app.config["V3_1_TRUSTED_PRODUCTION_SHADOW_CONSUMPTION_ENABLED"] is False

    report = V31TrustedProductionShadowConsumption().inspect(
        trusted_repository_probes=[_probe("affix", "available_affixes", 2)],
        legacy_output={"value": 10},
    )

    assert report["gate"]["enabled"] is False
    assert report["gate"]["default_enabled"] is False
    assert report["trusted_repository_rows"] == []
    assert report["summary"]["production_output_affected"] is False


def test_production_behavior_is_unchanged_when_disabled():
    legacy_output = {"route": "legacy", "score": 42}
    report = V31TrustedProductionShadowConsumption().inspect(
        enabled=False,
        trusted_repository_probes=[_probe("affix", "available_affixes", 99)],
        legacy_output=legacy_output,
    )

    assert report["legacy_routing"]["active"] is True
    assert report["legacy_routing"]["production_truth_source"] is True
    assert report["legacy_routing"]["trusted_shadow_can_replace_output"] is False
    assert report["summary"]["trusted_entity_count"] == 0
    assert report["summary"]["production_behavior_changed"] is False


def test_enabled_shadow_mode_does_not_replace_production_output():
    legacy_output = {"route": "legacy", "score": 42}
    report = V31TrustedProductionShadowConsumption().inspect(
        enabled=True,
        trusted_repository_probes=[_probe("affix", "available_affixes", 3)],
        legacy_output=legacy_output,
    )

    assert report["gate"]["mode"] == "shadow"
    assert report["gate"]["production_truth_source"] == "legacy"
    assert report["summary"]["trusted_entity_count"] == 3
    assert report["summary"]["production_output_affected"] is False
    assert report["safety_confirmations"]["trusted_repository_used_as_truth_source"] is False


def test_routing_debug_metadata_is_produced():
    report = V31TrustedProductionShadowConsumption().inspect(
        enabled=True,
        trusted_repository_probes=[_probe("affix", "available_affixes", 3)],
    )
    row = report["trusted_repository_rows"][0]

    assert row["routing_status"] == "trusted_repository_shadowed"
    assert row["trusted_repository_available"] is True
    assert row["trusted_entity_count"] == 3
    assert row["legacy_path_still_active"] is True
    assert row["trusted_path_shadowed_only"] is True
    assert row["production_output_affected"] is False


def test_unavailable_trusted_data_fails_visibly_in_metadata():
    report = V31TrustedProductionShadowConsumption().inspect(
        enabled=True,
        trusted_repository_probes=[_unavailable_probe("affix", "missing_affixes")],
    )
    row = report["trusted_repository_rows"][0]

    assert row["routing_status"] == "trusted_repository_unavailable"
    assert row["trusted_repository_available"] is False
    assert row["blocked_reasons"] == ["trusted_repository_unavailable"]
    assert "missing_affixes unavailable" in row["error"]
    assert report["fallback_behavior"]["fallback_silent"] is False
    assert report["fallback_behavior"]["fallback_occurred"] is True


def test_unsupported_trusted_domain_is_not_production_safe():
    report = V31TrustedProductionShadowConsumption().inspect(
        enabled=True,
        trusted_repository_probes=[_probe("monolith_echo", "unsupported_repo", 10)],
    )
    row = report["trusted_repository_rows"][0]

    assert row["routing_status"] == "blocked_unsupported_domain"
    assert row["blocked_reasons"] == ["unsupported_trusted_shadow_domain"]
    assert row["production_output_affected"] is False
    assert report["unsupported_or_blocked_domains"] == ["monolith_echo"]
    assert report["safety_confirmations"]["unsupported_domains_production_safe"] is False


def test_report_generation_is_deterministic(tmp_path):
    first = build_v3_1_trusted_shadow_consumption_report()
    second = build_v3_1_trusted_shadow_consumption_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["enabled_shadow_sample"]["deterministic_hash"] == second["enabled_shadow_sample"]["deterministic_hash"]

    output = tmp_path / "report.json"
    write_report(first, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v3_1.trusted_shadow_consumption_report.1"
    assert loaded["production_default_routing_authorized"] is False


def test_report_marks_phase_1_observational_only():
    report = build_v3_1_trusted_shadow_consumption_report()

    assert report["recommendation"] == "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING"
    assert report["metadata"]["observational_only"] is True
    assert report["metadata"]["production_behavior_changed"] is False
    assert report["metadata"]["planner_remap_performed"] is False
    assert "trusted repositories may be inspected only in shadow mode" in report["phase_1_boundaries"]


def _probe(domain: str, name: str, count: int) -> TrustedRepositoryProbe:
    return TrustedRepositoryProbe(
        domain=domain,
        repository_name=name,
        count_loader=lambda: count,
        metadata_loader=lambda: {"entity_count": count, "source_path": Path("fixture.json")},
    )


def _unavailable_probe(domain: str, name: str) -> TrustedRepositoryProbe:
    def _raise():
        raise FileNotFoundError(f"{name} unavailable")

    return TrustedRepositoryProbe(
        domain=domain,
        repository_name=name,
        count_loader=_raise,
        metadata_loader=_raise,
    )
