"""
J10 — Versioned Data Loader

Wraps RawDataLoader with version detection and compatibility checking.
Supports:
  - Detecting version from _version / _meta.version fields
  - Loading a versioned dataset (falls back to unversioned if missing)
  - Returning a compatibility report
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from data.loaders.raw_data_loader import RawDataLoader

__all__ = ["VersionedLoader", "VersionInfo"]

# Known version file paths to probe (in priority order)
_VERSION_PROBES = [
    "items/affixes.json",
    "entities/enemy_profiles.json",
    "combat/damage_types.json",
]


class VersionInfo:
    """Carries detected version metadata."""

    def __init__(self, version: str, source: str) -> None:
        self.version = version
        self.source = source  # which file was used to detect

    def __repr__(self) -> str:  # pragma: no cover
        return f"VersionInfo(version={self.version!r}, source={self.source!r})"

    def to_dict(self) -> dict:
        return {"version": self.version, "source": self.source}


class VersionedLoader:
    """
    Version-aware wrapper around :class:`RawDataLoader`.

    Parameters
    ----------
    data_dir:
        Passed directly to the underlying :class:`RawDataLoader`.
    """

    def __init__(self, data_dir: Union[str, Path, None] = None) -> None:
        self._loader = RawDataLoader(data_dir)

    # ------------------------------------------------------------------
    # Version detection
    # ------------------------------------------------------------------

    def detect_version(self) -> VersionInfo:
        """
        Detect the data version by reading ``_version`` / ``_meta.version``
        from the first available probe file.

        Returns ``"unknown"`` if no version field is found.
        """
        for probe in _VERSION_PROBES:
            if not self._loader.exists(probe):
                continue
            try:
                data = self._loader.load(probe)
            except (FileNotFoundError, ValueError):
                continue

            version = _extract_version(data)
            if version:
                return VersionInfo(version=version, source=probe)

        return VersionInfo(version="unknown", source="none")

    # ------------------------------------------------------------------
    # Versioned loading
    # ------------------------------------------------------------------

    def load(self, relative_path: str, version: str | None = None) -> dict | list:
        """
        Load *relative_path*, optionally from a version-specific subdirectory.

        If *version* is provided and a path ``<version>/<relative_path>``
        exists, that file is loaded instead.  Falls back to the unversioned
        path transparently.
        """
        if version:
            versioned = f"{version}/{relative_path}"
            if self._loader.exists(versioned):
                return self._loader.load(versioned)
        return self._loader.load(relative_path)

    def validate_compatibility(self, required_version: str) -> bool:
        """
        Return True if the detected data version matches *required_version*.
        ``"unknown"`` is never considered compatible.
        """
        info = self.detect_version()
        return info.version == required_version

    @property
    def raw_loader(self) -> RawDataLoader:
        return self._loader


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _extract_version(data: dict | list) -> str:
    """Try to pull a version string from a JSON payload."""
    if not isinstance(data, dict):
        return ""
    # Direct _version key
    if "_version" in data:
        return str(data["_version"])
    # Nested _meta.version
    meta = data.get("_meta")
    if isinstance(meta, dict) and "version" in meta:
        return str(meta["version"])
    return ""
