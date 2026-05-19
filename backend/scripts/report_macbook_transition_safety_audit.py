"""Generate the MacBook transition safety audit report.

This report is deterministic, read-only, and descriptive-only. It inventories
cross-platform transition risks without changing runtime behavior, enabling
planner execution, or altering production data consumption.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "docs" / "generated" / "macbook_transition_safety_audit.json"

SCHEMA_VERSION = "macbook_transition_safety_audit.v1"
AUDIT_STATUS = "read_only_descriptive_transition_audit"
REPORT_GENERATED_AT = "2026-05-19T00:00:00Z"

EXCLUDED_SCAN_PATHS = {
    "backend/scripts/report_macbook_transition_safety_audit.py",
    "backend/tests/test_macbook_transition_safety_audit.py",
    "docs/generated/macbook_transition_safety_audit.json",
    "docs/migration/MACBOOK_TRANSITION_SAFETY_AUDIT.md",
}

EXCLUDED_SCAN_PREFIXES = (
    ".git/",
    ".venv/",
    "backend/.venv/",
    "frontend/node_modules/",
    "node_modules/",
    "backend/pytest_bundle_tmp_run/",
    "__pycache__/",
)

TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".css",
    ".env",
    ".example",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".lock",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

WORKFLOW_FILES = {
    ".env.example",
    ".gitattributes",
    "README.md",
    "package.json",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "docs/LOCAL_DEVELOPMENT.md",
    "docs/WORKSPACE_HEALTHCHECK.md",
    "backend/requirements.txt",
    "frontend/package.json",
    "frontend/vite.config.ts",
    "scripts/check_forge_workspace.ps1",
    "scripts/smoke_data_bundle_handoff.ps1",
}

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "windows_absolute_path",
        re.compile(r"[A-Za-z]:\\(?:[A-Za-z0-9_. $(){}\[\]-]+\\?)+"),
    ),
    (
        "windows_python_venv",
        re.compile(
            r"(?:\.(?:\\{1,2}))?\.venv(?:\\{1,2})Scripts(?:\\{1,2})python\.exe|"
            r"backend(?:\\{1,2})\.venv(?:\\{1,2})Scripts",
            re.IGNORECASE,
        ),
    ),
    (
        "powershell_only",
        re.compile(
            r"\b(?:PowerShell|powershell|pwsh|Get-ChildItem|Test-Path|Select-String|"
            r"Invoke-RestMethod|Test-NetConnection|Copy-Item|Remove-Item)\b|\.ps1\b"
        ),
    ),
    (
        "backslash_repo_path",
        re.compile(r"\b(?:backend|frontend|docs|scripts|tests|data)(?:\\{1,2})[A-Za-z0-9_.\\/-]+"),
    ),
)


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(REPO_ROOT / line.strip() for line in result.stdout.splitlines() if line.strip())


def _is_scan_excluded(rel_path: str) -> bool:
    return rel_path in EXCLUDED_SCAN_PATHS or rel_path.startswith(EXCLUDED_SCAN_PREFIXES)


def _is_text_candidate(path: Path) -> bool:
    if path.name in {"Dockerfile", ".gitattributes", ".env.example"}:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def _read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _scan_path_assumptions(files: list[Path]) -> dict[str, Any]:
    hit_counts_by_type: Counter[str] = Counter()
    hit_counts_by_file: dict[str, Counter[str]] = {}
    examples_by_file: dict[str, dict[str, list[str]]] = {}
    generated_source_path_hits = 0

    for path in files:
        rel_path = _rel(path)
        if _is_scan_excluded(rel_path) or not _is_text_candidate(path):
            continue
        text = _read_text(path)
        if text is None:
            continue

        if rel_path.startswith("docs/generated/"):
            if "D:\\Forge" in text or "source_path" in text:
                generated_source_path_hits += text.count("D:\\Forge")
            continue

        file_counter: Counter[str] = Counter()
        file_examples: dict[str, list[str]] = {}
        for pattern_name, pattern in PATTERNS:
            matches = pattern.findall(text)
            if not matches:
                continue
            file_counter[pattern_name] = len(matches)
            hit_counts_by_type[pattern_name] += len(matches)
            normalized_matches = sorted({str(match)[:160] for match in matches})
            file_examples[pattern_name] = normalized_matches[:5]

        if file_counter:
            hit_counts_by_file[rel_path] = file_counter
            examples_by_file[rel_path] = file_examples

    weighted_files = []
    for rel_path, counts in hit_counts_by_file.items():
        weight = (
            counts["windows_absolute_path"] * 4
            + counts["windows_python_venv"] * 4
            + counts["powershell_only"] * 3
            + counts["backslash_repo_path"]
        )
        if rel_path in WORKFLOW_FILES:
            weight += 100
        weighted_files.append(
            {
                "path": rel_path,
                "scope": "active_workflow" if rel_path in WORKFLOW_FILES else "historical_or_supporting",
                "hit_counts": dict(sorted(counts.items())),
                "examples": examples_by_file[rel_path],
                "normalization_needed": rel_path in WORKFLOW_FILES or "docs/migration/" not in rel_path,
                "weight": weight,
            }
        )

    weighted_files.sort(key=lambda entry: (-entry["weight"], entry["path"]))
    for entry in weighted_files:
        entry.pop("weight")

    return {
        "hit_counts_by_type": dict(sorted(hit_counts_by_type.items())),
        "files_with_path_assumptions_count": len(hit_counts_by_file),
        "active_workflow_files_with_path_assumptions": [
            entry for entry in weighted_files if entry["scope"] == "active_workflow"
        ],
        "top_files_needing_path_normalization": weighted_files[:25],
        "historical_or_supporting_files_with_path_assumptions_count": sum(
            1 for entry in weighted_files if entry["scope"] == "historical_or_supporting"
        ),
        "generated_report_windows_source_path_hits": generated_source_path_hits,
        "scan_exclusions": sorted(EXCLUDED_SCAN_PATHS),
    }


def _scan_line_endings(files: list[Path]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    mixed_files: list[str] = []
    crlf_files: list[str] = []
    skipped_large_text_files = 0

    for path in files:
        rel_path = _rel(path)
        if _is_scan_excluded(rel_path) or not _is_text_candidate(path):
            continue
        try:
            if path.stat().st_size > 2_000_000:
                skipped_large_text_files += 1
                continue
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw:
            continue

        crlf = raw.count(b"\r\n")
        lf = raw.count(b"\n") - crlf
        cr = raw.count(b"\r") - crlf
        if crlf and (lf or cr):
            counts["mixed"] += 1
            mixed_files.append(rel_path)
        elif crlf:
            counts["crlf"] += 1
            crlf_files.append(rel_path)
        elif lf:
            counts["lf"] += 1
        elif cr:
            counts["cr_only"] += 1
        else:
            counts["no_newlines"] += 1

    gitattributes = REPO_ROOT / ".gitattributes"
    gitattributes_text = _read_text(gitattributes) or ""
    return {
        "gitattributes_present": gitattributes.exists(),
        "gitattributes_enforces_lf": "* text=auto eol=lf" in gitattributes_text,
        "line_ending_counts": dict(sorted(counts.items())),
        "mixed_line_ending_files": sorted(mixed_files)[:25],
        "crlf_files": sorted(crlf_files)[:25],
        "skipped_large_text_files": skipped_large_text_files,
        "classification": (
            "line_endings_guarded_by_gitattributes"
            if gitattributes.exists() and "* text=auto eol=lf" in gitattributes_text
            else "line_endings_guard_missing"
        ),
    }


def _scan_case_collisions(files: list[Path]) -> dict[str, Any]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for path in files:
        rel_path = _rel(path)
        buckets[rel_path.lower()].append(rel_path)
    collisions = [sorted(paths) for paths in buckets.values() if len(set(paths)) > 1]
    return {
        "case_collision_count": len(collisions),
        "case_collisions": sorted(collisions),
        "classification": "no_case_sensitive_filename_collisions_detected"
        if not collisions
        else "case_sensitive_filename_collisions_detected",
    }


def _read_required(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _inspect_docker_and_proxy() -> dict[str, Any]:
    compose = _read_required("docker-compose.yml")
    compose_prod = _read_required("docker-compose.prod.yml")
    vite_config = _read_required("frontend/vite.config.ts")

    docker_platform_pins = re.findall(r"^\s*platform\s*:\s*(.+)$", compose + "\n" + compose_prod, re.MULTILINE)
    relative_volume_markers = [
        "./backend:/app",
        "./docs/generated:/docs/generated:ro",
        "./data:/data",
        "./frontend:/app",
        "./backend/src/constants:/backend/src/constants:ro",
    ]

    return {
        "docker_compose_files_present": {
            "docker-compose.yml": (REPO_ROOT / "docker-compose.yml").exists(),
            "docker-compose.prod.yml": (REPO_ROOT / "docker-compose.prod.yml").exists(),
        },
        "docker_platform_pins": sorted(docker_platform_pins),
        "has_apple_silicon_blocking_platform_pin": any("linux/amd64" in pin for pin in docker_platform_pins),
        "relative_volume_markers_present": {
            marker: marker in compose for marker in relative_volume_markers
        },
        "backend_runtime_uses_container_venv_volume": "backend_venv:/venv" in compose,
        "frontend_node_modules_is_named_volume": "frontend_node_modules:/app/node_modules" in compose,
        "browser_api_base_is_relative_in_docker": "VITE_API_BASE_URL: /api" in compose,
        "vite_proxy_target_is_container_internal_in_docker": (
            "VITE_API_PROXY_TARGET: http://backend:5000" in compose
        ),
        "vite_proxy_target_env_supported": "VITE_API_PROXY_TARGET" in vite_config,
        "vite_local_default_backend_target": "http://localhost:5050" in vite_config,
        "classification": "docker_and_proxy_paths_cross_platform_ready"
        if (
            "VITE_API_BASE_URL: /api" in compose
            and "VITE_API_PROXY_TARGET: http://backend:5000" in compose
            and "VITE_API_PROXY_TARGET" in vite_config
            and not any("linux/amd64" in pin for pin in docker_platform_pins)
        )
        else "docker_or_proxy_review_required",
    }


def _inspect_docs_and_dependencies(path_scan: dict[str, Any]) -> dict[str, Any]:
    readme = _read_required("README.md")
    local_dev = _read_required("docs/LOCAL_DEVELOPMENT.md")
    package_json = json.loads(_read_required("package.json"))
    frontend_package_json = json.loads(_read_required("frontend/package.json"))
    requirements = _read_required("backend/requirements.txt").splitlines()

    root_scripts = package_json.get("scripts", {})
    return {
        "readme_has_macos_style_backend_setup": all(
            marker in readme
            for marker in [
                "python -m venv .venv",
                "source .venv/bin/activate",
                "pip install -r requirements.txt",
            ]
        ),
        "readme_backend_setup_uses_backend_local_venv": "cd backend\npython -m venv .venv" in readme,
        "local_development_doc_is_windows_first": "PowerShell path" in local_dev,
        "local_development_doc_has_macos_equivalents": "source backend/.venv/bin/activate" in local_dev,
        "root_npm_posix_backend_script": root_scripts.get("dev:backend"),
        "root_npm_windows_backend_script": root_scripts.get("dev:backend:win"),
        "root_npm_posix_script_expects_root_venv": "../.venv/bin/python" in root_scripts.get("dev:backend", ""),
        "electron_mac_targets": package_json.get("build", {}).get("mac", {}).get("target", []),
        "frontend_electron_dependency": frontend_package_json.get("devDependencies", {}).get("electron")
        or frontend_package_json.get("dependencies", {}).get("electron"),
        "apple_silicon_sensitive_python_dependencies": [
            dep
            for dep in requirements
            if dep.startswith(("psycopg2-binary", "numpy", "pyyaml"))
        ],
        "active_workflow_path_assumption_count": len(
            path_scan["active_workflow_files_with_path_assumptions"]
        ),
        "classification": "macos_setup_documentation_partial",
    }


def _required_setup_steps() -> list[dict[str, str]]:
    return [
        {
            "step": "install_platform_tools",
            "command": "xcode-select --install",
            "reason": "Provides compiler and git tooling expected by Python and Node dependency installation.",
        },
        {
            "step": "install_runtime_dependencies",
            "command": "brew install python@3.11 node@20",
            "reason": "Keeps Python and Node aligned with the repository's documented local versions.",
        },
        {
            "step": "install_docker_desktop",
            "command": "Install Docker Desktop for Mac with Apple Silicon support, then start Docker.",
            "reason": "PostgreSQL, Redis, and Compose validation depend on Docker Desktop locally.",
        },
        {
            "step": "create_backend_virtualenv",
            "command": "python3.11 -m venv backend/.venv && source backend/.venv/bin/activate",
            "reason": "Avoids Windows-only .venv\\Scripts paths and keeps backend dependencies under backend/.venv.",
        },
        {
            "step": "install_backend_dependencies",
            "command": "python -m pip install --upgrade pip && python -m pip install -r backend/requirements.txt",
            "reason": "Installs Flask, pytest, psycopg2-binary, numpy, and other backend dependencies on macOS.",
        },
        {
            "step": "install_node_dependencies",
            "command": "npm ci && npm --prefix frontend ci",
            "reason": "Uses lockfiles for root Electron tooling and frontend Vite tooling.",
        },
        {
            "step": "validate_compose",
            "command": "docker compose config",
            "reason": "Confirms Compose files render on the MacBook before starting services.",
        },
    ]


def _recommended_macos_commands() -> list[str]:
    return [
        "git switch dev",
        "git pull origin dev",
        "python3.11 -m venv backend/.venv",
        "source backend/.venv/bin/activate",
        "python -m pip install --upgrade pip",
        "python -m pip install -r backend/requirements.txt",
        "npm ci",
        "npm --prefix frontend ci",
        "docker compose config",
        "docker compose up -d db redis",
        "cd backend && FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. .venv/bin/python -m flask db upgrade",
        "cd backend && FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. .venv/bin/python -m flask seed",
        "cd backend && FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. .venv/bin/python -m flask seed-passives",
        "cd backend && FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. .venv/bin/python -m flask run --port=5050 --debug",
        "npm --prefix frontend run dev",
    ]


def _macbook_validation_commands() -> list[str]:
    return [
        "git status --short",
        "python3 -m py_compile backend/scripts/report_macbook_transition_safety_audit.py",
        "python3 backend/scripts/report_macbook_transition_safety_audit.py",
        "python3 -m json.tool docs/generated/macbook_transition_safety_audit.json",
        "python3 -m pytest backend/tests/test_macbook_transition_safety_audit.py -q",
        "npm --prefix frontend test -- src/__tests__/config/vite-proxy-routing.test.ts",
        "docker compose config",
        "git diff --check",
    ]


def _build_warnings(
    path_scan: dict[str, Any],
    docs_dependencies: dict[str, Any],
    line_endings: dict[str, Any],
    docker_proxy: dict[str, Any],
) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = [
        {
            "id": "active_docs_are_windows_first",
            "classification": "setup_documentation_gap",
            "files": ["docs/LOCAL_DEVELOPMENT.md", "docs/WORKSPACE_HEALTHCHECK.md"],
            "details": (
                "Active local setup and health-check docs still center PowerShell, D:\\Forge, "
                "and Windows venv commands. macOS equivalents are needed before the workflow is "
                "self-serve on a MacBook."
            ),
        },
        {
            "id": "root_npm_backend_venv_path_mismatch",
            "classification": "path_normalization_required",
            "files": ["package.json", "README.md"],
            "details": (
                "The README creates backend/.venv from inside backend, while root npm POSIX "
                "backend scripts call ../.venv/bin/python from backend. Pick one venv location "
                "or document the split explicitly for macOS."
            ),
        },
        {
            "id": "powershell_healthcheck_is_windows_only",
            "classification": "script_portability_gap",
            "files": ["scripts/check_forge_workspace.ps1", "scripts/smoke_data_bundle_handoff.ps1"],
            "details": (
                "PowerShell diagnostics remain useful on Windows but do not provide a native "
                "macOS/Linux equivalent."
            ),
        },
        {
            "id": "historical_docs_contain_windows_absolute_paths",
            "classification": "historical_command_translation_required",
            "files": [
                entry["path"]
                for entry in path_scan["top_files_needing_path_normalization"]
                if entry["scope"] == "historical_or_supporting"
            ][:10],
            "details": (
                "Older migration and data-bundle docs contain D:\\Forge paths and Windows "
                "interpreter examples. Treat them as historical evidence unless translated."
            ),
        },
        {
            "id": "apple_silicon_dependency_install_must_be_validated",
            "classification": "dependency_install_validation_required",
            "files": ["backend/requirements.txt", "package.json", "frontend/package.json"],
            "details": (
                "Python native-wheel packages and Electron download architecture should be "
                "validated on Apple Silicon with the chosen Python and Node versions."
            ),
            "sensitive_dependencies": docs_dependencies["apple_silicon_sensitive_python_dependencies"],
        },
    ]

    if not line_endings["gitattributes_enforces_lf"]:
        warnings.append(
            {
                "id": "line_ending_guard_missing",
                "classification": "line_ending_risk",
                "files": [".gitattributes"],
                "details": "The repository lacks an LF normalization guard.",
            }
        )
    if docker_proxy["has_apple_silicon_blocking_platform_pin"]:
        warnings.append(
            {
                "id": "docker_platform_pin_blocks_apple_silicon",
                "classification": "docker_apple_silicon_blocker",
                "files": ["docker-compose.yml", "docker-compose.prod.yml"],
                "details": "A linux/amd64 platform pin was detected.",
            }
        )
    return warnings


def build_report() -> dict[str, Any]:
    tracked_files = _tracked_files()
    path_scan = _scan_path_assumptions(tracked_files)
    line_endings = _scan_line_endings(tracked_files)
    case_scan = _scan_case_collisions(tracked_files)
    docker_proxy = _inspect_docker_and_proxy()
    docs_dependencies = _inspect_docs_and_dependencies(path_scan)

    blockers: list[dict[str, Any]] = []
    if case_scan["case_collision_count"]:
        blockers.append(
            {
                "id": "case_sensitive_filename_collisions",
                "classification": "macbook_transition_blocker",
                "details": "Tracked filenames collide on a case-insensitive checkout.",
                "files": case_scan["case_collisions"],
            }
        )
    if docker_proxy["has_apple_silicon_blocking_platform_pin"]:
        blockers.append(
            {
                "id": "apple_silicon_docker_platform_pin",
                "classification": "macbook_transition_blocker",
                "details": "Docker Compose pins linux/amd64, which can block native Apple Silicon usage.",
                "files": ["docker-compose.yml", "docker-compose.prod.yml"],
            }
        )

    warnings = _build_warnings(path_scan, docs_dependencies, line_endings, docker_proxy)
    classification = (
        "macbook_transition_blocked"
        if blockers
        else "macbook_transition_safe_with_setup_required"
        if warnings
        else "macbook_transition_safe"
    )

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": REPORT_GENERATED_AT,
        "audit_status": AUDIT_STATUS,
        "transition_classification": classification,
        "blockers": blockers,
        "warnings": warnings,
        "required_setup_steps": _required_setup_steps(),
        "recommended_macos_commands": _recommended_macos_commands(),
        "validation_commands_to_run_on_macbook": _macbook_validation_commands(),
        "windows_pc_still_required": {
            "required": False,
            "classification": "not_required_after_macbook_setup_and_validation",
            "conditions": [
                "Clone both repositories on macOS if last-epoch-data artifacts are needed.",
                "Create macOS-local .env values and data-bundle paths instead of reusing D:\\Forge paths.",
                "Complete Docker, backend, frontend, and report reproducibility validation on the MacBook.",
            ],
        },
        "path_assumption_scan": path_scan,
        "files_needing_path_normalization": path_scan["top_files_needing_path_normalization"],
        "docker_and_proxy_compatibility": docker_proxy,
        "line_ending_sensitivity": line_endings,
        "case_sensitive_filename_scan": case_scan,
        "documentation_and_dependency_readiness": docs_dependencies,
        "generated_report_reproducibility_risks": {
            "classification": "generated_reports_contain_historical_windows_source_paths"
            if path_scan["generated_report_windows_source_path_hits"]
            else "no_generated_report_windows_source_paths_detected",
            "windows_source_path_hit_count": path_scan["generated_report_windows_source_path_hits"],
            "deterministic_report_hashing_required": True,
            "report_reproducibility_validation": "run_generator_twice_and_compare_report_hash",
        },
        "prohibitions_preserved": {
            "planner_execution_enabled": False,
            "planner_recommendations_enabled": False,
            "ranking_enabled": False,
            "scoring_enabled": False,
            "production_consumption_enabled": False,
            "runtime_mutation_enabled": False,
            "orchestration_execution_enabled": False,
        },
        "audit_scope_boundaries": [
            "read_only",
            "descriptive_only",
            "fail_visible",
            "no_runtime_behavior_change",
            "no_planner_execution",
            "no_production_consumption",
        ],
    }
    report["report_hash"] = hashlib.sha256(_canonical_json(report).encode("utf-8")).hexdigest()
    return report


def write_report(path: Path = REPORT_PATH) -> dict[str, Any]:
    report = build_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_json(report).encode("utf-8"))
    return report


def main() -> None:
    report = write_report()
    print(
        json.dumps(
            {
                "report_path": str(REPORT_PATH.relative_to(REPO_ROOT)),
                "report_hash": report["report_hash"],
                "transition_classification": report["transition_classification"],
                "blocker_count": len(report["blockers"]),
                "warning_count": len(report["warnings"]),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
