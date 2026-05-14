"""
Read-only compatibility inspection for last-epoch-data bundle control planes.

Phase 1C deliberately does not load family JSON files or replace existing
Forge production data loaders. It only inspects metadata, manifest, validation
status, and optional reports so developers can see whether a bundle is safe to
consider before future migrations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_BUNDLE_DIR = Path(r"D:\Forge\last-epoch-data\data_bundle")
BUNDLE_DIR_ENV = "FORGE_DATA_BUNDLE_DIR"

SUPPORTED_BUNDLE_SCHEMA_VERSIONS = {"1.0.0"}
SUPPORTED_MANIFEST_SCHEMA_VERSIONS = {"1.0.0"}

STATUS_COMPATIBLE = "compatible"
STATUS_COMPATIBLE_WITH_WARNINGS = "compatible_with_warnings"
STATUS_INCOMPATIBLE = "incompatible"

REQUIRED_NOW = "Required Now"
AUTHORITATIVE_READY_LEVELS = {"Canonical-ready", "Simulation-ready"}
VALID_ACTION_BUCKETS = ("load", "warn", "degrade", "block", "ignore")


@dataclass
class BundleCompatibilityResult:
    status: str
    bundle_id: str | None = None
    game_version: str | None = None
    build_number: str | None = None
    data_patch: str | None = None
    validation_status: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    actions: dict[str, list[str]] = field(
        default_factory=lambda: {bucket: [] for bucket in VALID_ACTION_BUCKETS}
    )
    family_summary: dict[str, Any] = field(default_factory=dict)
    blocked_families: list[str] = field(default_factory=list)
    degraded_families: list[str] = field(default_factory=list)
    warning_families: list[str] = field(default_factory=list)
    ignored_families: list[str] = field(default_factory=list)
    known_gap_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "bundle_id": self.bundle_id,
            "game_version": self.game_version,
            "build_number": self.build_number,
            "data_patch": self.data_patch,
            "validation_status": self.validation_status,
            "errors": self.errors,
            "warnings": self.warnings,
            "actions": self.actions,
            "family_summary": self.family_summary,
            "blocked_families": self.blocked_families,
            "degraded_families": self.degraded_families,
            "warning_families": self.warning_families,
            "ignored_families": self.ignored_families,
            "known_gap_count": self.known_gap_count,
        }


def resolve_bundle_dir(bundle_dir: str | Path | None = None) -> Path:
    if bundle_dir is not None:
        return Path(bundle_dir)
    override = os.environ.get(BUNDLE_DIR_ENV)
    if override:
        return Path(override)
    return DEFAULT_BUNDLE_DIR


def check_bundle_compatibility(bundle_dir: str | Path | None = None) -> BundleCompatibilityResult:
    path = resolve_bundle_dir(bundle_dir)
    result = BundleCompatibilityResult(status=STATUS_COMPATIBLE)

    if not path.exists() or not path.is_dir():
        result.errors.append(f"Bundle directory does not exist: {path}")
        result.status = STATUS_INCOMPATIBLE
        return result

    metadata = _read_required_json(path / "metadata.json", "metadata.json", result)
    manifest = _read_required_json(path / "manifest.json", "manifest.json", result)
    validation = _read_required_json(path / "validation_status.json", "validation_status.json", result)
    known_gaps = _read_optional_json(path / "reports" / "known_gaps.json", "reports/known_gaps.json", result)
    _read_optional_text(path / "reports" / "migration_notes.md", "reports/migration_notes.md", result)

    if result.errors:
        result.status = STATUS_INCOMPATIBLE
        return result

    if not isinstance(metadata, dict) or not isinstance(manifest, dict) or not isinstance(validation, dict):
        result.errors.append("metadata.json, manifest.json, and validation_status.json must be JSON objects.")
        result.status = STATUS_INCOMPATIBLE
        return result

    result.bundle_id = metadata.get("bundle_id")
    result.game_version = metadata.get("game_version")
    result.build_number = metadata.get("build_number")
    result.data_patch = metadata.get("data_patch")
    result.validation_status = validation.get("status")

    _validate_bundle_ids(metadata, manifest, validation, result)
    _validate_schema_versions(metadata, manifest, result)
    _inspect_validation_status(validation, result)
    _inspect_manifest(manifest, validation, result)
    _inspect_known_gaps(known_gaps, result)

    if result.errors:
        result.status = STATUS_INCOMPATIBLE
    elif result.warnings:
        result.status = STATUS_COMPATIBLE_WITH_WARNINGS
    else:
        result.status = STATUS_COMPATIBLE

    return result


def _read_required_json(path: Path, label: str, result: BundleCompatibilityResult) -> Any | None:
    if not path.exists():
        result.errors.append(f"Missing {label}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.errors.append(f"Invalid JSON in {label}: {exc}")
    except OSError as exc:
        result.errors.append(f"Could not read {label}: {exc}")
    return None


def _read_optional_json(path: Path, label: str, result: BundleCompatibilityResult) -> Any | None:
    if not path.exists():
        result.warnings.append(f"Optional {label} is missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.warnings.append(f"Optional {label} has invalid JSON: {exc}")
    except OSError as exc:
        result.warnings.append(f"Could not read optional {label}: {exc}")
    return None


def _read_optional_text(path: Path, label: str, result: BundleCompatibilityResult) -> str | None:
    if not path.exists():
        result.warnings.append(f"Optional {label} is missing.")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        result.warnings.append(f"Could not read optional {label}: {exc}")
    return None


def _validate_bundle_ids(
    metadata: dict[str, Any],
    manifest: dict[str, Any],
    validation: dict[str, Any],
    result: BundleCompatibilityResult,
) -> None:
    ids = {
        "metadata.json": metadata.get("bundle_id"),
        "manifest.json": manifest.get("bundle_id"),
        "validation_status.json": validation.get("bundle_id"),
    }
    if any(value is None for value in ids.values()):
        missing = [label for label, value in ids.items() if value is None]
        result.errors.append(f"Missing bundle_id in {', '.join(missing)}")
        return
    if len(set(ids.values())) != 1:
        result.errors.append(
            "bundle_id mismatch: "
            + ", ".join(f"{label}={value}" for label, value in ids.items())
        )


def _validate_schema_versions(
    metadata: dict[str, Any],
    manifest: dict[str, Any],
    result: BundleCompatibilityResult,
) -> None:
    bundle_schema = metadata.get("bundle_schema_version")
    if bundle_schema not in SUPPORTED_BUNDLE_SCHEMA_VERSIONS:
        result.errors.append(f"Unsupported or missing bundle_schema_version: {bundle_schema!r}")

    manifest_schema = manifest.get("manifest_schema_version")
    if manifest_schema not in SUPPORTED_MANIFEST_SCHEMA_VERSIONS:
        result.errors.append(f"Unsupported or missing manifest_schema_version: {manifest_schema!r}")


def _inspect_validation_status(validation: dict[str, Any], result: BundleCompatibilityResult) -> None:
    status = validation.get("status")
    if status == "failed":
        result.errors.append("validation_status.status is failed.")
    elif status == "warning":
        result.warnings.append("validation_status.status is warning.")
    elif status not in {"passed", "warning", "failed"}:
        result.errors.append(f"Unsupported or missing validation_status.status: {status!r}")


def _inspect_manifest(
    manifest: dict[str, Any],
    validation: dict[str, Any],
    result: BundleCompatibilityResult,
) -> None:
    families = manifest.get("families")
    if not isinstance(families, list):
        result.errors.append("manifest.families must be a list.")
        return

    family_entries: dict[str, dict[str, Any]] = {}
    for entry in families:
        if not isinstance(entry, dict):
            result.warnings.append("Ignoring non-object manifest family entry.")
            continue
        family = entry.get("family")
        if not isinstance(family, str) or not family:
            result.warnings.append("Ignoring manifest family entry without a family id.")
            continue
        family_entries[family] = entry

    _inspect_action_summary(manifest, family_entries, result)
    _inspect_unknown_families(manifest, family_entries, result)

    family_status = validation.get("family_status")
    if not isinstance(family_status, dict):
        result.errors.append("validation_status.family_status must be an object.")
        family_status = {}

    blocked: set[str] = set(result.blocked_families)
    degraded: set[str] = set(result.degraded_families)
    warned: set[str] = set(result.warning_families)
    ignored: set[str] = set(result.ignored_families)

    for family, entry in family_entries.items():
        status_entry = family_status.get(family, {})
        requirement_level = entry.get("requirement_level")
        validation_status = entry.get("validation_status")
        family_status_value = status_entry.get("status") if isinstance(status_entry, dict) else None
        action = _family_action(entry, manifest)

        if requirement_level == REQUIRED_NOW and (entry.get("deferred") or entry.get("stale") or validation_status in {"failed", "stale", "deferred"}):
            result.warnings.append(
                f"Required Now family {family} is {validation_status or family_status_value}; action={action}."
            )

        if requirement_level == REQUIRED_NOW and family_status_value in {"failed", "stale", "deferred"}:
            result.warnings.append(
                f"validation_status marks Required Now family {family} as {family_status_value}."
            )

        if entry.get("feature_status") == "Authoritative" and entry.get("readiness_level") not in AUTHORITATIVE_READY_LEVELS:
            result.warnings.append(
                f"Family {family} is Authoritative but readiness_level is {entry.get('readiness_level')!r}."
            )

        if entry.get("canonical_migration_state") == "Approximation-backed" and entry.get("feature_status") == "Authoritative":
            result.warnings.append(f"Family {family} is Approximation-backed but marked Authoritative.")

        if action == "block":
            blocked.add(family)
        elif action == "degrade":
            degraded.add(family)
        elif action == "warn":
            warned.add(family)
        elif action == "ignore":
            ignored.add(family)

    result.blocked_families = sorted(blocked)
    result.degraded_families = sorted(degraded)
    result.warning_families = sorted(warned)
    result.ignored_families = sorted(ignored)
    result.family_summary = {
        "total": len(family_entries),
        "required_now": sum(1 for entry in family_entries.values() if entry.get("requirement_level") == REQUIRED_NOW),
        "deferred": sum(1 for entry in family_entries.values() if entry.get("deferred")),
        "stale": sum(1 for entry in family_entries.values() if entry.get("stale")),
        "failed": sum(1 for entry in family_entries.values() if entry.get("validation_status") == "failed"),
    }


def _inspect_action_summary(
    manifest: dict[str, Any],
    family_entries: dict[str, dict[str, Any]],
    result: BundleCompatibilityResult,
) -> None:
    action_summary = manifest.get("action_summary")
    if not isinstance(action_summary, dict):
        result.warnings.append("manifest.action_summary is missing or invalid.")
        return

    for bucket in VALID_ACTION_BUCKETS:
        values = action_summary.get(bucket, [])
        if not isinstance(values, list):
            result.warnings.append(f"manifest.action_summary.{bucket} is not a list.")
            continue
        clean_values = [family for family in values if isinstance(family, str)]
        result.actions[bucket] = clean_values
        for family in clean_values:
            if family not in family_entries:
                result.warnings.append(f"action_summary.{bucket} references unknown family {family}.")

    for family in result.actions["block"]:
        if family in family_entries:
            result.blocked_families.append(family)
    for family in result.actions["degrade"]:
        if family in family_entries:
            result.degraded_families.append(family)
    for family in result.actions["warn"]:
        if family in family_entries:
            result.warning_families.append(family)
    for family in result.actions["ignore"]:
        if family in family_entries:
            result.ignored_families.append(family)

    if result.actions["block"]:
        result.warnings.append(
            "manifest.action_summary.block is non-empty; reported as diagnostics only in Phase 1C."
        )


def _inspect_unknown_families(
    manifest: dict[str, Any],
    family_entries: dict[str, dict[str, Any]],
    result: BundleCompatibilityResult,
) -> None:
    contract = manifest.get("consumer_contract") if isinstance(manifest.get("consumer_contract"), dict) else {}
    default_action = contract.get("default_action_on_unknown_family", "ignore")
    known = {
        "metadata",
        "base_items",
        "item_types",
        "affixes",
        "affix_tiers",
        "affix_eligibility",
        "affix_tags",
        "uniques",
        "idols",
        "blessings",
        "passives",
        "passive_trees",
        "skills",
        "skill_trees",
        "class_mastery_stats",
        "enemy_profiles",
        "corruption_scaling",
    }
    unknown = sorted(set(family_entries) - known)
    if not unknown:
        return
    result.warnings.append(
        f"Unknown families follow default_action_on_unknown_family={default_action}: {', '.join(unknown)}"
    )
    if default_action == "ignore":
        result.ignored_families.extend(unknown)
    elif default_action == "warn":
        result.warning_families.extend(unknown)
    elif default_action == "degrade":
        result.degraded_families.extend(unknown)
    elif default_action == "block":
        result.blocked_families.extend(unknown)


def _family_action(entry: dict[str, Any], manifest: dict[str, Any]) -> str:
    contract = entry.get("consumer_contract") if isinstance(entry.get("consumer_contract"), dict) else {}
    action = contract.get("fallback_policy")
    if action in VALID_ACTION_BUCKETS:
        return action
    bundle_contract = manifest.get("consumer_contract") if isinstance(manifest.get("consumer_contract"), dict) else {}
    return bundle_contract.get("default_action_on_required_now_failure", "block")


def _inspect_known_gaps(known_gaps: Any | None, result: BundleCompatibilityResult) -> None:
    if known_gaps is None:
        result.known_gap_count = None
        return
    if not isinstance(known_gaps, dict):
        result.warnings.append("reports/known_gaps.json is not an object.")
        result.known_gap_count = None
        return
    gaps = known_gaps.get("gaps")
    if not isinstance(gaps, list):
        result.warnings.append("reports/known_gaps.json does not contain a gaps array.")
        result.known_gap_count = None
        return
    result.known_gap_count = len(gaps)
