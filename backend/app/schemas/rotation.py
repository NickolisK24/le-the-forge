"""
Marshmallow schemas for the /api/simulate/rotation endpoint.
"""

from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE

from app.schemas.simulate import (
    VALID_TEMPLATES,
    VALID_DISTRIBUTIONS,
    EncounterOverrideSchema,
)


class SkillDefinitionSchema(Schema):
    """Inline skill definition sent with the rotation request."""
    skill_id      = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    base_damage   = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    cast_time     = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    cooldown      = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    resource_cost = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    tags          = fields.List(fields.Str(), load_default=[])


class RotationStepSchema(Schema):
    skill_id         = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    delay_after_cast = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    priority         = fields.Int(load_default=0)
    repeat_count     = fields.Int(load_default=1, validate=validate.Range(min=1, max=100))


class RotationDefinitionSchema(Schema):
    rotation_id = fields.Str(load_default="custom")
    steps       = fields.List(fields.Nested(RotationStepSchema), required=True,
                              validate=validate.Length(min=1, max=50))
    loop        = fields.Bool(load_default=True)


class SimulateRotationSchema(Schema):
    """POST /api/simulate/rotation"""
    rotation  = fields.Nested(RotationDefinitionSchema, required=True)
    skills    = fields.List(fields.Nested(SkillDefinitionSchema), required=True,
                            validate=validate.Length(min=1, max=50))
    duration  = fields.Float(load_default=60.0, validate=validate.Range(min=1.0, max=3600.0))
    gcd       = fields.Float(load_default=0.0,  validate=validate.Range(min=0.0, max=10.0))
    encounter = fields.Nested(EncounterOverrideSchema, load_default=None, allow_none=True)
