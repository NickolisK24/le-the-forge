# R1 Certification Report (R1.14)

Command: `python tools/scripts/r1_certify.py [--strict]` (last-epoch-data). Machine report: `docs/generated/r1_certification_report.json`.

CI (`.github/workflows/r1-certification.yml`) runs on every PR and push to main:
- the R1 unit tests (176 tests);
- the "artifacts current" check, C12.

Strict certification, which fails unless certified, runs on manual dispatch and whenever `snapshots/raw/` or `snapshots/state/CERTIFIED.json` changes.

## Verdict for the committed snapshot (1.4.6 build 22986002)

**R1 NOT CERTIFIED.** That is expected: 1.4.6 cannot be certified, because its raw inputs were never preserved, and 1.5.x has not been extracted.

| Id | Criterion | Result | Evidence |
| --- | --- | --- | --- |
| C1 | No UNKNOWN denominator entries | FAIL | 744 of 1,326 entries UNKNOWN |
| C2 | Every manifest class in the denominator (no shrinking) | PASS | 1,170 / 1,170 |
| C3 | REQUIRED_NOW entity coverage 100% and measurable | FAIL | 144 / 174 entries have a canonical export; 45.2% of measurable entities; 18 entries not measurable |
| C4 | No unclassified fields, no blocked domains | FAIL | 4 UNKNOWN paths (SkillTreeNode `nodeStats`, `propertiesForAltText`, `isLockNode`, `isBaseLockNode`); 270 class domains BLOCKED_NO_RAW |
| C5 | No unallowlisted dangling relationships | FAIL | 8,171 in total: 7,855 tree stat → property definition, 238 in-scope class references, 67 passive prerequisites, 11 skill prerequisites |
| C6 | No unknown enum values | FAIL | `specialAffixType` 6, `displayCategory` 42/43, AT bit 536870912 |
| C7 | Authoritative raw snapshot + clean run manifest | FAIL | No snapshot of any install exists |
| C8 | Exports regenerate (normalize + extract) | FAIL | Normalize passes (4/4 canonical exports reproduced); extract stage not run |
| C9 | Patch identity explicit and cross-checked | PASS | 1.4.6 / 22986002 / 6000.0.42f1, cross-checked by GameAssembly sha256 |
| C10 | Every REQUIRED_NOW domain has a canonical export | FAIL | 30 entries without one (Ability, ItemList, UniqueList, property lists, enums, localization, ...) |
| C11 | Patch diff has no UNKNOWN or BREAKING change | FAIL | 3 UNKNOWN (undecodable enum values); baseline uncertified |
| C12 | Committed R1 artifacts current | PASS | Every generated report equals its regeneration |

**Semantic coverage: 0.** It is reported only and never gated.

## What the operator extraction can clear

| Criterion | How the operator run clears it |
| --- | --- |
| C7, C8, C9 | Authoritative snapshot, run manifest and extract-stage reproduction |
| C6 | Nested enums extracted by the fixed `extract_enums.py` |
| C4 (blocked), C10, part of C3 | Build-stamped raw TypeTree dumps and canonical envelopes for every in-scope class |
| C2 | Manifests for every serialized file |

These stay open beyond the operator run unless resolved by evidence:

| Criterion | Why it stays open |
| --- | --- |
| C1 | 744 UNKNOWN classes, mostly prefab components, need evidence-backed classification (policy work with the raw dumps in hand) |
| C5 | Tree stat → property-definition resolution needs the property lists decoded; class-reference dangling must be resolved or allowlisted with reasons |
| C4 (`nodeStats`) | Tree-walker decoder fix (EXT-12) |

R1 is therefore at: **R1 IMPLEMENTATION COMPLETE — OPERATOR EXTRACTION REQUIRED.**

Full R1 VERIFIED additionally needs the post-extraction classification and decoder work above.
