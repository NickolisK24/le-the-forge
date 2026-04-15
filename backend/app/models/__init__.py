"""
SQLAlchemy ORM models for The Forge.

All models inherit from a shared Base that adds:
  - id (UUID primary key)
  - created_at / updated_at timestamps

Relationships summary:
  User         ──< Build        (one user → many builds)
  User         ──< Vote         (one user → many votes; unique per build)
  Build        ──< Vote         (one build → many votes)
  Build        ──< BuildSkill   (one build → up to 5 skill entries)
  CraftSession ──< CraftStep    (one session → ordered craft log)

Reference tables (seeded, not user-created):
  ItemType, AffixDef, PassiveNode, SkillDef
"""

import uuid
from datetime import datetime, timezone

from app import db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------

class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    discord_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), nullable=False)
    discriminator = db.Column(db.String(8), nullable=True)  # legacy Discord tags
    avatar_url = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    builds = db.relationship("Build", back_populates="author", lazy="dynamic")
    votes = db.relationship("Vote", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

class Build(TimestampMixin, db.Model):
    __tablename__ = "builds"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    author_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True, index=True)
    slug = db.Column(db.String(64), unique=True, nullable=False, index=True)

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Character
    character_class = db.Column(db.String(32), nullable=False)  # Acolyte, Mage, etc.
    mastery = db.Column(db.String(32), nullable=False)
    level = db.Column(db.SmallInteger, default=100, nullable=False)

    # Tree — stored as a compact JSON array of allocated node IDs
    # e.g. [42, 117, 203, ...]
    passive_tree = db.Column(db.JSON, nullable=False, default=list)

    # Gear — JSON array of { slot, item_name, rarity, affixes: [...] }
    gear = db.Column(db.JSON, nullable=False, default=list)

    # Monolith blessings — JSON array of selected blessings (max 10, one per timeline).
    # Each entry: { timeline_id, blessing_id, is_grand, value }
    blessings = db.Column(db.JSON, nullable=False, default=list)

    # Meta tags
    is_ssf = db.Column(db.Boolean, default=False, nullable=False)
    is_hc = db.Column(db.Boolean, default=False, nullable=False)
    is_ladder_viable = db.Column(db.Boolean, default=True, nullable=False)
    is_budget = db.Column(db.Boolean, default=False, nullable=False)

    patch_version = db.Column(db.String(16), nullable=False, default="1.2.1")
    cycle = db.Column(db.String(16), nullable=False, default="1.2")

    # Community tier: S / A / B / C — set by votes or moderators
    tier = db.Column(db.String(1), nullable=True)

    # Cached vote total — updated on each vote for fast reads
    vote_count = db.Column(db.Integer, default=0, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    last_viewed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    is_public = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    author = db.relationship("User", back_populates="builds")
    skills = db.relationship(
        "BuildSkill", back_populates="build", cascade="all, delete-orphan",
        order_by="BuildSkill.slot"
    )
    votes = db.relationship("Vote", back_populates="build", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Build {self.name} [{self.character_class}/{self.mastery}]>"

    def recalculate_tier(self):
        """Derive tier from vote_count. Called after vote mutations."""
        if self.vote_count >= 2000:
            self.tier = "S"
        elif self.vote_count >= 1000:
            self.tier = "A"
        elif self.vote_count >= 400:
            self.tier = "B"
        else:
            self.tier = "C"


class BuildSkill(db.Model):
    """One of the 5 specialized skill slots on a build."""
    __tablename__ = "build_skills"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    build_id = db.Column(db.String(36), db.ForeignKey("builds.id"), nullable=False)
    slot = db.Column(db.SmallInteger, nullable=False)  # 0-4

    skill_name = db.Column(db.String(64), nullable=False)
    points_allocated = db.Column(db.SmallInteger, default=0, nullable=False)

    # Specialization tree — JSON array of allocated node IDs within this skill
    spec_tree = db.Column(db.JSON, nullable=False, default=list)

    build = db.relationship("Build", back_populates="skills")

    __table_args__ = (
        db.UniqueConstraint("build_id", "slot", name="uq_build_skill_slot"),
    )


# ---------------------------------------------------------------------------
# Vote
# ---------------------------------------------------------------------------

class Vote(TimestampMixin, db.Model):
    __tablename__ = "votes"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    build_id = db.Column(db.String(36), db.ForeignKey("builds.id"), nullable=False, index=True)
    direction = db.Column(db.SmallInteger, nullable=False)  # +1 or -1

    user = db.relationship("User", back_populates="votes")
    build = db.relationship("Build", back_populates="votes")

    __table_args__ = (
        db.UniqueConstraint("user_id", "build_id", name="uq_user_build_vote"),
    )


# ---------------------------------------------------------------------------
# Craft Session
# ---------------------------------------------------------------------------

class CraftSession(TimestampMixin, db.Model):
    """
    A saved craft simulation. Users can save, share, and resume sessions.
    All the math lives in the service layer — this is pure persistence.
    """
    __tablename__ = "craft_sessions"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True, index=True)
    slug = db.Column(db.String(64), unique=True, nullable=False, index=True)

    item_type = db.Column(db.String(32), nullable=False)
    item_name = db.Column(db.String(120), nullable=True)
    item_level = db.Column(db.SmallInteger, nullable=False, default=84)
    rarity = db.Column(db.String(16), nullable=False, default="Exalted")

    # Forge potential remaining
    forge_potential = db.Column(db.SmallInteger, default=28, nullable=False)

    # Current affixes — JSON array of { name, tier, sealed }
    affixes = db.Column(db.JSON, nullable=False, default=list)

    steps = db.relationship(
        "CraftStep", back_populates="session", cascade="all, delete-orphan",
        order_by="CraftStep.step_number"
    )

    def __repr__(self):
        return f"<CraftSession {self.item_name or self.item_type} fp={self.forge_potential}>"


class CraftStep(db.Model):
    """Immutable log of a single forge action within a session."""
    __tablename__ = "craft_steps"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    session_id = db.Column(
        db.String(36), db.ForeignKey("craft_sessions.id"), nullable=False, index=True
    )
    step_number = db.Column(db.SmallInteger, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    action = db.Column(db.String(32), nullable=False)
    # e.g. "add_affix", "upgrade_affix", "seal_affix", "unseal_affix"

    affix_name = db.Column(db.String(64), nullable=True)
    tier_before = db.Column(db.SmallInteger, nullable=True)
    tier_after = db.Column(db.SmallInteger, nullable=True)

    roll = db.Column(db.Float, nullable=True)  # The actual RNG roll (0-100)
    outcome = db.Column(db.String(16), nullable=False)
    # "success" | "perfect"

    fp_before = db.Column(db.SmallInteger, nullable=False)
    fp_after = db.Column(db.SmallInteger, nullable=False)

    # Affixes state before this action (for undo)
    affixes_before = db.Column(db.JSON, nullable=True)

    session = db.relationship("CraftSession", back_populates="steps")


# ---------------------------------------------------------------------------
# Reference tables (seeded from game data)
# ---------------------------------------------------------------------------

class ItemType(db.Model):
    """Base item types. Seeded from game data."""
    __tablename__ = "item_types"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    category = db.Column(db.String(32), nullable=False)
    # "weapon" | "armour" | "accessory" | "off_hand"
    base_implicit = db.Column(db.String(120), nullable=True)


class AffixDef(db.Model):
    """Known affix definitions. Seeded from game data."""
    __tablename__ = "affix_defs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    # "prefix"|"suffix"|"experimental"|"personal"|"champion"|"set"|"idol_enchant"|"idol_weaver"
    affix_type = db.Column(db.String(16), nullable=False)
    stat_key = db.Column(db.String(256), nullable=False)

    # Min/max values per tier (T1..T7), stored as JSON
    # e.g. {"1": [5, 9], "2": [10, 15], ...}
    tier_ranges = db.Column(db.JSON, nullable=False, default=dict)

    # Which item types can roll this affix
    applicable_types = db.Column(db.JSON, nullable=False, default=list)

    # Class restriction (null = any class; comma-separated for multi-class)
    class_requirement = db.Column(db.String(128), nullable=True)

    # Searchable tags
    tags = db.Column(db.JSON, nullable=False, default=list)


class PassiveNode(db.Model):
    """Passive tree node definition. Seeded from LE game data."""
    __tablename__ = "passive_nodes"

    id = db.Column(db.String(16), primary_key=True)  # namespaced: e.g. "ac_0"
    raw_node_id = db.Column(db.Integer, nullable=False)  # original in-game integer id
    character_class = db.Column(db.String(32), nullable=False)
    mastery = db.Column(db.String(32), nullable=True)   # null = base class tree
    mastery_index = db.Column(db.SmallInteger, nullable=False, default=0)
    mastery_requirement = db.Column(db.SmallInteger, nullable=False, default=0)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    node_type = db.Column(db.String(16), nullable=False)
    # "core" | "notable" | "keystone" | "mastery_gate"
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    max_points = db.Column(db.SmallInteger, default=1, nullable=False)

    # Connected node IDs (namespaced strings, e.g. ["ac_1", "ac_5"])
    connections = db.Column(db.JSON, nullable=False, default=list)

    # Stat effects as a JSON array of {key, value} dicts
    stats = db.Column(db.JSON, nullable=True, default=list)

    # Ability or skill unlocked by allocating this node (nullable)
    ability_granted = db.Column(db.String(128), nullable=True)

    # Icon sprite identifier (e.g. "a-r-42")
    icon = db.Column(db.String(32), nullable=True)


# ---------------------------------------------------------------------------
# Import Failure Tracking
# ---------------------------------------------------------------------------

class ImportFailure(TimestampMixin, db.Model):
    """Tracks failed or partial build imports for debugging and monitoring."""
    __tablename__ = "import_failures"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    source = db.Column(db.String(32), nullable=False)  # "lastepochtools" | "maxroll"
    raw_url = db.Column(db.String(2048), nullable=False)
    missing_fields = db.Column(db.JSON, nullable=False, default=list)
    partial_data = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    error_message = db.Column(db.String(1024), nullable=True)

    user = db.relationship("User", backref="import_failures")

    def __repr__(self):
        return f"<ImportFailure {self.source} {self.error_message or 'partial'}>"


# ---------------------------------------------------------------------------
# Build View Tracking (time-series)
# ---------------------------------------------------------------------------

class BuildView(db.Model):
    """Individual view record for time-series analytics."""
    __tablename__ = "build_views"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    build_id = db.Column(db.String(36), db.ForeignKey("builds.id"), nullable=False, index=True)
    viewed_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)
    viewer_ip_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash, never raw IP

    build = db.relationship("Build", backref="views")