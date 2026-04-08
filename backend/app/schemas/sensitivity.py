"""
Marshmallow schemas for the Phase 4 optimization endpoints.

Covers:
  - GET /api/builds/<slug>/optimize  (response)
"""

from marshmallow import Schema, fields, validate


VALID_OPTIMIZE_MODES = ("balanced", "offense", "defense")


class StatRankingSchema(Schema):
    """A single stat ranking entry from sensitivity analysis."""
    stat_key = fields.Str(dump_only=True)
    label = fields.Str(dump_only=True)
    dps_gain_pct = fields.Float(dump_only=True)
    ehp_gain_pct = fields.Float(dump_only=True)
    impact_score = fields.Float(dump_only=True)
    rank = fields.Int(dump_only=True)


class UpgradeCandidateSchema(Schema):
    """A single affix upgrade candidate with efficiency scoring."""
    affix_id = fields.Str(dump_only=True)
    label = fields.Str(dump_only=True)
    dps_gain_pct = fields.Float(dump_only=True)
    ehp_gain_pct = fields.Float(dump_only=True)
    fp_cost = fields.Int(dump_only=True)
    efficiency_score = fields.Float(dump_only=True)
    rank = fields.Int(dump_only=True)


class BuildOptimizeResponseSchema(Schema):
    """Response schema for GET /api/builds/<slug>/optimize."""
    stat_rankings = fields.List(fields.Nested(StatRankingSchema), dump_only=True)
    top_upgrade_candidates = fields.List(fields.Nested(UpgradeCandidateSchema), dump_only=True)
    mode = fields.Str(dump_only=True)
    offense_weight = fields.Float(dump_only=True)
    defense_weight = fields.Float(dump_only=True)
    base_dps = fields.Float(dump_only=True)
    base_ehp = fields.Float(dump_only=True)
    generated_at = fields.Str(dump_only=True)
