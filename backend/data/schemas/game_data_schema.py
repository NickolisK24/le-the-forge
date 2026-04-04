"""
J1 — Game Data Schema Definitions

Strict marshmallow validation schemas for:
  - Skills
  - Items
  - Affixes
  - Passive tree nodes
  - Enemies

Each schema is used by the DataMapper (J9) to validate raw JSON before
constructing domain model objects.
"""

from marshmallow import Schema, fields, validate, ValidationError, post_load

__all__ = [
    "SkillSchema",
    "ItemSchema",
    "AffixSchema",
    "PassiveNodeSchema",
    "EnemySchema",
    "ValidationError",
]


class SkillSchema(Schema):
    """Schema for a single skill definition."""

    skill_id = fields.Str(required=True)
    base_damage = fields.Float(required=True, validate=validate.Range(min=0))
    cooldown = fields.Float(required=True, validate=validate.Range(min=0))
    mana_cost = fields.Float(required=True, validate=validate.Range(min=0))
    tags = fields.List(fields.Str(), load_default=[])
    attack_speed = fields.Float(load_default=1.0, validate=validate.Range(min=0, min_inclusive=False))
    level_scaling = fields.Float(load_default=0.0)


_ITEM_VALID_SLOTS = {
    "helm", "chest", "gloves", "boots", "belt", "ring", "amulet",
    "sword", "axe", "mace", "dagger", "sceptre", "wand", "staff",
    "bow", "spear", "shield", "quiver", "catalyst",
    "idol_small", "idol_large", "idol_grand", "idol_stout",
}


class ItemSchema(Schema):
    """Schema for a base item definition."""

    item_id = fields.Str(required=True)
    slot_type = fields.Str(
        required=True,
        validate=validate.OneOf(_ITEM_VALID_SLOTS),
    )
    implicit_stats = fields.Dict(
        keys=fields.Str(),
        values=fields.Float(),
        load_default={},
    )
    explicit_affixes = fields.List(fields.Str(), load_default=[])


class AffixSchema(Schema):
    """Schema for a single affix definition (single-tier view)."""

    affix_id = fields.Str(required=True)
    stat_type = fields.Str(required=True)
    min_value = fields.Float(required=True)
    max_value = fields.Float(required=True)

    @post_load
    def validate_range(self, data: dict, **kwargs) -> dict:
        if data["min_value"] > data["max_value"]:
            raise ValidationError(
                {"max_value": ["max_value must be >= min_value"]}
            )
        return data


class PassiveNodeSchema(Schema):
    """Schema for a passive tree node."""

    node_id = fields.Str(required=True)
    stat_modifiers = fields.Dict(
        keys=fields.Str(),
        values=fields.Float(),
        load_default={},
    )
    dependencies = fields.List(fields.Str(), load_default=[])


class EnemySchema(Schema):
    """Schema for an enemy template."""

    enemy_id = fields.Str(required=True)
    max_health = fields.Float(required=True, validate=validate.Range(min=1))
    resistances = fields.Dict(
        keys=fields.Str(),
        values=fields.Float(),
        load_default={},
    )
    armor = fields.Float(required=True, validate=validate.Range(min=0))
    name = fields.Str(load_default="")
    category = fields.Str(load_default="")
    crit_chance = fields.Float(load_default=0.0, validate=validate.Range(min=0.0, max=1.0))
    crit_multiplier = fields.Float(load_default=1.5, validate=validate.Range(min=1.0))
