# Data Models

All SQLAlchemy models are defined in `backend/app/models/__init__.py`.

---

## User

```python
class User(db.Model):
    __tablename__ = "users"

    id            = String(36), primary_key, default=uuid4
    discord_id    = String(50), unique, nullable=False
    username      = String(100), nullable=False
    discriminator = String(10), nullable=True
    avatar_url    = String(500), nullable=True
    is_active     = Boolean, default=True
    is_admin      = Boolean, default=False
    created_at    = DateTime(timezone=True), default=utcnow

    # Relationships
    builds        = relationship("Build", backref="author")
    votes         = relationship("Vote", backref="user")
```

Represents a Discord-authenticated user. Created/updated during OAuth2 callback.

---

## Build

```python
class Build(db.Model):
    __tablename__ = "builds"

    id                = String(36), primary_key, default=uuid4
    slug              = String(50), unique, nullable=False
    name              = String(200), nullable=False
    description       = Text, nullable=True
    character_class   = String(50), nullable=False
    mastery           = String(50), nullable=True
    level             = Integer, default=1
    patch_version     = String(20), nullable=True
    cycle             = String(100), nullable=True
    passive_tree      = JSON, default=[]          # Ordered list of node IDs (allocation history)
    gear              = JSON, default=[]          # List of gear slot objects
    is_ssf            = Boolean, default=False
    is_hc             = Boolean, default=False
    is_ladder_viable  = Boolean, default=False
    is_budget         = Boolean, default=False
    is_public         = Boolean, default=True
    vote_count        = Integer, default=0
    view_count        = Integer, default=0
    tier              = String(1), default="C"    # S, A, B, or C (computed from votes)
    author_id         = String(36), ForeignKey("users.id"), nullable=True
    last_viewed_at    = DateTime(timezone=True), nullable=True
    created_at        = DateTime(timezone=True), default=utcnow
    updated_at        = DateTime(timezone=True), default=utcnow, onupdate=utcnow

    # Relationships
    skills            = relationship("BuildSkill", backref="build", cascade="all, delete-orphan")
    votes_rel         = relationship("Vote", backref="build", cascade="all, delete-orphan")
    views             = relationship("BuildView", backref="build")
```

Central model representing a character build. `passive_tree` stores allocation history in order (append on allocate, remove last occurrence on deallocate). `gear` stores a JSON array of slot objects with item name, rarity, and affixes. Tier is automatically recalculated on vote changes.

---

## BuildSkill

```python
class BuildSkill(db.Model):
    __tablename__ = "build_skills"

    id                = String(36), primary_key, default=uuid4
    build_id          = String(36), ForeignKey("builds.id"), nullable=False
    slot              = Integer, nullable=False         # 0-4 (max 5 skills per build)
    skill_name        = String(100), nullable=False
    points_allocated  = Integer, default=0
    spec_tree         = JSON, default=[]               # Spec tree node allocations
```

One of up to 5 skill slots per build. `spec_tree` stores specialization node allocations parsed by the skill tree resolver into build stat bonuses and skill modifiers.

---

## Vote

```python
class Vote(db.Model):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("user_id", "build_id"),)

    id        = String(36), primary_key, default=uuid4
    user_id   = String(36), ForeignKey("users.id"), nullable=False
    build_id  = String(36), ForeignKey("builds.id"), nullable=False
    direction = Integer, nullable=False    # +1 (upvote) or -1 (downvote)
```

Unique per user+build pair. Sending the same direction again toggles the vote off. Vote count and tier are recalculated on the Build after each vote change.

---

## CraftSession

```python
class CraftSession(db.Model):
    __tablename__ = "craft_sessions"

    id               = String(36), primary_key, default=uuid4
    slug             = String(50), unique, nullable=False
    user_id          = String(36), ForeignKey("users.id"), nullable=True
    item_type        = String(50), nullable=False
    item_name        = String(200), nullable=True
    item_level       = Integer, default=1
    rarity           = String(20), default="Rare"
    forge_potential   = Integer, default=0
    affixes          = JSON, default=[]          # Current affix state
    created_at       = DateTime(timezone=True), default=utcnow

    # Relationships
    steps            = relationship("CraftStep", backref="session", cascade="all, delete-orphan", order_by="CraftStep.step_number")
```

A saved crafting simulation session. Affixes are mutable JSON updated on each craft action. The full history is preserved in CraftStep records.

---

## CraftStep

```python
class CraftStep(db.Model):
    __tablename__ = "craft_steps"

    id             = String(36), primary_key, default=uuid4
    session_id     = String(36), ForeignKey("craft_sessions.id"), nullable=False
    step_number    = Integer, nullable=False
    timestamp      = DateTime(timezone=True), default=utcnow
    action         = String(30), nullable=False        # add_affix, upgrade_affix, seal_affix, unseal_affix, remove_affix
    affix_name     = String(200), nullable=True
    tier_before    = Integer, nullable=True
    tier_after     = Integer, nullable=True
    roll           = Integer, nullable=True
    outcome        = String(20), nullable=False        # success, perfect, fracture, error
    fp_before      = Integer, nullable=False
    fp_after       = Integer, nullable=False
    affixes_before = JSON, nullable=True               # Snapshot for undo support
```

Immutable audit log entry for each craft action. Ordered by step_number within a session. `affixes_before` stores the pre-action state for undo support.

---

## ItemType

```python
class ItemType(db.Model):
    __tablename__ = "item_types"

    id            = String(36), primary_key, default=uuid4
    name          = String(100), unique, nullable=False
    category      = String(50), nullable=False          # weapon, armour, accessory, off_hand
    base_implicit = String(200), nullable=True
```

Reference model for item types. Populated by `flask seed` from static data.

---

## AffixDef

```python
class AffixDef(db.Model):
    __tablename__ = "affix_defs"

    id               = String(36), primary_key, default=uuid4
    name             = String(200), nullable=False
    affix_type       = String(50), nullable=False       # prefix, suffix, idol, experimental, personal, etc.
    stat_key         = String(100), nullable=True
    tier_ranges      = JSON, default={}                 # {"1": [lo, hi], "2": [lo, hi], ...}
    applicable_types = JSON, default=[]                 # List of item types this affix can roll on
    class_requirement = String(50), nullable=True
    tags             = JSON, default=[]
```

Reference model for affix definitions. Populated by `flask seed` and `flask reseed-affixes` from `data/items/affixes.json`.

---

## PassiveNode

```python
class PassiveNode(db.Model):
    __tablename__ = "passive_nodes"

    id              = String(36), primary_key, default=uuid4
    raw_node_id     = String(50), nullable=False
    character_class = String(50), nullable=False
    mastery         = String(50), nullable=True          # null = base class tree
    node_type       = String(30), nullable=False         # core, notable, keystone, mastery_gate
    name            = String(200), nullable=True
    description     = Text, nullable=True
    x               = Float, nullable=True               # Real game x coordinate
    y               = Float, nullable=True               # Real game y coordinate
    connections     = JSON, default=[]                   # List of connected node raw_node_ids
    stats           = JSON, default={}                   # Stat bonuses {"stat_key": value}
    max_points      = Integer, default=1
    ability_granted = String(200), nullable=True
    icon            = String(50), nullable=True
```

Reference model for passive tree nodes. Populated by `flask seed-passives` from `data/classes/passives.json`. Uses real in-game coordinates from exported layout data.

---

## ImportFailure

```python
class ImportFailure(db.Model):
    __tablename__ = "import_failures"

    id             = String(36), primary_key, default=uuid4
    source         = String(50), nullable=False          # "lastepochtools" or "maxroll"
    raw_url        = String(500), nullable=False
    missing_fields = JSON, default=[]
    partial_data   = JSON, nullable=True
    error_message  = String(500), nullable=True
    user_id        = String(36), ForeignKey("users.id"), nullable=True
    created_at     = DateTime(timezone=True), default=utcnow
```

Tracks import failures for admin monitoring. Discord webhook alerts are sent for hard failures.

---

## BuildView

```python
class BuildView(db.Model):
    __tablename__ = "build_views"

    id             = String(36), primary_key, default=uuid4
    build_id       = String(36), ForeignKey("builds.id"), nullable=False, index=True
    viewed_at      = DateTime(timezone=True), default=utcnow, nullable=False
    viewer_ip_hash = String(64), nullable=False          # SHA-256 hash, never raw IP
```

Time-series view tracking. IP addresses are always stored as SHA-256 hashes -- raw IPs are never persisted. Rate limited to 1 view per IP per build per hour via Redis.

---

## Relationships Summary

```
User --< Build --< BuildSkill
  |        |--< Vote
  |        |--< BuildView
  |
  |--< Vote
  |--< CraftSession --< CraftStep
  |--< ImportFailure
```
