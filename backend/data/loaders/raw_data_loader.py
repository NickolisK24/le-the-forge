"""
J2 — Raw Data Loader

Locates and loads raw JSON game-data bundles from the /data/ directory.
Works standalone (no Flask dependency) — can be used in tests or CLIs.
"""

import json
from pathlib import Path
from typing import Union

__all__ = ["RawDataLoader"]

# Project-root /data/ directory, resolved relative to this file's location:
#   backend/data/loaders/raw_data_loader.py
#   parents[0] = backend/data/loaders/
#   parents[1] = backend/data/
#   parents[2] = backend/
#   parents[3] = project root (le-the-forge/)
_DEFAULT_DATA_DIR = Path(__file__).parents[3] / "data"


class RawDataLoader:
    """
    Load raw JSON files from the game-data directory.

    Parameters
    ----------
    data_dir:
        Path to the root data directory.  Defaults to
        ``<project_root>/data/``.
    """

    def __init__(self, data_dir: Union[str, Path, None] = None) -> None:
        self._dir = Path(data_dir) if data_dir is not None else _DEFAULT_DATA_DIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def data_dir(self) -> Path:
        return self._dir

    def load(self, relative_path: str) -> Union[dict, list]:
        """
        Load a single JSON file relative to the data directory.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file contains invalid JSON.
        """
        full = self._dir / relative_path
        if not full.exists():
            raise FileNotFoundError(
                f"Data file not found: {full}  (data_dir={self._dir})"
            )
        try:
            with open(full, encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {full}: {exc}") from exc

    def scan(self, subdir: str = "") -> list[str]:
        """
        Return all ``*.json`` paths (relative to data_dir) under *subdir*.

        If *subdir* is empty the entire data directory is scanned.
        """
        root = (self._dir / subdir) if subdir else self._dir
        if not root.exists():
            return []
        return sorted(
            str(p.relative_to(self._dir))
            for p in root.rglob("*.json")
        )

    def exists(self, relative_path: str) -> bool:
        """Return True if *relative_path* exists inside the data directory."""
        return (self._dir / relative_path).exists()
