"""
Marshmallow schemas for the /api/simulate endpoints.

These schemas validate raw simulation payloads that don't require
a saved build — the frontend sends stats/class/gear directly.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, EXCLUDE


VALID_CLASSES = ["Acolyte", "Mage", "Primalist", "Sentinel", "Rogue"]
VALID_MASTERIES = {
    "Acolyte": ["Necromancer", "Lich", "Warlock"],
    "Mage": ["Runemaster", "Sorcerer", "Spellblade"],
    "Primalist": ["Druid", "Beastmaster", "Shaman"],
    "Sentinel": ["Forge Guard", "Paladin", "Void Knight"],
    "Rogue": ["Bladedancer", "Marksman", "Falconer"],
}


class StatsInputSchema(Schema):
    """Flat BuildStats dict — all fields optional with sensible defaults.
    Accepts any field from BuildStats; unknown keys are silently ignored.
    """
    class Meta:
        unknown = EXCLUDE

    # Offense — base
    base_damage = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    attack_speed = fields.Float(load_default=1.0, validate=validate.Range(min=0.1, max=20.0))
    crit_chance = fields.Float(load_default=0.05, validate=validate.Range(min=0.0, max=1.0))
    crit_multiplier = fields.Float(load_default=1.5, validate=validate.Range(min=1.0, max=20.0))

    # Offense — percentage damage pools
    spell_damage_pct = fields.Float(load_default=0.0)
    physical_damage_pct = fields.Float(load_default=0.0)
    fire_damage_pct = fields.Float(load_default=0.0)
    cold_damage_pct = fields.Float(load_default=0.0)
    lightning_damage_pct = fields.Float(load_default=0.0)
    necrotic_damage_pct = fields.Float(load_default=0.0)
    void_damage_pct = fields.Float(load_default=0.0)
    poison_damage_pct = fields.Float(load_default=0.0)
    minion_damage_pct = fields.Float(load_default=0.0)
    melee_damage_pct = fields.Float(load_default=0.0)
    throwing_damage_pct = fields.Float(load_default=0.0)
    bow_damage_pct = fields.Float(load_default=0.0)
    elemental_damage_pct = fields.Float(load_default=0.0)
    dot_damage_pct = fields.Float(load_default=0.0)

    # Offense — speed / crit
    attack_speed_pct = fields.Float(load_default=0.0)
    cast_speed = fields.Float(load_default=0.0)
    throwing_attack_speed = fields.Float(load_default=0.0)
    crit_chance_pct = fields.Float(load_default=0.0)
    crit_multiplier_pct = fields.Float(load_default=0.0)
    more_damage_multiplier = fields.Float(load_default=1.0, validate=validate.Range(min=0.01, max=100.0))

    # Offense — flat added damage
    added_melee_physical = fields.Float(load_default=0.0)
    added_melee_fire = fields.Float(load_default=0.0)
    added_melee_cold = fields.Float(load_default=0.0)
    added_melee_lightning = fields.Float(load_default=0.0)
    added_melee_void = fields.Float(load_default=0.0)
    added_melee_necrotic = fields.Float(load_default=0.0)
    added_spell_damage = fields.Float(load_default=0.0)
    added_spell_fire = fields.Float(load_default=0.0)
    added_spell_cold = fields.Float(load_default=0.0)
    added_spell_lightning = fields.Float(load_default=0.0)
    added_spell_necrotic = fields.Float(load_default=0.0)
    added_spell_void = fields.Float(load_default=0.0)
    added_throw_physical = fields.Float(load_default=0.0)
    added_throw_fire = fields.Float(load_default=0.0)
    added_throw_cold = fields.Float(load_default=0.0)
    added_bow_physical = fields.Float(load_default=0.0)
    added_bow_fire = fields.Float(load_default=0.0)

    # Offense — ailment chance
    poison_chance_pct = fields.Float(load_default=0.0)
    bleed_chance_pct = fields.Float(load_default=0.0)
    ignite_chance_pct = fields.Float(load_default=0.0)
    shock_chance_pct = fields.Float(load_default=0.0)
    chill_chance_pct = fields.Float(load_default=0.0)
    slow_chance_pct = fields.Float(load_default=0.0)

    # Offense — DoT / ailment damage
    bleed_damage_pct = fields.Float(load_default=0.0)
    ignite_damage_pct = fields.Float(load_default=0.0)
    poison_dot_damage_pct = fields.Float(load_default=0.0)

    # Offense — minion
    minion_health_pct = fields.Float(load_default=0.0)
    minion_speed_pct = fields.Float(load_default=0.0)
    minion_physical_damage_pct = fields.Float(load_default=0.0)
    minion_spell_damage_pct = fields.Float(load_default=0.0)
    minion_melee_damage_pct = fields.Float(load_default=0.0)

    # Defense
    max_health = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    health_pct = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    hybrid_health = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    armour = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    dodge_rating = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    block_chance = fields.Float(load_default=0.0, validate=validate.Range(min=0, max=100))
    block_effectiveness = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    endurance = fields.Float(load_default=0.0, validate=validate.Range(min=0, max=100))
    endurance_threshold = fields.Float(load_default=0.0, validate=validate.Range(min=0, max=100))
    stun_avoidance = fields.Float(load_default=0.0, validate=validate.Range(min=0, max=100))
    crit_avoidance = fields.Float(load_default=0.0, validate=validate.Range(min=0, max=100))
    glancing_blow = fields.Float(load_default=0.0, validate=validate.Range(min=0, max=100))
    ward = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    ward_retention_pct = fields.Float(load_default=0.0, validate=validate.Range(min=0, max=100))
    ward_regen = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    fire_res = fields.Float(load_default=0.0, validate=validate.Range(min=-100, max=75))
    cold_res = fields.Float(load_default=0.0, validate=validate.Range(min=-100, max=75))
    lightning_res = fields.Float(load_default=0.0, validate=validate.Range(min=-100, max=75))
    void_res = fields.Float(load_default=0.0, validate=validate.Range(min=-100, max=75))
    necrotic_res = fields.Float(load_default=0.0, validate=validate.Range(min=-100, max=75))
    poison_res = fields.Float(load_default=0.0, validate=validate.Range(min=-100, max=75))
    physical_res = fields.Float(load_default=0.0, validate=validate.Range(min=-100, max=75))

    # Resources / Sustain
    max_mana = fields.Float(load_default=0.0)
    mana_regen = fields.Float(load_default=0.0)
    health_regen = fields.Float(load_default=0.0)
    leech = fields.Float(load_default=0.0)
    health_on_kill = fields.Float(load_default=0.0)
    mana_on_kill = fields.Float(load_default=0.0)
    ward_on_kill = fields.Float(load_default=0.0)

    # Utility
    movement_speed = fields.Float(load_default=0.0)
    cooldown_recovery_speed = fields.Float(load_default=0.0)
    channelling_cost_reduction = fields.Float(load_default=0.0)
    area_pct = fields.Float(load_default=0.0)
    stun_duration_pct = fields.Float(load_default=0.0)

    # Attributes
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
    passive_tree = fields.List(fields.Str(), load_default=[])

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
    seed = fields.Int(load_default=None, allow_none=True)


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
    passive_tree = fields.List(fields.Str(), load_default=[])
    skill_name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    skill_level = fields.Int(
        validate=validate.Range(min=1, max=40), load_default=20
    )
    n_simulations = fields.Int(
        validate=validate.Range(min=100, max=50_000), load_default=5_000
    )
    seed = fields.Int(load_default=None, allow_none=True)

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
