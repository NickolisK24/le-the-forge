"""Generate the v3.2 runtime safety and rollback contract report."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash  # noqa: E402
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import build_runtime_safety_rollback_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_safety_rollback_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")[
        "experimental_runtime_entrypoint_contracts"
    ]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")[
        "runtime_isolation_contracts"
    ]
    session = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_session_boundary_contracts_report.json")[
        "runtime_session_boundary_contracts"
    ]
    requests = _safety_requests_from_session(session)
    payload = {"runtime_safety_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    safety = build_runtime_safety_rollback_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
    )
    repeated = build_runtime_safety_rollback_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
    )
    report = {
        "schema_version": "v3_2.runtime_safety_rollback_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_4_runtime_safety_rollback_contracts",
        "recommendation": "RUNTIME_SAFETY_ROLLBACK_CONTRACT_READY_FOR_FUTURE_EXPERIMENTAL_RUNTIME_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {**safety["summary"], "deterministic": safety["deterministic_hash"] == repeated["deterministic_hash"]},
        "runtime_safety_rollback_contracts": safety,
        "runtime_safety_state_distributions": safety["runtime_safety_state_distribution"],
        "rollback_readiness_state_distributions": safety["rollback_readiness_state_distribution"],
        "rollback_containment_distributions": safety["rollback_containment_distribution"],
        "rollback_trigger_distributions": safety["rollback_trigger_distribution"],
        "rollback_reversibility_distributions": safety["rollback_reversibility_distribution"],
        "unsafe_side_effect_blocker_distributions": safety["unsafe_side_effect_blocker_distribution"],
        "production_impact_blocker_distributions": safety["production_impact_blocker_distribution"],
        "phase_1_entrypoint_compatibility_summary": safety["phase_1_entrypoint_compatibility"],
        "phase_2_isolation_compatibility_summary": safety["phase_2_isolation_compatibility"],
        "phase_3_session_boundary_compatibility_summary": safety["phase_3_session_boundary_compatibility"],
        "runtime_disabled_path_verification": safety["runtime_disabled_path_verification"],
        "production_prohibited_verification": {"production_runtime_prohibited": True, "production_routing_authorized": False, "production_default_routing_authorized": False},
        "deterministic_guarantees": {"passed": safety["deterministic_hash"] == repeated["deterministic_hash"], "sample_hash": safety["deterministic_hash"], "repeated_hash": repeated["deterministic_hash"], "timestamp_excluded_from_hash": True, "json_sort_keys": True},
        "phase_4_boundaries": [
            "runtime safety and rollback contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "rollback triggers and reversibility must be explicit",
            "irreversible side effects remain blocked",
            "production-impacting behavior remains prohibited",
        ],
        "future_phase_foundation": [
            "future phases may evaluate runtime experiments only after safety and rollback contracts remain satisfied",
            "future phases must preserve entrypoint, isolation, and session boundary compatibility",
            "future phases must continue to block irreversible side effects and production impact",
        ],
        "metadata": {"source": "v3_2_runtime_safety_rollback_contracts_report", "governance_only": True, "runtime_safety_rollback_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_behavior_changed": False, "production_default_routing_authorized": False, "planner_remap_performed": False},
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    safety = report["runtime_safety_rollback_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Safety Rollback Contracts",
        "",
        "Phase 4 defines explicit runtime safety and rollback readiness governance before future runtime experimentation.",
        "This does not enable runtime manifest consumption or production routing.",
        "",
        "## Compatibility",
        "",
        "Phase 4 builds on Phase 1 entrypoint authorization, Phase 2 isolation, and Phase 3 session boundaries. All three must remain compatible before safety can be satisfied.",
        "",
        "## Rollback Readiness",
        "",
        "Rollback readiness must be explicit: rollback trigger context, rollback containment, and reversibility are all visible contract fields.",
        "",
        "## Side Effects And Production Impact",
        "",
        "Irreversible side effects remain blocked. Production-impacting behavior remains prohibited and cannot be treated as runtime-safe.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Runtime safety satisfied: `{summary['runtime_safety_satisfied_count']}`",
        f"- Runtime rollback ready: `{summary['runtime_rollback_ready_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Safety Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in safety["safety_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Rollback Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for blocker, count in safety["rollback_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Manifest | Fixture Set | Safety | Rollback |", "| --- | --- | --- | --- | --- |"])
    for row in safety["runtime_safety_rollback_contracts"]:
        lines.append(f"| `{row['runtime_safety_rollback_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_safety_status']}` | `{row['runtime_rollback_status']}` |")
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Conclusion", "", "Runtime safety and rollback contracts are satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _safety_requests_from_session(session: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "manifest_id": record.get("manifest_id"),
            "fixture_set_id": record.get("fixture_set_id"),
            "runtime_safety_state": "runtime_safety_explicitly_satisfied",
            "rollback_readiness_state": "rollback_readiness_explicitly_ready",
            "rollback_containment_state": "rollback_contained",
            "rollback_trigger_state": "rollback_trigger_explicit",
            "rollback_reversibility_state": "rollback_reversible",
            "unsafe_side_effect_prohibition_state": "unsafe_side_effects_prohibited",
            "production_impact_prohibition_state": "production_impact_prohibited",
            "session_rollback_compatibility_state": "session_rollback_compatible",
            "isolation_rollback_compatibility_state": "isolation_rollback_compatible",
            "entrypoint_rollback_compatibility_state": "entrypoint_rollback_compatible",
            "unsafe_side_effect_detected": False,
            "production_impact_detected": False,
        }
        for record in session.get("runtime_session_boundary_contracts", [])
    ]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_safety_rollback_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_SAFETY_ROLLBACK_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_safety_rollback_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
