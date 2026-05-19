# MacBook Transition Safety Audit

## Purpose

This diagnostics phase audits whether the EpochForge repository and local workflow can move from a Windows PC to a MacBook without losing deterministic behavior, validation reliability, Docker compatibility, branch safety, or generated-report reproducibility.

This phase is read-only and descriptive-only. It does not enable planner execution, planner recommendations, scoring, ranking, production consumption, runtime mutation, or orchestration execution.

## Final Classification

`macbook_transition_safe_with_setup_required`

No hard transition blockers were found. The repository can transition to a MacBook after macOS-local setup and validation. The safety classification is not `macbook_transition_safe` because active setup docs and scripts still contain Windows-first assumptions that must be translated or documented for macOS.

## What Was Audited

- Windows-specific hardcoded paths and `D:\Forge` references.
- PowerShell-only command and script assumptions.
- `.venv\Scripts\python.exe` assumptions.
- Docker Compose path, volume, and platform assumptions.
- Frontend/backend Vite proxy assumptions.
- Line-ending sensitivity and repository normalization.
- Case-sensitive filename collision risk.
- Generated report reproducibility risk.
- Scripts that may fail on macOS/Linux.
- macOS setup documentation coverage.
- Apple Silicon dependency and binary-download risk.

## Generated Evidence

- `docs/generated/macbook_transition_safety_audit.json`
- Schema: `macbook_transition_safety_audit.v1`
- Report hash: `b237ffc97e807e89203408206a3ea3ea2b055f10a967ec4e172776b2a30b0c8c`
- Blockers: `0`
- Warnings: `5`

## Blockers

None detected.

The audit did not find tracked filename case collisions. Docker Compose does not pin `linux/amd64`, so no Apple Silicon Docker platform blocker was detected.

## Warnings

1. `docs/LOCAL_DEVELOPMENT.md` and `docs/WORKSPACE_HEALTHCHECK.md` are Windows-first and still use PowerShell, `D:\Forge`, and Windows virtualenv commands.
2. `package.json` POSIX backend scripts expect `../.venv/bin/python` from `backend`, while the README creates `backend/.venv`; the MacBook setup should standardize one backend virtualenv path.
3. `scripts/check_forge_workspace.ps1` and `scripts/smoke_data_bundle_handoff.ps1` are PowerShell diagnostics without native macOS/Linux equivalents.
4. Historical migration and data-bundle docs contain many Windows absolute paths and Windows interpreter examples. Treat those commands as historical unless translated.
5. Apple Silicon installation must validate Python native-wheel packages and Electron binary architecture. Sensitive dependencies include `psycopg2-binary==2.9.10`, `numpy>=1.26.0`, and `pyyaml>=6.0`.

## Files Needing Path Normalization

Highest-priority active workflow files:

- `docs/LOCAL_DEVELOPMENT.md`
- `docs/WORKSPACE_HEALTHCHECK.md`
- `package.json`
- `scripts/check_forge_workspace.ps1`
- `scripts/smoke_data_bundle_handoff.ps1`

Historical or supporting files with Windows command examples include data-bundle and migration notes such as:

- `docs/BUNDLE_ITEM_MIGRATION_MILESTONE_SUMMARY.md`
- `docs/LE_TOOLS_IMPORT_CONTEXT_DRY_RUN.md`
- `docs/LE_TOOLS_IMPORT_CONTEXT_SIDECAR_DESIGN.md`
- `docs/BUNDLE_ITEM_ADAPTER_MAP_PROPOSAL.md`
- `docs/DATA_BUNDLE_COMPATIBILITY.md`

These historical files do not block transition by themselves, but commands copied from them need macOS path translation.

## Docker And Proxy Result

Docker and frontend/backend proxy configuration is currently cross-platform compatible:

- Compose volumes use relative repository paths.
- Backend and frontend dependency directories use named volumes where appropriate.
- No `linux/amd64` platform pin was detected.
- Docker frontend config sets `VITE_API_BASE_URL=/api`.
- Docker frontend config sets `VITE_API_PROXY_TARGET=http://backend:5000`.
- Vite supports `VITE_API_PROXY_TARGET` and keeps the local default `http://localhost:5050`.

The prior browser/container proxy mismatch is not a MacBook blocker.

## Line Endings And Case Sensitivity

The repository includes `.gitattributes` with:

```text
* text=auto eol=lf
```

The audit classified line endings as guarded by repository normalization. No tracked case-sensitive filename collisions were detected.

## Required MacBook Setup

Use macOS-local paths and do not reuse Windows absolute paths:

```bash
xcode-select --install
brew install python@3.11 node@20
python3.11 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
npm ci
npm --prefix frontend ci
docker compose config
```

Install Docker Desktop for Mac with Apple Silicon support before Docker-backed validation.

## MacBook Validation Commands

Run these on the MacBook after setup:

```bash
git status --short
python3 -m py_compile backend/scripts/report_macbook_transition_safety_audit.py
python3 backend/scripts/report_macbook_transition_safety_audit.py
python3 -m json.tool docs/generated/macbook_transition_safety_audit.json
python3 -m pytest backend/tests/test_macbook_transition_safety_audit.py -q
npm --prefix frontend test -- src/__tests__/config/vite-proxy-routing.test.ts
docker compose config
git diff --check
```

## Windows PC Requirement

The Windows PC is not required after MacBook setup and validation complete.

Conditions:

- Clone any companion data repository needed for local diagnostics, such as `last-epoch-data`.
- Recreate `.env` and data-bundle paths with macOS-local paths.
- Validate Docker, backend, frontend, and deterministic report generation directly on the MacBook.

## Preserved Prohibitions

This audit preserves:

- `planner_execution_enabled=false`
- `planner_recommendations_enabled=false`
- `ranking_enabled=false`
- `scoring_enabled=false`
- `production_consumption_enabled=false`
- `runtime_mutation_enabled=false`
- `orchestration_execution_enabled=false`
