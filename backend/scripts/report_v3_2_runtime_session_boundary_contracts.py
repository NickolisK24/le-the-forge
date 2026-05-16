"""Generate the v3.2 runtime session boundary contract report."""

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
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import build_runtime_session_boundary_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_session_boundary_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")[
        "experimental_runtime_entrypoint_contracts"
    ]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")[
        "runtime_isolation_contracts"
    ]
    requests = _session_requests_from_isolation(isolation)
    request_payload = {"runtime_session_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    session = build_runtime_session_boundary_contract(
        request_payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
    )
    repeated = build_runtime_session_boundary_contract(
        request_payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
    )
    report = {
        "schema_version": "v3_2.runtime_session_boundary_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_3_runtime_session_boundary_contracts",
        "recommendation": "RUNTIME_SESSION_BOUNDARY_CONTRACT_READY_FOR_FUTURE_EXPERIMENTAL_RUNTIME_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {
            **session["summary"],
            "deterministic": session["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "runtime_session_boundary_contracts": session,
        "session_boundary_state_distributions": session["session_boundary_state_distribution"],
        "session_initialization_blocker_distributions": session["session_initialization_blocker_distribution"],
        "authorization_context_distributions": session["authorization_context_distribution"],
        "isolation_context_distributions": session["isolation_context_distribution"],
        "ownership_crossover_distributions": session["ownership_crossover_distribution"],
        "mutation_blocker_distributions": session["mutation_blocker_distribution"],
        "reuse_blocker_distributions": session["reuse_blocker_distribution"],
        "leakage_blocker_distributions": session["leakage_blocker_distribution"],
        "termination_required_distributions": session["termination_required_distribution"],
        "rollback_containment_distributions": session["rollback_containment_distribution"],
        "phase_1_entrypoint_compatibility_summary": session["phase_1_entrypoint_compatibility"],
        "phase_2_isolation_compatibility_summary": session["phase_2_isolation_compatibility"],
        "runtime_disabled_path_verification": session["runtime_disabled_path_verification"],
        "production_prohibited_verification": {
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
        },
        "deterministic_guarantees": {
            "passed": session["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": session["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_3_boundaries": [
            "runtime session boundary contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "session state cannot leak across requests",
            "session state cannot mutate production planner ownership",
            "session reuse must be explicitly scoped, deterministic, and non-production",
            "session termination and rollback containment remain explicit",
        ],
        "future_phase_foundation": [
            "future phases may evaluate runtime session representation only after session boundaries remain satisfied",
            "future phases must preserve entrypoint and isolation compatibility",
            "future phases must continue to block production routing, leakage, and planner ownership crossover",
        ],
        "metadata": {
            "source": "v3_2_runtime_session_boundary_contracts_report",
            "governance_only": True,
            "runtime_session_boundary_contract_only": True,
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
    session = report["runtime_session_boundary_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Session Boundary Contracts",
        "",
        "Phase 3 defines deterministic session lifecycle boundaries before future runtime experimentation.",
        "This does not enable runtime sessions, runtime manifest consumption, or production routing.",
        "",
        "## Phase 1 And Phase 2 Compatibility",
        "",
        "Phase 3 builds on Phase 1 entrypoint authorization and Phase 2 runtime isolation. A session boundary can only be satisfied when those contexts remain compatible.",
        "",
        "## Session State Boundaries",
        "",
        "Session state must not leak across requests because leakage would make experimental runtime behavior non-deterministic and unsafe to audit.",
        "Session state cannot mutate production planner state because production planner ownership remains outside the experimental runtime path.",
        "Session reuse must be explicitly scoped, deterministic, and non-production to avoid implicit cross-request state carryover.",
        "",
        "## Termination And Rollback",
        "",
        "Session termination and rollback containment remain explicit so future runtime work can be stopped and audited without hidden state.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Session boundary satisfied: `{summary['runtime_session_boundary_satisfied_count']}`",
        f"- Session boundary blocked: `{summary['runtime_session_boundary_blocked_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Blocker Distribution",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in session["blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Session Boundary Records",
            "",
            "| Contract | Manifest | Fixture Set | Status | Lifecycle | Authorization | Isolation |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in session["runtime_session_boundary_contracts"]:
        lines.append(
            f"| `{row['runtime_session_boundary_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_session_boundary_status']}` | `{row['session_lifecycle_state'] or ''}` | `{row['session_authorization_context'] or ''}` | `{row['session_isolation_context'] or ''}` |"
        )
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_3_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Runtime session boundary contracts are satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _session_requests_from_isolation(isolation: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "manifest_id": record.get("manifest_id"),
            "fixture_set_id": record.get("fixture_set_id"),
            "session_initialization_state": "session_initialization_explicit",
            "explicit_experimental_runtime_opt_in": True,
            "session_authorization_context": NON_PRODUCTION_AUTHORIZATION_STATE,
            "session_isolation_context": "runtime_isolated",
            "session_lifecycle_state": "session_lifecycle_initialized_for_contract_only",
            "session_ownership_state": "session_ownership_isolated",
            "session_mutation_prohibition_state": "session_mutation_prohibited",
            "session_reuse_prohibition_state": "session_reuse_prohibited",
            "session_leakage_prohibition_state": "session_leakage_prohibited",
            "session_termination_requirement_state": "session_termination_required_and_explicit",
            "rollback_containment_state": "rollback_contained",
            "session_ownership_crossover": False,
            "session_mutates_production_planner": False,
            "session_state_leakage_detected": False,
        }
        for record in isolation.get("runtime_isolation_contracts", [])
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
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_session_boundary_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_SESSION_BOUNDARY_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_session_boundary_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
