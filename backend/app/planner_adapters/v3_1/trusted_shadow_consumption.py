"""V3.1 trusted repository shadow-consumption gate.

This module inspects trusted repository availability beside legacy production
paths. It is intentionally read-only and never selects trusted data as the
production truth source.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


SUPPORTED_TRUSTED_SHADOW_DOMAINS = frozenset({"affix", "item_base", "passive_skill"})
DEFAULT_ALLOWED_DOMAINS = SUPPORTED_TRUSTED_SHADOW_DOMAINS
GATE_NAME = "V3_1_TRUSTED_PRODUCTION_SHADOW_CONSUMPTION_ENABLED"


@dataclass(frozen=True)
class TrustedRepositoryProbe:
    domain: str
    repository_name: str
    count_loader: Callable[[], int]
    metadata_loader: Callable[[], dict[str, Any]] | None = None


class V31TrustedProductionShadowConsumption:
    """Build routing/debug metadata for observational trusted consumption."""

    def inspect(
        self,
        *,
        enabled: bool = False,
        trusted_repository_probes: list[TrustedRepositoryProbe] | None = None,
        allowed_domains: set[str] | frozenset[str] | tuple[str, ...] | list[str] | None = None,
        legacy_path_name: str = "legacy_production_runtime",
        legacy_output: Any | None = None,
        run_id: str = "v3_1_phase_1_trusted_shadow_consumption",
    ) -> dict[str, Any]:
        normalized_domains = _normalize_allowed_domains(allowed_domains)
        if allowed_domains is None:
            normalized_domains = DEFAULT_ALLOWED_DOMAINS
        probes = list(trusted_repository_probes or [])

        if not enabled:
            envelope = _disabled_envelope(
                run_id=run_id,
                allowed_domains=normalized_domains,
                legacy_path_name=legacy_path_name,
                legacy_output=legacy_output,
            )
            envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
            return envelope

        probe_rows = [
            _inspect_probe(probe=probe, allowed_domains=normalized_domains)
            for probe in sorted(probes, key=lambda item: (item.domain, item.repository_name))
        ]
        unsupported_domains = sorted({row["domain"] for row in probe_rows if row["routing_status"] == "blocked_unsupported_domain"})
        unavailable = [row for row in probe_rows if row["routing_status"] == "trusted_repository_unavailable"]
        available = [row for row in probe_rows if row["trusted_repository_available"]]
        category_counts: dict[str, int] = {}
        for row in probe_rows:
            category_counts[row["routing_status"]] = category_counts.get(row["routing_status"], 0) + 1

        fallback_behavior = _fallback_behavior(enabled=True, unavailable=unavailable, unsupported_domains=unsupported_domains)
        envelope = {
            "schema_version": "v3_1.trusted_shadow_consumption.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "run": {
                "run_id": run_id,
                "probe_count": len(probe_rows),
                "allowed_domains": sorted(normalized_domains),
            },
            "gate": {
                "name": GATE_NAME,
                "enabled": True,
                "default_enabled": False,
                "mode": "shadow",
                "shadow_only": True,
                "production_truth_source": "legacy",
                "trusted_path_shadowed_only": True,
                "legacy_path_still_active": True,
                "production_output_affected": False,
            },
            "summary": {
                "trusted_repository_available": bool(available),
                "trusted_repository_available_count": len(available),
                "trusted_repository_unavailable_count": len(unavailable),
                "trusted_entity_count": sum(row["trusted_entity_count"] for row in available),
                "unsupported_domain_count": len(unsupported_domains),
                "legacy_path_still_active": True,
                "trusted_path_shadowed_only": True,
                "production_output_affected": False,
                "production_behavior_changed": False,
                "production_default_routing_authorized": False,
                "deterministic": True,
            },
            "routing_category_counts": dict(sorted(category_counts.items())),
            "trusted_repository_rows": probe_rows,
            "unsupported_or_blocked_domains": unsupported_domains,
            "fallback_behavior": fallback_behavior,
            "legacy_routing": _legacy_routing_metadata(
                legacy_path_name=legacy_path_name,
                legacy_output=legacy_output,
            ),
            "safety_confirmations": _safety_confirmations(),
            "metadata": {
                "source": "v3_1_trusted_shadow_consumption",
                "observational_only": True,
                "production_consumer": False,
                "production_behavior_changed": False,
                "planner_remap_performed": False,
                "production_default_routing_authorized": False,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
        return envelope


def build_default_trusted_repository_probes(repo_root: Path | None = None) -> list[TrustedRepositoryProbe]:
    root = repo_root or Path(__file__).resolve().parents[4]
    generated = root / "docs" / "generated"
    return [
        _json_record_probe(
            domain="affix",
            repository_name="v2_affix_bundle",
            path=generated / "v2_affix_bundle.json",
            records_key="affixes",
        ),
        _json_record_probe(
            domain="item_base",
            repository_name="v2_item_base_bundle",
            path=generated / "v2_item_base_bundle.json",
            records_key="item_bases",
        ),
        _json_record_probe(
            domain="passive_skill",
            repository_name="v2_passive_tree_bundle",
            path=generated / "v2_passive_tree_bundle.json",
            records_key="passive_trees",
        ),
    ]


def deterministic_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _json_record_probe(*, domain: str, repository_name: str, path: Path, records_key: str) -> TrustedRepositoryProbe:
    def _payload() -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"trusted repository not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{repository_name} payload must be a JSON object")
        records = data.get("records")
        if not isinstance(records, dict):
            raise ValueError(f"{repository_name} records must be an object")
        values = records.get(records_key)
        if not isinstance(values, list):
            raise ValueError(f"{repository_name} records.{records_key} must be a list")
        return {
            "entity_count": len(values),
            "schema_version": data.get("schema_version"),
            "source_path": str(path),
        }

    def _count_loader() -> int:
        return int(_payload()["entity_count"])

    return TrustedRepositoryProbe(
        domain=domain,
        repository_name=repository_name,
        count_loader=_count_loader,
        metadata_loader=_payload,
    )


def _inspect_probe(*, probe: TrustedRepositoryProbe, allowed_domains: frozenset[str]) -> dict[str, Any]:
    if probe.domain not in SUPPORTED_TRUSTED_SHADOW_DOMAINS:
        return {
            "domain": probe.domain,
            "repository_name": probe.repository_name,
            "routing_status": "blocked_unsupported_domain",
            "trusted_repository_available": False,
            "trusted_entity_count": 0,
            "legacy_path_still_active": True,
            "trusted_path_shadowed_only": True,
            "production_output_affected": False,
            "blocked_reasons": ["unsupported_trusted_shadow_domain"],
            "fallback_behavior": "legacy_remains_active_reported",
            "metadata": {},
        }
    if probe.domain not in allowed_domains:
        return {
            "domain": probe.domain,
            "repository_name": probe.repository_name,
            "routing_status": "blocked_domain_not_allowed",
            "trusted_repository_available": False,
            "trusted_entity_count": 0,
            "legacy_path_still_active": True,
            "trusted_path_shadowed_only": True,
            "production_output_affected": False,
            "blocked_reasons": ["domain_not_allowed_for_v3_1_shadow_consumption"],
            "fallback_behavior": "legacy_remains_active_reported",
            "metadata": {},
        }
    try:
        metadata = probe.metadata_loader() if probe.metadata_loader is not None else {}
        count = int(metadata.get("entity_count", probe.count_loader()))
    except Exception as exc:  # noqa: BLE001 - report visibility is the point.
        return {
            "domain": probe.domain,
            "repository_name": probe.repository_name,
            "routing_status": "trusted_repository_unavailable",
            "trusted_repository_available": False,
            "trusted_entity_count": 0,
            "legacy_path_still_active": True,
            "trusted_path_shadowed_only": True,
            "production_output_affected": False,
            "blocked_reasons": ["trusted_repository_unavailable"],
            "error": str(exc),
            "fallback_behavior": "legacy_remains_active_reported",
            "metadata": {},
        }
    return {
        "domain": probe.domain,
        "repository_name": probe.repository_name,
        "routing_status": "trusted_repository_shadowed",
        "trusted_repository_available": True,
        "trusted_entity_count": count,
        "legacy_path_still_active": True,
        "trusted_path_shadowed_only": True,
        "production_output_affected": False,
        "blocked_reasons": [],
        "fallback_behavior": "none_required_shadow_only",
        "metadata": _stable_metadata(metadata),
    }


def _normalize_allowed_domains(allowed_domains: set[str] | frozenset[str] | tuple[str, ...] | list[str] | None) -> frozenset[str]:
    if allowed_domains is None:
        return frozenset()
    return frozenset(str(domain) for domain in allowed_domains if str(domain) in SUPPORTED_TRUSTED_SHADOW_DOMAINS)


def _fallback_behavior(*, enabled: bool, unavailable: list[dict[str, Any]], unsupported_domains: list[str]) -> dict[str, Any]:
    return {
        "fallback_possible": True,
        "fallback_silent": False,
        "fallback_occurred": enabled and bool(unavailable or unsupported_domains),
        "fallback_target": "legacy_production_runtime",
        "reported_unavailable_repositories": [row["repository_name"] for row in unavailable],
        "reported_unsupported_domains": unsupported_domains,
    }


def _legacy_routing_metadata(*, legacy_path_name: str, legacy_output: Any | None) -> dict[str, Any]:
    return {
        "path_name": legacy_path_name,
        "active": True,
        "production_truth_source": True,
        "trusted_shadow_can_replace_output": False,
        "output_hash": deterministic_hash({"legacy_output": legacy_output}) if legacy_output is not None else None,
    }


def _safety_confirmations() -> dict[str, bool]:
    return {
        "production_output_affected": False,
        "production_behavior_changed": False,
        "production_default_routing_authorized": False,
        "trusted_repository_used_as_truth_source": False,
        "legacy_path_removed": False,
        "silent_fallback_allowed": False,
        "unsupported_domains_production_safe": False,
        "planner_remap_performed": False,
    }


def _disabled_envelope(
    *,
    run_id: str,
    allowed_domains: frozenset[str],
    legacy_path_name: str,
    legacy_output: Any | None,
) -> dict[str, Any]:
    return {
        "schema_version": "v3_1.trusted_shadow_consumption.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "run": {
            "run_id": run_id,
            "probe_count": 0,
            "allowed_domains": sorted(allowed_domains),
        },
        "gate": {
            "name": GATE_NAME,
            "enabled": False,
            "default_enabled": False,
            "mode": "disabled",
            "shadow_only": True,
            "production_truth_source": "legacy",
            "trusted_path_shadowed_only": False,
            "legacy_path_still_active": True,
            "production_output_affected": False,
        },
        "summary": {
            "trusted_repository_available": False,
            "trusted_repository_available_count": 0,
            "trusted_repository_unavailable_count": 0,
            "trusted_entity_count": 0,
            "unsupported_domain_count": 0,
            "legacy_path_still_active": True,
            "trusted_path_shadowed_only": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "deterministic": True,
        },
        "routing_category_counts": {},
        "trusted_repository_rows": [],
        "unsupported_or_blocked_domains": [],
        "fallback_behavior": _fallback_behavior(enabled=False, unavailable=[], unsupported_domains=[]),
        "legacy_routing": _legacy_routing_metadata(
            legacy_path_name=legacy_path_name,
            legacy_output=legacy_output,
        ),
        "safety_confirmations": _safety_confirmations(),
        "metadata": {
            "source": "v3_1_trusted_shadow_consumption",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }


def _stable_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(metadata)
    if "source_path" in stable:
        stable["source_path"] = str(stable["source_path"])
    return stable


def _stable_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(envelope)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
