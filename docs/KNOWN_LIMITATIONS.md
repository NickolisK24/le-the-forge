# Known Limitations

**Last updated:** 2026-04-22 (post-launch documentation audit)

The Forge is in public beta. Accuracy is the highest priority of the project, and the calculations that power DPS, EHP, crafting curves, and upgrade rankings are all open to inspection in this repository. This document exists so that users know, up front and without hunting through issue threads, what has been verified against real gameplay, what is an approximation, and what is not yet modeled at all.

If something here is out of date or incorrect, please open an issue or comment on an existing one — keeping this document accurate is part of the project, not an afterthought.

---

## Verified Systems

These systems have been validated either against documented game mechanics, mathematical proofs, or locked regression outputs so they produce the same result every run.

- **8-layer stat pipeline** — implemented at `backend/app/engines/stat_resolution_pipeline.py`. The layer ordering (base stats → flat → increased → more → conversions → derived → registry-derived → conditional) is asserted by snapshots and regression tests. Verification means: every layer is exercised in the test suite, layer order cannot be silently reordered without failing regression locks, and the `/api/simulate/stats` endpoint returns the post-Layer-8 snapshot.
- **Deterministic DPS** — `combat_engine.calculate_dps()` is pure and produces byte-identical output for identical input. Verification means: regression tests pin known-good DPS numbers for representative builds; any formula change forces a conscious test update.
- **Monte Carlo seeding** — `monte_carlo_dps()` accepts a seed and reproduces identical variance distributions on re-run. Verification means: seeded runs produce identical `p25/p50/p75/stddev` values across executions, across test orderings, and across adversarial RNG pollution in the surrounding process.
- **Craft engine RNG determinism** — `simulate_craft_attempt(..., seed=N)` threads the seeded RNG through `apply_craft_action` → `roll_fp_cost` so two invocations with the same seed produce byte-identical `(success, fp_spent, fractured, item_after)`. Verified by PR #225 with 10 isolated runs, 10 full-suite runs, and 200 invocations against deliberately polluted global RNG state.
- **EHP and resistance capping** — Layer-7 derived stats enforce the 75% resistance cap, combine armour and resistance mitigation layers, and report strengths/weaknesses from the computed deltas. Verification means: resistance cap boundary conditions at 0%, 75%, and >75% are tested, and the cap enforcement logs a warning when it trips.
- **Last Epoch Tools build import** — class, mastery, passive tree, skill loadouts, spec trees, and gear all import successfully from live Last Epoch Tools URLs, including base items, affixes, and unique resolution. Verification means: unit fixtures for representative builds round-trip through the import pipeline with zero missing fields for the canonical meta builds.

## Approximate or Unverified Systems

These systems are computed from formulas believed to match the game, but the underlying input values have not been validated against live in-game benchmarks. Numbers from these systems may be systematically high or low.

- **Skill base damage values for 34 skills** — confidence approximately 70–80%. Thirty-four skills (out of 179 in `backend/app/game_data/skills.json`) have `base_damage` values that were calibrated from adjacent skills rather than extracted from verified game data. The calibration methodology and per-skill values are documented in `docs/skill_damage_audit.md`. The canonical list is tracked in issue [#148](https://github.com/NickolisK24/le-the-forge/issues/148). To verify: use each listed skill on the in-game training dummy with no gear or passives and report the observed base damage.
- **Ailment DPS (Bleed, Ignite, Poison)** — computed from `calc_ailment_dps()` at `backend/app/domain/calculators/ailment_calculator.py:62` using documented stack formulas (BLEED_BASE_RATIO=0.70, IGNITE_DPS_RATIO=0.20, POISON_DPS_RATIO=0.30). These constants match community documentation but have not been reconciled against live DoT DPS meters. Tracked in [#159](https://github.com/NickolisK24/le-the-forge/issues/159). To verify: compare The Forge's reported ailment DPS to in-game training dummy DoT numbers on single-damage-skill builds.
- **Enemy armour and resistance profiles** — values in `data/entities/enemy_profiles.json` (training dummy through boss archetypes) are community-sourced approximations, not datamined extracts. They affect every DPS-vs-enemy calculation. Tracked in [#162](https://github.com/NickolisK24/le-the-forge/issues/162). To verify: report real armour and resistance values from Last Epoch enemy files or in-game testing.
- **Maxroll build import** — the importer parses class, mastery, passives, skills, and gear but has not been exhaustively validated against live Maxroll URLs. Users may encounter builds where a field imports silently wrong (wrong mastery ID, skipped skill, or a mapping gap). Tracked in [#163](https://github.com/NickolisK24/le-the-forge/issues/163).
- **Passive tree stat resolution** — all 541 passive nodes now load their real stat payload from the game data file rather than the estimated modulo cycle, and 39.2% of stat entries (79.8% of stat keys that appear on ≥2 nodes) resolve into numeric `BuildStats` fields. The four S4 meta builds — Ballista Falconer, Warpath Void Knight, Profane Veil Warlock, Lightning Blast Runemaster — are validated with zero stat leakage into `special_effects` for their canonical allocations. The remaining 60.8% of stat entries are preserved in `special_effects` (conditional mechanics, proc triggers, flag-style effects). Coverage expansion is ongoing under [#156](https://github.com/NickolisK24/le-the-forge/issues/156).
- **LE Tools / Maxroll item-ID resolution residuals** — the gear importer handles the canonical meta item set cleanly, but rare or newly introduced base items and affixes may land in `gear_missing` when their IDs fall outside the current lookup maps. Tracked in [#247](https://github.com/NickolisK24/le-the-forge/issues/247).

## Known Incomplete Systems

These features are visible somewhere in the UI or API surface, but the modeling is deliberately partial and will report zero, missing, or placeholder values for some builds.

- **Minion DPS is not modeled** — minion-summoning skills (Summon Bear, Summon Wraith, Thorn Totem, Ballista, 28 skills total) are correctly classified as "minion" in `backend/app/skills/skill_classifier.py` and excluded from primary-skill auto-detection, but there is no `MinionDamageEngine`. Necromancer and Beastmaster minion-focused builds will see 0 hit-DPS from their primary skill. Tracked in [#157](https://github.com/NickolisK24/le-the-forge/issues/157).
- **Conditional stat bonuses are not wired into DPS** — Layer 8 of the stat pipeline evaluates conditional modifiers (`apply_conditional_stats()` at `backend/app/engines/stat_resolution_pipeline.py:442`) and the infrastructure accepts a `runtime_context`, but `simulate_full_build()` at `backend/app/services/simulation_service.py:213` does not forward runtime context or conditional modifiers into the combat engine. Bonuses like "20% more damage while moving" or "30% increased damage vs bosses" are computed but not consumed. Tracked in [#158](https://github.com/NickolisK24/le-the-forge/issues/158).
- **Armor-shred stack accumulation is not modeled** — `armor_shred_amount()` returns a point-in-time shred value that `combat_engine.py:642` consumes on a per-hit basis, but there is no accumulation model over fight duration. Against heavily armoured bosses this can understate DPS by 20–50%. Tracked in [#246](https://github.com/NickolisK24/le-the-forge/issues/246).
- **Classes landing page is a partial redesign** — `/classes` routes each class to `/build?class=<name>`, but there are no per-mastery "Create Build" buttons, no popular-builds panel, and no passive/skill tree previews. Tracked in [#161](https://github.com/NickolisK24/le-the-forge/issues/161).
- **Simulation dashboard lacks a benchmark grade** — the results page shows DPS breakdown, upgrade priorities, and an upgrade-priority matrix, but there is no build grade (S/A/B/C/D) anchored to per-class DPS benchmarks, no per-stat contextual tooltip, and no class/mastery average comparison. Tracked in [#160](https://github.com/NickolisK24/le-the-forge/issues/160).

## Data Pipeline Status

- **Last Epoch patch:** 1.4.3, Season 4 (from `data/version.json`).
- **Data sync timestamp:** `data/version.json` last modified 2026-04-21 (pre-launch sync).
- **Schema version:** 1.0.0-beta.
- **Coverage:** 179 skills, 1,163 affix entries, 541 passive nodes, 8 enemy profiles, 52 data files validated by `flask validate-data`.
- **Known data gaps:** passive-node stat-key coverage at 39.2%; enemy armour/resistance values are community estimates; 34 skills have calibrated-estimate base damage. See the preceding sections for the tracking issues.
- **Validation command:** `FLASK_APP=wsgi.py PYTHONPATH=. flask validate-data` runs at CI time on every PR and must pass before merge.

## How to Report Issues

The fastest path to improving accuracy is telling us when the numbers do not match the game.

- **GitHub Issues:** https://github.com/NickolisK24/le-the-forge/issues — please include:
  - The build (class, mastery, primary skill, a link to the build if you saved one on The Forge or a shareable Last Epoch Tools URL).
  - What number The Forge reported vs what you observed in game.
  - How you observed the in-game number (training dummy, combat log, boss fight, etc.).
  - Any relevant screenshots.
- **Import failures** are auto-captured via a Discord webhook and recorded in the `ImportFailure` table. If you can import a build via `POST /api/import/build`, the import payload is automatically logged for analysis — simply mention the timestamp and source URL in the issue.
- **Label priorities:** please apply `priority: high`, `priority: medium`, or `priority: low` if you can assess impact. If the issue falls under community verification (skill damage, enemy armour, ailment DPS), consider adding the `community-verification` label.

The single most impactful contribution right now is one or more data points per skill on the training dummy — see [#148](https://github.com/NickolisK24/le-the-forge/issues/148) for the full list of skills needing validation.

---

Thank you for using The Forge while it is still rough around the edges. The project aims to be accurate enough that theorycrafting decisions can be made from its numbers alone; every bug report, benchmark, and data correction you contribute moves it closer to that bar.
