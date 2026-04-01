"""
Combat mechanic constants — hit, crit, and ailment formulas.

Update when LE patches change ailment ratios, durations, or crit caps.
"""

# Player crit chance hard cap
CRIT_CHANCE_CAP: float = 0.95

# BuildStats defaults — also used as dataclass field defaults in stat_engine.py
BASE_CRIT_CHANCE: float = 0.05
BASE_CRIT_MULTIPLIER: float = 1.5

# Ailment DoT — Last Epoch baseline values, pre-modifier
BLEED_BASE_RATIO: float = 0.70    # 70% of hit damage spread over duration per stack
BLEED_DURATION: float = 4.0       # seconds

IGNITE_DPS_RATIO: float = 0.20    # 20% of hit damage per second per stack
IGNITE_DURATION: float = 3.0      # seconds

POISON_DPS_RATIO: float = 0.30    # 30% of hit damage per second per stack
POISON_DURATION: float = 3.0      # seconds
