# Simulation Design

This document describes how The Forge simulates combat, calculates stats, and runs Monte Carlo analysis.

---

## Stat Pipeline

The stat engine implements an 8-layer deterministic pipeline that mirrors Last Epoch's modifier stacking rules.

### Layer 1: Base Stats
Each class has base health, mana, damage, and attributes defined in `CLASS_BASE_STATS`. Mastery selection adds additional flat bonuses from `MASTERY_BONUSES`.

### Layer 2: Flat Additions
Gear implicits and affix flat values are added to the stat pool. Each affix definition includes a `stat_key` mapping to a `BuildStats` field and tier-based value ranges.

### Layer 3: Increased (%)
All "increased" modifiers are summed into an additive pool per stat. The total is applied as: `value * (1 + sum(increased) / 100)`.

### Layer 4: More Multipliers
"More" modifiers are multiplicative. Each is applied as a separate multiplier: `value * product(1 + more_i / 100)`.

### Layer 5: Conversions
Damage type conversions (e.g., physical to fire) are applied after base damage calculation. Converted damage inherits all relevant increased/more modifiers for the target type.

### Layer 6: Derived Stats
Attributes expand to secondary stats:
- Strength: +1 max health per point
- Intelligence: +0.1% ward retention per point
- Attunement: +0.2 mana regen per point

### Layer 7: Registry Derived
EHP, armor mitigation, and dodge chance are computed from the resolved stats. These are compound values that depend on multiple input stats.

### Layer 8: Conditional Stats
Context-dependent bonuses are evaluated last: "while moving", "against bosses", "enemy is frozen", etc. These are additive to the already-resolved stat values.

---

## DPS Calculation

The combat engine calculates DPS deterministically:

```
base_damage = skill_base * (1 + level_scaling * (level - 1))
flat_added = sum(all flat damage additions from stats)
total_base = base_damage + flat_added

increased_total = sum(all relevant increased% modifiers)
more_total = product(all relevant more% modifiers)

raw_hit = total_base * (1 + increased_total / 100) * more_total

non_crit_hit = raw_hit
crit_hit = raw_hit * crit_multiplier

average_hit = non_crit_hit * (1 - crit_chance) + crit_hit * crit_chance

dps = average_hit * effective_attack_speed
```

Each skill has a definition in `SKILL_STATS` (165+ skills) specifying: base_damage, level_scaling, attack_speed, damage_types, is_spell/melee/bow flags.

Skill modifiers from spec tree allocation (parsed by `skill_tree_resolver`) are applied as additional multipliers: `more_damage_pct`, `added_hits_per_cast`, `cast_speed_pct`, `attack_speed_pct`, `crit_chance_pct`, `crit_multiplier_pct`.

---

## Ailment DPS

Ailments (Ignite, Bleed, Poison) are calculated separately:

```
ailment_dps = base_ailment_damage * ailment_chance * (1 + increased_ailment%) * more_ailment
```

Each ailment has a base damage derived from the hit that applied it, a proc chance based on the character's chance to apply that ailment, and separate increased/more modifiers.

Ailment DPS is additive to hit DPS for `total_dps`.

---

## Enemy-Aware DPS

When simulating against a specific enemy, the combat engine applies:

```
armor_reduction = enemy_armor / (enemy_armor + ARMOR_DIVISOR)
effective_armor_reduction = armor_reduction * (1 - armor_shred%)
resistance_reduction = max(0, enemy_resistance - penetration)
effective_dps = raw_dps * (1 - effective_armor_reduction) * (1 - resistance_reduction / 100)
```

Enemy profiles are loaded from `data/entities/enemy_profiles.json` and include health, armor, resistances, and enrage timers.

---

## Monte Carlo Simulation

The Monte Carlo DPS simulation runs N independent combat samples (default 10,000) to measure variance:

1. For each sample:
   - Roll crit: random < crit_chance
   - Compute hit damage (crit or non-crit)
   - Apply damage variance (skill-dependent)
   - Record DPS for this sample

2. Aggregate statistics:
   - mean_dps, min_dps, max_dps, std_dev
   - Percentiles: p5, p25, p50, p75, p95

Supports deterministic seeding for reproducible results. Parallelizable via `ProcessPoolExecutor` with configurable worker count.

---

## Defense Calculation

### EHP (Effective Health Pool)

```
damage_reduction = 1 - (1 - armor_reduction) * (1 - avg_resistance / 100)
avoidance = (1 - dodge_chance) * (1 - block_chance * block_mitigation)
effective_hp = max_health / ((1 - damage_reduction) * avoidance)
total_ehp = effective_hp + ward_buffer
```

### Resistance Model
Seven elemental/damage resistances (fire, cold, lightning, void, necrotic, physical, poison), each capped at 75%. Average resistance used for EHP calculation.

### Endurance
Endurance provides conditional damage reduction when health is below the threshold. Non-linear EHP boost modeled as: `health_below_threshold * endurance_damage_reduction + health_above_threshold`.

### Ward
Ward acts as an additional health buffer with natural decay: `decay = max(0, ward * (DECAY_RATE - retention_pct / 100))`. Net ward per second factors in ward generation minus decay.

### Survivability Score
Composite score (0-100) accounting for EHP, resistance coverage, avoidance layers, sustain (regen, leech), and weakness count.

---

## Boss Encounter Simulation

Multi-phase boss fights:

1. Parse boss profile into phase list (or single phase if no phase definitions)
2. For each phase:
   - Calculate phase health: `boss_hp * (threshold[i] - threshold[i+1])`
   - Calculate effective DPS: `raw_dps * armor_factor * res_factor * damage_reduction_factor`
   - Handle immunity phases (0 DPS, ~5 second duration)
   - Calculate time-to-kill: `phase_hp / effective_dps`
   - Calculate survival score based on defense vs boss damage
3. Sum phase TTK for total encounter time
4. Check enrage: flag if `total_ttk > boss.enrage_time`

### Corruption Scaling

At each corruption breakpoint (default: 0, 100, 200, 300, 400, 500):
- Health multiplier: linear 0-200 (1.0 to 3.0x), accelerating 200+ via `3.0 + 0.005 * (corruption - 200)^1.5`
- Damage multiplier: linear `1.0 + corruption * 0.005`
- Run full boss encounter simulation
- Track DPS efficiency: `baseline_ttk / current_ttk`
- Recommended max corruption = highest where survival >= threshold (default 70)

---

## Optimization Methodology

### Sensitivity Analysis
For each of 50+ analyzable stats:
1. Bump stat by +10% (or flat 10 for zero-value stats)
2. Recalculate DPS and EHP with bumped value
3. Record gain percentages
4. Weight: `impact = dps_gain * offense_weight + ehp_gain * defense_weight`

### Efficiency Scoring
For affix upgrade candidates:
1. Calculate DPS and EHP gain from the affix
2. Estimate FP cost by tier
3. `efficiency = (dps_gain * offense_weight + ehp_gain * defense_weight) / fp_cost`

### Multi-Objective Optimization
Test 86 candidate stat increments:
1. For each: bump stat, recalculate DPS and EHP, record gains
2. Composite score: `dps_gain * dps_weight + ehp_gain * ehp_weight`
3. Pareto front: candidates where no other candidate dominates in both DPS and EHP simultaneously
