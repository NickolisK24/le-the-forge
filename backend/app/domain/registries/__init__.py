"""
Domain Registries — O(1) indexed lookups over typed domain objects.

Registries are part of the domain layer: they hold and serve domain objects,
not raw data dicts. All registries are initialized in create_app() from the
GameDataPipeline (which is responsible for normalization) and stored on
app.extensions. Access them via current_app:

    from flask import current_app
    skill_registry = current_app.extensions["skill_registry"]
    affix_registry = current_app.extensions["affix_registry"]
"""

from app.domain.registries.skill_registry import SkillRegistry, SkillNotFoundError
from app.domain.registries.affix_registry import AffixRegistry, AffixNotFoundError

__all__ = [
    "SkillRegistry",
    "SkillNotFoundError",
    "AffixRegistry",
    "AffixNotFoundError",
]
