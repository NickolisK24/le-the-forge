"""
Marshmallow schemas for the /api/simulate endpoints.

These schemas validate raw simulation payloads that don't require
a saved build — the frontend sends stats/class/gear directly.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load


VALID_CLASSES = ["Acolyte", "Mage", "Primalist", "Sentinel", "Rogue"]
VALID_MASTERIES = {
    "Acolyte": ["Necromancer", "Lich", "Warlock"],
    "Mage": ["Runemaster", "Sorcerer", "Spellblade"],
    "Primalist": ["Druid", "Beastmaster", "Shaman"],
    "Sentinel": ["Forge Guard", "Paladin", "Void Knight"],
    "Rogue": ["Bladedancer", "Marksman", "Falconer"],
}


class StatsInputSchema(Schema):
    """Flat BuildStats dict — all fields optional with sensible defaults."""
    base_damage = fields.Float(load_default=0.0)
    attack_speed = fields.Float(load_default=1.0)
    crit_chance = fields.Float(load_default=0.05)
    crit_multiplier = fields.Float(load_default=1.5)
    spell_damage_pct = fields.Float(load_default=0.0)
    physical_damage_pct = fields.Float(load_default=0.0)
    fire_damage_pct = fields.Float(load_default=0.0)
    cold_damage_pct = fields.Float(load_default=0.0)
    lightning_damage_pct = fields.Float(load_default=0.0)
    necrotic_damage_pct = fields.Float(load_default=0.0)
    void_damage_pct = fields.Float(load_default=0.0)
    poison_damage_pct = fields.Float(load_default=0.0)
    minion_damage_pct = fields.Float(load_default=0.0)
    attack_speed_pct = fields.Float(load_default=0.0)
    cast_speed = fields.Float(load_default=0.0)
    crit_chance_pct = fields.Float(load_default=0.0)
    crit_multiplier_pct = fields.Float(load_default=0.0)
    more_damage_multiplier = fields.Float(load_default=1.0)
    max_health = fields.Float(load_default=0.0)
    armour = fields.Float(load_default=0.0)
    dodge_rating = fields.Float(load_default=0.0)
    ward = fields.Float(load_default=0.0)
    ward_retention_pct = fields.Float(load_default=0.0)
    ward_regen = fields.Float(load_default=0.0)
    fire_res = fields.Float(load_default=0.0)
    cold_res = fields.Float(load_default=0.0)
    lightning_res = fields.Float(load_default=0.0)
    void_res = fields.Float(load_default=0.0)
    necrotic_res = fields.Float(load_default=0.0)
    poison_res = fields.Float(load_default=0.0)
    max_mana = fields.Float(load_default=0.0)
    mana_regen = fields.Float(load_default=0.0)
    health_regen = fields.Float(load_default=0.0)
    strength = fields.Float(load_default=0.0)
    intelligence = fields.Float(load_default=0.0)
    dexterity = fields.Float(load_default=0.0)
    vitality = fields.Float(load_default=0.0)
    attunement = fields.Float(load_default=0.0)


class SimulateStatsSchema(Schema):
    """POST /api/simulate/stats — aggregate stats from raw build data."""
    character_class = fields.Str(
        required=True, validate=validate.OneOf(VALID_CLASSES)
    )
    mastery = fields.Str(required=True)
    allocated_node_ids = fields.List(fields.Int(), load_default=[])
    gear_affixes = fields.List(fields.Dict(), load_default=[])

    @validates("mastery")
    def validate_mastery(self, value, **kwargs):
        all_masteries = [m for ms in VALID_MASTERIES.values() for m in ms]
        if value not in all_masteries:
            raise ValidationError(f"Unknown mastery: {value}")

    @post_load
    def check_mastery_class_match(self, data, **kwargs):
        cls = data.get("character_class")
        mastery = data.get("mastery")
        if cls and mastery and mastery not in VALID_MASTERIES.get(cls, []):
            raise ValidationError(
                {"mastery": [f"{mastery} is not a valid mastery for {cls}."]}
            )
        return data


class SimulateCombatSchema(Schema):
    """POST /api/simulate/combat — DPS + Monte Carlo from stats + skill."""
    stats = fields.Nested(StatsInputSchema, required=True)
    skill_name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    skill_level = fields.Int(
        validate=validate.Range(min=1, max=40), load_default=20
    )
    n_simulations = fields.Int(
        validate=validate.Range(min=100, max=50_000), load_default=10_000
    )


class SimulateDefenseSchema(Schema):
    """POST /api/simulate/defense — EHP + survivability from stats."""
    stats = fields.Nested(StatsInputSchema, required=True)


class SimulateOptimizeSchema(Schema):
    """POST /api/simulate/optimize — stat upgrade recommendations."""
    stats = fields.Nested(StatsInputSchema, required=True)
    skill_name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    skill_level = fields.Int(
        validate=validate.Range(min=1, max=40), load_default=20
    )
    top_n = fields.Int(
        validate=validate.Range(min=1, max=16), load_default=5
    )


class SimulateBuildSchema(Schema):
    """POST /api/simulate/build — full pipeline from raw build data."""
    character_class = fields.Str(
        required=True, validate=validate.OneOf(VALID_CLASSES)
    )
    mastery = fields.Str(required=True)
    allocated_node_ids = fields.List(fields.Int(), load_default=[])
    gear_affixes = fields.List(fields.Dict(), load_default=[])
    skill_name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    skill_level = fields.Int(
        validate=validate.Range(min=1, max=40), load_default=20
    )
    n_simulations = fields.Int(
        validate=validate.Range(min=100, max=50_000), load_default=5_000
    )

    @validates("mastery")
    def validate_mastery(self, value, **kwargs):
        all_masteries = [m for ms in VALID_MASTERIES.values() for m in ms]
        if value not in all_masteries:
            raise ValidationError(f"Unknown mastery: {value}")

    @post_load
    def check_mastery_class_match(self, data, **kwargs):
        cls = data.get("character_class")
        mastery = data.get("mastery")
        if cls and mastery and mastery not in VALID_MASTERIES.get(cls, []):
            raise ValidationError(
                {"mastery": [f"{mastery} is not a valid mastery for {cls}."]}
            )
        return data
