"""
Marshmallow schemas for Phase 7 — Advanced Analysis endpoints.
"""

from marshmallow import Schema, fields, validate


# ---------------------------------------------------------------------------
# Boss Encounter Analysis
# ---------------------------------------------------------------------------

class BossPhaseResultSchema(Schema):
    phase = fields.Int()
    health_threshold = fields.Float()
    dps = fields.Int()
    ttk_seconds = fields.Float()
    survival_score = fields.Int()
    mana_sustainable = fields.Bool()
    warnings = fields.List(fields.Str())


class BossSummarySchema(Schema):
    total_ttk_seconds = fields.Float()
    can_kill_before_enrage = fields.Bool()
    overall_survival_score = fields.Int()
    weakest_phase = fields.Int()


class BossAnalysisResponseSchema(Schema):
    boss_id = fields.Str()
    boss_name = fields.Str()
    corruption = fields.Int()
    phases = fields.List(fields.Nested(BossPhaseResultSchema))
    summary = fields.Nested(BossSummarySchema)
    warnings = fields.List(fields.Str())


# ---------------------------------------------------------------------------
# Corruption Scaling
# ---------------------------------------------------------------------------

class CorruptionDataPointSchema(Schema):
    corruption = fields.Int()
    dps_efficiency = fields.Float()
    survivability_score = fields.Int()


class CorruptionAnalysisResponseSchema(Schema):
    boss_id = fields.Str()
    recommended_max_corruption = fields.Int()
    curve = fields.List(fields.Nested(CorruptionDataPointSchema))


# ---------------------------------------------------------------------------
# Gear Upgrade Ranking
# ---------------------------------------------------------------------------

class GearUpgradeCandidateSchema(Schema):
    item_name = fields.Str()
    base_type = fields.Str()
    slot = fields.Str()
    affixes = fields.List(fields.Dict())
    dps_delta_pct = fields.Float()
    ehp_delta_pct = fields.Float()
    fp_cost = fields.Int()
    efficiency_score = fields.Float()
    rank = fields.Int()


class SlotUpgradeResultSchema(Schema):
    slot = fields.Str()
    candidates = fields.List(fields.Nested(GearUpgradeCandidateSchema))


class GearUpgradeResponseSchema(Schema):
    slots = fields.List(fields.Nested(SlotUpgradeResultSchema))
    top_10_overall = fields.List(fields.Nested(GearUpgradeCandidateSchema))
