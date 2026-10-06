# R1 Trust / Quarantine Contract

Implemented by `tools/scripts/r1_trust.py` and `generate_r1_trust_manifest.py`.

Machine-readable outputs:
- `docs/generated/r1_trust_manifest.json` (gate copy);
- `exports_canonical/TRUST_MANIFEST.json` (consumer copy, byte-identical).

Forge carry-through: `le-the-forge/scripts/sync_game_data.py` (`upstream_trust` in `data/version.json`, plus `data/upstream_trust_manifest.json`).

## Every exported family carries

| Field | Meaning |
| --- | --- |
| `source_provenance` | Denominator entries mapped to the export, raw status, builder, raw sha256 |
| `patch` | Patch, build, Unity, GameAssembly sha256 and identity status |
| `extraction_status` | `EXTRACTED`, or `ORPHAN` (no source class maps to the export) |
| `coverage_status` | `FIELDS_CLASSIFIED`, `FIELDS_UNKNOWN` or `FIELDS_UNMEASURED` (from R1.5) |
| `relationship_status` | `RESOLVED_OR_ALLOWLISTED`, `DANGLING` or `NONE_DISCOVERED` (from R1.12) |
| `semantic_status` | Always `UNVERIFIED` in R1: there are no ground-truth fixtures |
| `consumer_state` | `CERTIFIED`, `PRESERVED_ONLY`, `QUARANTINED`, `UNSUPPORTED` or `UNKNOWN` |
| `trusted_calculation_eligible` | True only for `CERTIFIED` |
| `reasons` | Every recorded defect or provenance gap |

In-scope domains with no export are listed separately (`domains_without_export`), each with its consumer state.

## Consumer states

| State | When | Consumer rule |
| --- | --- | --- |
| CERTIFIED | Canonical export, no recorded reason at all, and covered by a passing R1 certification | May feed trusted production calculations |
| PRESERVED_ONLY | PRESERVE_ONLY domain whose raw input is preserved | Not consumed |
| QUARANTINED | Exported, with at least one recorded defect or gap | Advisory or display only, labelled as such |
| UNSUPPORTED | No export (not extracted), or proven out of scope | Not consumed |
| UNKNOWN | Not classified, or orphan export | Must not be consumed by trusted calculations |

States are computed from the generated R1 reports only; nothing is hand-set.

Certification alone cannot make a family CERTIFIED. It must also have no recorded reasons.

## Rules for downstream sync layers

1. Copy `consumer_state` and `reasons` for every family you copy, unchanged.
2. Never upgrade a state. A missing manifest means **UNKNOWN**, not trusted.
3. Upstream `data_bundle` BLOCK/DEGRADE actions are carried into `reasons` (audit SYS-4).
4. Actual enforcement in the Forge runtime (refusing QUARANTINED input in trusted calculations) is R2 work. R1 delivers the contract and the carry-through.

## 1.4.6 state

- **Canonical families:** all 4 are QUARANTINED.
  - Affixes: undecodable `specialAffixType` 6 and `displayCategory` 42/43.
  - Trees: the raw dump is not build-stamped, there are integrity defects, and prerequisites dangle.
  - Weaver tree: the raw dump is not build-stamped.
- **Legacy `exports_json` families:** QUARANTINED, because none is reproducible from preserved raw. The upstream BLOCK (affixes) and DEGRADE actions are carried.
- **Orphan exports:** `actors.json`, `loot_filter_relevant_entities.json` and `metadata.json` are UNKNOWN.
- **Certified families:** none.
