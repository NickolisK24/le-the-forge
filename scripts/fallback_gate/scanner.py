"""Fallback-pattern scanner for data-consumption paths (AUDIT-R2 P16).

A faithful port of the R2 census extractor (R2_FALLBACK_AUDIT.md, method
section). It finds fallback *candidates*; classification lives in
``registry.json``. Scope:

    backend/app/**            (excluding tests, migrations, __pycache__)
    scripts/sync_game_data.py, scripts/generate_tree_data.py, scripts/build_sprite_map.py
    frontend/src/**           (excluding __tests__, test/, *.test.*, *.spec.*)

Each candidate gets a content fingerprint (file, pattern, normalised source
line) that is stable when unrelated lines move. Identical fingerprints in one
file are compared as a multiset by the gate.
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

BE_SCRIPTS = ("scripts/sync_game_data.py", "scripts/generate_tree_data.py", "scripts/build_sprite_map.py")

UNK = r"""['"](?:Unknown|unknown|UNKNOWN)[^'"]*['"]"""
BE_PATTERNS = [
    ("get_default_unknown", re.compile(r"\.get\([^()\n]*?,\s*" + UNK + r"\s*\)")),
    ("get_default_0", re.compile(r"\.get\([^()\n]*?,\s*-?0(?:\.0)?\s*\)")),
    ("get_default_empty_str", re.compile(r"""\.get\([^()\n]*?,\s*(?:''|"")\s*\)""")),
    ("get_default_empty_list", re.compile(r"\.get\([^()\n]*?,\s*\[\]\s*\)")),
    ("get_default_empty_dict", re.compile(r"\.get\([^()\n]*?,\s*\{\}\s*\)")),
    ("get_default_none", re.compile(r"\.get\([^()\n]*?,\s*None\s*\)")),
    ("or_unknown", re.compile(r"\bor\s+" + UNK)),
    ("or_0", re.compile(r"\bor\s+-?0(?:\.0)?\b(?![.\d])")),
    ("or_empty_list", re.compile(r"\bor\s+\[\]")),
    ("or_empty_dict", re.compile(r"\bor\s+\{\}")),
    ("or_empty_str", re.compile(r"""\bor\s+(?:''|"")""")),
    ("next_iter", re.compile(r"next\(iter\(")),
    ("first_index_pick", re.compile(r"\[0\]")),
    ("name_lookup_get_none", re.compile(r"\.get\((?:\w*name\w*|mastery\w*|unique\w*|skill_\w+|class_\w+|cls)\)")),
    ("next_generator_first_match", re.compile(r"next\(\s*\(")),
    ("config_get_literal_default",
     re.compile(r"config\.get\(\s*['\"](?:DATA_VERSION|CURRENT_PATCH|CURRENT_SEASON)['\"]")),
    ("get_default_game_identity",
     re.compile(r"\.get\(\s*['\"]\w*(?:class|mastery|skill|boss)\w*['\"],\s*['\"][A-Za-z_]+['\"]\s*\)")),
    ("logger_debug", re.compile(r"\b(?:logger|log|_log|current_app\.logger)\.debug\(")),
]
EXC_RE = re.compile(r"^(\s*)except\b([^:]*):\s*(.*)$")

FE_PATTERNS = [
    ("nullish_unknown", re.compile(r"\?\?\s*[`'\"]Unknown")),
    ("or_unknown", re.compile(r"\|\|\s*[`'\"]Unknown")),
    ("nullish_0", re.compile(r"\?\?\s*-?0(?![.\d])\b")),
    ("or_0", re.compile(r"\|\|\s*-?0(?![.\d])\b")),
    ("nullish_empty_list", re.compile(r"\?\?\s*\[\]")),
    ("or_empty_list", re.compile(r"\|\|\s*\[\]")),
    ("nullish_empty_obj", re.compile(r"\?\?\s*\{\}")),
    ("or_empty_obj", re.compile(r"\|\|\s*\{\}")),
    ("nullish_empty_str", re.compile(r"""\?\?\s*(?:''|""|``)""")),
    ("or_empty_str", re.compile(r"""\|\|\s*(?:''|""|``)""")),
    ("optional_index_0", re.compile(r"\?\.\[0\]")),
    ("first_index_pick", re.compile(r"(?<!\?\.)\[0\]")),
    ("find_result", re.compile(r"\.find\(")),
    ("nullish_game_identity", re.compile(r"(?:\?\?|\|\|)\s*['\"](?:Sentinel|Mage|Primalist|Acolyte|Rogue)['\"]")),
]


@dataclass(frozen=True)
class Candidate:
    file: str
    line: int
    pattern: str
    snippet: str
    symbol: str

    @property
    def key(self) -> str:
        return fingerprint(self.file, self.pattern, self.snippet)


def normalise(snippet: str) -> str:
    return re.sub(r"\s+", " ", snippet.strip())


def fingerprint(file: str, pattern: str, snippet: str) -> str:
    raw = f"{file}\x00{pattern}\x00{normalise(snippet)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def backend_files(root: Path) -> list[str]:
    out = []
    for dp, _dn, fn in os.walk(root / "backend" / "app"):
        rel = os.path.relpath(dp, root).replace("\\", "/")
        if "/tests" in rel or rel.endswith("tests") or "migrations" in rel or "__pycache__" in rel:
            continue
        out.extend(f"{rel}/{f}" for f in fn if f.endswith(".py"))
    return sorted(out) + [s for s in BE_SCRIPTS if (root / s).exists()]


def frontend_files(root: Path) -> list[str]:
    out = []
    for dp, _dn, fn in os.walk(root / "frontend" / "src"):
        rel = os.path.relpath(dp, root).replace("\\", "/")
        if "__tests__" in rel or rel.split("/")[-1] == "test" or "/test/" in rel + "/":
            continue
        out.extend(f"{rel}/{f}" for f in fn
                   if re.search(r"\.(ts|tsx)$", f) and ".test." not in f and ".spec." not in f)
    return sorted(out)


_PY_DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)|^\s*class\s+(\w+)")
_TS_DEF = re.compile(r"(?:function\s+(\w+)|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\(|function)"
                     r"|^\s*(\w+)\s*\([^)]*\)\s*\{)")


def _symbol(lines: list[str], idx: int, py: bool) -> str:
    rx = _PY_DEF if py else _TS_DEF
    for j in range(idx, -1, -1):
        m = rx.search(lines[j])
        if m:
            return next(g for g in m.groups() if g)
    return "<module>"


def scan_backend_file(root: Path, path: str) -> list[Candidate]:
    lines = (root / path).read_text(encoding="utf-8", errors="replace").split("\n")
    out: list[Candidate] = []
    in_doc = False

    def add(i, pat):
        out.append(Candidate(path, i + 1, pat, lines[i].strip()[:120], _symbol(lines, i, True)))

    for i, line in enumerate(lines):
        s = line.strip()
        if s.count('"""') == 1 or s.count("'''") == 1:
            in_doc = not in_doc
            continue
        if in_doc or s.startswith("#"):
            continue
        code = line.split("  #")[0]
        for name, rx in BE_PATTERNS:
            if rx.search(code):
                add(i, name)
        m = EXC_RE.match(line)
        if not m:
            continue
        indent = len(m.group(1))
        body = [m.group(3).strip()] if m.group(3).strip() else []
        j = i + 1
        while j < len(lines) and len(body) < 8:
            nxt = lines[j]
            if nxt.strip() == "":
                j += 1
                continue
            if len(nxt) - len(nxt.lstrip()) <= indent:
                break
            body.append(nxt.strip())
            j += 1
        btxt = " | ".join(body)
        if re.search(r"^raise\b|\| raise\b", btxt) and not re.search(r"\breturn\b", btxt):
            continue
        first = body[0] if body else ""
        if first == "pass" or (len(body) == 1 and body[0] == "pass"):
            kind = "except_pass"
        elif first == "continue":
            kind = "except_continue"
        elif re.search(r"\bcontinue\b", btxt):
            kind = "except_log_continue"
        elif re.search(r"\breturn\s+(\[\]|\{\}|None|0|0\.0|''|\"\"|False|set\(\)|\(\))\s*($|\|)", btxt) \
                or re.search(r"return\s*$", btxt):
            kind = "except_return_empty"
        elif re.search(r"return .*ok\(|jsonify\(", btxt) and re.search(r"\[\]|\{\}", btxt):
            kind = "except_return_200_empty"
        elif re.search(r"=\s*(\[\]|\{\}|None|0|''|\"\")\s*($|\|)", btxt):
            kind = "except_assign_empty"
        elif re.search(r"\breturn\b", btxt):
            kind = "except_return_value"
        elif re.search(r"\bpass\b", btxt):
            kind = "except_log_pass"
        else:
            kind = "except_other"
        add(i, ("bare_" if m.group(2).strip() == "" else "") + kind)
    return out


def scan_frontend_file(root: Path, path: str) -> list[Candidate]:
    lines = (root / path).read_text(encoding="utf-8", errors="replace").split("\n")
    out: list[Candidate] = []
    in_block = False

    def add(i, pat):
        out.append(Candidate(path, i + 1, pat, lines[i].strip()[:120], _symbol(lines, i, False)))

    for i, line in enumerate(lines):
        s = line.strip()
        if in_block:
            if "*/" in s:
                in_block = False
            continue
        if s.startswith("/*") and "*/" not in s:
            in_block = True
            continue
        if s.startswith(("//", "*")):
            continue
        code = re.sub(r"\s//\s.*$", "", line)
        for name, rx in FE_PATTERNS:
            if rx.search(code):
                add(i, name)
        m = re.search(r"catch\s*(\([^)]*\))?\s*\{\s*(.*)$", code)
        if m:
            body = [m.group(2)]
            j = i + 1
            tail = code[m.start():]
            depth = tail.count("{") - tail.count("}")
            while j < len(lines) and depth > 0 and len(body) < 8:
                body.append(lines[j].strip())
                depth += lines[j].count("{") - lines[j].count("}")
                j += 1
            if re.search(r"\bthrow\b", " | ".join(b for b in body if b)):
                continue
            add(i, "catch_fallback")
    return out


def scan(root: Path) -> list[Candidate]:
    out: list[Candidate] = []
    for f in backend_files(root):
        out.extend(scan_backend_file(root, f))
    for f in frontend_files(root):
        out.extend(scan_frontend_file(root, f))
    return out
