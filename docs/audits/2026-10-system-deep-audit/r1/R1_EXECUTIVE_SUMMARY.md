# AUDIT-R1 Extraction Truth & Completeness: Executive Summary

**Status: R1 IMPLEMENTATION COMPLETE — OPERATOR EXTRACTION REQUIRED.**

Not verified, not certified, no 1.5.x extraction claimed.

## What R1 set out to answer

For every Last Epoch data domain:
- what exists upstream;
- what we extract, preserve or intentionally skip;
- which fields and relationships survive;
- which version produced it;
- whether it can be reproduced;
- whether new data can slip through unnoticed.

R1 makes all of this **measurable**. It does not make it complete yet.

## What exists now (all generated, all tested, CI-enforced)

| Capability | Result on the committed 1.4.6 snapshot |
| --- | --- |
| **Denominator** (R1.1): generated from the game's own manifest, broader than "*List" | **1,326 candidates**. Classification: REQUIRED_NOW 174, REQUIRED_FUTURE 221, PRESERVE_ONLY 21, PROVEN_OUT_OF_SCOPE 166, **UNKNOWN 744**. All 17 audit-listed missing families are rediscovered automatically. |
| **Raw preservation** made visible | RAW_AVAILABLE **1**, RAW_MISSING 1,180, raw UNKNOWN 145. 1.4.6 is not reproducible from raw. |
| **Snapshot contract** (R1.2): every install file hashed, inputs in a content store outside git | Implemented; no snapshot of any install exists yet |
| **Canonical affixes** (R1.6) | Source scale, every property and roll, numeric identity, unknown enums surfaced. Golden: Added Health T1 = 5–15 (Forge holds 500–1,500). |
| **Canonical trees** (R1.7/R1.9) | Passive, skill and weaver trees with integrity gates. Weaver tree recovered (77 nodes). Passive trees DEFECTIVE: 6 Acolyte nodes lost by the decoder, plus garbage prerequisites. |
| **Field survival** (R1.5): automatic new-field detection | 184 gated paths, 4 UNKNOWN; 270 in-scope classes blocked on missing raw. Legacy affix export loses 15 of 48 raw fields; canonical loses 0. |
| **Patch diff** (R1.10) | 3 UNKNOWN changes (undecodable enum values). Added data only fails while it is unclassified. |
| **Reproducibility** (R1.11) | 4 of 4 canonical exports regenerate byte-identically; 42 legacy exports are NOT_REGENERABLE_FROM_RAW |
| **Coverage metrics** (R1.12) | REQUIRED_NOW entry coverage 82.8%, entity coverage 45.2% of measurable, field coverage 97.8% of evaluated paths (270 blocked), relationships 44.1% resolved, **semantic 0** (separate) |
| **Trust contract** (R1.13) | Canonical families QUARANTINED; legacy families QUARANTINED with upstream BLOCK/DEGRADE carried; 0 certified. The Forge sync now carries trust states unchanged. |
| **Certification gate** (R1.14) | **NOT CERTIFIED**. 9 of 12 criteria fail, 3 pass (no shrinking, identity, artifacts current). |
| **Operator command** (R1.3) | One PowerShell command produces snapshot, extraction, evidence and certification, and commits locally |

## Root causes found

- **Nested enums never extracted.** `extract_enums.py` skipped nested enum types, which is why `specialAffixType` 6 leaked as a string. Fixed in code.
- **"Forge-only" Acolyte passive nodes.** These are six nodes the binary tree walker failed to decode. The same walker never decodes structured node stats.
- **No patch-time dump.** The pipeline never re-runs Il2CppDumper on a new patch, so enums and layouts would go stale. The operator command does it.
- **Mixed-run raw inputs.** The raw tree inputs come from different extraction runs and carry no build stamp.
- **MaterialList misread.** `MaterialList` is rendering materials, not crafting materials. The audit had misread it by name.

## The operator gate

From the `last-epoch-data` checkout on the Windows machine:

```
.\scripts\r1_operator_extract.ps1 -Store "E:\LastEpochRawStore"
```

Send back the printed verdict block and `git log -1 --stat`, then push `fix/audit-r1-extraction-truth`.

## After the operator run, R1 still needs

- **Classification:** the remaining UNKNOWN classes, mostly prefab components, need evidence-backed classification with the raw dumps in hand.
- **Property definitions:** decode the property-definition tables, which resolve 7,855 tree stat references.
- **Decoder fix:** fix the tree decoder (`nodeStats`, missing nodes) against real 1.5 bytes.

Each is gated; none can be skipped by shrinking the denominator.

## Untouched

- Forge production data and runtime (R1.15).
- R0 code paths.
- `dev`.
- docs PR #573.
- The R0 production proof debt is tracked in `R0_DEFERRED_PRODUCTION_VERIFICATION.md` (harness `ops/r0-production-smoke` @ `270a81c`).
