# AUDIT-R1 Extraction Truth & Completeness: Executive Summary

**Status: R1 PRE-EXTRACTION READY — OPERATOR RUN REQUIRED** (R1.15; see R1_PRE_EXTRACTION_READINESS.md).

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
| **Denominator** (R1.1, R1.15): generated from the game's own manifest, broader than "*List" | **1,326 candidates**. Classification: REQUIRED_NOW 175, REQUIRED_FUTURE 405, PRESERVE_ONLY 138, PROVEN_OUT_OF_SCOPE 209, **UNKNOWN 399** (744 before the R1.15 structural rules). All 17 audit-listed missing families are rediscovered automatically. |
| **Raw preservation** made visible | RAW_AVAILABLE **1**, RAW_MISSING 1,180, raw UNKNOWN 145. 1.4.6 is not reproducible from raw. |
| **Snapshot contract** (R1.2): every install file hashed, inputs in a content store outside git | Implemented; no snapshot of any install exists yet |
| **Canonical affixes** (R1.6) | Source scale, every property and roll, numeric identity, unknown enums surfaced. Golden: Added Health T1 = 5–15 (Forge holds 500–1,500). |
| **Canonical trees** (R1.7/R1.9) | Passive, skill and weaver trees with integrity gates. Weaver tree recovered (77 nodes). Passive trees DEFECTIVE: 6 Acolyte nodes lost by the decoder, plus garbage prerequisites. R1.15 proved the decoder's field shift (185 nodes flagged) and replaced it with a strict layout-ordered decoder. |
| **Field survival** (R1.5): automatic new-field detection | 184 gated paths, 4 UNKNOWN; 715 in-scope class domains blocked on missing raw (270 before R1.15 classified more classes in scope). Legacy affix export loses 15 of 48 raw fields; canonical loses 0. |
| **Patch diff** (R1.10) | 3 UNKNOWN changes (undecodable enum values). Added data only fails while it is unclassified. |
| **Reproducibility** (R1.11) | 5 of 5 canonical exports regenerate byte-identically; 43 legacy exports are NOT_REGENERABLE_FROM_RAW |
| **Coverage metrics** (R1.12) | REQUIRED_NOW entry coverage 82.3%, entity coverage 45.2% of measurable, field coverage 97.8% of evaluated paths (715 blocked), relationships 79.9% resolved (44.1% before R1.15), **semantic 0** (separate) |
| **Trust contract** (R1.13) | Canonical families QUARANTINED; legacy families QUARANTINED with upstream BLOCK/DEGRADE carried; 0 certified. The Forge sync now carries trust states unchanged. |
| **Property definitions** (R1.15) | Canonical property families with numeric identity; 5,724 of 7,855 tree stat references resolved through validated bands, the rest classified, never defaulted |
| **Enum gate** (R1.15) | 218 of 275 referenced enums not extracted (nested enums); new criterion C13 |
| **Certification gate** (R1.14) | **NOT CERTIFIED**. 10 of 13 criteria fail, 3 pass (no shrinking, identity, artifacts current). |
| **Operator command** (R1.3, R1.15) | One PowerShell command runs 22 ordered, resumable stages, stops certification on any failure, writes a non-secret handoff bundle, and commits locally |

## Root causes found

- **Nested enums never extracted.** `extract_enums.py` skipped nested enum types, which is why `specialAffixType` 6 leaked as a string. Fixed in code.
- **"Forge-only" Acolyte passive nodes.** These are six nodes the binary tree walker failed to decode. The walker never read `SkillTreeNode.nodeStats`; it read one count where the layout has two and hid the shift with heuristics (proven on 185 nodes). The six passive failures most likely carry a non-empty `nodeStats`. The strict decoder now fails such nodes loudly, and the operator TypeTree dump is the lossless source.
- **No patch-time dump.** The pipeline never re-runs Il2CppDumper on a new patch, so enums and layouts would go stale. The operator command does it.
- **Mixed-run raw inputs.** The raw tree inputs come from different extraction runs and carry no build stamp.
- **MaterialList misread.** `MaterialList` is rendering materials, not crafting materials. The audit had misread it by name.

## The operator gate

From the `last-epoch-data` checkout on the Windows machine:

```
.\scripts\r1_operator_extract.ps1 -Store "E:\LastEpochRawStore"
```

After a failure, fix the cause and re-run with `-Resume`. Then send back `RUN_VERDICT.txt` and push `fix/audit-r1-extraction-truth`; the handoff bundle is committed under `snapshots/handoff/`.

## After the operator run, R1 still needs

- **Classification:** the 399 UNKNOWN classes that have no structural evidence need classification once the raw dumps are in hand.
- **Tree stat bands:** the 5000–9999 tree stat band and the tree stat name table (`NodeTooltipPropertyList`) need decoding from the dump.
- **Tree nodes:** confirm the six Acolyte nodes from the TypeTree dump, and decode `AutomaticNodeStat`.

Each is gated; none can be skipped by shrinking the denominator.

## Untouched

- Forge production data and runtime (R1.15).
- R0 code paths.
- `dev`.
- docs PR #573.
- The R0 production proof debt is tracked in `R0_DEFERRED_PRODUCTION_VERIFICATION.md` (harness `ops/r0-production-smoke` @ `270a81c`).
