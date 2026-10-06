#!/usr/bin/env python3
"""AUDIT-R1: inventory which last-epoch-data exports The Forge actually consumes.

Produces a deterministic snapshot (no timestamps) that last-epoch-data commits as
``docs/r1/forge_consumption_snapshot.json`` so its extraction denominator can
show SOURCE -> RAW -> EXTRACTOR -> EXPORT -> CONSUMER without a Forge checkout.

Method (mechanical):

1. Parse ``scripts/sync_game_data.py`` with ``ast``. Every ``SRC_DIR / "<x>.json"``
   (or ``SRC_DIR / "<dir>"``) read inside a function is an export it syncs, and
   every ``DATA_DIR / ... / "<y>.json"`` written in the same function is the
   Forge data file it produces.
2. For each produced data file, search non-test backend and frontend source for
   a path reference to it (path parts as adjacent string literals, or a
   ``dir/file.json`` string). Matches in report/diagnostic/comparison modules are
   recorded separately from runtime consumers.
3. Runtime-loaded Forge data files that no synced export produces are listed as
   non-extracted runtime inputs (hand-authored or third-party).

Usage:
    python3 scripts/r1_forge_consumption_inventory.py --output <path>
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "scripts" / "sync_game_data.py"
GENERATOR = "le-the-forge/scripts/r1_forge_consumption_inventory.py"
SNAPSHOT_VERSION = 1

BACKEND_GLOB = ("backend/app", (".py",))
FRONTEND_GLOB = ("frontend/src", (".ts", ".tsx", ".js", ".jsx"))
REPORT_MODULE_RE = re.compile(r"(report|diagnostic|comparison|validator|_diff|audit|adapter_report|prototype)",
                              re.IGNORECASE)
TEST_PATH_RE = re.compile(r"(^|/)(tests?|__tests__)(/|$)|\.test\.|\.spec\.")


def _const_parts(node: ast.AST) -> tuple[str | None, list[str]]:
    """Flatten ``BASE / "a" / "b"`` into (BASE name, ["a", "b"])."""
    parts: list[str] = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
            parts.insert(0, node.right.value)
        else:
            return None, []
        node = node.left
    if isinstance(node, ast.Name):
        return node.id, parts
    return None, []


def parse_sync(path: Path = SYNC) -> dict[str, dict[str, list[str]]]:
    """Map export name -> {sync_functions, data_files}."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, set[str]]] = {}

    def paths_in(node: ast.AST, base_name: str) -> tuple[set[str], set[str]]:
        files, dirs = set(), set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.BinOp):
                base, parts = _const_parts(sub)
                if base != base_name or not parts:
                    continue
                (files if parts[-1].endswith(".json") else dirs).add("/".join(parts))
        return files, dirs

    # main() writes some sync results itself: `if flag: path = DATA_DIR/...; sync_x(...)`.
    main_writes: dict[str, set[str]] = {}
    for fn in tree.body:
        if isinstance(fn, ast.FunctionDef) and fn.name == "main":
            for stmt in ast.walk(fn):
                if isinstance(stmt, ast.If):
                    files, _ = paths_in(stmt, "DATA_DIR")
                    calls = {c.func.id for c in ast.walk(stmt)
                             if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
                    for name in calls:
                        main_writes.setdefault(name, set()).update(files)

    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        if fn.name == "main" or fn.name.startswith("_"):
            continue
        read_files, read_dirs = paths_in(fn, "SRC_DIR")
        write_files, write_dirs = paths_in(fn, "DATA_DIR")
        reads = read_files | read_dirs
        # A directory write counts only when the function writes no named file
        # (e.g. localization/*); otherwise it is just a mkdir of the parent.
        writes = set(write_files) or {d + "/*" for d in write_dirs}
        if not write_files and fn.name in main_writes:
            writes = set(main_writes[fn.name]) or writes
        for r in reads:
            if r == "metadata.json":
                continue
            entry = out.setdefault(r, {"sync_functions": set(), "data_files": set()})
            entry["sync_functions"].add(fn.name)
            entry["data_files"].update(writes)
    return {k: {kk: sorted(vv) for kk, vv in v.items()} for k, v in sorted(out.items())}


def _source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for base, exts in (BACKEND_GLOB, FRONTEND_GLOB):
        d = root / base
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            rel = p.relative_to(root).as_posix()
            if p.is_file() and p.suffix in exts and not TEST_PATH_RE.search(rel):
                files.append(p)
    return files


def _ref_regex(data_file: str) -> re.Pattern[str]:
    parts = data_file.split("/")
    joined = r"\s*[,/)]\s*".join(r"""["']""" + re.escape(p) + r"""["']""" for p in parts)
    slash = re.escape("/".join(parts))
    return re.compile(rf"({joined})|({slash})")


def find_references(root: Path, data_files: list[str]) -> dict[str, dict[str, list[str]]]:
    texts = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8", errors="replace")
             for p in _source_files(root)}
    out: dict[str, dict[str, list[str]]] = {}
    for df in sorted(set(data_files)):
        if df.endswith("/*"):
            pattern = re.compile(r"""["']""" + re.escape(df[:-2]) + r"""["']\s*[,/)]""")
        else:
            pattern = _ref_regex(df)
        runtime, report = [], []
        for rel, text in texts.items():
            if pattern.search(text):
                (report if REPORT_MODULE_RE.search(Path(rel).name) else runtime).append(rel)
        out[df] = {"runtime_consumers": sorted(runtime), "report_only_references": sorted(report)}
    return out


def runtime_data_inputs(root: Path) -> list[str]:
    """Every data/**/*.json path referenced by non-test, non-report runtime code."""
    data_files = sorted(p.relative_to(root / "data").as_posix() for p in (root / "data").rglob("*.json"))
    refs = find_references(root, data_files)
    return sorted(df for df, r in refs.items() if r["runtime_consumers"])


def _git_head(root: Path) -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def build_snapshot(root: Path = ROOT, forge_commit: str | None = None) -> dict:
    sync = parse_sync(root / "scripts" / "sync_game_data.py")
    all_data = sorted({df for v in sync.values() for df in v["data_files"]})
    refs = find_references(root, all_data)
    exports = {}
    for name, info in sync.items():
        runtime = sorted({c for df in info["data_files"] for c in refs[df]["runtime_consumers"]})
        report = sorted({c for df in info["data_files"] for c in refs[df]["report_only_references"]})
        exports[name.rstrip("/")] = {
            "sync_functions": info["sync_functions"],
            "data_files": info["data_files"],
            "runtime_consumers": runtime,
            "report_only_references": report,
            "per_data_file": {df: refs[df] for df in info["data_files"]},
        }
    synced_outputs = set(all_data)
    runtime_inputs = runtime_data_inputs(root)
    return {
        "snapshot_id": "r1_forge_consumption_snapshot",
        "snapshot_version": SNAPSHOT_VERSION,
        "generator": GENERATOR,
        "forge_commit": forge_commit or _git_head(root),
        "method": __doc__.split("Usage:")[0].strip(),
        "exports": dict(sorted(exports.items())),
        "non_extracted_runtime_inputs": sorted(df for df in runtime_inputs if df not in synced_outputs),
        "hand_authored_backend_inputs": sorted(
            p.relative_to(root).as_posix() for p in (root / "backend" / "app" / "game_data").glob("*.json")),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", required=True, help="where to write the snapshot JSON")
    ap.add_argument("--forge-commit", default=None, help="override the recorded commit (tests)")
    args = ap.parse_args(argv)
    snap = build_snapshot(ROOT, args.forge_commit)
    Path(args.output).write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    consumed = sum(1 for e in snap["exports"].values() if e["runtime_consumers"])
    print(f"exports synced: {len(snap['exports'])}; consumed at runtime: {consumed}; "
          f"non-extracted runtime inputs: {len(snap['non_extracted_runtime_inputs'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
