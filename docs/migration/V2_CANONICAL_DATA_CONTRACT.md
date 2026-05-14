# v2 Canonical Data Contract

## Purpose

The canonical contract defines the shared language later v2 phases must use for trusted data. It establishes support status, trust level, provenance, stable IDs, modifier references, and canonical shapes for major Last Epoch data categories.

This phase does not generate gameplay bundles, remap planner behavior, change crafting behavior, alter stat aggregation, or change simulation.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_canonical_contract.py --output docs\generated\v2_canonical_contract_report.json --markdown-output docs\migration\V2_CANONICAL_DATA_CONTRACT.md
```

## Support Statuses

| Status | Meaning |
| --- | --- |
| `trusted` | Structured, validated, and allowed for stable use. |
| `partial` | Structured in part, but requires explicit policy before calculation. |
| `text_only` | Displayable only; not calculated. |
| `unsupported` | Known but not supported for calculation. |
| `experimental` | Isolated from stable behavior. |
| `unknown` | Not classified enough for stable calculation. |

## Trust Levels

| Trust level | Meaning |
| --- | --- |
| `game_extracted` | Direct accepted game-data extract. |
| `generated_from_game_data` | Deterministically generated from accepted extracts. |
| `manual_bridge` | Explicit temporary compatibility bridge. |
| `inferred` | Derived from incomplete evidence; not silently trusted. |
| `placeholder` | Temporary scaffold; never stable planner eligible. |
| `deprecated` | Retained only for compatibility or audit history. |

## Provenance Requirements

Every canonical record requires `provenance`. Generated records must identify source path, source type, extraction method, schema version, and patch/version when available. Manual bridges must remain explicitly marked as `manual_bridge`.

## Stable vs Experimental Rules

- Stable calculation eligibility defaults to `trusted` plus `game_extracted` or `generated_from_game_data`.
- `unknown`, `unsupported`, `text_only`, and `experimental` records are displayable but not stable-calculable.
- `partial` records require later policy before stable calculation.
- `placeholder`, `inferred`, `deprecated`, and `manual_bridge` records are not stable planner eligible by default.
- Tooltip text must not be used to infer mechanics.

## Backend Contract Modules

| Module |
| --- |
| `backend/app/data_contracts/trust_status.py` |
| `backend/app/data_contracts/trust_level.py` |
| `backend/app/data_contracts/source_provenance.py` |
| `backend/app/data_contracts/canonical_id.py` |
| `backend/app/data_contracts/canonical_modifier.py` |
| `backend/app/data_contracts/canonical_affix.py` |
| `backend/app/data_contracts/canonical_item.py` |
| `backend/app/data_contracts/canonical_idol.py` |
| `backend/app/data_contracts/canonical_unique.py` |
| `backend/app/data_contracts/canonical_set.py` |
| `backend/app/data_contracts/canonical_class_mastery.py` |
| `backend/app/data_contracts/canonical_passive.py` |
| `backend/app/data_contracts/canonical_skill.py` |
| `backend/app/data_contracts/validation.py` |

## Frontend Type Files

| Type file |
| --- |
| `frontend/src/types/trustStatus.ts` |
| `frontend/src/types/sourceProvenance.ts` |
| `frontend/src/types/canonicalBase.ts` |
| `frontend/src/types/canonicalModifier.ts` |
| `frontend/src/types/canonicalAffix.ts` |
| `frontend/src/types/canonicalItem.ts` |
| `frontend/src/types/canonicalIdol.ts` |
| `frontend/src/types/canonicalUnique.ts` |
| `frontend/src/types/canonicalSet.ts` |
| `frontend/src/types/canonicalClassMastery.ts` |
| `frontend/src/types/canonicalPassive.ts` |
| `frontend/src/types/canonicalSkill.ts` |

## Canonical Models

| Model |
| --- |
| `CanonicalRecord` |
| `CanonicalModifierReference` |
| `CanonicalModifier` |
| `CanonicalAffix` |
| `CanonicalImplicit` |
| `CanonicalItemBase` |
| `CanonicalIdol` |
| `CanonicalUnique` |
| `CanonicalSetItem` |
| `CanonicalSet` |
| `CanonicalClass` |
| `CanonicalMastery` |
| `CanonicalPassiveNode` |
| `CanonicalPassiveTree` |
| `CanonicalSkill` |
| `CanonicalSkillTreeNode` |
| `CanonicalSkillTree` |

## How Later Phases Should Use This

Later phases should build ingestion, generated bundles, repositories, APIs, frontend consumers, and planner/debug behavior on these contracts. Any generated bundle should validate canonical IDs, support status, trust level, and provenance before becoming a candidate for consumption.

## Deferred Until Later Phases

- Bundle generation.
- Backend repository loading.
- Runtime API route changes.
- Frontend runtime consumption.
- Planner, crafting, stat aggregation, and simulation remapping.
- Item, affix, passive, skill, unique, set, and idol generation.

## Checkpoint 2

Checkpoint 2 is ready for review when the contract modules, frontend types, report, and focused tests pass.
