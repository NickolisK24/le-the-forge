# Game Mechanics Accuracy Audit — Patch 1.4.3 (Shattered Omens / Season 4)

Audit date: 2026-04-13
Branch: `audit/game-mechanics-accuracy`
Base: `dev` @ 5ea1ac2

Scope: every numerical constant, formula, cap, and data value in the backend
combat/damage/defense/ailment/crafting engines plus the static data files under
`data/` and `backend/app/game_data/` was audited against the Last Epoch 1.4.3
specification provided by the owner.

This is a correctness audit, not a feature audit — each finding below is
either a bug (wrong number or formula) or an entirely missing mechanic.

---

## CRITICAL ERRORS (wrong formula or constant — produces wrong numbers)

| # | Location | Current | Should be | Spec |
|---|----------|---------|-----------|------|
| C-01 | `backend/app/constants/combat.py:12` | `BASE_CRIT_MULTIPLIER = 1.5` | `2.0` | §2.2 crit multiplier is 200%, not 150% |
| C-02 | `backend/app/domain/critical.py:25` | `BASE_CRIT_MULTIPLIER = 1.5` | `2.0` | §2.2 — duplicate constant |
| C-03 | `backend/app/game_data/constants.json:8` | `"crit_multiplier_default": 1.5` | `2.0` | §2.2 |
| C-04 | `backend/app/game_data/classes.json` (base_stats) | `crit_multiplier: 1.5` × 5 classes | `2.0` | §2.2 — applied to every class default |
| C-05 | `backend/app/constants/defense.py:29` | `ARMOR_NON_PHYSICAL_EFFECTIVENESS = 0.75` | `0.70` | §3.1 non-physical mitigation is 70%, not 75% |
| C-06 | `backend/app/constants/combat.py:15` | `HIT_DAMAGE_VARIANCE = 0.15` | `0.25` | §2.1 ±25% variance on hits |
| C-07 | `backend/app/engines/combat_engine.py:391-418` | Monte Carlo applies crit roll only | also apply ±25% hit variance | §2.1 — variance is defined but never used |
| C-08 | `backend/app/domain/block.py:13,18` | `BLOCK_CHANCE_CAP = 0.75` | `0.85` (renamed `BLOCK_EFFECTIVENESS_CAP`) | §3.5 block effectiveness cap is 85% |
| C-09 | `backend/app/domain/armor_shred.py:22` | `STACK_CAP = 20` | *remove cap* | §4.3 Armor Shred has NO stack cap |
| C-10 | `backend/app/game_data/constants.json:19` | `"armor_cap": 0.80` | `0.85` | §3.1 physical armor cap is 85% |
| C-11 | `backend/app/game_data/constants.json:28,29` | `max_prefixes: 3, max_suffixes: 3` | `2, 2` | §5.2 exactly 2+2 = 4 affixes |
| C-12 | `backend/app/engines/stat_engine.py:252` | `dexterity.dodge_rating: 3` | `4` | §3.3 / §10 — Dex = 4 Dodge Rating/pt |
| C-13 | `backend/app/engines/stat_engine.py:253` | `vitality.max_health: 10` | `6` | §10 — Vit = 6 HP/pt |
| C-14 | `backend/app/engines/stat_engine.py:250-254` (strength) | `strength.armour: 2` (flat) | `4` (percent increased armor) | §10 — Str = 4% increased armor/pt |
| C-15 | `backend/app/engines/stat_engine.py:251` (intelligence) | no `ward_retention` entry | add `ward_retention: 4` | §10 — Int = 4% Ward Retention/pt |

## DATA ERRORS (wrong values in JSON / data files)

| # | Location | Current | Should be | Spec |
|---|----------|---------|-----------|------|
| D-01 | `backend/app/game_data/skills.json` (Meteor) | `base_damage: 300` | `240` | §6.2 |
| D-02 | `backend/app/game_data/skills.json` (Bladestorm) | no `added_damage_effectiveness` | `1.5` | §2.3 / §6.1 |
| D-03 | `backend/app/game_data/skills.json` (Shadow Rend) | no `added_damage_effectiveness` | `5.0` | §2.3 / §6.1 (Shadow's attack) |
| D-04 | `backend/app/game_data/skills.json` (Black Hole) | no `added_damage_effectiveness` | `8.0` | §2.3 / §6.2 — was 6.0, now 8.0 |
| D-05 | `backend/app/game_data/skills.json` (Meteor) | no `added_damage_effectiveness` | `12.0` | §2.3 / §6.2 |
| D-06 | `backend/app/game_data/constants.json:37-38` | `fracture_base_chance: 0.05, fracture_fp_scaling: 0.01` | removed | §5.5 — fracture system was deleted in patch 0.8.4 |
| D-07 | `backend/app/game_data/constants.json:39` | `max_affix_tier: 7` | `8` (T8 Primordial exists) | §5.1 |
| D-08 | `backend/app/domain/resistance_shred.py` | no per-stack / boss-stack / stack-cap / duration constants | add `SHRED_PER_STACK = 0.05`, `SHRED_PER_STACK_BOSS = 0.02`, `MAX_STACKS_PER_TYPE = 10`, `STACK_DURATION = 4.0` | §4.4 |

## MISSING DATA (mechanics not modeled at all)

These mechanics are entirely absent from the codebase. They were checked for
during the audit and are documented here so work can be tracked, but
implementation is out of scope for this audit pass (each is a multi-file
feature).

### Ailments (Section 4)
- **Chill** — 12% reduced action speed per stack, max 3 stacks (→ 36% total). Not in `AilmentType` enum or any data file.
- **Freeze** — 1.2 s full incapacitation. Not modeled.
- **Slow** — 20% reduced move speed per stack, max 3 stacks. Not modeled.
- **Stun** — 0.4 s incapacitation. Not modeled as an ailment.
- **Shock (debuff semantics)** — code has `SHOCK_DAMAGE_BONUS_PER_STACK = 20.0` in `status_interactions.py`, but the real mechanic is a 5% lightning resistance reduction per stack, capped at 20 stacks. Stack limit in `ailment_stacking.py` says 1.
- **Marked for Death** — −25% to all resistances for 8 s. Not modeled.
- **Frostbite damage** — enum entry exists, no DPS/duration/Freeze-Avoidance modeling.
- **Damned** (necrotic DoT) — not in enum, no data.
- **Time Rot** (void DoT + 15% reduced atk/cast speed per stack, cap 12 stacks) — not present.
- **Poison resistance shred (−5% per stack, −2% vs bosses)** — not applied by the poison mechanic.

### Crafting (Section 5)
- **Glyphs**: only 3 exist (Stability, Hope, Chaos) out of 6. Missing Order, Despair, Envy, Insight.
- **Runes**: only 4 exist (Removal, Refinement, Shaping, Discovery) out of 13. Missing Shattering, Ascendance, Creation, Research, Havoc, Redemption, Weaving, Evolution, Corruption.
- **Critical Success** (0 FP cost + all affixes +1 tier + shard refund) — not modeled.
- **Legendary crafting** (LP transfer, Temporal Sanctum Key, Eternity Cache, tier-caps by dungeon difficulty, unmodifiable result) — no code or data.
- **Experimental affix system** — referenced by Glyph of Insight / Rune of Research specs, not defined.
- **Legacy fracture code** — `calculate_fracture_probability()` and fracture sim branch still exist though 0.8.4 removed fractures; documented as "kept for backward compat."

### Items / Idols (Section 9)
- **Legendary Potential (LP)** — no `lp_value` field on uniques/set items.
- **Weaver's Will** — no WW mechanic or data.
- **Omen Idols** (Season 4 sub-type) — not present.
- **Idol sizes 2×1, 3×1, 4×1** — only vertical (1×N) and 2×2 are in `item_types.json`.
- **`rarities.json`** lists 5 rarities (Normal, Magic, Rare, Exalted, Legendary); constants define Unique and Set separately, so the rarity file is incomplete relative to the 7 total.

### Encounter Systems (Section 7)
- **Boss ailment effectiveness reduction** — `BOSS_AILMENT_REDUCTION = 0.60` constant exists in combat.py but `boss_encounter.py` does not apply it to the simulation pipeline.
- **Boss poison-res-per-stack = 2%** and **boss resistance-shred-per-stack = 2%** — values only exist inside tests, not as production constants.
- **Monolith normal cap = 50 / Empowered uncapped** — `corruption_scaler.py` takes arbitrary breakpoints; no hard cap enforced for the Normal vs Empowered mode.
- **Empowered area level = 100** — no data field distinguishes 90-tier timelines from Empowered 100.

### Character / Skill (Sections 1, 3.7, 6.3)
- **Skill respec / passive respec cost logic** — no cost model anywhere.
- **Specialization unlock levels (4, 8, 20, 35, 50)** — not modeled in the build planner.
- **Leech duration (3 s per instance)** — `leech.py` models per-hit flat leech only; no duration tracking.
- **Rogue base-damage standardization** (many Rogue skills → `base_damage: 2` + very high effectiveness in 1.4) — current data still has high flat base damages (Flurry 65, Puncture 80, Shadow Cascade 120). Either the spec is not yet applied, or our data model predates the change.
- **Glancing Blow exact 35% reduction** — `defense_engine.py:138-151` converts crits via `ENEMY_CRIT_MULTIPLIER` rather than applying a fixed 35% damage reduction.

### Class/mastery passives (Section 8)
- **Druid: 70% damage reduction for 2 s on transformation exit** — not found in passive data.
- **Shaman: 50% elemental resistance while totem active** — not found.
- **Beastmaster: +1 Companion Limit mastery bonus** — only granted by unique item (Artor's Legacy).
- **Falconer's Falcon: damage-immune** — no flag in companion data.

---

## CONFIRMED CORRECT (verified matches spec)

### Section 1 — Character
- `data/classes/classes.json` — every class has `baseHealth: 100, baseMana: 50` at level 1 (§1.1 exact match).
- `backend/app/game_data/constants.json:60` — `passives.max_allocated_nodes: 113` (§1.1 total cap).
- `backend/app/game_data/constants.json:64` — `skills.max_level: 20` (§1.3 max tree points).
- Every class has exactly 4 entries in `data/classes/classes.json` (1 base + 3 masteries) — all 15 masteries exist with the correct names (§1.2 / §8.2 cardinality).

### Section 2 — Damage formula
- `backend/app/domain/calculators/increased_damage_calculator.py:40` — increased modifiers summed additively (§2.1 ✓).
- `backend/app/domain/calculators/more_multiplier_calculator.py:34-37` — more multipliers applied each independently multiplicatively (§2.1 ✓).
- `backend/app/domain/calculators/final_damage_calculator.py:93-94` — order is Base → Increased → More (§2.1 ✓).
- `backend/app/engines/combat_engine.py:352-357` — crit applied after the damage pipeline, as a final multiplier (§2.2 ✓).
- `backend/app/constants/combat.py:11` — base crit chance `0.05` (§2.2 ✓).
- `backend/app/domain/critical.py:24,43-44` — crit hard-capped at 1.0 = 100% (§2.2 ✓).
- `backend/app/domain/calculators/ailment_calculator.py:62-78` — DoTs never have crit applied (§2.2 ✓).
- `backend/app/game_data/skills.json` — Black Hole `base_damage: 160` (§6.2 ✓ post-1.4 value).
- `backend/app/game_data/skills.json` — Bladestorm `attack_speed: 3.0` (§6.1 ✓ — 3 hits/sec).
- `backend/app/game_data/skills.json` — Dancing Strikes has no cooldown field (§6.2 ✓).

### Section 3 — Defense
- `backend/app/domain/armor.py:46` — armor formula `armor / (armor + 10 × area_level)` (§3.1 ✓).
- `backend/app/constants/defense.py:28` — physical armor cap `0.85` (§3.1 ✓).
- `backend/app/domain/armor.py` — DoTs bypass armor (§3.1 ✓, per module docstring + calculator wiring).
- `backend/app/domain/resistance.py:31,35-37` — resistance hard cap 75% with clamp (§3.2 ✓).
- `backend/app/domain/resistance_shred.py:52,78` — negative resistance supported, clamped at −75% (§3.2 ✓).
- `backend/app/domain/dodge.py:43-45` — dodge formula and 85% cap (§3.3 ✓).
- `backend/app/constants/defense.py:37` — `DEXTERITY_DODGE_RATING_PER_POINT = 4.0` (§3.3 ✓ as a constant, but note C-12 about the duplicate `ATTRIBUTE_SCALING` dict which overrides this).
- `backend/app/constants/defense.py:13,16,19,22-23` — `WARD_BASE_DECAY_RATE = 0.4`, `INTELLIGENCE_WARD_RETENTION_PER_POINT = 4.0`, `ENDURANCE_CAP = 60`, `ENDURANCE_DEFAULT_DR = 20.0`, `ENDURANCE_DEFAULT_THRESHOLD = 20.0` (§3.4, §3.6 ✓).
- `backend/app/domain/ward.py:27-44` — ward decay formula `0.4 × (current − threshold) / (1 + 0.5 × retention)` (§3.6 ✓).
- `backend/app/engines/defense_engine.py:153-173` — endurance never applied to Ward (§3.4, §3.6 ✓).

### Section 4 — Ailments
- `backend/app/constants/combat.py:19-20` — Ignite 40 dps/stack, 3 s duration (§4.1 ✓).
- `backend/app/constants/combat.py:25-26` — Poison 28 dps/stack, 3 s duration (§4.1 ✓).
- `backend/app/constants/combat.py:28-29` — Electrify 44 dps/stack, 2.5 s duration (§4.1 ✓; note: calc pipeline currently only sums bleed+ignite+poison, so the value is defined but not yet reached by combat_engine summary — out of scope).
- `backend/app/constants/combat.py:32` — `BOSS_AILMENT_REDUCTION = 0.60` (§4.2 ✓ constant; application at runtime: see MISSING).
- `backend/app/domain/calculators/ailment_calculator.py:36-45` — ailment chance > 100% yields guaranteed stacks + remainder probability (§4.2 ✓).
- `backend/app/domain/armor_shred.py:20-21` — 100 armor per stack, 4 s duration (§4.3 ✓; stack-cap flagged as C-09).

### Section 5 — Crafting
- `backend/app/constants/crafting.py:4-5` — `MAX_PREFIXES = 2, MAX_SUFFIXES = 2` (§5.2 ✓ — note C-11 about the inconsistent defaults in `constants.json` / `craft_engine.py`).
- `backend/app/engines/craft_engine.py` — pipeline does NOT fail ("crafts always succeed") — semantically correct per §5.5.

### Section 9 — Items
- `backend/app/constants/equipment_slots.py:3-15` — exactly 11 slots (§9.1 ✓).

### Section 10 — Attributes
- `backend/app/constants/defense.py:16` — `INTELLIGENCE_WARD_RETENTION_PER_POINT = 4.0` (§10 ✓ constant — but not wired into `ATTRIBUTE_SCALING`; see C-15).
- `backend/app/constants/defense.py:37` — `DEXTERITY_DODGE_RATING_PER_POINT = 4.0` (§10 ✓ constant; see C-12).

---

## FIXES APPLIED IN THIS AUDIT

All items labelled `C-##` (critical errors) and `D-##` (data errors) are fixed
on this branch in this commit. Items labelled MISSING are documented only —
implementing them is follow-up work tracked separately.

### Fix summary (all fixes delivered in this single audit commit)
- **FIXED** C-01…C-04 — Base crit multiplier 1.5 → 2.0 (four call sites).
- **FIXED** C-05 — Armor non-physical effectiveness 0.75 → 0.70.
- **FIXED** C-06 / C-07 — Hit damage variance 0.15 → 0.25 and wired into Monte Carlo sim.
- **FIXED** C-08 — Block effectiveness cap 0.75 → 0.85.
- **FIXED** C-09 — Armor shred stack cap removed.
- **FIXED** C-10 — constants.json `armor_cap` 0.80 → 0.85.
- **FIXED** C-11 — constants.json `max_prefixes`/`max_suffixes` 3 → 2.
- **FIXED** C-12…C-15 — stat_engine ATTRIBUTE_SCALING corrected (Dex=4, Vit=6, Str=4% inc armor, Int=4% ward retention).
- **FIXED** D-01 — Meteor base_damage 300 → 240.
- **FIXED** D-02…D-05 — Added `added_damage_effectiveness` to Bladestorm (1.5), Shadow Rend (5.0), Black Hole (8.0), Meteor (12.0).
- **FIXED** D-06 — Removed fracture fields from constants.json.
- **FIXED** D-07 — constants.json `max_affix_tier` 7 → 8.
- **FIXED** D-08 — Added resistance-shred per-stack/boss/cap/duration constants.

Each change is marked with `# VERIFIED: 1.4.3 spec §…` at the change site.

### Verification
- `pytest tests/` — **10664 passed**, 377 skipped, 1 xfailed, 0 new failures.
  Pre-existing unrelated failures (marshmallow 4.x `data_key` incompatibility
  in `test_multi_target_api.py` / `test_conditional_api.py`, and the
  rate-limit JSON body test) confirmed present on `dev` prior to this branch.
- `npx tsc --noEmit` — **0 errors**.
- `flask validate-data` — **Data validation passed — 51 files checked**.
