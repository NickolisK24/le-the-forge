"""
Marshmallow schemas for Community Tools — comparison, meta, and report responses.
"""

from marshmallow import Schema, fields


# ---------------------------------------------------------------------------
# Build Comparison
# ---------------------------------------------------------------------------

class DPSComparisonSchema(Schema):
    raw_dps_a = fields.Float(dump_only=True)
    raw_dps_b = fields.Float(dump_only=True)
    crit_contribution_a = fields.Float(dump_only=True)
    crit_contribution_b = fields.Float(dump_only=True)
    ailment_dps_a = fields.Float(dump_only=True)
    ailment_dps_b = fields.Float(dump_only=True)
    total_dps_a = fields.Float(dump_only=True)
    total_dps_b = fields.Float(dump_only=True)
    winner = fields.Str(dump_only=True)


class EHPComparisonSchema(Schema):
    max_health_a = fields.Float(dump_only=True)
    max_health_b = fields.Float(dump_only=True)
    effective_hp_a = fields.Float(dump_only=True)
    effective_hp_b = fields.Float(dump_only=True)
    armor_reduction_pct_a = fields.Float(dump_only=True)
    armor_reduction_pct_b = fields.Float(dump_only=True)
    avg_resistance_a = fields.Float(dump_only=True)
    avg_resistance_b = fields.Float(dump_only=True)
    survivability_score_a = fields.Float(dump_only=True)
    survivability_score_b = fields.Float(dump_only=True)
    winner = fields.Str(dump_only=True)


class StatDeltaSchema(Schema):
    stat_key = fields.Str(dump_only=True)
    value_a = fields.Float(dump_only=True)
    value_b = fields.Float(dump_only=True)
    delta = fields.Float(dump_only=True)


class GearSlotComparisonSchema(Schema):
    slot = fields.Str(dump_only=True)
    item_a = fields.Str(dump_only=True, allow_none=True)
    rarity_a = fields.Str(dump_only=True, allow_none=True)
    item_b = fields.Str(dump_only=True, allow_none=True)
    rarity_b = fields.Str(dump_only=True, allow_none=True)


class SkillComparisonSchema(Schema):
    skills_a = fields.List(fields.Dict(), dump_only=True)
    skills_b = fields.List(fields.Dict(), dump_only=True)
    shared = fields.List(fields.Str(), dump_only=True)
    unique_to_a = fields.List(fields.Str(), dump_only=True)
    unique_to_b = fields.List(fields.Str(), dump_only=True)


class ComparisonResultSchema(Schema):
    slug_a = fields.Str(dump_only=True)
    slug_b = fields.Str(dump_only=True)
    name_a = fields.Str(dump_only=True)
    name_b = fields.Str(dump_only=True)
    dps = fields.Nested(DPSComparisonSchema, dump_only=True)
    ehp = fields.Nested(EHPComparisonSchema, dump_only=True)
    stat_deltas = fields.List(fields.Nested(StatDeltaSchema), dump_only=True)
    overall_winner = fields.Str(dump_only=True)
    overall_score_a = fields.Float(dump_only=True)
    overall_score_b = fields.Float(dump_only=True)
    skill_comparison = fields.Nested(SkillComparisonSchema, dump_only=True)
    gear_comparison = fields.List(fields.Nested(GearSlotComparisonSchema), dump_only=True)


# ---------------------------------------------------------------------------
# Meta Analytics
# ---------------------------------------------------------------------------

class ClassDistributionSchema(Schema):
    class_ = fields.Str(data_key="class", dump_only=True)
    count = fields.Int(dump_only=True)
    percentage = fields.Float(dump_only=True)


class PopularSkillSchema(Schema):
    skill_name = fields.Str(dump_only=True)
    usage_count = fields.Int(dump_only=True)


class PopularAffixSchema(Schema):
    affix_name = fields.Str(dump_only=True)
    usage_count = fields.Int(dump_only=True)


class TrendingBuildSchema(Schema):
    id = fields.Str(dump_only=True)
    slug = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    character_class = fields.Str(dump_only=True)
    mastery = fields.Str(dump_only=True)
    tier = fields.Str(dump_only=True, allow_none=True)
    vote_count = fields.Int(dump_only=True)
    view_count = fields.Int(dump_only=True)
    trending_score = fields.Float(dump_only=True)
    author = fields.Str(dump_only=True, allow_none=True)


class MetaSnapshotSchema(Schema):
    class_distribution = fields.List(fields.Dict(), dump_only=True)
    mastery_distribution = fields.Dict(dump_only=True)
    popular_skills = fields.List(fields.Nested(PopularSkillSchema), dump_only=True)
    popular_affixes = fields.List(fields.Nested(PopularAffixSchema), dump_only=True)
    average_stats_by_class = fields.List(fields.Dict(), dump_only=True)
    patch_breakdown = fields.List(fields.Dict(), dump_only=True)
    last_updated = fields.Str(dump_only=True)
    current_patch = fields.Str(dump_only=True)


# ---------------------------------------------------------------------------
# Build Report
# ---------------------------------------------------------------------------

class BuildReportSchema(Schema):
    identity = fields.Dict(dump_only=True)
    stat_summary = fields.Dict(dump_only=True)
    dps_summary = fields.Dict(dump_only=True)
    ehp_summary = fields.Dict(dump_only=True)
    top_upgrades = fields.List(fields.Dict(), dump_only=True)
    skills = fields.List(fields.Dict(), dump_only=True)
    gear = fields.List(fields.Dict(), dump_only=True)
    generated_at = fields.Str(dump_only=True)
    og_title = fields.Str(dump_only=True)
    og_description = fields.Str(dump_only=True)
    og_url = fields.Str(dump_only=True)
