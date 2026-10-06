# R1 Affix Truth (R1.6)

Canonical export: `last-epoch-data/exports_canonical/affixes.json`, built by `tools/scripts/build_canonical_affixes.py`.

Its only source is the build-stamped raw dump `extracted_raw/MasterAffixesList.json`:
- 1.4.6 GameAssembly sha256 `d4a68f3f…`;
- 578 single-property and 534 multi-property affixes.

Golden tests: `tools/scripts/test_r1_canonical_affixes.py`.

## Audit defects and what changed

| Audit finding | Defect | Canonical model |
| --- | --- | --- |
| EXT-2, LOSS-1 | Every tier is stored ×100 in Forge, then heuristically divided back (only 32 of 387 flat affixes) | Source floats are kept unscaled (`value_scale: SOURCE_UNSCALED`), with no transform. Golden: Added Health T1 = 5–15 and T8 = 275–325; Strength T1 = 1, T8 = 24–28. |
| EXT-2, LOSS-2 | 534 multi-property affixes flattened to one stat; second property's rolls lost | `properties[]` holds every property. Each tier has one roll per property: `minRoll/maxRoll` belong to property 0, and `extraRolls[i]` to property i+1. Checked for every tier: 0 anomalies. |
| LOSS-2 | Property identity was a name slug | The numeric SP id is kept (`properties[].property.raw`), and the name comes from the game's SP enum. 1,646 property rows decode at 100%. |
| (new) | Idol-altar property ids read as signed bytes (-126, -128) | Corrected to the uint8 values 130 (`IdolAltarProperty`) and 128 (`AilmentImmunity`), using the il2cpp layout type. The serialized value is kept in `sign_correction`. |
| DRIFT-6, EXT-7 | `specialAffixType` 6 leaked as the string `"6"` while `_meta` reported 0 unknowns | Kept as `{raw: 6, decode: UNKNOWN_VALUE}` on 134 affixes, and counted in `_meta.enums.unknown_values`. `displayCategory` 42/43 is also undecoded (the hand-coded table ends at 41). |
| EXT-7 | 115 "idol" records duplicate equipment ids | The canonical export has 1,112 unique ids; idol affixes are ordinary records (`rolls_on: Idols`, 469). The legacy idol section comes from `AffixImport.csv`, not the game: every id duplicates a raw affix, and its tiers disagree with the raw (affix 826: CSV 5 tiers + `tiers2` holding 4096/-0.01; raw 1 tier, 0.11–0.15). It is not carried. |
| LOSS-2 | `specialTag`, `setProperty`, `extraTag`, `modDisplayName`, `disableAltText` dropped | All carried per property. |
| field survival | `standardAffixEffectModifier`, `maximumAffixEffectModifierForT6`, shard hue/saturation, `specificRerollChances[].rerollChance` and `affixLootFilterOverrideName` lost by the legacy export | All carried (field survival: canonical 48/48 paths, 0 UNKNOWN; legacy 15 UNKNOWN). |

## Root cause of the enum leak

`extract_enums.py` iterated `MainModule.Types` only. Enums nested in their owning class, such as `AffixList.SpecialAffixType`, were never extracted. The processors then used hand-coded tables (0–5 for specialAffixType).

`extract_enums.py` now walks nested types (tested with mock Cecil types). The fix takes effect on the next operator run. Until then, every hand-coded label is flagged `HAND_CODED_LEGACY` in `_meta.enums.label_sources`.

## Remaining blockers (affixes)

- Undecodable enum values: `specialAffixType` 6, `displayCategory` 42/43. These clear when the operator run extracts the nested enums.
- **Status:** QUARANTINED in the trust manifest.

## Forge consumption

Not changed in R1, per R1.15. Forge `data/items/affixes.json` still holds the ×100 legacy data, and `stat_engine.py` keeps its heuristic.

Switching Forge to the canonical model is R2 work, staged behind certification.
