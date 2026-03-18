"""
Defense Engine — calculates effective health pool and survivability metrics.

Mirrors the logic in frontend/src/lib/simulation.ts:calculateDefense().

Formulas:
  ArmorReduction    = Armor / (Armor + 1000)
  ResistReduction   = AvgResistance / 100  (each element capped at 75%)
  TotalReduction    = 1 - (1 - ArmorReduction) * (1 - ResistReduction)
  EHP               = Health / (1 - TotalReduction)
  DodgeChancePct    = DodgeRating / (DodgeRating + 1000) * 100
  WardDecay/s       = Ward * max(0, WARD_BASE_DECAY_RATE - ward_retention_pct/100)
  WardRegen/s       = ward_regen (flat, from affixes/passives)
  NetWard/s         = WardRegen/s - WardDecay/s

Survivability score is a 0–100 composite of health (40%), resistances (40%),
and armour reduction (20%).

Pure module — no DB, no HTTP.
"""

from dataclasses import dataclass, asdict

from app.engines.stat_engine import BuildStats


RES_CAP = 75                  # Last Epoch resistance cap
WARD_BASE_DECAY_RATE = 0.25   # Ward decays at 25%/s before retention modifiers


@dataclass
class DefenseResult:
    max_health: int
    effective_hp: int
    armor_reduction_pct: int
    avg_resistance: int
    fire_res: int
    cold_res: int
    lightning_res: int
    void_res: int
    necrotic_res: int
    dodge_chance_pct: float      # converted from dodge_rating
    ward_regen_per_second: float
    ward_decay_per_second: float
    net_ward_per_second: float   # positive = sustaining ward
    survivability_score: int     # 0–100 composite
    weaknesses: list             # list of descriptive strings
    strengths: list              # list of descriptive strings

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def calculate_defense(stats: BuildStats) -> DefenseResult:
    """
    Calculate effective health pool and survivability for a build.

    Mirrors calculateDefense() in frontend/src/lib/simulation.ts.
    """
    # Armour mitigation
    armor_reduction = stats.armour / (stats.armour + 1000)

    # Cap each resistance at 75%
    fire_res    = min(RES_CAP, stats.fire_res)
    cold_res    = min(RES_CAP, stats.cold_res)
    lightning_res = min(RES_CAP, stats.lightning_res)
    void_res    = min(RES_CAP, stats.void_res)
    necrotic_res = min(RES_CAP, stats.necrotic_res)

    avg_res = (fire_res + cold_res + lightning_res + void_res + necrotic_res) / 5

    # TotalReduction = 1 - (1 - ArmorReduction) * (1 - AvgResistance/100)
    avg_res_decimal = avg_res / 100
    total_reduction = 1 - (1 - armor_reduction) * (1 - avg_res_decimal)

    # EHP = Health / (1 - TotalReduction)
    denom = max(0.01, 1 - total_reduction)
    effective_hp = round(stats.max_health / denom)

    # Dodge chance: rating → probability (same diminishing-returns formula as armour)
    dodge_chance_pct = round(stats.dodge_rating / (stats.dodge_rating + 1000) * 100, 1)

    # Ward sustainability
    # Decay rate is reduced by ward_retention_pct (percentage points off the base rate)
    effective_decay_rate = max(0.0, WARD_BASE_DECAY_RATE - stats.ward_retention_pct / 100)
    ward_decay_per_second = round(stats.ward * effective_decay_rate, 1)
    ward_regen_per_second = round(stats.ward_regen, 1)
    net_ward_per_second   = round(ward_regen_per_second - ward_decay_per_second, 1)

    # Survivability score — composite 0–100
    health_score  = min(100, stats.max_health / 30)         # 3000 hp = 100
    resist_score  = avg_res / RES_CAP * 100                 # 75% avg = 100
    armour_score  = min(100, armor_reduction * 200)         # 50% reduction = 100
    score = round(health_score * 0.4 + resist_score * 0.4 + armour_score * 0.2)

    # Weakness / strength detection
    weaknesses = []
    strengths = []

    if stats.fire_res < 40:
        weaknesses.append(f"Fire res {int(stats.fire_res)}% (uncapped)")
    if stats.cold_res < 40:
        weaknesses.append(f"Cold res {int(stats.cold_res)}% (uncapped)")
    if stats.lightning_res < 40:
        weaknesses.append(f"Lightning res {int(stats.lightning_res)}% (uncapped)")
    if stats.void_res < 40:
        weaknesses.append(f"Void res {int(stats.void_res)}% (uncapped)")
    if stats.necrotic_res < 40:
        weaknesses.append(f"Necrotic res {int(stats.necrotic_res)}% (uncapped)")
    if stats.armour < 500:
        weaknesses.append("Low armour — vulnerable to physical hits")
    if stats.max_health < 1500:
        weaknesses.append("Low health pool")
    if stats.ward > 100 and net_ward_per_second < 0:
        weaknesses.append(f"Ward decaying ({net_ward_per_second}/s) — needs more retention or regen")

    if stats.fire_res >= 70:
        strengths.append("Fire capped")
    if stats.cold_res >= 70:
        strengths.append("Cold capped")
    if stats.lightning_res >= 70:
        strengths.append("Lightning capped")
    if armor_reduction > 0.4:
        strengths.append("Strong armour mitigation")
    if stats.max_health > 2500:
        strengths.append("Large health pool")
    if stats.ward > 200:
        strengths.append("Ward absorption layer")
    if net_ward_per_second > 0:
        strengths.append(f"Ward sustaining (+{net_ward_per_second}/s)")
    if dodge_chance_pct >= 20:
        strengths.append(f"Dodge {dodge_chance_pct}%")

    return DefenseResult(
        max_health=round(stats.max_health),
        effective_hp=effective_hp,
        armor_reduction_pct=round(armor_reduction * 100),
        avg_resistance=round(avg_res),
        fire_res=round(fire_res),
        cold_res=round(cold_res),
        lightning_res=round(lightning_res),
        void_res=round(void_res),
        necrotic_res=round(necrotic_res),
        dodge_chance_pct=dodge_chance_pct,
        ward_regen_per_second=ward_regen_per_second,
        ward_decay_per_second=ward_decay_per_second,
        net_ward_per_second=net_ward_per_second,
        survivability_score=min(100, score),
        weaknesses=weaknesses,
        strengths=strengths,
    )
