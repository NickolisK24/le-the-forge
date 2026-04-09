"""
Marshmallow schemas for the /api/skills endpoints.

Covers:
  - GET /api/skills/{skill_id}/tree  (response)
  - GET /api/builds/{slug}/skills    (response)
  - PATCH /api/builds/{slug}/skills/{skill_id}/nodes/{node_id}  (request + response)
"""

from marshmallow import Schema, fields, validate


class SkillNodeStatSchema(Schema):
    """A single stat granted by a skill tree node."""
    statName = fields.Str(dump_only=True)
    value = fields.Str(dump_only=True)
    noScaling = fields.Bool(dump_only=True)
    downside = fields.Bool(dump_only=True)


class SkillNodeRequirementSchema(Schema):
    """Prerequisite to unlock a skill tree node."""
    node = fields.Int(dump_only=True)
    requirement = fields.Int(dump_only=True)


class SkillNodeTransformSchema(Schema):
    """Position and scale of a node."""
    x = fields.Float(dump_only=True)
    y = fields.Float(dump_only=True)
    scale = fields.Float(dump_only=True, load_default=1.0)
    rotation = fields.Float(dump_only=True, load_default=0.0)


class SkillNodeSchema(Schema):
    """A single node in a skill tree."""
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    maxPoints = fields.Int(dump_only=True)
    stats = fields.List(fields.Nested(SkillNodeStatSchema), dump_only=True)
    requirements = fields.List(fields.Nested(SkillNodeRequirementSchema), dump_only=True)
    transform = fields.Nested(SkillNodeTransformSchema, dump_only=True)
    icon = fields.Raw(dump_only=True, allow_none=True)
    abilityGrantedByNode = fields.Str(dump_only=True, allow_none=True)


class SkillTreeResponseSchema(Schema):
    """Response for GET /api/skills/{skill_id}/tree."""
    skill_id = fields.Str(dump_only=True)
    skill_name = fields.Str(dump_only=True)
    nodes = fields.List(fields.Nested(SkillNodeSchema), dump_only=True)
    root_node_id = fields.Int(dump_only=True)


class SkillAllocationSchema(Schema):
    """Allocation state for a single skill on a build."""
    skill_id = fields.Str(dump_only=True)
    skill_name = fields.Str(dump_only=True)
    slot = fields.Int(dump_only=True)
    allocated_nodes = fields.Dict(
        keys=fields.Str(),
        values=fields.Int(),
        dump_only=True,
    )
    total_points = fields.Int(dump_only=True)


class SkillAllocationsResponseSchema(Schema):
    """Response for GET /api/builds/{slug}/skills."""
    skills = fields.List(fields.Nested(SkillAllocationSchema), dump_only=True)


class NodeAllocateRequestSchema(Schema):
    """Request body for PATCH /api/builds/{slug}/skills/{skill_id}/nodes/{node_id}."""
    points = fields.Int(
        required=True,
        validate=validate.Range(min=0, max=20),
    )
