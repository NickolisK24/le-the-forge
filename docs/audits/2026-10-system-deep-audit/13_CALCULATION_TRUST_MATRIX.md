# 13 — Calculation / Simulation Trust Matrix (Phase 11)

- Audit date: 2026-10-06
- Code under audit: `le-the-forge` HEAD `1efcef7` (2026-05-14)
- Reference data: `/home/user/last-epoch-data/exports_json/*` (extracted from game build `1.4.6_22986002`, generated 2026-05-06)
- Mode: read-only. No code was changed. Scratch scripts lived outside the repo.

## 0. Headline

| Classification | Count (of 38 rows in §3) |
|---|---|
| TRUSTED | 0 |
| PARTIALLY TRUSTED | 12 |
| UNVERIFIED | 9 |
| KNOWN INCORRECT | 13 |
| NOT IMPLEMENTED (in user-facing paths) | 4 |

Nothing reaches TRUSTED. No calculation has a test that checks it against an independent source such as an in-game measurement, extracted game data or official documentation. Every DPS and EHP number on the main build page comes from the hand-entered skill table in `backend/app/game_data/skills.json`. Compared with the 1.4.6 game extract, that table's base damage is off by more than 25% for 53 of the 54 skills that can be compared. The median gap is 24.6×.

The API responses that the main frontend uses for DPS, EHP and boss numbers have no trust, provenance or confidence fields. The `V2TrustBadge` component is used only on the informational "Trusted Data" pages.

## 1. Method and commands

```bash
# Reachability from Flask routes (static import graph over every import statement, including lazy ones)
python3 scratchpad/reach.py   # seeds: backend/app/routes/*.py + backend/app/__init__.py
#  -> 282 reachable modules; of 166 calc-candidate modules in the scanned dirs, 92 reachable, 74 not

# Duplicate-formula discovery
grep -rnE "armou?r\s*/\s*\(|armou?r\s*\+\s*[0-9]|ARMOR_DIVISOR|ARMOR_AREA_LEVEL_FACTOR" backend frontend/src
grep -rnE "dodge\w*\s*/\s*\(|DODGE_DIVISOR|DODGE_CAP|BLOCK_DIVISOR|block_effectiveness" backend frontend/src
grep -rnE "^\s*[A-Z_]*(CRIT|ARMOR|RES|DODGE|BLOCK|LEECH|WARD|ENDURANCE|BLEED|IGNITE|POISON|VARIANCE)[A-Z_]*\s*=" backend

# Route -> engine tracing
grep -nE "post\(|get\(" frontend/src/lib/api.ts          # frontend calls
sed -n 213,286p backend/app/services/simulation_service.py
sed -n 132,300p backend/app/services/build_analysis_service.py

# Extracted-data comparison (skills, ailments)
python3 - <<'EOF'   # forge skills.json vs last-epoch-data exports_json/skills.json damageSources[isHit]
...  # see §5; result: 179 forge skills, 159 name-matched, 56 with an extracted hit source, 54 comparable
EOF
python3 -c "... exports_json/ailments.json ..."   # Bleed 53/3.0s, Ignite 40/2.5s, Poison 28/3.0s, Electrify 44/2.5s

# Runtime probes (venv in scratchpad, requirements.txt)
venv/bin/python scratchpad/probe.py   # minion DPS, armor/EHP across implementations, penetration semantics, Increased Armor affix
venv/bin/python -m pytest -q -p no:cacheprovider <25 calc test files>   # 607 passed, 1 failed
```

Web sources: `support.lastepoch.com` and `maxroll.gg` could not be fetched because egress to them is blocked. Only search-result snippets were available, so every web-derived statement below is marked **[community]** or **[official-snippet]** and counts as secondary evidence.

## 2. Production call graph (what users actually see)

| Frontend call (`frontend/src/lib/api.ts`) | Route | Engine chain |
|---|---|---|
| `POST /builds/<slug>/simulate` (:464), report, compare | `routes/builds.py:252` | `build_service.simulate_build` → `build_analysis_service.analyze_build` → `stat_engine.aggregate_stats` → `combat_engine.calculate_dps` + `monte_carlo_dps` → `defense_engine.calculate_defense` → `optimization_engine.get_stat_upgrades`. **No conversions are passed (:229-238)** |
| `POST /simulate/build` (:466) | `routes/simulate.py:281` | `simulation_service.simulate_full_build`. **`SimulateBuildSchema` (schemas/simulate.py:310-318) has no `spec_tree`, so skill-tree modifiers and conversions are always empty on this route.** With no `passive_tree`, `aggregate_stats` uses the synthetic modulo stat cycle (`stat_engine.py:559-583`) |
| `GET /builds/<slug>/analysis/boss/<id>` (:640), `/analysis/corruption` | `routes/analysis.py:129` | `boss_encounter.simulate_boss_encounter` → `_phase_dps` (own armor/res formula, `boss_encounter.py:145-182`) |
| `/simulate/encounter`, `/simulate/encounter-build` | `routes/simulate.py:244,261` | `builds.build_stats_engine.to_encounter_params` (`:151-164`) → `encounter.state_machine.EncounterMachine` → `encounter.enemy_damage_pipeline` → `domain.combat_validation.resolve_hit` |
| `/simulate/conditional` (:468) | `routes/conditional.py` | `StateEncounterIntegration.evaluate_damage` (`services/state_encounter_integration.py:76-83`) |
| `/simulate/multi-target`, `/simulate/rotation` | `routes/multi_target.py`, `routes/rotation.py` | caller-supplied `base_damage`, `cooldown`, `cast_time` (sandbox engines) |
| `/simulate/stats` | `routes/simulate.py:86` | `stat_engine.aggregate_stats`, **not** `stat_resolution_pipeline` (this contradicts `docs/KNOWN_LIMITATIONS.md`, "Verified Systems" bullet 1) |

Not reachable from any route (static import graph): `app/engines/combat_simulator.py`, `app/combat/*`, `app/domain/{fight_simulator,full_combat_loop,ward,resistance_shred,mana,cooldown,speed_scaling,ailments,ailment_stacking,ailment_scaling,status_interactions,…}`, `app/enemies/enemy_defense.py`, `stats/stat_data_integration.py`, `combat/*`, `buffs/*`, `build/*`, `frontend/src/lib/simulation.ts` (zero importers). `calculate_dps_vs_enemy` (`combat_engine.py:589`) has **no production caller**.

## 3. Trust matrix

Legend: "Data?" asks whether the inputs come from extracted game data. "Mechanic?" asks whether the formula has been shown to match the game. Tests are marked **self** when they only pin the implementation's own output or restate its formula, and **indep** when they check against an outside source. No row has **indep** tests.

| # | Domain | Used by API? (file:line) | Formula as implemented / constants | Data? | Mechanic? | Tests | Class | Justification |
|---|---|---|---|---|---|---|---|---|
| 1 | Skill base damage + level scaling | yes, `combat_engine.py:353-354`, `skill_calculator.py:83` | `base × (1 + level_scaling × (lvl−1))`; base and scaling hand-entered in `game_data/skills.json` (179) **and** duplicated in `SKILL_STATS` (`combat_engine.py:56-243`, 179, 4 drift) | **No.** `docs/skill_damage_audit.md` says the values were "estimated"/"calibrated" | **No.** In the 1.4.6 extract, 150/184 skills have empty `levelScaling`; no uniform per-level coefficient exists | self (snapshot `test_regression_suite.py:137`) | KNOWN INCORRECT | 53/54 comparable skills differ from the extracted hit base by >25% (median 24.6×, e.g. Fireball 110 vs 25) |
| 2 | Added-damage effectiveness | yes, `combat_engine.py:359` | `flat × added_damage_effectiveness`, default 1.0 | 4/179 set | Yes in principle [extracted `addedDamageScaling`] | self | KNOWN INCORRECT | 34/56 comparable skills disagree with the extracted `addedDamageScaling` (e.g. Earthquake 1.0 vs 6.0) |
| 3 | Flat added damage routing | yes, `skill_calculator.py:95-161` | sums `added_{spell,melee,throw,bow}_<type>` by tag/type | affix values from `affixes.json` midpoints | Plausible | self | PARTIALLY TRUSTED | Routing is reasonable. The weapon base damage of melee attacks is not modeled |
| 4 | Increased (additive) pool | yes, `increased_damage_calculator.py:42-60` | Σ of matching `*_pct` fields | partial | Matches the community model "increased adds, more multiplies" | self | PARTIALLY TRUSTED | Correct structure. Depends on stat-key mapping (39.2% passive coverage per KNOWN_LIMITATIONS) |
| 5 | More multipliers (main path) | yes, `more_multiplier_calculator.py:26-29`, `final_damage_calculator.py:78` | `Π(1+v/100)` over `[stats.more_damage_pct, spec_more]` | partial | Correct form | self | PARTIALLY TRUSTED | Only two "more" buckets exist, and `stats.more_damage_pct` is a single summed value, so several "more" sources would be added together |
| 6 | Encounter-build damage aggregation | yes, `builds/build_stats_engine.py:151-158` | `base × (1 + (spell+phys+elemental+more)/100)` | SKILL_STATS (row 1) | **No.** "More" is treated as additive, all type pools are summed regardless of the skill, and there is no level scaling or flat damage | self | KNOWN INCORRECT | Contradicts the main pipeline (row 5) |
| 7 | Damage conversion | partly: `simulation_service.py:253` but **dropped** in `build_analysis_service.py:229-238`; never on `/simulate/build` | `apply_conversions` then type re-pool | parsed from narrative text (`skill_tree_resolver`) | Plausible | self | PARTIALLY TRUSTED | Two of three user paths never apply it |
| 8 | Crit chance | yes, `stat_engine.py:780`, `combat_engine.py:375` | `(base + flat) × (1 + inc)`, cap 1.0; spec-tree crit added **after** increased | n/a | Formula matches the "1.4.3 spec" (owner-provided, not a public source) | self | PARTIALLY TRUSTED | Order bug for spec-tree crit. The dead `frontend/src/lib/simulation.ts:213` uses an additive formula with a 0.95 cap |
| 9 | Crit multiplier | yes, `crit_calculator.py:35` | `max(1, 2.0 + bonus/100)` | n/a | Base 200% matches [community] | self | PARTIALLY TRUSTED | Reasonable. Not checked against independent data |
| 10 | Hit variance (Monte Carlo) | yes, `combat_engine.py:403-441`, `constants/combat.py:17` | uniform ×[0.75, 1.25] | n/a | Only low-quality web pages give ±25% | self | UNVERIFIED | No authoritative source |
| 11 | Attack/cast speed | yes, `speed_calculator.py:30-33` | `skill.attack_speed × (1 + Σbonus)` | **No.** Hand-entered `attack_speed` often differs from extracted `1/useDuration` (e.g. Surge 1.6 vs 5.0, Void Cleave 1.1 vs 0.5) | Weapon attack speed and speed multipliers are not modeled | self | UNVERIFIED | Inputs are unsourced |
| 12 | Hits per cast | yes, `skill_calculator.py:90` | `1 + added` | spec tree | Simplified | self | PARTIALLY TRUSTED | Ailment stacking ignores it (row 13) |
| 13 | Ailment DPS (bleed/ignite/poison) | yes, `ailment_calculator.py:62-105`, `constants/combat.py:22-28` | `base_dps × (aps × chance × duration) × (1+inc)`. Bleed **43/4.0 s**, Ignite 40/**3.0 s**, Poison 28/3.0 s | **No.** `data/combat/ailments.json` (Bleed 3.0 s) exists but no code reads it | Extract 1.4.6: **Bleed 53/3.0 s, Ignite 40/2.5 s**, Poison 28/3.0 s; [community] Bleed 53/3 s | self. **1 failing**: `test_combat_engine.py:398` expects the chance capped at 100 | KNOWN INCORRECT | Bleed base −19%, bleed stacks +33%, ignite stacks +20%. Ignores hits-per-cast. Electrify (44/2.5), Frostbite (50), Damned, Time Rot are missing |
| 14 | Boss ailment reduction | **no**: `is_boss` never passed (`ailment_calculator.py:67`) | ×0.40 | constant | UNKNOWN | self | NOT IMPLEMENTED | Constant exists but nothing applies it |
| 15 | Enemy armor vs player DPS | main DPS: **not applied**. Boss: `boss_encounter.py:164-166` | boss: `a/(a+1000)`, **cap 0.80**; calculator: `a/(a+10·AL)`, cap 0.85; `combat_simulator.py:64` `a/(a+300)`; `stat_data_integration.py:92` `a/(a+300)` | enemy profiles community-estimated (KNOWN_LIMITATIONS) | Official-snippet: `x/(x+10a)`, cap 85% | self | KNOWN INCORRECT | Four formulas and two caps. The headline DPS includes no enemy mitigation and the response does not say so |
| 16 | Enemy resistance + penetration | boss: `boss_encounter.py:169-178`; encounter: `domain/penetration.py:36-51`; calculator (no caller): `enemy_mitigation_calculator.py:66-91` | boss: **min** resistance across all 6 types, no penetration; domain: `clamp(res−shred−pen, −100, 75)` (penetration before the cap); calculator: `max(0, min(75,res)−pen)` | community estimates | [community] penetration applies **after** the cap and can go negative; shred applies before the cap | self | KNOWN INCORRECT | Three incompatible semantics. Probe: pen 30 vs res 20 gives 0 (calculator) and −10 (domain); pen 10 vs res 100 gives 65 and 75 |
| 17 | Armor/resistance shred | encounter only (`armor_shred.py`, reached via `combat_validation`); `resistance_shred.py` unreachable | 100 armor per stack, 4 s; res 5%/2% boss, **max 10 stacks** | extract: shred ailments `maxInstances` 10 | [community] says 20 stacks, which conflicts with the extract | self | NOT IMPLEMENTED | Not in the main DPS path (KNOWN_LIMITATIONS #246) |
| 18 | Player armor mitigation | yes, `defense_engine.py:101-104` | `armour·(1+pct)/(…+1000)`, cap 0.85, applied to **all** damage | stats | [official-snippet] `x/(x+10a)`, cap 85%, **70% vs non-physical**, does not apply to DoT | self (`test_defense_engine.py:66` restates the formula) | KNOWN INCORRECT | Ignores the 70% non-physical rule. Area level fixed at 100. The calculators treat 70% as an armor multiplier (0.41 at 1000 armor), while the community describes 70% of the mitigation (0.35). Docstrings in `domain/armor.py:15,49-50` still say 75% |
| 19 | Player resistances | yes, `defense_engine.py:107-122` | each capped at 75, then the **mean of 7** becomes one mitigation layer | stats | Cap 75% matches [community] | self | PARTIALLY TRUSTED | Cap is right. Collapsing everything to the average is a modeling choice. Enemy penetration of +1%/area level [community] is ignored |
| 20 | EHP | yes, `defense_engine.py:125-176`; second impl `derived_stats.py:105-121` (`/simulate/stats` pipeline path) | `HP/(1−total)/(block·dodge·crit)·endurance + ward` vs armor-only `HP/(1−mit)` (no `armour_pct`, no resistances) | stats | Heuristic composite | self | UNVERIFIED | Two different EHP definitions. Neither is labelled as an estimate |
| 21 | Dodge | yes, `defense_engine.py:135-139` | `r/(r+1000)`, cap 0.85 | stats | `x/(x+10a)`, 85% [community, consistent] | self | PARTIALLY TRUSTED | Area level fixed at 100 |
| 22 | Block | yes, `defense_engine.py:129-132`; `domain/block.py` uses a different semantic (fraction input, chance cap 0.85) | `BE/(BE+1000)`, **no 85% cap** | stats | [official-snippet] depends on area level, cap 85%; exact formula UNKNOWN | self | UNVERIFIED | Divisor unsourced. Cap missing in the production path |
| 23 | Endurance | yes, `defense_engine.py:160-169` | factor `1/(1 − t·r)`, cap 60 | class base 20 / threshold 22 | The exact value is `(1−t) + t/(1−r)`, so this is an approximation | self | PARTIALLY TRUSTED | About 1.5% low at default values. Does not handle DoT or ward ordering |
| 24 | Ward decay | yes, `defense_engine.py:181-183`; dup `domain/ward.py` | `0.4·W/(1+0.5R)` (`constants/defense.py:13`) | n/a | [community + dev patch notes] current formula `(0.2W + 0.00005W²)/(1+0.5R)`; `0.4W` is the **old** formula | self | KNOWN INCORRECT | Outdated formula. The module docstring (`defense_engine.py:12`) describes a third formula |
| 25 | Ward retention per INT | yes, `stat_engine.py:313` (2.0) | 2%/pt; `constants/defense.py:16` and `domain/ward.py:56` use **4%/pt**; `ACCURACY_AUDIT.md` C-15 claims 4 | n/a | [official-snippet] 2%/pt, [community] 4% | self | PARTIALLY TRUSTED | The production value matches the official snippet. The constant and the audit doc are stale |
| 26 | Crit avoidance / glancing blow | yes, `defense_engine.py:142-154` | enemy crit rate 0.35 and ×1.5 (`constants/defense.py:51-52`, invented); glancing turns crits into normal hits | n/a | `constants.json` and ACCURACY_AUDIT both note glancing blow = 35% less damage on glancing hits | self | KNOWN INCORRECT | Mechanic misread and constants invented |
| 27 | Stun avoidance | yes, `defense_engine.py:188` | `s/(s+1000)` | stats | UNKNOWN | self | UNVERIFIED | Unsourced |
| 28 | Class base stats + attributes | yes, `stat_engine.py:225-316,764-771` | 110 HP, 51 mana, Vit 6 HP, Dex 4 dodge, Str 4% armor | n/a | Comments say "in-game sheet". Not reproducible from the repo | self | PARTIALLY TRUSTED | Plausible but not independently checked |
| 29 | Mastery / keystone / passive fallback | yes, `stat_engine.py:264-297,559-583,670-675` | hard-coded bonuses (e.g. Juggernaut +200 armor); unknown keystone defaults to `{spell 10, hp 50}`; Lich +8 ward/pt; modulo stat cycle when no passive data | **No.** Fabricated | No | self | KNOWN INCORRECT | Injects invented stats into DPS and EHP. The `/simulate/build` route triggers the modulo cycle whenever `passive_tree` is omitted |
| 30 | "Increased Armor" affix | yes, `stat_engine.py:609-631` + StatPool | stat_key `armour` (flat); the T5 roll adds **+29 flat armour** instead of +29% | affix data | No | none found | KNOWN INCORRECT | Probe: `armour 0 → 29`, `armour_pct` unchanged |
| 31 | Minion damage | yes, through `calculate_dps` | minion skills scaled by player crit/speed and `minion_damage_pct` only; `minion_attack_speed/crit/*` unused | No | No | self | KNOWN INCORRECT | Probe: Summon Wolf DPS 343, Summon Bear 492. `KNOWN_LIMITATIONS.md` says these show 0 |
| 32 | Leech / sustain | defense: sustain score only (`defense_engine.py:191-196`); encounter `domain/leech.py` (cap 10%) | heuristic points | n/a | Leech duration (3 s) not modeled | self | UNVERIFIED | The score is a made-up heuristic |
| 33 | Mana / costs | no (`mana_cost` in skills.json is never read by DPS; `domain/mana.py` unreachable) | — | partial data | — | self (unit only) | NOT IMPLEMENTED | DPS assumes infinite mana |
| 34 | Cooldowns / rotation | `/simulate/rotation` only | caller-supplied `cooldown`, `cast_time` | caller input | Sandbox | self | UNVERIFIED | Correctness depends entirely on user input |
| 35 | Conditional modifiers | `/simulate/conditional` (`state_encounter_integration.py:76-83`); not in main DPS | "multiplicative" modifiers turned into a % and **added** to the increased pool; only spell/physical/damage_pct counted | caller input | More-vs-increased violated | self | KNOWN INCORRECT | Contradicts row 5 |
| 36 | Boss/encounter templates | encounter + boss routes | hard-coded HP, armor, res (`encounter/boss_templates.py:119-163`) | No | — | self | UNVERIFIED | Invented enemies |
| 37 | Area-level scaling | none in API paths (fixed 100: `constants/defense.py:42-47`) | — | — | Every armor, dodge and block formula depends on area level | — | NOT IMPLEMENTED | All defense numbers assume area level 100 |
| 38 | Composite scores (survivability, sustain, Build Score, "Overall Winner 60/40") | yes, `defense_engine.py:198-206`; `frontend/.../BuildScoreCard.tsx:34,70`; `SimulationComparison.tsx:85` | weighted heuristics | n/a | Not game mechanics | self | UNVERIFIED | Shown without a "heuristic" label |

Extra cross-cutting row: DPS vs enemy (`calculate_dps_vs_enemy`) is fully implemented and tested but is **dead in production**. Its tests prove nothing about anything users see.

## 4. Duplicate-implementation table

| Formula | Implementations (file:line) | Divergence |
|---|---|---|
| Armor mitigation | `defense_engine.py:101-104` (`/(a+1000)`, cap .85, all damage); `derived_stats.py:87,118` (`/(a+10·100)`, no `armour_pct`); `domain/armor.py:62` (`/(a+10·AL)`, non-physical ×0.70, cap .85·.70); `enemy_mitigation_calculator.py:53` (same as domain); `combat_validation.py:149-153` (physical only, non-physical **bypasses** armor); `boss_encounter.py:165-166` (`/(a+1000)`, **cap 0.80**); `engines/combat_simulator.py:64-65,143` (`/(a+300)`, cap 0.80); `stats/stat_data_integration.py:92` (`/(a+300)`); `frontend/src/lib/simulation.ts:299` (`/(a+1000)`, dead) | **9 implementations, 3 divisors (300 / 1000 / 10·AL), 3 caps (0.80 / 0.85 / 0.595), 3 non-physical rules (100% / 70%-of-armor / 0%)** |
| Dodge | `defense_engine.py:136-137`; `derived_stats.py:128-141`; `domain/dodge.py:43-45` | Same form. Area level fixed in two of the three |
| Block | `defense_engine.py:130` (`BE/(BE+1000)`, no cap); `domain/block.py:33-55` (effectiveness given as a fraction, chance cap 0.85) | Different input semantics |
| Resistance cap / penetration | `defense_engine.py:107-113`; `domain/resistance.py:31-53` (floor −100); `domain/penetration.py:49-51` (before cap); `enemy_mitigation_calculator.py:66-84` (after cap, floor 0); `boss_encounter.py:169-178` (min across all types) | 3 penetration semantics |
| Ward decay | `defense_engine.py:181-183`; `domain/ward.py` (+INT 4%/pt) | Same outdated formula. INT retention 2 vs 4 |
| INT → ward retention | `stat_engine.py:313` (2.0); `stat_resolution_pipeline.py:70` (2.0); `constants/defense.py:16` (4.0, used by `domain/ward.py:56`) | 2 vs 4 |
| Crit | `crit_calculator.py:26-35`; `domain/critical.py:24-26`; `combat/crit/critical_engine.py`; `frontend/src/lib/simulation.ts:213` (additive, cap 0.95) | Frontend copy is dead but contradicts the backend |
| Skill table | `game_data/skills.json` (registry, Flask context); `combat_engine.SKILL_STATS` (fallback **and** the only source for `build_stats_engine.py:125` and encounter-build) | 179 each. 4 drifted entries (Aura of Decay 25 vs 20, Umbral Blades ls .08 vs .10, plus case-duplicate keys "Aura Of Decay" and "Mark For Death" with different values) |
| Constants source | `app/constants/*.py`; `app/game_data/constants.json` (e.g. `endurance_threshold_default: 0`, `endurance_damage_reduction: 0.6`, `base_hit_chance: 0.92`); `backend/src/constants/defense.ts` | Three constant stores that disagree |
| Stat aggregation | `stat_engine.aggregate_stats`; `stat_resolution_pipeline` (8-layer, reached via `domain/build_state`); `builds/build_stats_engine` (wraps stat_engine and adds its own damage formula); `build/*` (unreachable) | Docs say the 8-layer pipeline serves `/simulate/stats`. It does not |
| EHP | `defense_engine.calculate_defense`; `derived_stats.compute_effective_health` | Different definitions |

## 5. "We have the data" vs "we understand the mechanic"

| Item | Data available? | Used? | Mechanic understood? |
|---|---|---|---|
| Skill hit base damage | Partly. The extract has direct `damageSources` for 81/184 skills (`skill_mechanics_coverage_1.4.6.md`), and the extractor says these are "not complete base damage" | **No.** Forge uses hand-calibrated values | No. For melee skills the extract shows base 2 plus effectiveness, which implies weapon-damage scaling that Forge does not model |
| Added damage effectiveness | Yes (`addedDamageScaling`) | No (4/179 set by hand) | Yes |
| Skill use speed | Yes (`useDuration`, `speedMultiplier`) | No | Partly |
| Ailment base / duration | Yes (`exports_json/ailments.json`, 1.4.6; `data/combat/ailments.json` in repo) | No (hard-coded constants) | Stacking model plausible |
| Armor/dodge/block curves | Not in the extract | — | Armor/dodge: community-consistent. Block: UNKNOWN |
| Ward decay | Not in the extract | — | Outdated |
| Enemy armor / resistances | `actors.json` exists in the extract (not evaluated here, UNKNOWN) | No; enemy profiles are community estimates | Penetration semantics inconsistent |

## 6. Trust labels in API output

- `simulate_full_build` / `analyze_build` return `stats, dps, monte_carlo, defense, stat_upgrades, …`. They carry **no** `trust`, `provenance`, `data_version` or `confidence` field. The only data-quality fields are `conversion_data_gap` (`simulation_service.py:75-105`) and `warnings` (`boss_encounter.py:102,138`).
- `SkillStatDef.data_version="hardcoded"` exists internally (`combat_engine.py:46-49`) but is never serialized.
- Frontend: `V2TrustBadge` appears only on `TrustedDataSupportMatrixPage`, `TrustedDataExplanationPage` and `PreV3MechanicalReadinessPage`. The analysis cards (`OffenseCard`, `DefenseCard`, `AnalysisPanel`, `BuildScoreCard`) have no estimate or trust wording. The only notices are a global Known Limitations link (`AppLayout.tsx:108`) and a benchmark disclaimer in `OffenseDefenseSplit.tsx:211`.
- `docs/migration/V2_5_SUPPORT_MATRIX.md:48-49` admits "planner-calculable count is 0 / stable-calculable count is 0". So the V2 trusted-data effort does not yet power any calculation, and the legacy engines described above do.

## 7. Claims-doc verification

| Claim | Doc | Verdict |
|---|---|---|
| "Ailment DPS … BLEED_BASE_RATIO=0.70, IGNITE_DPS_RATIO=0.20, POISON_DPS_RATIO=0.30" | KNOWN_LIMITATIONS.md | **Stale.** The code uses flat 43/40/28 per second |
| "34 skills" have approximate base damage | KNOWN_LIMITATIONS.md, skill_damage_audit.md | **Understated.** All 179 are hand-entered, and 53/54 comparable skills disagree with the extract |
| Minion skills "will see 0 hit-DPS" | KNOWN_LIMITATIONS.md | **False.** Non-zero DPS is computed from player stats |
| `/api/simulate/stats` returns the post-Layer-8 pipeline snapshot | KNOWN_LIMITATIONS.md | **False.** The route calls `stat_engine.aggregate_stats` |
| Armor shred consumed at `combat_engine.py:642` | KNOWN_LIMITATIONS.md | Only inside `calculate_dps_vs_enemy`, which has no production caller |
| "Int = 4% Ward Retention" (C-15 fixed) | ACCURACY_AUDIT.md | Production now uses 2%. The constant still says 4 |
| ward decay `0.4×(W−T)/(1+0.5R)` "✓" | ACCURACY_AUDIT.md | Outdated per [community / dev patch notes] |
| `BOSS_AILMENT_REDUCTION` "constant ✓, application MISSING" | ACCURACY_AUDIT.md | Still not applied |
| "This formula is correct per Last Epoch mechanics" | dps_audit_report.md §1 | Structure only. Inputs (row 1, 2, 11) are wrong |
| Everything "VERIFIED: 1.4.3 spec §…" | code comments | The "spec" was supplied by the owner and is not in the repo. UNVERIFIABLE |

## 8. Tests

- Ran 25 calculation-related test files: **607 passed, 1 failed** (`tests/test_combat_engine.py::TestAilmentDPS::test_ailment_chance_capped_at_100`, which expects bleed DPS at 200% chance to equal 100%; the engine gives 619 vs 310). Either the test or the engine is wrong. Both cannot be right.
- Kinds of assertion: formula restatement (e.g. `test_defense_engine.py:66` "Armor/(Armor+1000)") and pinned snapshots (`test_regression_suite.py:123-170`, e.g. Fireball DPS == 549). The file says outright that snapshots are "pinned output values from the live engine". 0 tests compare against extracted game data, in-game measurements or an independent calculator.

## 9. UNKNOWNs

- Exact block-effectiveness formula and area-level coefficient (official page unreachable).
- Whether ±25% hit variance exists in 1.4.x.
- Max shred stacks (extract `maxInstances` 10 vs [community] 20). The meaning of `maxInstances` was not confirmed.
- Whether enemy penetration of +1%/area level still applies in 1.4.x.
- Whether extracted ailment `damage` values are per second or per full duration. The per-second reading was assumed because Poison 28 and Electrify 44 match the Forge per-second constants.
- How extracted melee "base 2" combines with weapon damage. This decides whether Forge's 80–160 bases are approximating weapon damage.
- Enemy armor/resistance values in `last-epoch-data/exports_json/actors.json` (not examined).
- Correctness of class base stats (110 HP, 51 mana, endurance threshold 22). The repo says they come from in-game sheets, and no capture is stored.
- Runtime behaviour when the DB has no passive nodes (DB-dependent; not run).

## 10. What this does NOT prove

- It does not show that any formula marked PARTIALLY TRUSTED is correct. It only shows that the formula is consistent with secondary sources.
- Web evidence is search-snippet level only (support.lastepoch.com and maxroll.gg fetches were blocked). Treat [official-snippet] as unconfirmed.
- The extracted-data comparison covers only the 54 skills that have a direct hit damage source. The extractor itself calls `damageSources` partial. A large ratio proves that Forge values are not the extracted values. It does not prove what the in-game tooltip shows.
- Reachability comes from static import analysis. A reachable module may still go unused at runtime, and the reverse can happen through dynamic imports.
- No in-game measurement was taken. No DPS or EHP number was checked against the live game.
- Crafting, FP, BIS search and optimizer ranking are only covered where they consume the engines above.
