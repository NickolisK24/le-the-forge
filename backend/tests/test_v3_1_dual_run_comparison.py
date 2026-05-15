import json

from app.planner_adapters.v3_1.dual_run_comparison import (
    V31DualRunComparison,
)
from app.planner_adapters.v3_1.trusted_shadow_consumption import (
    TrustedRepositoryProbe,
    V31TrustedProductionShadowConsumption,
)
from scripts.report_v3_1_dual_run_comparison import (
    build_v3_1_dual_run_comparison_report,
    write_report,
)


def test_comparison_output_is_deterministic():
    legacy = [_legacy("affix", "available", 3)]
    trusted = _shadow([_probe("affix", "affixes", 3)])

    first = V31DualRunComparison().compare(legacy_summaries=legacy, trusted_shadow_metadata=trusted)
    second = V31DualRunComparison().compare(legacy_summaries=legacy, trusted_shadow_metadata=trusted)

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["summary"]["deterministic"] is True


def test_equivalent_cases_classify_correctly():
    result = _compare([_legacy("affix", "available", 3)], [_probe("affix", "affixes", 3)])

    assert result["comparison_results"][0]["drift_classification"] == "equivalent"
    assert result["summary"]["equivalent_count"] == 1
    assert result["summary"]["production_affected_count"] == 0


def test_divergent_cases_classify_correctly():
    result = _compare([_legacy("affix", "available", 3)], [_probe("affix", "affixes", 4)])

    row = result["comparison_results"][0]
    assert row["drift_classification"] == "divergent"
    assert row["reason_codes"] == ["comparable_value_hash_mismatch"]
    assert result["summary"]["divergent_count"] == 1


def test_missing_legacy_data_is_not_silently_accepted():
    result = _compare([], [_probe("affix", "affixes", 3)])

    row = result["comparison_results"][0]
    assert row["drift_classification"] == "trusted_only"
    assert row["unsupported_or_blocked_reason"] == "legacy_summary_missing"
    assert result["summary"]["trusted_only_count"] == 1


def test_missing_trusted_data_is_not_silently_accepted():
    result = _compare([_legacy("affix", "available", 3)], [])

    row = result["comparison_results"][0]
    assert row["drift_classification"] == "legacy_only"
    assert row["unsupported_or_blocked_reason"] == "trusted_shadow_summary_missing"
    assert result["summary"]["legacy_only_count"] == 1


def test_unavailable_trusted_data_remains_visible():
    result = _compare([_legacy("affix", "available", 3)], [_unavailable_probe("affix", "missing_affixes")])

    row = result["comparison_results"][0]
    assert row["drift_classification"] == "unavailable"
    assert row["trusted_shadow_status"] == "unavailable"
    assert row["unsupported_or_blocked_reason"] == "trusted_repository_unavailable"
    assert result["summary"]["unavailable_count"] == 1


def test_unsupported_cases_remain_visible():
    result = _compare([_legacy("affix", "unsupported", None)], [_probe("affix", "affixes", 3)])

    row = result["comparison_results"][0]
    assert row["drift_classification"] == "unsupported"
    assert row["reason_codes"] == ["unsupported_state_visible"]
    assert result["summary"]["unsupported_count"] == 1


def test_blocked_cases_remain_visible():
    trusted = _shadow([_probe("affix", "affixes", 3)], allowed_domains=[])
    result = V31DualRunComparison().compare(
        legacy_summaries=[_legacy("affix", "available", 3)],
        trusted_shadow_metadata=trusted,
    )

    row = result["comparison_results"][0]
    assert row["drift_classification"] == "blocked"
    assert row["trusted_shadow_status"] == "blocked"
    assert row["unsupported_or_blocked_reason"] == "domain_not_allowed_for_v3_1_shadow_consumption"
    assert result["summary"]["blocked_count"] == 1


def test_shadow_gate_disabled_marks_not_evaluated():
    trusted = V31TrustedProductionShadowConsumption().inspect(
        enabled=False,
        trusted_repository_probes=[_probe("affix", "affixes", 3)],
    )
    result = V31DualRunComparison().compare(
        legacy_summaries=[_legacy("affix", "available", 3)],
        trusted_shadow_metadata=trusted,
    )

    assert result["comparison_results"][0]["drift_classification"] == "not_evaluated"
    assert result["summary"]["not_evaluated_count"] == 1


def test_production_output_affected_is_always_false():
    result = _compare(
        [_legacy("affix", "available", 3), _legacy("item_base", "available", 2)],
        [_probe("affix", "affixes", 4), _probe("item_base", "items", 2)],
    )

    assert result["summary"]["production_output_affected"] is False
    assert result["summary"]["production_affected_count"] == 0
    assert all(row["production_output_affected"] is False for row in result["comparison_results"])
    assert result["safety_confirmations"]["runtime_state_mutated"] is False


def test_aggregate_counts_are_correct():
    trusted = _trusted_metadata(
        [
            _trusted_row("equivalent", "trusted_repository_shadowed", 1),
            _trusted_row("divergent", "trusted_repository_shadowed", 2),
            _trusted_row("trusted_only", "trusted_repository_shadowed", 3),
            _trusted_row("unavailable", "trusted_repository_unavailable", 0, ["trusted_repository_unavailable"]),
            _trusted_row("unsupported_trusted", "blocked_unsupported_domain", 0, ["unsupported_trusted_shadow_domain"]),
            _trusted_row("blocked", "blocked_domain_not_allowed", 0, ["blocked_for_test"]),
        ]
    )
    legacy = [
        _legacy("equivalent", "available", 1),
        _legacy("divergent", "available", 99),
        _legacy("legacy_only", "available", 1),
        _legacy("unavailable", "available", 1),
        _legacy("blocked", "available", 1),
    ]
    result = V31DualRunComparison().compare(legacy_summaries=legacy, trusted_shadow_metadata=trusted)

    assert result["summary"]["total_comparisons"] == 7
    assert result["summary"]["equivalent_count"] == 1
    assert result["summary"]["divergent_count"] == 1
    assert result["summary"]["unsupported_count"] == 1
    assert result["summary"]["blocked_count"] == 1
    assert result["summary"]["legacy_only_count"] == 1
    assert result["summary"]["trusted_only_count"] == 1
    assert result["summary"]["unavailable_count"] == 1
    assert result["summary"]["not_evaluated_count"] == 0


def test_report_generation_is_deterministic(tmp_path):
    first = build_v3_1_dual_run_comparison_report()
    second = build_v3_1_dual_run_comparison_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["comparison"]["deterministic_hash"] == second["comparison"]["deterministic_hash"]
    assert first["summary"] == second["summary"]

    output = tmp_path / "dual_run.json"
    write_report(first, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v3_1.dual_run_comparison_report.1"
    assert loaded["production_default_routing_authorized"] is False
    assert loaded["metadata"]["observational_only"] is True


def _compare(legacy_rows, probes):
    return V31DualRunComparison().compare(
        legacy_summaries=legacy_rows,
        trusted_shadow_metadata=_shadow(probes),
    )


def _shadow(probes, allowed_domains=None):
    if allowed_domains is None:
        allowed_domains = {probe.domain for probe in probes}
    return V31TrustedProductionShadowConsumption().inspect(
        enabled=True,
        trusted_repository_probes=probes,
        allowed_domains=allowed_domains,
    )


def _legacy(comparison_id, status, value):
    return {
        "comparison_id": comparison_id,
        "legacy_status": status,
        "comparable_value": value,
        "production_output": True,
    }


def _probe(domain, name, count):
    return TrustedRepositoryProbe(
        domain=domain,
        repository_name=name,
        count_loader=lambda: count,
        metadata_loader=lambda: {"entity_count": count, "source_path": f"fixture:{name}"},
    )


def _unavailable_probe(domain, name):
    def _raise():
        raise FileNotFoundError(f"{name} unavailable")

    return TrustedRepositoryProbe(
        domain=domain,
        repository_name=name,
        count_loader=_raise,
        metadata_loader=_raise,
    )


def _trusted_metadata(rows):
    return {
        "gate": {
            "enabled": True,
            "mode": "shadow",
            "shadow_only": True,
            "production_truth_source": "legacy",
            "production_output_affected": False,
        },
        "trusted_repository_rows": rows,
    }


def _trusted_row(domain, routing_status, count, blocked_reasons=None):
    return {
        "domain": domain,
        "repository_name": f"{domain}_repo",
        "routing_status": routing_status,
        "trusted_repository_available": routing_status == "trusted_repository_shadowed",
        "trusted_entity_count": count,
        "blocked_reasons": blocked_reasons or [],
        "production_output_affected": False,
    }
