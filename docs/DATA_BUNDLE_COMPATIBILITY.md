# Data Bundle Compatibility

This document covers the Phase 1C Forge data bundle compatibility reader and the Phase 1D cross-repo handoff smoke test.

The reader is read-only. It inspects a `last-epoch-data` bundle control plane and does not replace production data loaders, change simulation math, migrate family data, update game data, or affect frontend behavior.

## Bundle Path

By default, local development checks use:

```text
D:\Forge\last-epoch-data\data_bundle
```

Override the bundle path with:

```powershell
$env:FORGE_DATA_BUNDLE_DIR = "D:\Forge\last-epoch-data\data_bundle"
```

## Run The Check

From the repo root:

```powershell
python backend\scripts\check_data_bundle.py
```

Or pass a path directly:

```powershell
python backend\scripts\check_data_bundle.py --bundle-dir D:\Forge\last-epoch-data\data_bundle
```

For JSON output:

```powershell
python backend\scripts\check_data_bundle.py --json
```

## Status Meanings

`compatible` means the control-plane files are present, supported, consistent, and contain no warnings.

`compatible_with_warnings` means the bundle can be inspected, but some families or metadata require warnings, degrade behavior, or block diagnostics before future loader migration.

`incompatible` means the control plane is not safe to inspect or use for migration decisions because required files are missing, JSON is invalid, bundle IDs mismatch, schema versions are unsupported, or validation status failed.

## Expected Current Result

The Phase 1A/1B bundle from `last-epoch-data` is expected to return `compatible_with_warnings`.

That is intentional because the bundle is currently control-plane only:

- Required Now families are represented in the manifest.
- Family JSON files are not migrated yet.
- Many families are deferred, hybrid, hardcoded, or approximation-backed.
- Block actions are reported as developer diagnostics only in Phase 1C.
- No family should be treated as authoritative, canonical-ready, or simulation-ready yet.

## Next Phase

Phase 1D should manually smoke test the cross-repo handoff: generate and validate the bundle in `last-epoch-data`, point this reader at it, confirm diagnostics, and verify existing Forge behavior remains unchanged.

## Phase 1D Handoff Smoke Test

The Phase 1D smoke test verifies that the two repos agree on the bundle control-plane contract:

- `last-epoch-data` can generate the bundle skeleton.
- `last-epoch-data` can validate the bundle control plane.
- `le-the-forge` can inspect the generated bundle and classify compatibility.

It does not replace production loaders, start the app, start Docker containers, load family JSON files into production registries, change simulation math, or migrate data families.

Run it from `D:\Forge\le-the-forge`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_data_bundle_handoff.ps1
```

Override the workspace root when needed:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_data_bundle_handoff.ps1 -WorkspaceRoot "D:\Forge"
```

The expected current result is `compatible_with_warnings`. Warnings are expected because the Phase 1A/1B bundle is control-plane only, most Required Now families are deferred, and block/degrade actions are diagnostics until future loader migrations intentionally consume bundle families.

## Smoke Test Troubleshooting

Missing backend venv:

```powershell
cd D:\Forge\le-the-forge\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Missing `last-epoch-data` scripts:

- Confirm the workspace layout is `D:\Forge\last-epoch-data`.
- Confirm Phase 1A/1B exists in `last-epoch-data`:
  - `tools\scripts\generate_data_bundle_skeleton.py`
  - `tools\scripts\validate_data_bundle.py`

Incompatible result:

- Run `python tools\scripts\validate_data_bundle.py` in `last-epoch-data`.
- Check for missing control-plane files, invalid JSON, unsupported schema versions, or bundle ID mismatches.

JSON parse failure:

- Run the Forge compatibility command directly with `--json`.
- Confirm no extra output is printed before or after the JSON payload.

Path or layout mismatch:

- Use `-WorkspaceRoot` to point the smoke test at the parent folder containing both repos.
- Use `FORGE_DATA_BUNDLE_DIR` only for the standalone compatibility reader; the Phase 1D smoke script derives the bundle path from `-WorkspaceRoot`.
