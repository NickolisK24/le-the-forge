# R1 Raw Snapshot and Provenance Contract

Status: implemented (`tools/scripts/r1_snapshot.py`, tests in `tools/scripts/test_r1_snapshot.py`).
It has not yet been applied to a real install. The first real snapshot is the 1.5.x operator extraction (R1.3).

## Why

The 2026-10 audit found three gaps (SYS-12, EXT-5):
- The 1.4.6 exports cannot be regenerated: the game files they came from were never preserved and never hashed.
- The patch label was an operator-named folder.
- Nothing recorded which extractor commit or tool versions produced them.

This contract makes every extraction answer one question: **which exact bytes, read by which code, produced these exports?**

## Two manifests

### 1. Raw snapshot manifest (`snapshots/raw/<snapshot_id>.json`, committed)

It is built by `r1_snapshot.py snapshot` from a game install.

| Field | Content |
| --- | --- |
| `snapshot_schema` | `r1_raw_snapshot/1` |
| `snapshot_id` | `<version>_<build>_<first 12 hex of content_hash>` |
| `source_identity.game_version` | Read from the install: `globalgamemanagers` → `PlayerSettings.bundleVersion` (needs UnityPy). The operator's declared label is used **only** as a fallback, and is then marked `PARTIAL`. |
| `source_identity.build_id` | Steam `appmanifest_899770.acf` `buildid` |
| `source_identity.unity_version` | Serialized-file header of `globalgamemanagers` (fallback: `boot.config`) |
| `source_identity.game_assembly_sha256`, `global_metadata_sha256` | Hashes of the IL2CPP binary and metadata |
| `source_identity.identity_status` | `AUTHORITATIVE` (version, build, Unity and GameAssembly all read from the install), `PARTIAL`, or `INCOMPLETE` |
| `source_identity.declared_matches` | Whether the operator's `--declared-patch` agrees with what the install says |
| `content_hash` | sha256 over `{relative_path, size, sha256}` for **every** file in the install |
| `source_files[]` | Every file: `relative_path`, `size`, `sha256`, `role`, `stored`, `content_available` |
| `totals.by_role` | Files, bytes and stored files per role |
| `store` | Strategy, scope, a non-path location label, and the git policy |
| `nondeterministic` | Capture time, host OS, Python version and install folder name. **Excluded from `content_hash`.** |

### 2. Extraction run manifest (`snapshots/runs/<run_id>.json`, committed)

It is built by `r1_snapshot.py run-manifest` after the pipeline runs.

| Requirement | Field |
| --- | --- |
| Game patch and version | `source_identity.game_version` and `patch_label` |
| Game build identifier | `source_identity.build_id` |
| Extraction timestamp | `nondeterministic.recorded_at` |
| Extractor commit SHA | `extractor.commit`, `extractor.dirty`, `extractor.dirty_paths` |
| Source file identities and hashes | `raw_snapshot.manifest` → `source_files[]` |
| Raw snapshot identity | `raw_snapshot.snapshot_id`, `raw_snapshot.content_hash` |
| Tool versions | `tools`: Python, UnityPy, TypeTreeGeneratorAPI, pythonnet, pefile; `external.lock` pins and its sha256 |
| OS and runtime | `nondeterministic.host_os`, `machine` |
| Export hashes | `exports[].sha256` (bytes) and `exports[].content_sha256` (volatile keys removed) |
| Record counts | `record_counts` |
| Warnings | `warnings` |
| Unknown tables | `unknown_tables` (the denominator's UNKNOWN entries) |
| Unknown fields | `unknown_fields` (from the field-survival report, R1.5) |
| Unknown enums | `unknown_enums` (from the enum/patch-diff report, R1.10) |
| Failed and partial domains | `failed_domains` (in-scope entries with no export, plus failed pipeline steps); `partial_domains` |
| Content identity | `exports_content_hash` and `manifest_content_hash` (both exclude `nondeterministic`, `extractor` and `tools`) |

## Deterministic content vs capture metadata

These keys never contribute to a content hash: `generated_at`, `generated_on`, `extracted_at`, `timestamp`, `run_started_at`, `created_at`, `generation_time`, `installPath` and `install_path`.

Each export gets two hashes:
- `sha256`: the exact bytes;
- `content_sha256`: canonical JSON with those keys removed.

Reproducibility (R1.11) compares `content_sha256`.

## File roles and preservation scope

Every file is hashed. Only the extraction inputs are copied into the store by default (`--store-scope extraction-inputs`):

| Role | Examples | Stored by default |
| --- | --- | --- |
| `il2cpp_binary`, `il2cpp_metadata` | `GameAssembly.dll`, `global-metadata.dat` | yes |
| `engine_binary` | `UnityPlayer.dll` (Unity version) | yes |
| `serialized_file` | `globalgamemanagers*`, `resources.assets`, `sharedassets*.assets`, `level*` | yes |
| `addressables_bundle`, `addressables_catalog` | `StreamingAssets/aa/**` | yes |
| `build_config` | `boot.config`, `app.info`, `ScriptingAssemblies.json` | yes |
| `streamed_resource` | `*.resS`, `*.resource` (texture, mesh and audio payloads) | no: hash only, so `RAW_REFERENCE_ONLY` |
| `native_binary`, `other` | `*.exe`, plugin DLLs | no: hash only |

`--store-scope all` stores everything, and `none` only hashes.

No current extractor reads streamed resources, so storing them is optional. Their hashes still pin the exact install.

## Storage strategy and licensing

- **Game files are never committed to git.** They are Eleventh Hour Games' proprietary content, and redistribution is not licensed. Only the manifests (hashes, sizes, roles and identity) are committed.
- **The content store** is a directory the operator controls: `objects/sha256/<aa>/<sha256>`. Identical files across patches are stored once.
  - The tool refuses a store inside the repository or inside the game install.
  - Keep it on durable private storage, such as a local disk plus a private backup. The manifest records only a non-path `location_label`.
- **Integrity:**
  - `r1_snapshot.py verify` re-hashes every stored object and re-derives `content_hash`.
  - `materialize()` rebuilds the stored part of the install tree for regeneration (R1.11).
- **Existing `patch_versions/`:** 1.3.7.1 and 1.4.3 `GameAssembly.dll` and `global-metadata.dat` are already committed. This contract does not delete them (out of scope, and the history keeps them anyway). It does stop adding binaries: future patches go to the content store. Whether to purge them from history is an owner decision on licensing.

## 1.4.6 status (retroactive)

`snapshots/runs/1.4.6_22986002.retroactive.json` records what exists for the current exports:
- export byte and content hashes, and record counts;
- the identity taken from `exports_json/metadata.json` (operator-declared label; GameAssembly sha256 matches the resources manifest);
- the 744 UNKNOWN denominator entries;
- the in-scope domains that have no export.

It has `raw_snapshot: null` and `reproducible_from_raw: false`. **1.4.6 is not reproducible from preserved raw input.** The only build-stamped raw dump is `extracted_raw/MasterAffixesList.json` (affixes).

The denominator reports this mechanically: 1 entry is RAW_AVAILABLE, 1,180 are RAW_MISSING and 145 are raw UNKNOWN.

## How the denominator uses snapshots

`r1_denominator.py` reads `snapshots/raw/*.json`. If a snapshot whose GameAssembly sha256 matches the denominator's build hashes the entry's source file:
- the entry becomes `RAW_AVAILABLE` when the content is stored;
- it becomes `RAW_REFERENCE_ONLY` when the file is hashed only.

Once the operator commits a 1.5.x snapshot, raw availability for the new denominator changes from RAW_MISSING with no further code change.

## Rules

1. An extraction run without a raw snapshot is a provenance record, not an extraction. It can never be certified (R1.14).
2. `identity_status` must be `AUTHORITATIVE` for certification. `PARTIAL` (for example, the operator-declared version) needs an explicit waiver in the certification report.
3. Snapshot manifests are append-only. A changed install is a new snapshot with a new `content_hash`.
4. `extractor.dirty: true` fails certification.
