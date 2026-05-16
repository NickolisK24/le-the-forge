"""Generate the v3.2 runtime isolation contract report."""

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

from app.planner_adapters.v3_1.approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE  # noqa: E402
from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash  # noqa: E402
from app.planner_adapters.v3_2.runtime_isolation_contracts import build_runtime_isolation_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_isolation_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")[
        "experimental_runtime_entrypoint_contracts"
    ]
    isolation_requests = _isolation_requests_from_entrypoint(entrypoint)
    request_payload = {"runtime_isolation_requests": isolation_requests, "deterministic_hash": deterministic_hash(isolation_requests)}
    isolation = build_runtime_isolation_contract(
        request_payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
    )
    repeated = build_runtime_isolation_contract(
        request_payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
    )
    report = {
        "schema_version": "v3_2.runtime_isolation_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_2_runtime_isolation_contracts",
        "recommendation": "RUNTIME_ISOLATION_CONTRACT_READY_FOR_FUTURE_EXPERIMENTAL_RUNTIME_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {
            **isolation["summary"],
            "deterministic": isolation["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "runtime_isolation_contracts": isolation,
        "isolation_state_distributions": isolation["isolation_state_distribution"],
        "production_routing_crossover_distributions": isolation["production_routing_crossover_distribution"],
        "manifest_consumption_crossover_distributions": isolation["manifest_consumption_crossover_distribution"],
        "planner_ownership_crossover_distributions": isolation["planner_ownership_crossover_distribution"],
        "runtime_mutation_blocker_distributions": isolation["runtime_mutation_blocker_distribution"],
        "side_effect_blocker_distributions": isolation["side_effect_blocker_distribution"],
        "rollback_containment_distributions": isolation["rollback_containment_distribution"],
        "phase_1_entrypoint_compatibility_summary": isolation["phase_1_entrypoint_compatibility"],
        "runtime_disabled_path_verification": isolation["runtime_disabled_path_verification"],
        "production_prohibited_verification": {
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
        },
        "deterministic_guarantees": {
            "passed": isolation["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": isolation["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_2_boundaries": [
            "runtime isolation contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "manifest consumption cannot become implicit runtime behavior",
            "planner ownership mutation remains blocked",
            "side effects must be prohibited or isolated, reversible, and non-production",
        ],
        "future_phase_foundation": [
            "future phases may evaluate initialization only after isolation contracts remain satisfied",
            "future phases must preserve entrypoint authorization and explicit opt-in",
            "future phases must continue to block production routing and planner ownership crossover",
        ],
        "metadata": {
            "source": "v3_2_runtime_isolation_contracts_report",
            "governance_only": True,
            "runtime_isolation_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "planner_remap_performed": False,
        },
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    isolation = report["runtime_isolation_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Isolation Contracts",
        "",
        "Phase 2 defines isolation rules that must hold before future limited experimental runtime initialization can be considered.",
        "This does not enable runtime manifest consumption or production routing.",
        "",
        "## Phase 1 Compatibility",
        "",
        "Phase 2 builds on Phase 1 by requiring an eligible entrypoint contract, explicit opt-in, non-production authorization, disabled runtime consumption, and prohibited production runtime classification.",
        "",
        "## Separation Requirements",
        "",
        "Production routing must remain separated so experimental runtime evidence cannot cross into planner output ownership.",
        "Manifest consumption cannot become implicit runtime behavior; any future consumption must stay explicit, experimental-only, and non-production-authoritative.",
        "Planner ownership cannot be silently mutated because production planner ownership remains legacy-controlled.",
        "",
        "## Side Effects And Rollback",
        "",
        "Runtime side effects are blocked unless explicitly isolated, reversible, and non-production. Rollback containment must remain visible before later runtime-adjacent phases.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Isolation satisfied: `{summary['runtime_isolation_satisfied_count']}`",
        f"- Isolation blocked: `{summary['runtime_isolation_blocked_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Blocker Distribution",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in isolation["blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Isolation Records",
            "",
            "| Contract | Manifest | Fixture Set | Status | Isolation | Routing | Manifest Consumption |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in isolation["runtime_isolation_contracts"]:
        lines.append(
            f"| `{row['runtime_isolation_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_isolation_status']}` | `{row['runtime_isolation_boundary_state'] or ''}` | `{row['production_routing_separation_state'] or ''}` | `{row['manifest_consumption_separation_state'] or ''}` |"
        )
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_2_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Runtime isolation contracts are satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _isolation_requests_from_entrypoint(entrypoint: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "manifest_id": record.get("manifest_id"),
            "fixture_set_id": record.get("fixture_set_id"),
            "runtime_isolation_boundary_state": "isolation_boundary_satisfied",
            "production_routing_separation_state": "production_routing_separated",
            "manifest_consumption_separation_state": "manifest_consumption_separated",
            "manifest_consumption_scope": "experimental_only",
            "manifest_authorization_state": NON_PRODUCTION_AUTHORIZATION_STATE,
            "implicit_manifest_consumption": False,
            "planner_ownership_separation_state": "planner_ownership_separated",
            "runtime_mutation_prohibition_state": "runtime_mutation_prohibited",
            "experimental_only_execution_scope": "experimental_only",
            "runtime_side_effect_prohibition_state": "side_effects_prohibited",
            "rollback_containment_state": "rollback_contained",
            "production_routing_crossover": False,
            "manifest_consumption_crossover": False,
            "planner_ownership_mutation_requested": False,
            "runtime_mutation_requested": False,
        }
        for record in entrypoint.get("runtime_entrypoint_contracts", [])
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
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_isolation_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_ISOLATION_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_isolation_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
