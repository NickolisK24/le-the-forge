# Bundle Item Needs-Adapter Review

## 1. Purpose

This document reviews the 15 `needs_adapter` mappings from the developer-only reviewed item type fixture before any non-production consumer is introduced.

This is not a production migration. It does not activate bundle item type consumption, replace loaders, change simulation behavior, or make any mapping `production_safe`. It defines proposed adapter translation rules for later developer-only use.

## 2. Current Fixture Summary

- Fixture path: `backend/tests/fixtures/bundle_item_type_mapping_review.json`
- Source report: `docs/generated/bundle_item_adapter_map_report.md`
- `accepted`: 19
- `needs_adapter`: 15
- `needs_review`: 9
- `deferred`: 8
- `unsafe`: 0
- `production_safe`: false globally and per entry

The `needs_adapter` category contains mappings that are backed by `base_type_id`, but cannot be treated as direct slug matches.

## 3. Needs-Adapter Mapping Table

| Forge item type | Forge slot | Bundle item type ID | Bundle base type ID | Match method | Confidence | Why adapter is needed | Proposed translation rule | Migration risk | Recommendation |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| `helm` | `head` | `helmet` | 0 | `base_type_id` | Verified | Forge slug differs from bundle ID. | Translate Forge `helm` to bundle `helmet` only when `base_type_id=0`. | Low, but direct slug equality would fail. | Simple rename candidate after tests. |
| `chest` | `body` | `body_armor` | 1 | `base_type_id` | Verified | Forge slug and slot vocabulary differ from bundle armor identity. | Translate Forge `chest` to bundle `body_armor` only when `base_type_id=1`. | Low to medium because Forge uses `body` slot language. | Simple rename plus slot/category normalization test. |
| `axe` | `weapon` | `one_handed_axe` | 5 | `base_type_id` | Verified | Forge slug collapses one-handed and two-handed axe context. | Translate Forge `axe` to bundle `one_handed_axe` only when `base_type_id=5`. | Medium because `axe` is ambiguous without base type context. | Require weapon context preservation tests. |
| `dagger` | `weapon` | `one_handed_dagger` | 6 | `base_type_id` | Verified | Forge slug omits one-handed bundle context. | Translate Forge `dagger` to bundle `one_handed_dagger` only when `base_type_id=6`. | Low to medium if future dagger variants appear. | Require explicit base type check. |
| `mace` | `weapon` | `one_handed_maces` | 7 | `base_type_id` | Verified | Forge slug collapses one-handed and two-handed mace context. | Translate Forge `mace` to bundle `one_handed_maces` only when `base_type_id=7`. | Medium because `mace` is ambiguous without base type context. | Require weapon context preservation tests. |
| `sceptre` | `weapon` | `one_handed_sceptre` | 8 | `base_type_id` | Verified | Forge slug omits one-handed bundle context. | Translate Forge `sceptre` to bundle `one_handed_sceptre` only when `base_type_id=8`. | Low to medium if future sceptre variants appear. | Require explicit base type check. |
| `sword` | `weapon` | `one_handed_sword` | 9 | `base_type_id` | Verified | Forge slug collapses one-handed and two-handed sword context. | Translate Forge `sword` to bundle `one_handed_sword` only when `base_type_id=9`. | Medium because `sword` is ambiguous without base type context. | Require weapon context preservation tests. |
| `fist` | `weapon` | `one_handed_fist` | 11 | `base_type_id` | Verified | Forge slug omits one-handed bundle context. | Translate Forge `fist` to bundle `one_handed_fist` only when `base_type_id=11`. | Low to medium if future fist variants appear. | Require explicit base type check. |
| `axe` | `weapon` | `two_handed_axe` | 12 | `base_type_id` | Verified | Forge slug collapses one-handed and two-handed axe context. | Translate Forge `axe` to bundle `two_handed_axe` only when `base_type_id=12`. | Medium because `axe` is ambiguous without base type context. | Require weapon context preservation tests. |
| `mace` | `weapon` | `two_handed_mace` | 13 | `base_type_id` | Verified | Forge slug collapses one-handed and two-handed mace context. | Translate Forge `mace` to bundle `two_handed_mace` only when `base_type_id=13`. | Medium because `mace` is ambiguous without base type context. | Require weapon context preservation tests. |
| `polearm` | `weapon` | `two_handed_spear` | 14 | `base_type_id` | Verified | Forge legacy alias differs from bundle spear naming. | Translate Forge `polearm` to bundle `two_handed_spear` only when `base_type_id=14`. | Medium because `spear` also exists as an unmapped Forge type needing review. | Keep `spear` blocked; test `polearm` separately. |
| `staff` | `weapon` | `two_handed_staff` | 15 | `base_type_id` | Verified | Forge slug omits two-handed bundle context. | Translate Forge `staff` to bundle `two_handed_staff` only when `base_type_id=15`. | Low to medium if future staff variants appear. | Require explicit base type check. |
| `sword` | `weapon` | `two_handed_sword` | 16 | `base_type_id` | Verified | Forge slug collapses one-handed and two-handed sword context. | Translate Forge `sword` to bundle `two_handed_sword` only when `base_type_id=16`. | Medium because `sword` is ambiguous without base type context. | Require weapon context preservation tests. |
| `idol_1x1` | `idol` | `idol_1x1_eterra` | 25 | `base_type_id` | Verified | Forge slug collapses bundle-specific idol context. | Translate Forge `idol_1x1` to bundle `idol_1x1_eterra` only when `base_type_id=25`. | Medium because shape alone is not enough. | Require idol base type and shape tests. |
| `idol_1x1` | `idol` | `idol_1x1_lagon` | 26 | `base_type_id` | Verified | Forge slug collapses bundle-specific idol context. | Translate Forge `idol_1x1` to bundle `idol_1x1_lagon` only when `base_type_id=26`. | Medium because shape alone is not enough. | Require idol base type and shape tests. |

## 4. Translation Rule Categories

### Simple Slug Rename

Mappings:

- `helm -> helmet` by `base_type_id=0`
- `dagger -> one_handed_dagger` by `base_type_id=6`
- `sceptre -> one_handed_sceptre` by `base_type_id=8`
- `fist -> one_handed_fist` by `base_type_id=11`
- `staff -> two_handed_staff` by `base_type_id=15`

The adapter exists because Forge slugs are shorter or legacy-oriented while the bundle keeps source-oriented item type IDs. These are safe only as ID-backed diagnostic translations. Tests must prove the translation does not run from slug alone.

### Slot/Category Normalization

Mappings:

- `chest -> body_armor` by `base_type_id=1`

The adapter exists because Forge uses `chest` and slot `body`, while the bundle item type is `body_armor`. Tests must cover both the item type translation and any slot/category vocabulary used by a future consumer.

### Weapon Type Distinction

Mappings:

- `axe -> one_handed_axe` by `base_type_id=5`
- `axe -> two_handed_axe` by `base_type_id=12`
- `mace -> one_handed_maces` by `base_type_id=7`
- `mace -> two_handed_mace` by `base_type_id=13`
- `sword -> one_handed_sword` by `base_type_id=9`
- `sword -> two_handed_sword` by `base_type_id=16`

The adapter exists because Forge currently uses broad weapon slugs where the bundle distinguishes one-handed and two-handed base type groups. These are unsafe without `base_type_id`. Tests must prove the adapter preserves one-handed/two-handed distinctions and does not collapse bundle IDs back to a single Forge slug silently.

### Forge Legacy Alias

Mappings:

- `polearm -> two_handed_spear` by `base_type_id=14`

The adapter exists because the Forge vocabulary uses `polearm`, while the bundle source identifies the type as `two_handed_spear`. This is separate from the unmapped Forge `spear` record, which remains in `needs_review`. Tests must prove `polearm` and `spear` are not conflated.

### Idol Shape Distinction

Mappings:

- `idol_1x1 -> idol_1x1_eterra` by `base_type_id=25`
- `idol_1x1 -> idol_1x1_lagon` by `base_type_id=26`

The adapter exists because Forge shape vocabulary collapses bundle-specific idol contexts. These mappings are unsafe from shape alone. Tests must require `base_type_id` and preserve the Eterra/Lagon distinction.

## 5. Safety Rules

- `base_type_id`-backed mapping is preferred.
- `subtype_id` alone is forbidden.
- Name-only matching is not authoritative.
- `production_safe` remains false.
- Adapter translations may be used only in developer diagnostics until a separate migration step.
- Every translation must have tests before any consumer uses it.
- Translation rules must not collapse meaningful bundle distinctions.
- Missing translation must produce a warning, not silent fallback.

## 6. Proposed Future Adapter Fixture Shape

Do not create this fixture in this task. A later developer-only step could introduce a separate translation fixture shaped like:

```json
{
  "fixture": "bundle_item_type_adapter_translations",
  "production_safe": false,
  "translations": [
    {
      "forge_item_type": "helm",
      "bundle_item_type_id": "helmet",
      "bundle_base_type_id": 0,
      "translation_type": "simple_slug_rename",
      "confidence": "Verified",
      "source": "base_type_id",
      "notes": []
    }
  ]
}
```

That future fixture should remain developer-only until a separate migration explicitly defines a consumer, fallback behavior, and test coverage.

## 7. Test Requirements Before Use

Before a developer-only non-production consumer can use adapter translations:

- every translation is `base_type_id`-backed or explicitly reviewed
- no duplicate Forge item type maps to conflicting bundle type unless intentional and covered by context tests
- no bundle item type receives conflicting Forge aliases unless intentional
- no `subtype_id`-only translation exists
- weapon distinctions are preserved
- idol shape distinctions are preserved
- deferred and non-equipment bundle types remain excluded
- `production_safe` remains false
- missing translation causes a warning, not silent fallback
- `spear` remains blocked unless a later source-backed mapping is reviewed

## 8. What Not To Do Yet

- Do not wire translations into production loaders.
- Do not migrate `base_items` yet.
- Do not map `base_items` by name.
- Do not mark item legality authoritative.
- Do not remove current Forge item constants.
- Do not treat implicit refs as stat mechanics.
- Do not merge deferred non-equipment types into equipment item types.
- Do not make `production_safe` true.

## 9. Recommended Next Step

Create a developer-only adapter translation fixture for the reviewed `needs_adapter` mappings, with tests, still not used by production loaders.
