# R1 Current Patch Status

## What the repositories hold

| Item | Value | Evidence |
| --- | --- | --- |
| Newest extraction | 1.4.6, build 22986002, Unity 6000.0.42f1 | `extracted_raw/resources_manifest.json` `_meta` (install folder `1.4.6_22986002`), cross-checked against `exports_json/metadata.json` by GameAssembly.dll sha256 `d4a68f3f…88ae1` |
| Identity status | `COMPLETE_CROSS_CHECKED` | `r1_extraction_denominator.json` `source_identity` |
| Live game | 1.5.x (Season 5) | Audit DRIFT-1; the 1.5 game files are not in this environment |
| 1.5.x extraction | **None** | No 1.5 manifest, raw dump, export or snapshot exists |

## Why there is no current-patch extraction here

R1.3 needs the installed game: `resources.assets`, `sharedassets*.assets`, the Addressables bundles, `GameAssembly.dll` and `global-metadata.dat`. This cloud environment has no Last Epoch install and no access to the operator's Windows machine.

So no 1.5.x extraction was attempted, and none is claimed.

## How the patch will be identified

`tools/scripts/r1_snapshot.py` reads the identity from the install itself, not from folder names or old docs:

| Field | Authoritative source |
| --- | --- |
| Game version | `globalgamemanagers` → `PlayerSettings.bundleVersion` (UnityPy) |
| Build | Steam `appmanifest_899770.acf` `buildid` |
| Unity | `globalgamemanagers` serialized-file header (fallback: `boot.config`) |
| Binary identity | sha256 of `GameAssembly.dll` and `global-metadata.dat` |

If the version cannot be read, the operator-declared label is used. It is marked `PARTIAL` and cannot certify without a waiver. `--declared-patch` is only a cross-check.

## Operator extraction gate

One command, run on the Windows extraction host from the `last-epoch-data` checkout:

```
.\scripts\r1_operator_extract.ps1 -Store "E:\LastEpochRawStore"
```

(Optional: `-Install "<Last Epoch dir>"` and `-DeclaredPatch "<version>_<build>"`.)

Re-run after a failure: the same command with `-Resume`.

What it does: 22 ordered stages. In order:
1. environment, install, exact version/build, tools, free space and raw-store validation;
2. raw acquisition, hashing and the snapshot manifest;
3. all-domain extraction: Il2CppDumper, layouts, pipeline, raw affixes, manifests, and TypeTree dumps of every extraction contract;
4. enums, property definitions, canonical exports, field survival and relationships;
5. denominator, patch diff, reproducibility, coverage, trust and certification;
6. the handoff bundle.

Any failed stage stops the run before certification, keeps the evidence, prints the stage, and still writes `RUN_VERDICT.txt`. Outputs must be fresh and build-stamped, so stale files stop the run. On resume, the raw snapshot is not reacquired. It commits locally on `fix/audit-r1-extraction-truth`. It never pushes, never touches `le-the-forge` and never deploys.

Prerequisites: `scripts\fetch_tools.ps1` (pinned Il2CppDumper), `pip install -r requirements.txt`, the game installed and updated, and a store directory outside the repo. Stage 5 measures the install and refuses to start without room for:
- store: 1.05 × the extraction inputs, minus objects already stored;
- repo: 1.5 × the serialized files, plus 3 GB;
- temp: 1 × the extraction inputs.

**Send back:** `snapshots/handoff/<snapshot>/RUN_VERDICT.txt` (or the `[STOPPED]` block), then push the branch. The whole bundle is committed and holds no raw game data.

Until that run lands and certifies, R1 is **R1 PRE-EXTRACTION READY — OPERATOR RUN REQUIRED**.
