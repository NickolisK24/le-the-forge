"""Generate the v3.2 experimental runtime entrypoint contract report."""

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
from app.planner_adapters.v3_2.experimental_runtime_entrypoint_contracts import build_runtime_entrypoint_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_experimental_runtime_entrypoint_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    closeout = _read_json(repo_root / "docs" / "generated" / "v3_1_experimental_runtime_readiness_closeout_report.json")[
        "experimental_runtime_readiness_closeout"
    ]
    runtime_entry_requests = _entry_requests_from_closeout(closeout)
    contracts = build_runtime_entrypoint_contract(
        {"runtime_entry_requests": runtime_entry_requests, "deterministic_hash": _requests_hash(runtime_entry_requests)},
        experimental_runtime_readiness_closeout=closeout,
    )
    repeated = build_runtime_entrypoint_contract(
        {"runtime_entry_requests": runtime_entry_requests, "deterministic_hash": _requests_hash(runtime_entry_requests)},
        experimental_runtime_readiness_closeout=closeout,
    )
    report = {
        "schema_version": "v3_2.experimental_runtime_entrypoint_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_1_experimental_runtime_entrypoint_contracts",
        "recommendation": "ENTRYPOINT_CONTRACT_READY_FOR_FUTURE_EXPERIMENTAL_RUNTIME_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {
            **contracts["summary"],
            "deterministic": contracts["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "experimental_runtime_entrypoint_contracts": contracts,
        "authorization_state_distributions": contracts["authorization_state_distribution"],
        "isolation_state_distributions": contracts["isolation_state_distribution"],
        "blocker_distributions": contracts["blocker_distribution"],
        "prohibited_runtime_classifications": {
            "production_runtime_prohibited": contracts["summary"]["production_runtime_prohibited_count"],
            "production_runtime_always_prohibited": True,
        },
        "rollback_required_classifications": {
            "runtime_rollback_required": contracts["summary"]["runtime_rollback_required_count"],
            "rollback_safe_gating_required": True,
        },
        "runtime_disabled_path_verification": contracts["runtime_disabled_path_verification"],
        "deterministic_guarantees": {
            "passed": contracts["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": contracts["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_1_boundaries": [
            "entrypoint contracts are governance and authorization only",
            "runtime manifest consumption remains disabled",
            "production runtime remains prohibited",
            "production planner routing remains unchanged",
            "explicit authorization and isolation states are required",
            "rollback-safe gating is mandatory before future runtime work",
        ],
        "future_phase_foundation": [
            "future phases may evaluate limited experimental runtime initialization against this contract",
            "future phases must preserve non-production authorization and isolation checks",
            "future phases must continue to report blockers before any runtime-adjacent behavior is considered",
        ],
        "metadata": {
            "source": "v3_2_experimental_runtime_entrypoint_contracts_report",
            "governance_only": True,
            "runtime_adjacent_boundary": True,
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
    contracts = report["experimental_runtime_entrypoint_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Experimental Runtime Entrypoint Contracts",
        "",
        "Phase 1 establishes an explicit runtime-adjacent entrypoint contract for future limited experimental runtime work.",
        "It does not enable runtime manifest consumption and does not authorize production routing.",
        "",
        "## Runtime Isolation",
        "",
        "Runtime remains isolated because every contract requires explicit non-production authorization, explicit isolation state, explicit opt-in, and rollback eligibility before an experimental entrypoint can be considered.",
        "",
        "## Production Runtime Prohibition",
        "",
        "Production runtime remains prohibited by contract. A production runtime request is classified separately as `production_runtime_prohibited` and cannot become an experimental eligibility state.",
        "",
        "## Explicit Authorization",
        "",
        "Explicit authorization matters because missing or invalid authorization is classified as `runtime_disabled_by_authorization`, not silently converted into a default-safe state.",
        "",
        "## Rollback-Safe Gating",
        "",
        "Rollback-safe gating exists so future runtime-adjacent phases cannot initialize unless rollback eligibility is visible and deterministic.",
        "",
        "## Deterministic Governance",
        "",
        "Deterministic runtime governance keeps contract records, blockers, and distributions stable across repeated evaluations.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Experimental runtime eligible: `{summary['experimental_runtime_eligible_count']}`",
        f"- Experimental runtime blocked: `{summary['experimental_runtime_blocked_count']}`",
        f"- Production runtime prohibited: `{summary['production_runtime_prohibited_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Blocker Distribution",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in contracts["blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Contract Records",
            "",
            "| Contract | Manifest | Fixture Set | Status | Authorization | Isolation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in contracts["runtime_entrypoint_contracts"]:
        lines.append(
            f"| `{row['runtime_entrypoint_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_entrypoint_status']}` | `{row['runtime_authorization_state'] or ''}` | `{row['runtime_isolation_state'] or ''}` |"
        )
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_1_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The entrypoint contract is ready for governance review only. Production runtime routing remains prohibited and runtime manifest consumption remains disabled.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _entry_requests_from_closeout(closeout: dict[str, Any]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    for record in closeout.get("closeout_records", []):
        requests.append(
            {
                "manifest_id": record.get("manifest_id"),
                "fixture_set_id": record.get("fixture_set_id"),
                "runtime_mode": "limited_experimental_runtime",
                "runtime_authorization_state": NON_PRODUCTION_AUTHORIZATION_STATE,
                "runtime_isolation_state": "runtime_isolated",
                "runtime_policy_allows_entrypoint": True,
                "explicit_experimental_runtime_opt_in": True,
                "runtime_rollback_eligibility": True,
                "runtime_rollback_required": False,
                "runtime_activation_intent": "contract_evaluation_only",
                "runtime_manifest_consumption_enabled": False,
                "runtime_production_consumption_enabled": False,
            }
        )
    return requests


def _requests_hash(requests: list[dict[str, Any]]) -> str:
    return build_runtime_entrypoint_contract(
        requests,
        experimental_runtime_readiness_closeout=[],
        run_id="v3_2_phase_1_request_hash_probe",
    )["deterministic_hash"]


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
    parser.add_argument("--output", default="docs/generated/v3_2_experimental_runtime_entrypoint_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_EXPERIMENTAL_RUNTIME_ENTRYPOINT_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_experimental_runtime_entrypoint_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
