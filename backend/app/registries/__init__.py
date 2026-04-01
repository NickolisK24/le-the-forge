"""
Registries package — indexed, validated lookups over game data.

All registries are initialized in create_app() from the GameDataPipeline
and stored on app.extensions. Access them via current_app:

    from flask import current_app
    skill_registry = current_app.extensions["skill_registry"]
    affix_registry = current_app.extensions["affix_registry"]
"""

from app.registries.skill_registry import SkillRegistry, SkillNotFoundError
from app.registries.affix_registry import AffixRegistry, AffixNotFoundError

__all__ = [
    "SkillRegistry",
    "SkillNotFoundError",
    "AffixRegistry",
    "AffixNotFoundError",
]
