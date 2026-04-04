"""
Defense Engine — calculates effective health pool and survivability metrics.

Formulas (Last Epoch mechanics):
  ArmorReduction    = Armor / (Armor + 1000)
  ResistReduction   = AvgResistance / 100  (each element capped at 75%)
  TotalReduction    = 1 - (1 - ArmorReduction) * (1 - ResistReduction)
  EHP               = Health / (1 - TotalReduction)
  DodgeChancePct    = DodgeRating / (DodgeRating + 1000) * 100
  BlockMitigation   = BlockEffectiveness / (BlockEffectiveness + 1000)
  EnduranceEHP      = when below threshold%, damage reduced by endurance%
  WardDecay/s       = Ward * max(0, WARD_BASE_DECAY_RATE - ward_retention_pct/100)
  WardRegen/s       = ward_regen (flat, from affixes/passives)
  NetWard/s         = WardRegen/s - WardDecay/s

Survivability score is a 0–100 composite of health (30%), resistances (30%),
armour (15%), avoidance layers (15%), and sustain (10%).

Pure module — no DB, no HTTP.
"""

from dataclasses import dataclass, asdict

from app.constants.defense import (
    RES_CAP,
    WARD_BASE_DECAY_RATE,
    ENDURANCE_CAP,
    ARMOR_DIVISOR,
    DODGE_DIVISOR,
    BLOCK_DIVISOR,
    STUN_AVOIDANCE_DIVISOR,
    ENEMY_CRIT_RATE,
    ENEMY_CRIT_MULTIPLIER,
)
from app.engines.stat_engine import BuildStats
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


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
    # Extended defense metrics
    physical_res: int = 0
    poison_res: int = 0
    block_chance_pct: float = 0.0
    block_mitigation_pct: float = 0.0
    endurance_pct: float = 0.0
    endurance_threshold_pct: float = 0.0
    crit_avoidance_pct: float = 0.0
    glancing_blow_pct: float = 0.0
    stun_avoidance_pct: float = 0.0
    ward_buffer: int = 0            # ward as effective HP buffer
    total_ehp: int = 0              # EHP including ward + avoidance layers
    # Sustain metrics
    leech_pct: float = 0.0
    health_on_kill: float = 0.0
    mana_on_kill: float = 0.0
    ward_on_kill: float = 0.0
    health_regen: float = 0.0
    mana_regen: float = 0.0
    sustain_score: int = 0           # 0–100 sustain composite

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_defense(stats: BuildStats) -> DefenseResult:
    """
    Calculate effective health pool and survivability for a build.

    Includes block, endurance, crit avoidance, glancing blow, ward buffer,
    physical/poison resistance, and sustain metrics.
    """
    log.debug(
        "calculate_defense",
        health=stats.max_health,
        armour=stats.armour,
        ward=stats.ward,
    )
    # Armour mitigation
    armor_reduction = stats.armour / (stats.armour + ARMOR_DIVISOR)

    # Cap each resistance at 75%
    fire_res    = min(RES_CAP, stats.fire_res)
    cold_res    = min(RES_CAP, stats.cold_res)
    lightning_res = min(RES_CAP, stats.lightning_res)
    void_res    = min(RES_CAP, stats.void_res)
    necrotic_res = min(RES_CAP, stats.necrotic_res)
    physical_res = min(RES_CAP, stats.physical_res)
    poison_res   = min(RES_CAP, stats.poison_res)

    # Average of all 7 resistances (including physical and poison)
    all_res = [fire_res, cold_res, lightning_res, void_res, necrotic_res,
               physical_res, poison_res]
    avg_res = sum(all_res) / len(all_res)

    # TotalReduction = 1 - (1 - ArmorReduction) * (1 - AvgResistance/100)
    avg_res_decimal = avg_res / 100
    total_reduction = 1 - (1 - armor_reduction) * (1 - avg_res_decimal)

    # Base EHP from health + armour + resistance
    denom = max(0.01, 1 - total_reduction)
    base_ehp = stats.max_health / denom

    # Block: reduces incoming hit damage by block_mitigation on block_chance% of hits
    block_chance = min(100, stats.block_chance) / 100
    block_mitigation = stats.block_effectiveness / (stats.block_effectiveness + BLOCK_DIVISOR) if stats.block_effectiveness > 0 else 0
    # Average damage taken factor with block: (1 - block_chance * block_mitigation)
    block_factor = max(0.01, 1 - block_chance * block_mitigation)

    # Dodge: avoidance layer
    dodge_chance = stats.dodge_rating / (stats.dodge_rating + DODGE_DIVISOR)
    dodge_chance_pct = round(dodge_chance * 100, 1)
    dodge_factor = max(0.01, 1 - dodge_chance)

    # Glancing blow: reduces crit damage taken (assume 35% of incoming hits are crits)
    glancing_blow_chance = min(100, stats.glancing_blow) / 100
    # Glancing blow converts crits to normal hits — effective damage reduction on crits
    crit_avoidance = min(100, stats.crit_avoidance) / 100
    # Effective crit rate against us after crit avoidance
    effective_enemy_crit = ENEMY_CRIT_RATE * (1 - crit_avoidance)
    # Glancing blow then converts remaining crits
    crits_after_glancing = effective_enemy_crit * (1 - glancing_blow_chance)
    # Damage multiplier from enemy crits: normal hits + reduced crit hits
    crit_damage_factor = (1 - effective_enemy_crit) + crits_after_glancing * ENEMY_CRIT_MULTIPLIER + \
                         (effective_enemy_crit - crits_after_glancing) * 1.0
    # Normalize: without avoidance it would be (1 - ENEMY_CRIT_RATE) + ENEMY_CRIT_RATE * ENEMY_CRIT_MULTIPLIER
    base_crit_factor = (1 - ENEMY_CRIT_RATE) + ENEMY_CRIT_RATE * ENEMY_CRIT_MULTIPLIER
    crit_reduction_factor = crit_damage_factor / base_crit_factor if base_crit_factor > 0 else 1.0

    # Endurance: reduces damage by endurance% when below threshold% health
    # Model as weighted average: fraction of time below threshold benefits from reduction
    endurance_pct = min(ENDURANCE_CAP, stats.endurance)
    endurance_threshold = min(100, stats.endurance_threshold)
    # Simplified: endurance adds effective HP to the portion below threshold
    endurance_factor = 1.0
    if endurance_pct > 0 and endurance_threshold > 0:
        threshold_frac = endurance_threshold / 100
        reduction = endurance_pct / 100
        # Below threshold, damage is reduced → that portion of health is worth more
        endurance_factor = 1 / (1 - threshold_frac * reduction)

    # Combined EHP with all layers
    effective_hp = base_ehp / (block_factor * dodge_factor * crit_reduction_factor) * endurance_factor

    # Ward as additional HP buffer
    ward_buffer = round(stats.ward)
    total_ehp = round(effective_hp) + ward_buffer

    # Ward sustainability
    effective_decay_rate = max(0.0, WARD_BASE_DECAY_RATE - stats.ward_retention_pct / 100)
    ward_decay_per_second = round(stats.ward * effective_decay_rate, 1)
    ward_regen_per_second = round(stats.ward_regen, 1)
    net_ward_per_second   = round(ward_regen_per_second - ward_decay_per_second, 1)

    # Stun avoidance (diminishing returns like dodge)
    stun_avoidance_pct = round(stats.stun_avoidance / (stats.stun_avoidance + STUN_AVOIDANCE_DIVISOR) * 100, 1) if stats.stun_avoidance > 0 else 0.0

    # Sustain score (0-100)
    leech_score = min(30, stats.leech * 3)  # 10% leech = 30pts
    regen_score = min(20, stats.health_regen)  # 20 regen = 20pts
    on_kill_score = min(20, stats.health_on_kill / 2)  # 40 on kill = 20pts
    ward_sustain_score = min(15, max(0, net_ward_per_second))  # +15 net ward/s = 15pts
    mana_score = min(15, stats.mana_regen)  # 15 mana regen = 15pts
    sustain_score = round(min(100, leech_score + regen_score + on_kill_score + ward_sustain_score + mana_score))

    # Survivability score — composite 0–100
    health_score  = min(100, stats.max_health / 30)         # 3000 hp = 100
    resist_score  = avg_res / RES_CAP * 100                 # 75% avg = 100
    armour_score  = min(100, armor_reduction * 200)          # 50% reduction = 100
    avoidance_score = min(100, (dodge_chance_pct + block_chance * 100 +
                                crit_avoidance * 100 + endurance_pct) / 2)
    score = round(health_score * 0.30 + resist_score * 0.30 +
                  armour_score * 0.15 + avoidance_score * 0.15 +
                  sustain_score * 0.10)

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
    if stats.physical_res < 20:
        weaknesses.append(f"Physical res {int(stats.physical_res)}% (low)")
    if stats.armour < 500:
        weaknesses.append("Low armour — vulnerable to physical hits")
    if stats.max_health < 1500:
        weaknesses.append("Low health pool")
    if stats.ward > 100 and net_ward_per_second < 0:
        weaknesses.append(f"Ward decaying ({net_ward_per_second}/s) — needs more retention or regen")
    if crit_avoidance * 100 < 30:
        weaknesses.append("Low crit avoidance — vulnerable to enemy crits")
    if stats.leech == 0 and stats.health_regen < 5 and stats.health_on_kill == 0:
        weaknesses.append("No sustain — no leech, regen, or on-kill recovery")

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
    if block_chance >= 0.3:
        strengths.append(f"Block {round(block_chance * 100)}%")
    if endurance_pct >= 20:
        strengths.append(f"Endurance {round(endurance_pct)}%")
    if crit_avoidance >= 0.5:
        strengths.append(f"Crit avoidance {round(crit_avoidance * 100)}%")
    if stats.leech >= 3:
        strengths.append(f"Life leech {stats.leech}%")
    if stats.health_regen >= 15:
        strengths.append(f"Strong health regen ({stats.health_regen}/s)")

    return DefenseResult(
        max_health=round(stats.max_health),
        effective_hp=round(effective_hp),
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
        physical_res=round(physical_res),
        poison_res=round(poison_res),
        block_chance_pct=round(block_chance * 100, 1),
        block_mitigation_pct=round(block_mitigation * 100, 1),
        endurance_pct=round(endurance_pct, 1),
        endurance_threshold_pct=round(endurance_threshold, 1),
        crit_avoidance_pct=round(crit_avoidance * 100, 1),
        glancing_blow_pct=round(glancing_blow_chance * 100, 1),
        stun_avoidance_pct=stun_avoidance_pct,
        ward_buffer=ward_buffer,
        total_ehp=total_ehp,
        leech_pct=round(stats.leech, 1),
        health_on_kill=round(stats.health_on_kill, 1),
        mana_on_kill=round(stats.mana_on_kill, 1),
        ward_on_kill=round(stats.ward_on_kill, 1),
        health_regen=round(stats.health_regen, 1),
        mana_regen=round(stats.mana_regen, 1),
        sustain_score=sustain_score,
    )


# ---------------------------------------------------------------------------
# calculate_ehp — plan-specified alias
# ---------------------------------------------------------------------------

def calculate_ehp(stats: BuildStats) -> float:
    """Return the effective health pool for *stats*.

    This is the canonical interface specified in architecture_implementation_plan.md.
    Delegates to :func:`calculate_defense` and returns the ``total_ehp`` value,
    which includes the ward buffer on top of the armour/resistance-adjusted EHP.

    Args:
        stats: Aggregated :class:`~app.engines.stat_engine.BuildStats`.

    Returns:
        ``total_ehp`` as a float (health adjusted for all mitigation layers + ward).
    """
    result = calculate_defense(stats)
    return float(result.total_ehp)
