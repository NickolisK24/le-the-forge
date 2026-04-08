"""
Importer factory — detects the source from a URL and returns the right importer.
"""

from app.services.importers.base_importer import BaseImporter
from app.services.importers.lastepochtools_importer import (
    LastEpochToolsImporter,
    URL_PATTERN as LET_PATTERN,
)
from app.services.importers.maxroll_importer import (
    MaxrollImporter,
    URL_PATTERN as MAXROLL_PATTERN,
)


def detect_source(url: str) -> str:
    """
    Return the source name for a URL, or raise ValueError for unsupported URLs.
    """
    if LET_PATTERN.search(url):
        return "lastepochtools"
    if MAXROLL_PATTERN.search(url):
        return "maxroll"
    raise ValueError(
        f"Unsupported URL: {url}. "
        "Supported sources: lastepochtools.com/planner/..., maxroll.gg/last-epoch/planner/..."
    )


def get_importer(url: str) -> BaseImporter:
    """
    Return the correct importer instance for the given URL.
    Raises ValueError if the URL doesn't match any known source.
    """
    source = detect_source(url)
    if source == "lastepochtools":
        return LastEpochToolsImporter()
    if source == "maxroll":
        return MaxrollImporter()
    raise ValueError(f"No importer for source: {source}")
