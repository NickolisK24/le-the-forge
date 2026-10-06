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

What it does: preflight checks, then snapshot, verify, Il2CppDumper and layout parse, the pipeline, a fresh raw affix dump, class manifests for every serialized file, raw TypeTree dumps of every in-scope class, canonical exports, then all R1 evidence and certification. It then commits locally on `fix/audit-r1-extraction-truth`. It never pushes, never touches `le-the-forge` and never deploys.

Prerequisites: `scripts\fetch_tools.ps1` (pinned Il2CppDumper), `pip install -r requirements.txt`, the game installed and updated, and a store directory outside the repo with room for the extraction inputs.

**Send back:** the printed verdict block, the output of `git log -1 --stat`, and then push the branch.

Until that run lands and certifies, R1 is **R1 IMPLEMENTATION COMPLETE — OPERATOR EXTRACTION REQUIRED**.
