# R1 Remediation Report

## Branches

| Repository | Base | Base SHA | R1 branch | Working tree at start |
| --- | --- | --- | --- | --- |
| last-epoch-data | `main` | `73e2ab0` | `fix/audit-r1-extraction-truth` | clean |
| le-the-forge | `main` (production) | `80bd559` | `fix/audit-r1-extraction-consumption` | clean |

Production `main` is untouched. `dev` was not used and was not reconciled. Nothing was merged or deployed.

## Packages delivered (last-epoch-data)

| Package | Commit | Content |
| --- | --- | --- |
| R1.1 denominator | `9954203` | `r1_denominator.py`, policy, generator, 57 tests, Forge consumption snapshot |
| R1.2 snapshot/provenance | `1a03878`, `d60012d` | `r1_snapshot.py`, contract, retroactive 1.4.6 record |
| R1.4/R1.6 affixes and enums | `e6078d9` | Canonical affixes, nested-enum extraction fix, golden tests |
| R1.5/R1.7 field survival and trees | `2a9b82b` | `r1_field_survival.py`, policy, canonical passive/skill/weaver trees, integrity gates |
| R1.3/R1.4/R1.8/R1.9 operator dumps | `b862217` | Serialized-file manifests, raw TypeTree dumper, lossless envelopes, multi-file denominator |
| R1.10 patch diff | `775500b` | `r1_patch_diff.py`, baseline state, report |
| R1.11 reproducibility | `aac585f` | `r1_reproduce.py` normalize/extract |
| R1.12–R1.14 metrics, trust, certification | `f175341` | Metrics, trust manifest, certification gate, CI workflow |
| R1.3 operator command | `11e6e00` | `r1_operator_extract.py` + `scripts/r1_operator_extract.ps1` |
| R1.12 docs | `77dafb0` | Trust contract, domain coverage |

## Packages delivered (le-the-forge)

| Commit | Content |
| --- | --- |
| `f3031b7` | `scripts/r1_forge_consumption_inventory.py` + tests; `R0_DEFERRED_PRODUCTION_VERIFICATION.md` |
| `6bdb436` | `sync_game_data.py` carries upstream trust (`data/version.json` `upstream_trust`, `data/upstream_trust_manifest.json`) + tests |
| (this commit) | `r1/` deliverables; `AUDIT_EVIDENCE.json` R1 annotations |

## Finding-by-finding

No finding status changed: nothing is fixed in production, and no current-patch extraction is certified. Each R1 finding now carries `r1_state` in AUDIT_EVIDENCE.json.

| Finding | r1_state | Summary |
| --- | --- | --- |
| DRIFT-1 | BLOCKED_OPERATOR_EXTRACTION | No 1.5.x extraction; the one operator command is ready |
| EXT-1 | R2_CONSUMPTION | Forge `data/` untouched; provenance and trust carry-through added |
| EXT-2 | EXTRACTION_FIX_IMPLEMENTED_UNCERTIFIED | Canonical affixes: source scale, all properties and rolls |
| LOSS-1 | R2_CONSUMPTION | Forge ×100 data and heuristic remain until R2 |
| EXT-10 | MEASURED | Semantic coverage reported separately (0) |
| EXT-3 | MEASURED | Non-extracted runtime inputs inventoried |
| EXT-4 | BLOCKED_OPERATOR_EXTRACTION | Families rediscovered and classified; extraction runs on operator; weaver tree survives; MaterialList correction |
| EXT-5 | BLOCKED_OPERATOR_EXTRACTION | Snapshot contract ready; no snapshot yet |
| LOSS-2 | EXTRACTION_FIX_IMPLEMENTED_UNCERTIFIED | Property ids, modifier types, extraRolls carried |
| LOSS-3 | R2_CONSUMPTION | Extraction carries passive structured fields; Forge sync drops them |
| LOSS-4 | R2_CONSUMPTION | Export has ids; curated Forge base items are the loss |
| LOSS-5 | BLOCKED_OPERATOR_EXTRACTION | Raw unique/set dumps on operator; Forge slug keying is R2 |
| SYS-4 | EXTRACTION_FIX_IMPLEMENTED_UNCERTIFIED | Trust manifest + Forge sync carry-through; runtime enforcement R2 |
| DRIFT-6 | EXTRACTION_FIX_IMPLEMENTED_UNCERTIFIED | Root cause: nested enums never extracted; fixed in `extract_enums.py` |
| EXT-7 | EXTRACTION_FIX_IMPLEMENTED_UNCERTIFIED | Canonical: 1,112 unique ids; CSV idol section not game data |
| LOSS-6 | BLOCKED_OPERATOR_EXTRACTION | Raw class/ailment dumps on operator |
| SYS-12 | BLOCKED_OPERATOR_EXTRACTION | Content store + manifests; no new binaries in git |
| EXT-9 | MEASURED | Unconsumed synced domains confirmed mechanically |
| DRIFT-2 | MEASURED | Unchanged |

### New findings from R1 evidence

| Finding | Description |
| --- | --- |
| EXT-11 | Raw affix dumper reads uint8 property ids as signed (corrected in canonical) |
| EXT-12 | Tree walker misses 11 nodes (the 6 "Forge-only" Acolyte ids) and decodes garbage prerequisites; `nodeStats` and `propertiesForAltText` are never decoded |
| EXT-13 | Raw tree inputs come from different runs; no build stamp |
| EXT-14 | `run_all.py` never re-runs Il2CppDumper, so enums and layouts go stale on a new patch (the operator command fixes this) |
| EXT-15 | The il2cpp layout index omits base classes and nested value types |
| OPS-9 | last-epoch-data Regeneration Gate failing on main since at least run 157 (pre-existing, outside R1) |

## Unchanged by design

- **Forge production data and runtime:** no change (R1.15).
- **R0 code paths:** untouched. R0 production checks remain proof debt (`R0_DEFERRED_PRODUCTION_VERIFICATION.md`).
- **Existing binaries:** the committed `patch_versions/` binaries are not deleted; that is an owner licensing decision.

## Test evidence (this environment)

| Suite | Result |
| --- | --- |
| last-epoch-data R1 tests (`tools/scripts/test_r1_*.py`) | 176 passed |
| le-the-forge R1 tests (`test_r1_forge_consumption_inventory.py`, `test_r1_sync_trust_contract.py`) | 15 passed |
| Regeneration gate (last-epoch-data) | All R1 artifacts `match`; the 7 pre-existing drifts are unrelated (OPS-9) |
