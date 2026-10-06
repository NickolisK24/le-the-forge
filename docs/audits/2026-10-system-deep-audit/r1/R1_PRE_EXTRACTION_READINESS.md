# R1.15 Pre-Extraction Uncertainty Reduction

**Status: R1 PRE-EXTRACTION READY — OPERATOR RUN REQUIRED.** Not certified, not verified, nothing deployed or merged.

All work below uses only the committed 1.4.6 evidence. Source: last-epoch-data `fix/audit-r1-extraction-truth` @ `308cf2f`. Later R1 contract fixes found during R2 preparation: `7dc1ad6` (C7/C8 were unpassable by construction) and `0111f1e` (tree → ability reference); branch head `0111f1e`.

## Before → after (committed 1.4.6 snapshot)

| Metric | Before (R1, `77dafb0`) | After (R1.15) | What changed |
| --- | --- | --- | --- |
| Denominator UNKNOWN | 744 | **399** | 10 structural rules (S01–S10) from layout evidence; anything unproven stays UNKNOWN |
| REQUIRED_NOW entries / with canonical export | 174 / 144 (0.8276) | 175 / 144 (0.8229) | `NodeTooltipPropertyList` (tree stat name table) joined REQUIRED_NOW |
| REQUIRED_NOW entity coverage (measurable) | 0.4516 | 0.4516 | Needs raw instances (operator run) |
| REQUIRED_FUTURE entries / canonical | 221 / 0 | 405 / 0 | 184 classes moved out of UNKNOWN; all 405 now have extraction contracts |
| Field coverage of evaluated paths | 0.978 (270 domains blocked) | 0.978 (**715** blocked) | More in-scope classes, plus the tree file's classes, now wait on raw: an honest increase |
| Relationships resolved | 0.4414 (6,457 / 14,628; 8,171 dangling) | **0.7989** (12,603 / 15,776; 3,173 dangling) | Tree stat references resolved through validated property bands; affix sub-properties linked |
| Tree stat property references | 7,855 undecoded | RESOLVED 5,724 · UNKNOWN_PROPERTY_TYPE 2,129 · UNRESOLVED 2 · AMBIGUOUS 0 | Never defaulted; raw id always kept |
| Unknown enum values | 3 fields | 3 fields (unchanged) | Need the nested-enum dump (operator run) |
| Referenced enums not extracted | not measured | **218 / 275** (new gate C13) | Nested enums missing from the 1.4.6 dump |
| Certification criteria passing | 3 / 12 | 3 / 13 | C2, C9, C12 pass; new C13 fails until the enum dump |
| Canonical exports reproduced (normalize) | 4 / 4 | 5 / 5 | Property definitions added |

## What R1.15 delivered

| Priority | Result | Commit |
| --- | --- | --- |
| P1 UNKNOWN classification | 10 rules. Each reports rule id, evidence basis, matched count, classification, confidence and exceptions. Classes without a resolved layout never match. The in-scope safety net still downgraded 2 rule hits. | `f68d881` |
| P2 property definitions | `exports_canonical/property_definitions.json`: master (SP), player (617), ability (567), tracker, conditional-damage and idol-altar families, all with numeric identity. Unknown semantics are kept as `NOT_IN_AVAILABLE_EVIDENCE`; the tree name table is RAW_MISSING. | `5fad68f` |
| P3 reference resolution | Affix encodings validated (PlayerProperty, AbilityProperty with a +1 offset chosen by evidence, IdolAltarProperty). Tree bands: 0–4999 SP, 10000/15000/20000 + AilmentID accepted; 5000–9999 undecoded; 25000+ insufficient sample. | `5fad68f` |
| P4 tree decoder | Root cause proven (see R1_PASSIVE_TRUTH.md). The strict layout-ordered decoder fails loudly instead of guessing; it covers the six Acolyte nodes and the field-shift regression. | `02e4b34` |
| P5 enum completeness | `R1_ENUM_COVERAGE.json/.md`, certification C13 | `14a8230` |
| P6 extraction contracts | `R1_EXTRACTION_CONTRACTS.json/.md`: 581 contracts (176 REQUIRED_NOW incl. 2 tree-node components, 405 REQUIRED_FUTURE). They drive the operator TypeTree dump across every manifested file. | `5bd8272` |
| P7 operator run | 22 ordered stages, freshness and build-stamp checks, space check, resumable. A failure stops certification. | `9519c79`, `308cf2f` |
| P8 handoff bundle | `snapshots/handoff/<snapshot>/` with RUN_VERDICT.txt, RUN_MANIFEST.json, PATCH_DIFF, COVERAGE_METRICS, CERTIFICATION_REPORT, UNKNOWN_DATA_REPORT, FIELD_SURVIVAL_REPORT, RELATIONSHIP_REPORT, ENUM_COVERAGE, EXTRACTION_CONTRACTS, GIT_STATUS and GIT_DIFF_STAT; commit SHA in LOCAL_COMMIT.txt. Generated reports only. | `9519c79` |
| P9 regeneration | All R1 evidence regenerated; 221 R1 tests pass | `5b4510d`, `c38c6bf` |

## Remaining blockers (all need the installed game)

| Criterion | Blocker | Cleared by |
| --- | --- | --- |
| C1 | 399 UNKNOWN classes, without enough layout evidence for any rule | Raw TypeTree dumps (instance content) and policy work after the run; never by shrinking |
| C3, C10 | 31 REQUIRED_NOW entries have no canonical export (no raw instances) | Contracts → TypeTree dumps → lossless envelopes |
| C4 | 715 domains BLOCKED_NO_RAW; 4 UNKNOWN `SkillTreeNode` paths | TypeTree dumps (including `*TreeNode` with the real `nodeStats` layout) |
| C5 | 3,173 dangling: 2,131 tree stat refs (5000–9999 band and the tree name table), 935 class references, 78 prerequisites, 29 affix sub-properties | `NodeTooltipPropertyList` content; strict decoder output; raw dumps |
| C6, C11 | `specialAffixType` 6, `displayCategory` 42/43, AT bit 536870912 | Nested-enum dump |
| C13 | 218 referenced enums not extracted | Nested-enum dump (`extract_enums.py` fix) |
| C7, C8 | No snapshot of any install; extract stage not run | Stages 7–9 and 18 |

## Known risks for the run

- **Oversized files:** a raw TypeTree dump over 95 MB stops the run at stage 10 or 13, with evidence kept. A code fix then resumes from stage 10, and the raw snapshot is not reacquired.
- **Degraded legacy steps:** legacy `run_all.py` steps that degrade are recorded in RUN_VERDICT.txt. R1 consumes only freshness-checked outputs.
- **Tests pinned to 1.4.6:** some R1 unit tests assert 1.4.6 numbers (tree counts, missing nodes). After the 1.5 data lands they need a golden refresh. That is expected and is not a regression.
