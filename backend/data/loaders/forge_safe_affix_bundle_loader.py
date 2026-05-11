"""Controlled loader for Forge-safe affix bundles.

The Forge-safe affix bundle is the preferred controlled ingestion artifact from
last-epoch-data because it preserves validated affix/modifier relationships.
This loader validates the bundle shape and safety contract without wiring the
data into production planner, crafting, or simulation behavior.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "ForgeSafeAffixBundle",
    "ForgeSafeAffixBundleLoader",
    "ForgeSafeAffixBundleLoaderError",
]


EXPECTED_EXPORT_POLICY = "deterministic_affix_bundle"
REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "export_policy",
    "summary",
    "cross_reference_validation",
    "records",
)


class ForgeSafeAffixBundleLoaderError(ValueError):
    """Raised when a Forge-safe affix bundle cannot be loaded safely."""


@dataclass(frozen=True)
class ForgeSafeAffixBundle:
    """Validated Forge-safe affix bundle payload."""

    affixes: tuple[dict[str, Any], ...]
    modifiers: tuple[dict[str, Any], ...]
    modifiers_by_affix_identity: dict[str, tuple[dict[str, Any], ...]]
    summary: dict[str, Any]
    cross_reference_validation: dict[str, Any]
    source_path: Path
    warnings: tuple[str, ...]
    schema_version: str
    export_policy: str


class ForgeSafeAffixBundleLoader:
    """Load and validate a Forge-safe affix bundle JSON file."""

    def load(self, path: str | Path) -> ForgeSafeAffixBundle:
        source_path = Path(path)
        payload = self._read_json(source_path)
        return self.load_payload(payload, source_path=source_path)

    def load_payload(
        self,
        payload: dict[str, Any],
        *,
        source_path: str | Path = "<memory>",
    ) -> ForgeSafeAffixBundle:
        if not isinstance(payload, dict):
            raise ForgeSafeAffixBundleLoaderError("Forge-safe affix bundle must be a JSON object.")
        self._validate_top_level(payload)
        _reject_production_safe_true(payload)

        summary = payload["summary"]
        cross_reference = payload["cross_reference_validation"]
        records = payload["records"]
        if not isinstance(summary, dict):
            raise ForgeSafeAffixBundleLoaderError("Bundle summary must be an object.")
        if not isinstance(cross_reference, dict):
            raise ForgeSafeAffixBundleLoaderError("Bundle cross_reference_validation must be an object.")
        if not isinstance(records, dict):
            raise ForgeSafeAffixBundleLoaderError("Bundle records must be an object.")

        if payload["export_policy"] != EXPECTED_EXPORT_POLICY:
            raise ForgeSafeAffixBundleLoaderError(
                f"Bundle export_policy must be {EXPECTED_EXPORT_POLICY!r}."
            )
        if summary.get("production_safe") is not False:
            raise ForgeSafeAffixBundleLoaderError("Bundle summary.production_safe must be false.")
        if summary.get("forge_safe_records_only") is not True:
            raise ForgeSafeAffixBundleLoaderError("Bundle summary.forge_safe_records_only must be true.")
        self._validate_cross_reference(cross_reference)

        affixes = records.get("affixes")
        modifiers = records.get("modifiers")
        if not isinstance(affixes, list):
            raise ForgeSafeAffixBundleLoaderError("Bundle records.affixes must be a list.")
        if not isinstance(modifiers, list):
            raise ForgeSafeAffixBundleLoaderError("Bundle records.modifiers must be a list.")
        if not affixes:
            raise ForgeSafeAffixBundleLoaderError("Bundle records.affixes must not be empty.")
        if not modifiers:
            raise ForgeSafeAffixBundleLoaderError("Bundle records.modifiers must not be empty.")

        self._validate_affixes(affixes)
        self._validate_modifiers(modifiers)
        modifiers_by_affix_identity = self._build_modifier_index(affixes, modifiers)

        warnings = self._summary_warnings(summary, affixes, modifiers)
        return ForgeSafeAffixBundle(
            affixes=tuple(affixes),
            modifiers=tuple(modifiers),
            modifiers_by_affix_identity=modifiers_by_affix_identity,
            summary=dict(summary),
            cross_reference_validation=dict(cross_reference),
            source_path=Path(source_path),
            warnings=tuple(warnings),
            schema_version=str(payload["schema_version"]),
            export_policy=str(payload["export_policy"]),
        )

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Forge-safe affix bundle not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ForgeSafeAffixBundleLoaderError(f"Invalid JSON in Forge-safe affix bundle {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise ForgeSafeAffixBundleLoaderError(f"Forge-safe affix bundle must be a JSON object: {path}")
        return data

    @staticmethod
    def _validate_top_level(payload: dict[str, Any]) -> None:
        missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in payload]
        if missing:
            raise ForgeSafeAffixBundleLoaderError(
                "Forge-safe affix bundle is missing required top-level fields: "
                + ", ".join(missing)
            )
        if not payload.get("schema_version"):
            raise ForgeSafeAffixBundleLoaderError("Bundle schema_version is required.")

    @staticmethod
    def _validate_cross_reference(cross_reference: dict[str, Any]) -> None:
        if cross_reference.get("status") != "pass":
            raise ForgeSafeAffixBundleLoaderError("Bundle cross_reference_validation.status must be 'pass'.")
        zero_fields = (
            "unmatched_affix_count",
            "unmatched_modifier_count",
            "duplicate_affix_id_count",
            "duplicate_modifier_id_count",
        )
        for field in zero_fields:
            if cross_reference.get(field) != 0:
                raise ForgeSafeAffixBundleLoaderError(f"Bundle cross-reference {field} must be 0.")

    @staticmethod
    def _validate_affixes(affixes: list[Any]) -> None:
        seen_affix_ids: set[Any] = set()
        seen_identities: set[str] = set()
        for index, affix in enumerate(affixes):
            if not isinstance(affix, dict):
                raise ForgeSafeAffixBundleLoaderError(f"Affix record {index} must be an object.")
            if affix.get("affix_id") in (None, ""):
                raise ForgeSafeAffixBundleLoaderError(f"Affix record {index} is missing affix_id.")
            if affix["affix_id"] in seen_affix_ids:
                raise ForgeSafeAffixBundleLoaderError(f"Duplicate affix_id in Forge-safe affix bundle: {affix['affix_id']}")
            seen_affix_ids.add(affix["affix_id"])
            if _safety(affix).get("forge_safe") is not True:
                raise ForgeSafeAffixBundleLoaderError(f"Affix record {index} must have safety.forge_safe=true.")
            identity = _affix_identity(affix)
            if not identity:
                raise ForgeSafeAffixBundleLoaderError(f"Affix record {index} is missing provenance.source_affix_identity.")
            if identity in seen_identities:
                raise ForgeSafeAffixBundleLoaderError(f"Duplicate source_affix_identity in Forge-safe affix bundle: {identity}")
            seen_identities.add(identity)

    @staticmethod
    def _validate_modifiers(modifiers: list[Any]) -> None:
        seen_modifier_ids: set[Any] = set()
        for index, modifier in enumerate(modifiers):
            if not isinstance(modifier, dict):
                raise ForgeSafeAffixBundleLoaderError(f"Modifier record {index} must be an object.")
            if modifier.get("modifier_id") in (None, ""):
                raise ForgeSafeAffixBundleLoaderError(f"Modifier record {index} is missing modifier_id.")
            if modifier["modifier_id"] in seen_modifier_ids:
                raise ForgeSafeAffixBundleLoaderError(f"Duplicate modifier_id in Forge-safe affix bundle: {modifier['modifier_id']}")
            seen_modifier_ids.add(modifier["modifier_id"])
            if _safety(modifier).get("forge_safe") is not True:
                raise ForgeSafeAffixBundleLoaderError(f"Modifier record {index} must have safety.forge_safe=true.")
            if not _modifier_affix_identity(modifier):
                raise ForgeSafeAffixBundleLoaderError(f"Modifier record {index} is missing source.source_affix_identity.")

    @staticmethod
    def _build_modifier_index(
        affixes: list[dict[str, Any]],
        modifiers: list[dict[str, Any]],
    ) -> dict[str, tuple[dict[str, Any], ...]]:
        affix_identities = {_affix_identity(affix) for affix in affixes}
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for index, modifier in enumerate(modifiers):
            identity = _modifier_affix_identity(modifier)
            if identity not in affix_identities:
                raise ForgeSafeAffixBundleLoaderError(
                    f"Modifier record {index} references unknown source_affix_identity: {identity}"
                )
            grouped[identity].append(modifier)
        missing = sorted(identity for identity in affix_identities if not grouped.get(identity))
        if missing:
            raise ForgeSafeAffixBundleLoaderError(
                "Every Forge-safe affix must have at least one modifier; missing: "
                + ", ".join(missing[:10])
            )
        return {identity: tuple(values) for identity, values in grouped.items()}

    @staticmethod
    def _summary_warnings(
        summary: dict[str, Any],
        affixes: list[dict[str, Any]],
        modifiers: list[dict[str, Any]],
    ) -> list[str]:
        warnings: list[str] = []
        expected_affixes = (
            summary.get("exported_affix_records")
            or summary.get("bundle_affixes")
            or summary.get("affix_count")
        )
        if expected_affixes is not None and expected_affixes != len(affixes):
            warnings.append(
                f"summary affix count {expected_affixes} does not match loaded affix count {len(affixes)}."
            )
        expected_modifiers = (
            summary.get("exported_modifier_records")
            or summary.get("bundle_modifiers")
            or summary.get("modifier_count")
        )
        if expected_modifiers is not None and expected_modifiers != len(modifiers):
            warnings.append(
                f"summary modifier count {expected_modifiers} does not match loaded modifier count {len(modifiers)}."
            )
        return warnings


def _reject_production_safe_true(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        if value.get("production_safe") is True:
            raise ForgeSafeAffixBundleLoaderError(f"Bundle must not contain production_safe=true at {path}.")
        for key, child in value.items():
            _reject_production_safe_true(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_production_safe_true(child, f"{path}[{index}]")


def _safety(record: dict[str, Any]) -> dict[str, Any]:
    safety = record.get("safety")
    if not isinstance(safety, dict):
        return {}
    return safety


def _affix_identity(affix: dict[str, Any]) -> str:
    provenance = affix.get("provenance")
    if not isinstance(provenance, dict):
        return ""
    identity = provenance.get("source_affix_identity")
    return str(identity) if identity else ""


def _modifier_affix_identity(modifier: dict[str, Any]) -> str:
    source = modifier.get("source")
    if isinstance(source, dict) and source.get("source_affix_identity"):
        return str(source["source_affix_identity"])
    provenance = modifier.get("provenance")
    if isinstance(provenance, dict) and provenance.get("source_affix_identity"):
        return str(provenance["source_affix_identity"])
    return ""
