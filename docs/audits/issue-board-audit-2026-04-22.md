# Issue Board Audit — 2026-04-22

**Date:** 2026-04-22
**Branch:** `claude/complete-issue-audit-ZonOT`
**Repository:** `NickolisK24/le-the-forge`

## Totals

| Metric | Count |
|---|---|
| Open issues evaluated | 11 |
| Closed as resolved | 2 (#223, #155) |
| Kept open — still valid (unchanged scope) | 4 (#163, #162, #159, #157, #148 → 5) |
| Kept open — partially resolved (body updated) | 3 (#161, #160, #158, #156 → 4) |
| Flagged for manual review | 0 |
| New issues opened for documented gaps | 2 (#246, #247) |

_Note on counts: the "still valid" bucket holds 5 issues (#163, #162, #159, #157, #148) and the "partially resolved" bucket holds 4 issues (#161, #160, #158, #156). 2 + 5 + 4 = 11._

A `needs-manual-review` label was NOT created because no issue landed in that bucket after re-evaluation.

## Key Correction

`data/version.json` exists at the repository root (`patch: "1.4.3"`, `season: 4`, `version: "1.0.0-beta"`). No new issue was opened for missing versioning data.

Issue #223 (referenced in the audit prompt as potentially the versioning tracker) is actually the **determinism bug** for `simulate_craft_attempt`. It was resolved by PR #225 (merged 2026-04-15) and closed in this audit based on code verification.

## Per-issue Breakdown

### #223 — Determinism bug → **CLOSED (completed)**

Fully resolved by PR #225 (merged 2026-04-15).

- `backend/app/engines/craft_engine.py:704` — `simulate_craft_attempt` creates `rng = random.Random(seed)`.
- `backend/app/engines/craft_engine.py:734` — threads rng through `apply_craft_action(..., rng=rng)`.
- `backend/app/engines/craft_engine.py:76-104` — `apply_craft_action` signature includes `rng: Optional[random.Random]` and forwards to `roll_fp_cost(action, rng=rng)` at line 104.
- `backend/tests/test_architecture_determinism.py:430-439` — xfail marker replaced with a fix-branch comment; test asserts byte-identical results on identical seeds.

### #163 — Maxroll import coverage unknown → **KEEP OPEN (re-verified)**

- `backend/app/services/importers/maxroll_importer.py` — 1240 lines, `MaxrollImporter.parse()` at line 686.
- `backend/tests/test_build_import.py:1757-2321` — unit tests for URL parsing, class/mastery, skills, normalization, specialized format.
- End-to-end validation against live Maxroll builds has not been executed. Community verification remains the ask.

### #162 — Enemy armor values unverified → **KEEP OPEN (re-verified)**

- `data/entities/enemy_profiles.json` still contains the original estimated armor/resistance values.
- `backend/app/domain/enemy.py` `EnemyArchetype` still hardcodes the same base stats.

### #161 — Classes page redesign → **KEEP OPEN (reduced scope)**

Partial: `frontend/src/pages/classes/ClassesPage.tsx:155` wires each class to `/build?class=<name>`. Issue body updated.

Remaining: per-mastery routing, popular-builds link, tree previews, base-stat summary.

### #160 — Simulation page UX overhaul → **KEEP OPEN (reduced scope)**

Partial: `SimulationDashboard.tsx` has `DpsBreakdown` (line 78), `UpgradeChart` (line 250), `UpgradePriorityMatrix` (line 346). Issue body updated.

Remaining: build grade tier, stat tooltips, primary-skill DPS lead, class/mastery comparison.

### #159 — Ailment DPS accuracy → **KEEP OPEN (re-verified)**

- `backend/app/domain/calculators/ailment_calculator.py:62` — `calc_ailment_dps()`.
- `backend/app/skills/skill_execution.py:221-229` — ailment DPS integration.
- In-game benchmarking still not performed.

### #158 — Conditional stat bonuses excluded from DPS → **KEEP OPEN (reduced scope)**

Partial at pipeline layer:
- `backend/app/engines/stat_resolution_pipeline.py:281-282` — `resolve_final_stats()` accepts `conditional_modifiers` / `runtime_context`.
- `backend/app/engines/stat_resolution_pipeline.py:442-447` — `apply_conditional_stats()` runs during Layer 8.

Remaining: `simulate_full_build()` at `backend/app/services/simulation_service.py:213` has no `runtime_context` parameter and does not forward to DPS. Frontend combat-context panel does not exist. Issue body updated.

### #157 — Minion skill DPS not modeled → **KEEP OPEN (re-verified)**

No `minion_dps`, `MinionDamageEngine`, or `MinionStatDef` exist in `backend/app/`. Classifier at `skill_classifier.py:20` still labels these correctly but there is no DPS path.

### #156 — Passive tree stats use estimated values → **KEEP OPEN (reduced scope)**

Substantial progress: resolver is operational at `backend/app/services/passive_stat_resolver.py`, `stat_engine.py:710-722` skips the modulo fallback when real data covers a node. README documents 39.2% numeric coverage (commit `0b1d3af`).

Remaining: stat-key-map expansion beyond ~39% coverage, in-game tooltip parity verification. Issue body updated.

### #155 — Gear does not import from LE Tools → **CLOSED (completed)**

Fully implemented:
- `backend/app/services/importers/lastepochtools_importer.py:938-1200+` — `_parse_gear()` with base-item map, slot aliases, rarity map, multi-strategy ID / affix resolution.
- `backend/app/routes/import_route.py:244-251` — `_map_let_build()` calls `_parse_gear()` and returns real gear; original `gear_note` ("Gear not imported — …") no longer emitted.

Residual ID-coverage work tracked as new issue #247.

### #148 — Skill base damage community validation → **KEEP OPEN (re-verified)**

- `backend/app/game_data/skills.json` now has 179 skills (up from 175).
- `docs/skill_damage_audit.md` unchanged. Community validation remains the external ask.

## New Issues Opened

### #246 — Armor shred stack accumulation not modeled in combat simulator

Labels: `engine`, `data-accuracy`, `priority: medium`

Derived from `docs/dps_audit_report.md` GAP 5. `armor_shred_amount` is computed in `combat_engine.py:642-644` but no stack-accumulation model exists over fight duration.

### #247 — LE Tools import: track residual base-type and affix ID resolution gaps

Labels: `import`, `data-accuracy`, `priority: medium`

Follows from #155. `_parse_gear` still records unresolved base-type/affix IDs in `gear_missing`. Tracks the ID-map coverage work that was out of scope for the core "gear does not import" blocker.

## Recommendations (Structural Observations)

1. **Audit-trail discipline.** Issues #156, #155, and #158 moved substantially since filing, but their original bodies described the problem as if no work had been done. When a PR resolves part of an issue, update the issue body with a "Remaining" section so triage always reflects current state.

2. **Known-limitation vs. issue alignment.** Issue #156 has been tracked in the README as a "Known Limitation" with quantified coverage metrics while the GitHub issue stayed frozen. Cross-reference the README section from the issue body (or vice versa) so they can't drift.

3. **Separate community verification from engineering work.** Issues #148, #159, #162, #163 all ask for community-driven verification. Consider a consistent `community-verification` label and omit them from engineering-cycle triage so they don't compete for attention with actionable engineering work.

4. **Determinism-class bugs set a strong bar.** #223 was resolved with evidence of 10 isolated runs, 10 full-suite runs, and 200 adversarial invocations. That evidence bar should be the default template for any future RNG-reproducibility bug.
