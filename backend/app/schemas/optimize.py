"""
Marshmallow schemas for the /api/optimize endpoints.
"""

from marshmallow import Schema, fields, validate, EXCLUDE

from app.schemas.simulate import BuildDefinitionSchema, EncounterOverrideSchema

__all__ = ["OptimizationConfigSchema", "OptimizeBuildSchema"]

VALID_METRICS = ("dps", "total_damage", "ttk", "uptime", "composite")


class OptimizationConfigSchema(Schema):
    """Mirrors OptimizationConfig dataclass."""
    target_metric  = fields.Str(
        load_default="dps",
        validate=validate.OneOf(VALID_METRICS),
    )
    max_variants   = fields.Int(
        load_default=50,
        validate=validate.Range(min=1, max=1000),
    )
    mutation_depth = fields.Int(
        load_default=2,
        validate=validate.Range(min=1, max=10),
    )
    constraints    = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        load_default={},
    )
    random_seed    = fields.Int(load_default=42)


class OptimizeBuildSchema(Schema):
    """POST /api/optimize/build — input schema."""
    build     = fields.Nested(BuildDefinitionSchema, required=True)
    config    = fields.Nested(OptimizationConfigSchema, load_default=None, allow_none=True)
    encounter = fields.Nested(EncounterOverrideSchema,  load_default=None, allow_none=True)
    top_n     = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
