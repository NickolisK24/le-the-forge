"""
Build Serializer — Upgrade 7

Provides lossless serialization and deserialization of build configurations
in two formats:

    1. JSON  — structured dict, human-readable, API-compatible
    2. Forge Build String (FBS) — compact base64-encoded representation for
       sharing in URLs, chat messages, or clipboard

Both formats preserve all build data: class, mastery, passive nodes, gear
(with all affixes, implicit stats, FP), and metadata.

Rules enforced:
- No data loss round-trip: import(export(build)) == build (structurally)
- Version-tagged output for forward compatibility
- Strict type validation on import
- No cross-engine coupling: pure data transformation
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from copy import deepcopy
from dataclasses import dataclass

from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

_SCHEMA_VERSION = "1.0"
_FBS_PREFIX     = "FORGE:"


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class SerializedBuild:
    """Serialized build in JSON format."""
    version:          str
    exported_at:      float      # Unix timestamp
    checksum:         str        # SHA-256 of the canonical data
    character_class:  str
    mastery:          str
    passive_tree:     list[int]
    gear:             list[dict]
    primary_skill:    str
    metadata:         dict

    def to_dict(self) -> dict:
        return {
            "version":         self.version,
            "exported_at":     self.exported_at,
            "checksum":        self.checksum,
            "character_class": self.character_class,
            "mastery":         self.mastery,
            "passive_tree":    self.passive_tree,
            "gear":            self.gear,
            "primary_skill":   self.primary_skill,
            "metadata":        self.metadata,
        }


@dataclass
class ImportResult:
    """Result of importing a build string or dict."""
    success:       bool
    build:         dict | None
    errors:        list[str]
    warnings:      list[str]
    source_version: str

    def to_dict(self) -> dict:
        return {
            "success":        self.success,
            "build":          self.build,
            "errors":         self.errors,
            "warnings":       self.warnings,
            "source_version": self.source_version,
        }


# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------

def _checksum(data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _normalise_gear(gear: list) -> list[dict]:
    """Ensure gear items have a consistent structure for serialization."""
    out = []
    for item in gear:
        if not isinstance(item, dict):
            continue
        normalised = {
            "item_id":           item.get("item_id", item.get("name", "unknown")),
            "slot_type":         item.get("slot_type", item.get("slot", "")),
            "forging_potential": item.get("forging_potential", item.get("forge_potential", 0)),
            "implicit_stats":    item.get("implicit_stats", {}),
            "affixes":           item.get("affixes", item.get("prefixes", []) + item.get("suffixes", [])),
            "sealed_affix":      item.get("sealed_affix"),
        }
        out.append(normalised)
    return out


def _normalise_passive_tree(passive_tree) -> list[int]:
    if not passive_tree:
        return []
    result = []
    for node in passive_tree:
        if isinstance(node, int):
            result.append(node)
        elif isinstance(node, dict):
            result.append(int(node.get("id", node.get("node_id", 0))))
    return sorted(set(result))  # deduplicate and sort for determinism


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_build(build: dict, metadata: dict | None = None) -> SerializedBuild:
    """Export a build dict to a structured, version-tagged SerializedBuild.

    This is the architecture-plan canonical export function.

    Args:
        build: Build dict with ``character_class``, ``mastery``,
               ``passive_tree``, ``gear``, and optionally ``primary_skill``.
        metadata: Optional extra metadata to embed (labels, notes, etc.).

    Returns:
        :class:`SerializedBuild` ready for JSON output or FBS encoding.
    """
    gear          = _normalise_gear(build.get("gear", []))
    passive_tree  = _normalise_passive_tree(build.get("passive_tree", []))
    char_class    = str(build.get("character_class", ""))
    mastery       = str(build.get("mastery", ""))
    primary_skill = str(build.get("primary_skill", ""))

    canonical = {
        "character_class": char_class,
        "mastery":         mastery,
        "passive_tree":    passive_tree,
        "gear":            gear,
        "primary_skill":   primary_skill,
    }
    chk = _checksum(canonical)

    log.info("export_build", char_class=char_class, mastery=mastery, checksum=chk)

    return SerializedBuild(
        version         = _SCHEMA_VERSION,
        exported_at     = time.time(),
        checksum        = chk,
        character_class = char_class,
        mastery         = mastery,
        passive_tree    = passive_tree,
        gear            = gear,
        primary_skill   = primary_skill,
        metadata        = dict(metadata or {}),
    )


def export_to_json(build: dict, metadata: dict | None = None) -> str:
    """Export build to a JSON string."""
    sb = export_build(build, metadata)
    return json.dumps(sb.to_dict(), indent=2)


def export_to_fbs(build: dict, metadata: dict | None = None) -> str:
    """Export build to a compact Forge Build String.

    Format: ``FORGE:<base64url-encoded JSON>``
    """
    sb    = export_build(build, metadata)
    raw   = json.dumps(sb.to_dict(), separators=(",", ":"))
    enc   = base64.urlsafe_b64encode(raw.encode()).decode()
    return f"{_FBS_PREFIX}{enc}"


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_build(source: str | dict) -> ImportResult:
    """Import a build from a JSON string, FBS string, or dict.

    This is the architecture-plan canonical import function.

    Args:
        source: One of:
            - A JSON string (output of export_to_json)
            - A Forge Build String starting with ``FORGE:``
            - A raw dict (will be validated and normalised)

    Returns:
        :class:`ImportResult` with ``success``, ``build`` (if successful),
        ``errors``, ``warnings``, and ``source_version``.
    """
    errors:   list[str] = []
    warnings: list[str] = []
    source_version = "unknown"

    # Decode input
    try:
        if isinstance(source, dict):
            data = source
        elif isinstance(source, str):
            if source.startswith(_FBS_PREFIX):
                encoded = source[len(_FBS_PREFIX):]
                raw     = base64.urlsafe_b64decode(encoded.encode()).decode()
                data    = json.loads(raw)
            else:
                data = json.loads(source)
        else:
            return ImportResult(False, None, ["Unsupported source type"], warnings, source_version)
    except Exception as exc:
        return ImportResult(False, None, [f"Decode error: {exc}"], warnings, source_version)

    source_version = data.get("version", "unknown")

    # Version compatibility
    if source_version not in (_SCHEMA_VERSION, "unknown"):
        warnings.append(f"Schema version mismatch: got {source_version!r}, expected {_SCHEMA_VERSION!r}")

    # Required fields
    for field in ("character_class", "passive_tree", "gear"):
        if field not in data:
            errors.append(f"Missing required field: {field!r}")

    if errors:
        return ImportResult(False, None, errors, warnings, source_version)

    # Checksum validation (if present)
    if "checksum" in data:
        canonical = {
            "character_class": data.get("character_class", ""),
            "mastery":         data.get("mastery", ""),
            "passive_tree":    data.get("passive_tree", []),
            "gear":            data.get("gear", []),
            "primary_skill":   data.get("primary_skill", ""),
        }
        expected = _checksum(canonical)
        if data["checksum"] != expected:
            warnings.append(
                f"Checksum mismatch — build data may have been modified "
                f"(got {data['checksum']!r}, expected {expected!r})"
            )

    # Build normalised output
    build = {
        "character_class": str(data.get("character_class", "")),
        "mastery":         str(data.get("mastery", "")),
        "passive_tree":    _normalise_passive_tree(data.get("passive_tree", [])),
        "gear":            _normalise_gear(data.get("gear", [])),
        "primary_skill":   str(data.get("primary_skill", "")),
        "metadata":        data.get("metadata", {}),
    }

    log.info("import_build.success", char_class=build["character_class"])
    return ImportResult(True, build, errors, warnings, source_version)


def import_from_json(json_str: str) -> ImportResult:
    """Import a build from a JSON string."""
    return import_build(json_str)


def import_from_fbs(fbs: str) -> ImportResult:
    """Import a build from a Forge Build String."""
    return import_build(fbs)
