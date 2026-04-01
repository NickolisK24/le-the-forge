"""
Defense mechanic constants — Last Epoch formulas.

All values here encode game rules, not display thresholds.
Update when LE patches change caps or formula divisors.
"""

# Resistance cap — all elemental, physical, and poison resist capped at 75%
RES_CAP: int = 75

# Ward decay: base fraction of current ward lost per second before retention mods
WARD_BASE_DECAY_RATE: float = 0.25

# Endurance stat hard cap
ENDURANCE_CAP: int = 60

# Diminishing-returns divisors for stat / (stat + DIVISOR) formulas.
# Named separately so a patch to one mechanic doesn't silently affect others.
ARMOR_DIVISOR: int = 1000
DODGE_DIVISOR: int = 1000
BLOCK_DIVISOR: int = 1000
STUN_AVOIDANCE_DIVISOR: int = 1000

# Enemy baseline model used for EHP projections
ENEMY_CRIT_RATE: float = 0.35        # fraction of enemy hits that are crits
ENEMY_CRIT_MULTIPLIER: float = 1.5   # damage multiplier applied to enemy crits
