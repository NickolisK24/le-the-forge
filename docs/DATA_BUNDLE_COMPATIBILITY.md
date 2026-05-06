# Data Bundle Compatibility

This document covers the Phase 1C Forge data bundle compatibility reader.

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
