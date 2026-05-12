# Forge-Safe Legacy Affix Comparison Review

Generated: 2026-05-11

## Report Source

Command used:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_forge_safe_legacy_affix_comparison.py --bundle-path D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json --output docs\generated\forge_safe_legacy_affix_comparison.json --limit 2000
```

Feature flags used:

- `FORGE_SAFE_AFFIX_CATALOG_ENABLED=true`
- `FORGE_SAFE_AFFIX_BUNDLE_ENABLED=true`
- `FORGE_SAFE_AFFIX_BUNDLE_PATH=D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json`

Source bundle:

`D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json`

Saved report:

`docs/generated/forge_safe_legacy_affix_comparison.json`

The script invokes `GET /experimental/forge-safe-affixes/compare-legacy?include_details=true&limit=2000` through the local Flask test client. The endpoint's normal list cap is raised only inside the diagnostic process so the full response can be preserved. The saved report metadata confirms `read_only=true`, `experimental=true`, `production_consumer=false`, `production_safe=false`, exact `affix_id` matching, and no truncated detail lists.

## Summary Counts

| Metric | Count |
| --- | ---: |
| legacy_affix_count | 1113 |
| bundle_affix_count | 1098 |
| matched_count | 1098 |
| missing_in_legacy_count | 0 |
| missing_in_bundle_count | 14 |
| slot_difference_count | 1098 |
| tier_difference_count | 1098 |
| stat_key_difference_count | 1098 |
| structural_difference_count | 466 |
| modifier_count_difference_count | 526 |
| safety_difference_count | 0 |
| difference_count | 1098 |

## A. Identity Blockers

No bundle affixes are missing from legacy by exact numeric `affix_id`.

Legacy has 14 affixes missing from the Forge-safe bundle. These are immediate identity blockers for any migration that needs full legacy coverage:

- 74: Less Damage Taken on Block
- 165: Idol Mage Less Damage Over Time Taken While Channelling
- 213: Idol Primalist Chance To Gain Haste When You Summon A Totem
- 262: Idol Acolyte Less Damage Over Time Taken While Transformed
- 267: Idol Acolyte Less Health Regen And Damage Taken Over Time
- 289: Idol Acolyte Less Damage Over Time Taken
- 369: Sentinel Reduced Channel Cost
- 699: of the Timelost Outcast
- 710: Experimental Armor applies to Damage over Time
- 781: Boardman's Legacy Reforged
- 921: Idol Increased Armor and Armor Applies to DoTs
- 966: Added Critical Strike Chance and Chance to cast Shurikens on Bow Crit
- 972: Increased Melee Area of Effect and Chance to Summon Forged Weapon on Melee Hit
- 1079: Less Damage Taken on Block and Block Effectiveness applies to Damage over Time

The match strategy is exact numeric `affix_id`; no fuzzy name matching is performed. Migration risk remains high until missing legacy IDs are classified as intentionally excluded or restored in the bundle.

## B. Slot and Item Applicability Blockers

All 1098 matched affixes have slot differences. The dominant pattern is vocabulary mismatch between legacy Forge slot names and bundle item type names, for example:

- `amulet` vs `AMULET`
- `helm` vs `HELMET`
- `chest` vs `BODY_ARMOR`
- `axe_1h` vs `ONE_HANDED_AXE`
- `mace_2h` vs `TWO_HANDED_MACE`
- `spear` vs `TWO_HANDED_SPEAR`

This blocks planner and crafting migration because item applicability cannot be trusted until an explicit adapter maps both vocabularies and proves equivalence.

Class restrictions are also a migration concern. Legacy records carry class requirements for 659 matched affixes, while the compact bundle comparison records expose no class requirement field. That does not prove the bundle lacks class semantics, but it does prove this comparison output cannot validate class/category gating yet.

## C. Tier and Value Blockers

All 1098 matched affixes have tier differences.

The compact report shows no tier count mismatch and no malformed-tier signal mismatch among matched records. The endpoint notes therefore point to min/max value differences rather than tier list shape differences.

This blocks crafting, stat aggregation, and simulation migration until value-scale policy is validated. The current report is enough to show the systems disagree, but not enough to authorize normalizing those values or changing gameplay math.

## D. Stat-Key and Modifier-Routing Blockers

All 1098 matched affixes have stat-key differences. Legacy uses one Forge `stat_key` per affix, while the bundle exposes modifier/property/reference candidates. Examples:

- `void_penetration` vs `ADDED`, `Penetration`, `ADDED:Penetration:Void`, `equipment:0`
- `armour` vs `INCREASED`, `Armour`, `INCREASED:Armour:None`, `equipment:1`
- `attack_speed_pct` vs `INCREASED`, `AttackSpeed`, `INCREASED:AttackSpeed:Melee`, `equipment:2`

Modifier count also differs for 526 matched affixes. The count pattern is:

- 572 affixes: legacy `1` -> bundle `1`
- 526 affixes: legacy `1` -> bundle `2`

This is the first blocker category to solve. Planner, crafting, stat aggregation, and simulation all depend on deterministic stat/modifier routing. A migration needs an explicit mapping contract from legacy `stat_key` to bundle modifier references, including rules for split modifiers and unsupported deterministic reference gaps.

## E. Safety and Provenance Blockers

The report found zero safety differences. Bundle records in the comparison use `forge_safe=true` and `production_safe=false`, and the response metadata also reports `production_consumer=false` and `production_safe=false`.

That is the correct state for diagnostics. `production_safe` must remain false until a separate migration gate proves identity, applicability, tier/value, and stat-routing equivalence.

The bundle provenance is present and uses source identities such as `equipment:0` with source paths from the last-epoch-data export. This is useful for auditability, but it is not enough by itself to prove production migration readiness.

## Migration Readiness Conclusion

Planner migration is not ready. Slot vocabulary differences affect all matched affixes, and stat-key routing differs for all matched affixes.

Crafting migration is not ready. There are 14 legacy-only affixes, all matched affixes have tier/value differences, and all matched affixes have applicability differences.

Stat aggregation migration is not ready. All matched affixes need an explicit `stat_key` to modifier/property mapping, and 526 matched affixes have a legacy-to-bundle modifier count change.

Simulation migration is not ready. Simulation depends on stable stat routing and value semantics, neither of which is proven by this report.

The first implementation blocker to solve is stat-key and modifier routing. Without a deterministic mapping from legacy `stat_key` behavior to bundle modifier references, the other migration surfaces cannot safely consume the Forge-safe bundle.
