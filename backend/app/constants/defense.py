"""
Defense mechanic constants — Last Epoch formulas.

All values here encode game rules, not display thresholds.
Update when LE patches change caps or formula divisors.
"""

# Resistance cap — all elemental, physical, and poison resist capped at 75%
RES_CAP: int = 75

# Ward decay: base coefficient in the ward decay formula
# Ward_Lost/sec = WARD_BASE_DECAY_RATE × (CurrentWard - Threshold) / (1 + 0.5 × WardRetention)
WARD_BASE_DECAY_RATE: float = 0.4

# Intelligence grants ward retention at this rate (4% per point)
INTELLIGENCE_WARD_RETENTION_PER_POINT: float = 4.0

# Endurance stat hard cap (maximum 60% damage reduction)
ENDURANCE_CAP: int = 60

# Default endurance values (before any gear/passives)
ENDURANCE_DEFAULT_DR: float = 20.0         # default damage reduction %
ENDURANCE_DEFAULT_THRESHOLD: float = 20.0  # default HP threshold %

# Armor formula: DR% = Armor / (Armor + ARMOR_AREA_LEVEL_FACTOR × AreaLevel)
# Cap: 85% for physical, non-physical at 70% effectiveness
# VERIFIED: 1.4.3 spec §3.1 — armor is 70% effective vs non-physical hit damage
ARMOR_AREA_LEVEL_FACTOR: float = 10.0
ARMOR_MITIGATION_CAP: float = 0.85
ARMOR_NON_PHYSICAL_EFFECTIVENESS: float = 0.70  # armor is 70% effective vs non-physical

# Dodge formula: Dodge% = DodgeRating / (DodgeRating + DODGE_AREA_LEVEL_FACTOR × AreaLevel)
# Cap: 85%
DODGE_AREA_LEVEL_FACTOR: float = 10.0
DODGE_CAP: float = 0.85

# Dexterity grants dodge rating at this rate (4 per point)
DEXTERITY_DODGE_RATING_PER_POINT: float = 4.0

# Legacy divisor constants — used by defense_engine.py for stat/(stat+DIVISOR) curves
# where area_level is not available. ARMOR_DIVISOR = 10 × 100 (area_level=100 default).
ARMOR_DIVISOR: int = 1000
DODGE_DIVISOR: int = 1000
BLOCK_DIVISOR: int = 1000
STUN_AVOIDANCE_DIVISOR: int = 1000

# Default area level for formulas when not explicitly provided
DEFAULT_AREA_LEVEL: int = 100

# Enemy baseline model used for EHP projections
ENEMY_CRIT_RATE: float = 0.35        # fraction of enemy hits that are crits
ENEMY_CRIT_MULTIPLIER: float = 1.5   # damage multiplier applied to enemy crits
