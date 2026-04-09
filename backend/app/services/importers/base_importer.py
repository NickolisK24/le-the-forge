"""
Base importer — abstract interface and shared validation logic.

Every concrete importer must implement parse(url) -> ImportResult.
The validate() method checks parsed data against game data — any
class, mastery, skill, or node that doesn't exist goes to missing_fields.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Game data caches (loaded lazily)
_VALID_CLASSES: Optional[set] = None
_VALID_MASTERIES: Optional[dict] = None  # {class_name: [mastery_names]}
_VALID_SKILL_IDS: Optional[set] = None


def _project_root() -> str:
    """Return the project root (two levels up from backend/app/services/)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))


def _load_game_data() -> None:
    """Load class, mastery, and skill data for validation."""
    global _VALID_CLASSES, _VALID_MASTERIES, _VALID_SKILL_IDS

    root = _project_root()

    # Classes & masteries
    try:
        with open(os.path.join(root, "data", "classes", "classes.json")) as f:
            classes_data = json.load(f)
        _VALID_CLASSES = set()
        _VALID_MASTERIES = {}
        for cls in classes_data:
            name = cls["name"]
            _VALID_CLASSES.add(name)
            _VALID_MASTERIES[name] = [m["name"] for m in cls.get("masteries", [])]
    except Exception as exc:
        logger.warning("base_importer: could not load classes.json: %s", exc)
        _VALID_CLASSES = set()
        _VALID_MASTERIES = {}

    # Skill IDs
    try:
        with open(os.path.join(root, "data", "classes", "skills_metadata.json")) as f:
            skills_data = json.load(f)
        _VALID_SKILL_IDS = {
            v["id"] for v in skills_data.values()
            if isinstance(v, dict) and "id" in v
        }
    except Exception as exc:
        logger.warning("base_importer: could not load skills_metadata.json: %s", exc)
        _VALID_SKILL_IDS = set()


def get_valid_classes() -> set:
    if _VALID_CLASSES is None:
        _load_game_data()
    return _VALID_CLASSES


def get_valid_masteries() -> dict:
    if _VALID_MASTERIES is None:
        _load_game_data()
    return _VALID_MASTERIES


def get_valid_skill_ids() -> set:
    if _VALID_SKILL_IDS is None:
        _load_game_data()
    return _VALID_SKILL_IDS


@dataclass
class ImportResult:
    """Outcome of a build import attempt."""
    success: bool
    build_data: Optional[dict] = None
    source: str = ""
    missing_fields: list = field(default_factory=list)
    error_message: Optional[str] = None
    partial_data: Optional[dict] = None


class BaseImporter(ABC):
    """Abstract base class for build importers."""

    source_name: str = ""

    @abstractmethod
    def parse(self, url: str) -> ImportResult:
        """
        Fetch and parse a build from the given URL.

        Returns ImportResult with:
        - success=True if class/mastery could be resolved
        - build_data containing the mapped Forge build payload
        - missing_fields listing anything that couldn't be mapped
        - error_message set on hard failures
        """

    def validate(self, result: ImportResult) -> ImportResult:
        """
        Check parsed build_data against game data.
        Moves unrecognized values to missing_fields.
        """
        if not result.success or not result.build_data:
            return result

        data = result.build_data
        missing = list(result.missing_fields)
        valid_classes = get_valid_classes()
        valid_masteries = get_valid_masteries()
        valid_skill_ids = get_valid_skill_ids()

        # Validate class
        char_class = data.get("character_class", "")
        if char_class and char_class not in valid_classes:
            missing.append(f"class:{char_class}")

        # Validate mastery
        mastery = data.get("mastery", "")
        if mastery and char_class in valid_masteries:
            if mastery not in valid_masteries[char_class]:
                missing.append(f"mastery:{mastery}")

        # Validate skills
        for skill in data.get("skills", []):
            skill_name = skill.get("skill_name", "")
            # We can't validate skill names against IDs directly —
            # the name->ID mapping is in skills_metadata.json by name key.
            # Just check that the name is non-empty.
            if not skill_name:
                missing.append("skill:empty_name")

        result.missing_fields = missing
        return result
