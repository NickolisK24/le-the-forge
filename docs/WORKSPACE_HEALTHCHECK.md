# Forge Workspace Health Check

This document describes the local health-check script for the two-repo Forge workspace. The script exists to verify that the workspace still has the expected shape after moving both repositories under `D:\Forge`.

## Expected Layout

```text
D:\Forge\
  le-the-forge\
  last-epoch-data\
```

Both `le-the-forge` and `last-epoch-data` should be Git repositories with a `.git` directory.

## Run It

From `D:\Forge\le-the-forge`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_forge_workspace.ps1
```

The script can also be run from another directory because it defaults to checking `D:\Forge`.

## Result Meanings

`PASS` means the check found the expected local condition.

`WARN` means something may need attention, but the script did not find a critical workspace layout problem. Warnings do not cause a non-zero exit code.

`FAIL` means a critical issue was found, such as a missing repo folder, missing `.git` directory, or a Git remote that does not match the expected GitHub repository. Failures cause exit code `1`.

## What The Script Checks

- `D:\Forge`, `D:\Forge\le-the-forge`, and `D:\Forge\last-epoch-data` exist.
- Both repositories contain `.git`.
- `git status --short` and `git remote -v` work for both repositories.
- `le-the-forge` has a remote containing `NickolisK24/le-the-forge`.
- `last-epoch-data` has a remote containing `NickolisK24/last-epoch-data`.
- Both repositories are scanned for old hardcoded paths:
  - `D:\LastEpochTools`
  - `D:\Programming\the-forge`
- The old path scan is intentionally bounded. It targets source, config, and documentation file types such as PowerShell, Python, TypeScript, JavaScript, JSON, Markdown, YAML, TOML, INI, CFG, env/example, and text files.
- The scan skips common heavy or generated directories such as `.git`, `node_modules`, `.venv`, `venv`, `.venv311`, `.venv313`, `.python311`, `__pycache__`, `.pytest_cache`, `dist`, `build`, `coverage`, `.cache`, `.mypy_cache`, `.ruff_cache`, `.vite`, `.next`, and large local extraction/output folders. This keeps the health check fast and safe instead of treating the path scan as a fully exhaustive repository crawl.
- The frontend toolchain is present, dependencies appear installed, and the safest available TypeScript check can run.
- The backend Python environment exists and can run a lightweight pytest collection check when pytest is available.
- Docker Compose configuration can be validated with `docker compose config` when Docker is available.
- `last-epoch-data` has common documentation and environment markers.

## What The Script Does Not Do

- It does not modify application code.
- It does not modify simulation logic.
- It does not modify game data.
- It does not modify generated data.
- It does not modify `.env` files.
- It does not delete or recreate `.venv`.
- It does not delete `node_modules`.
- It does not install npm or Python dependencies.
- It does not start or stop Docker containers.
- It does not run the expensive `last-epoch-data` extraction pipeline.
- It does not automatically fix old hardcoded paths.

## Common Fixes

Reopen VS Code from the workspace parent:

```powershell
cd D:\Forge
code .
```

Recreate the backend virtual environment only when you intentionally want to replace it:

```powershell
cd D:\Forge\le-the-forge\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install frontend dependencies if `frontend\node_modules` is missing:

```powershell
cd D:\Forge\le-the-forge\frontend
npm install
```

If old hardcoded paths are detected, update them manually after confirming the reference is still active.

Run Docker Compose validation manually if needed:

```powershell
cd D:\Forge\le-the-forge
docker compose config
```
