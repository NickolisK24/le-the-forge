"""
Marshmallow schemas for request validation and response serialization.

Convention:
  - <Model>Schema     → full representation (reads)
  - <Model>CreateSchema → input validation for POST
  - <Model>UpdateSchema → input validation for PATCH (all fields optional)
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, post_dump, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app import db
from app.models import (
    User, Build, BuildSkill, Vote,
    CraftSession, CraftStep,
)
from app.constants import BASE_CLASSES, CLASS_MASTERIES, ITEM_RARITIES

# ---------------------------------------------------------------------------
# Shared validators
# ---------------------------------------------------------------------------

VALID_CLASSES = BASE_CLASSES
VALID_MASTERIES = CLASS_MASTERIES
VALID_TIERS = ["S", "A", "B", "C"]
VALID_RARITIES = [r for r in ITEM_RARITIES if r != "Legendary"]  # crafting only


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        exclude = ("builds", "votes")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

class BuildSkillSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BuildSkill
        load_instance = True
        sqla_session = db.session
        exclude = ("build",)


class BuildSchema(SQLAlchemyAutoSchema):
    author = fields.Nested(UserSchema, only=("id", "username", "avatar_url"), dump_only=True)
    skills = fields.List(fields.Nested(BuildSkillSchema), dump_only=True)
    user_vote = fields.Integer(dump_only=True)  # populated by service

    class Meta:
        model = Build
        load_instance = True
        sqla_session = db.session
        exclude = ("votes",)

    @post_dump
    def _normalize_blessings(self, data, **kwargs):
        """Coerce a null blessings column to an empty list for API consumers."""
        if data.get("blessings") is None:
            data["blessings"] = []
        return data


class BuildCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    description = fields.Str(validate=validate.Length(max=2000), load_default=None)
    character_class = fields.Str(
        required=True, validate=validate.OneOf(VALID_CLASSES)
    )
    mastery = fields.Str(required=True)
    level = fields.Int(validate=validate.Range(min=1, max=100), load_default=100)
    # Accept both legacy integer IDs and modern namespaced string IDs (e.g. "ac_0")
    passive_tree = fields.List(fields.Raw(), load_default=[])
    gear = fields.List(fields.Dict(), load_default=[])
    skills = fields.List(fields.Dict(), load_default=[])
    blessings = fields.List(fields.Dict(), load_default=[])
    is_ssf = fields.Bool(load_default=False)
    is_hc = fields.Bool(load_default=False)
    is_ladder_viable = fields.Bool(load_default=True)
    is_budget = fields.Bool(load_default=False)
    patch_version = fields.Str(load_default="1.2.1")
    cycle = fields.Str(load_default="1.2")
    is_public = fields.Bool(load_default=True)

    @validates("mastery")
    def validate_mastery(self, value, **kwargs):
        # Full cross-field validation in the service layer; basic check here
        all_masteries = [m for ms in VALID_MASTERIES.values() for m in ms]
        if value not in all_masteries:
            raise ValidationError(f"Unknown mastery: {value}")

    @post_load
    def check_mastery_class_match(self, data, **kwargs):
        cls = data.get("character_class")
        mastery = data.get("mastery")
        if cls and mastery and mastery not in VALID_MASTERIES.get(cls, []):
            raise ValidationError(
                {
                    "mastery": [
                        f"{mastery} is not a valid mastery for {cls}. "
                        f"Valid options: {', '.join(VALID_MASTERIES[cls])}"
                    ]
                }
            )
        return data


class BuildUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(validate=validate.Length(min=3, max=120))
    description = fields.Str(validate=validate.Length(max=2000))
    level = fields.Int(validate=validate.Range(min=1, max=100))
    passive_tree = fields.List(fields.Raw())
    gear = fields.List(fields.Dict())
    skills = fields.List(fields.Dict())
    blessings = fields.List(fields.Dict())
    is_ssf = fields.Bool()
    is_hc = fields.Bool()
    is_ladder_viable = fields.Bool()
    is_budget = fields.Bool()
    patch_version = fields.Str()
    is_public = fields.Bool()


class BuildListSchema(Schema):
    """Lightweight schema for list endpoints — omits heavy tree/gear blobs."""
    id = fields.Str(dump_only=True)
    slug = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    character_class = fields.Str(dump_only=True)
    mastery = fields.Str(dump_only=True)
    tier = fields.Str(dump_only=True)
    vote_count = fields.Int(dump_only=True)
    is_ssf = fields.Bool(dump_only=True)
    is_hc = fields.Bool(dump_only=True)
    is_ladder_viable = fields.Bool(dump_only=True)
    is_budget = fields.Bool(dump_only=True)
    patch_version = fields.Str(dump_only=True)
    cycle = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    author = fields.Nested(UserSchema, only=("id", "username"), dump_only=True)
    description = fields.Str(dump_only=True)


# ---------------------------------------------------------------------------
# Vote
# ---------------------------------------------------------------------------

class VoteSchema(Schema):
    direction = fields.Int(
        required=True, validate=validate.OneOf([1, -1]),
        metadata={"description": "1 = upvote, -1 = downvote"}
    )


# ---------------------------------------------------------------------------
# Craft Session
# ---------------------------------------------------------------------------

class CraftStepSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CraftStep
        load_instance = True
        sqla_session = db.session
        exclude = ("session",)


class CraftSessionSchema(SQLAlchemyAutoSchema):
    steps = fields.List(fields.Nested(CraftStepSchema), dump_only=True)

    class Meta:
        model = CraftSession
        load_instance = True
        sqla_session = db.session
        exclude = ("user_id",)


class CraftSessionCreateSchema(Schema):
    item_type = fields.Str(required=True, validate=validate.Length(min=2, max=32))
    item_name = fields.Str(validate=validate.Length(max=120), load_default=None)
    item_level = fields.Int(
        validate=validate.Range(min=1, max=100), load_default=84
    )
    rarity = fields.Str(
        validate=validate.OneOf(VALID_RARITIES), load_default="Exalted"
    )
    forge_potential = fields.Int(
        validate=validate.Range(min=0, max=60), load_default=None
    )
    fp_mode = fields.Str(
        validate=validate.OneOf(["random", "manual", "fixed"]), load_default="random"
    )
    manual_fp = fields.Int(
        validate=validate.Range(min=0, max=60), load_default=None
    )
    affixes = fields.List(fields.Dict(), load_default=[])


class CraftActionSchema(Schema):
    """Body for POST /api/craft/:id/action"""
    action = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["add_affix", "upgrade_affix", "seal_affix", "unseal_affix", "remove_affix"]
        )
    )
    affix_name = fields.Str(load_default=None)
    target_tier = fields.Int(validate=validate.Range(min=1, max=5), load_default=None)


class CraftPredictSchema(Schema):
    """Body for POST /api/craft/predict (stateless — no session required)."""
    forge_potential = fields.Int(validate=validate.Range(min=0, max=60), load_default=28)
    affixes = fields.List(fields.Dict(), load_default=[])
    n_simulations = fields.Int(
        validate=validate.Range(min=100, max=50_000), load_default=10_000
    )
    seed = fields.Int(load_default=None, allow_none=True)


class CraftSimulateSchema(Schema):
    """Body for POST /api/craft/simulate — high-fidelity path simulation."""
    forge_potential = fields.Int(validate=validate.Range(min=0, max=60), load_default=28)
    steps = fields.List(fields.Dict(), required=True)
    n_simulations = fields.Int(
        validate=validate.Range(min=100, max=50_000), load_default=1_000
    )
    seed = fields.Int(load_default=None, allow_none=True)


