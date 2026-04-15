"""
Combat mechanic constants — hit, crit, and ailment formulas.

Update when LE patches change ailment ratios, durations, or crit caps.
"""

# Player crit chance hard cap (100% — can always reach guaranteed crits)
CRIT_CHANCE_CAP: float = 1.0

# BuildStats defaults — also used as dataclass field defaults in stat_engine.py
BASE_CRIT_CHANCE: float = 0.05
# VERIFIED: 1.4.3 spec §2.2 — base crit multiplier is 200% (2.0×), not 150%
BASE_CRIT_MULTIPLIER: float = 2.0

# Hit damage variance: ±25% for hits, none for DoTs
# VERIFIED: 1.4.3 spec §2.1 — hit damage rolls uniformly in [0.75×, 1.25×]
HIT_DAMAGE_VARIANCE: float = 0.25

# Ailment DoT — Last Epoch flat base damage per stack, pre-modifier
# These are the base DPS values per stack; total = stacks × base × (1 + increased)
IGNITE_BASE_DPS: float = 40.0     # 40 fire DoT per second per stack
IGNITE_DURATION: float = 3.0      # seconds

# UNVERIFIED: Last Epoch 1.4.3 publishes no single authoritative "base bleed DPS"
# number. 43.0 is a community-derived approximation used across the engine and
# regression tests; re-check before any patch-driven recalibration.
BLEED_BASE_DPS: float = 43.0      # ~43 physical DoT per second per stack
BLEED_DURATION: float = 4.0       # seconds

POISON_BASE_DPS: float = 28.0     # 28 poison DoT per second per stack
POISON_DURATION: float = 3.0      # seconds

ELECTRIFY_BASE_DPS: float = 44.0  # 44 lightning DoT per second per stack
ELECTRIFY_DURATION: float = 2.5   # seconds

# Boss ailment effectiveness reduction (60% less effective vs bosses)
BOSS_AILMENT_REDUCTION: float = 0.60
