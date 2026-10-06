"""Dangerous-fallback ratchet gate (AUDIT-R2 P16).

    python scripts/fallback_gate/gate.py check          # CI: fail on new or stale entries, or a count increase
    python scripts/fallback_gate/gate.py report         # counts as JSON
    python scripts/fallback_gate/gate.py tighten        # lower baseline.json after debt was paid
    python scripts/fallback_gate/gate.py cutover-check  # R2-P20 precondition: zero OPEN R2-owned entries

Every scanner candidate must be classified, either by an entry in
``registry.jsonl`` (matched on content fingerprint, so moving lines is free)
or by an inline annotation on the line or the line above:

    # fallback: SAFE_PRESENTATION — <reason>         (TS: // fallback: ...)
    # fallback: EXPLICIT_UNSUPPORTED — <reason>
    # fallback: NOT_A_FALLBACK — <reason>

A dangerous fallback cannot be annotated away; it needs a registry entry with
an owner package. Dangerous entries carry a status:

    OPEN                                still in the code, counted against the baseline
    REMOVED                             code is gone
    REPLACED_WITH_EXPLICIT_UNSUPPORTED  code is gone, replaced by an explicit state/error
    PROVEN_SAFE                         still in the code, with a ``proof``

The OPEN count per owner may never exceed ``baseline.json``; when it drops,
``check`` fails until the baseline is tightened, so paid debt cannot return.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scanner import Candidate, normalise, scan  # noqa: E402

ROOT = HERE.parents[1]
REGISTRY = HERE / "registry.jsonl"
BASELINE = HERE / "baseline.json"

DANGEROUS = "DANGEROUS_SILENT_FALLBACK"
CLASSES = {DANGEROUS, "SAFE_PRESENTATION_FALLBACK", "EXPLICIT_UNSUPPORTED_STATE", "NOT_A_FALLBACK"}
STATUSES = {"OPEN", "REMOVED", "REPLACED_WITH_EXPLICIT_UNSUPPORTED", "PROVEN_SAFE"}
GONE = {"REMOVED", "REPLACED_WITH_EXPLICIT_UNSUPPORTED"}
ANNOTATION = re.compile(r"fallback:\s*(SAFE_PRESENTATION|EXPLICIT_UNSUPPORTED|NOT_A_FALLBACK)\s*(?:—|--|-|:)\s*\S")


def is_r2_owned(owner: str | None) -> bool:
    return bool(owner) and "R2-P" in owner


def load_registry(path: Path = REGISTRY) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate_registry(entries: list[dict]) -> list[str]:
    errs = []
    for i, e in enumerate(entries):
        where = f"registry line {i + 1} ({e.get('file')}:{e.get('line')})"
        if e.get("classification") not in CLASSES:
            errs.append(f"{where}: unknown classification {e.get('classification')!r}")
        if not e.get("reason"):
            errs.append(f"{where}: no reason")
        if not e.get("fp") and not e.get("manual"):
            errs.append(f"{where}: no fingerprint")
        if e.get("classification") == DANGEROUS:
            for k in ("owner", "replacement", "family", "symbol" if not e.get("manual") else "file"):
                if not e.get(k):
                    errs.append(f"{where}: dangerous entry without {k}")
            if e.get("status") not in STATUSES:
                errs.append(f"{where}: dangerous entry status {e.get('status')!r} not in {sorted(STATUSES)}")
            if e.get("status") == "PROVEN_SAFE" and not e.get("proof"):
                errs.append(f"{where}: PROVEN_SAFE needs a proof")
        elif "status" in e:
            errs.append(f"{where}: only dangerous entries carry a status")
    return errs


def annotated(root: Path, c: Candidate, cache: dict) -> bool:
    lines = cache.get(c.file)
    if lines is None:
        lines = cache[c.file] = (root / c.file).read_text(encoding="utf-8", errors="replace").split("\n")
    here = lines[c.line - 1]
    above = lines[c.line - 2] if c.line >= 2 else ""
    return bool(ANNOTATION.search(here) or (above.strip().startswith(("#", "//")) and ANNOTATION.search(above)))


def manual_present(root: Path, e: dict, cache: dict) -> int:
    """Occurrences of a manual (non-scanner) entry's source line in its file."""
    p = root / e["file"]
    if not p.is_file():
        return 0
    lines = cache.get(e["file"])
    if lines is None:
        lines = cache[e["file"]] = p.read_text(encoding="utf-8", errors="replace").split("\n")
    target = normalise(e["snippet"])
    return sum(1 for ln in lines if normalise(ln.strip()[:120]) == target)


def evaluate(root: Path = ROOT, entries: list[dict] | None = None) -> dict:
    entries = load_registry() if entries is None else entries
    cache: dict = {}
    found = collections.Counter()
    sample: dict[str, Candidate] = {}
    annotated_n = 0
    for c in scan(root):
        if annotated(root, c, cache):
            annotated_n += 1
            continue
        found[c.key] += 1
        sample.setdefault(c.key, c)

    by_fp: dict[str, list[dict]] = collections.defaultdict(list)
    for e in entries:
        if e.get("fp"):
            by_fp[e["fp"]].append(e)

    unclassified, stale_dangerous, stale_other, still_present = [], [], [], []
    for fp, n in found.items():
        live = [e for e in by_fp.get(fp, []) if e.get("status") not in GONE]
        if n > len(live):
            c = sample[fp]
            unclassified.append({"file": c.file, "line": c.line, "pattern": c.pattern, "symbol": c.symbol,
                                 "snippet": c.snippet, "fp": fp, "count": n - len(live)})
    for fp, group in by_fp.items():
        n = found.get(fp, 0)
        live = [e for e in group if e.get("status") not in GONE]
        gone = [e for e in group if e.get("status") in GONE]
        if n < len(live):
            # Conservative: a vanished occurrence in a mixed group is attributed to a dangerous entry first.
            danger = [e for e in live if e["classification"] == DANGEROUS]
            if danger:
                stale_dangerous.extend(danger[:len(live) - n])
            else:
                stale_other.extend(live[:len(live) - n])
        if gone and n > len(live):
            still_present.extend(gone[:n - len(live)])
    for e in entries:
        if not e.get("manual"):
            continue
        present = manual_present(root, e, cache) > 0
        if e.get("status") in GONE and present:
            still_present.append(e)
        elif e.get("status") not in GONE and not present:
            (stale_dangerous if e["classification"] == DANGEROUS else stale_other).append(e)

    open_by_owner = collections.Counter(e["owner"] for e in entries
                                        if e["classification"] == DANGEROUS and e.get("status") == "OPEN")
    return {
        "unclassified": unclassified, "stale_dangerous": stale_dangerous, "stale_other": stale_other,
        "marked_gone_but_present": still_present, "annotated": annotated_n,
        "open_by_owner": dict(sorted(open_by_owner.items())),
        "candidates": sum(found.values()) + annotated_n,
    }


def summary(entries: list[dict], result: dict) -> dict:
    d = [e for e in entries if e["classification"] == DANGEROUS]
    status = collections.Counter(e["status"] for e in d)
    open_ = [e for e in d if e["status"] == "OPEN"]
    return {
        "registry_entries": len(entries),
        "classification": dict(sorted(collections.Counter(e["classification"] for e in entries).items())),
        "dangerous_by_status": dict(sorted(status.items())),
        "dangerous_open_total": len(open_),
        "dangerous_open_runtime": sum(1 for e in open_ if e.get("tier") == "RUNTIME"),
        "dangerous_open_r2_owned": sum(1 for e in open_ if is_r2_owned(e["owner"])),
        "dangerous_open_by_owner": result["open_by_owner"],
        "scanner_candidates": result["candidates"],
        "inline_annotated": result["annotated"],
        "new_unclassified": sum(u["count"] for u in result["unclassified"]),
    }


def ratchet(open_by_owner: dict, baseline: dict) -> list[str]:
    errs = []
    base = baseline["dangerous_open_by_owner"]
    for owner, n in open_by_owner.items():
        if n > base.get(owner, 0):
            errs.append(f"OPEN dangerous fallbacks for {owner!r} rose from {base.get(owner, 0)} to {n}")
    for owner, b in base.items():
        if open_by_owner.get(owner, 0) < b:
            errs.append(f"OPEN dangerous fallbacks for {owner!r} fell from {b} to {open_by_owner.get(owner, 0)}: "
                        f"run `gate.py tighten` so the gain is locked in")
    return errs


def check(root: Path = ROOT, entries: list[dict] | None = None, baseline: dict | None = None) -> list[str]:
    entries = load_registry() if entries is None else entries
    baseline = json.loads(BASELINE.read_text()) if baseline is None else baseline
    errs = validate_registry(entries)
    r = evaluate(root, entries)
    for u in r["unclassified"]:
        errs.append(f"unclassified fallback candidate {u['file']}:{u['line']} [{u['pattern']}] in {u['symbol']}: "
                    f"{u['snippet']!r} — add a registry entry or an inline `fallback:` annotation")
    for e in r["stale_dangerous"]:
        errs.append(f"dangerous fallback {e.get('census_id') or e.get('fp')} ({e['file']}:{e['line']}) no longer "
                    f"matches the code: mark it REMOVED / REPLACED_WITH_EXPLICIT_UNSUPPORTED, or re-fingerprint it "
                    f"if the line was only edited")
    for e in r["marked_gone_but_present"]:
        errs.append(f"{e.get('census_id') or e.get('fp')} ({e['file']}:{e['line']}) is marked {e['status']} but "
                    f"is still in the code")
    errs.extend(ratchet(r["open_by_owner"], baseline))
    return errs


def tighten(entries: list[dict] | None = None) -> dict:
    entries = load_registry() if entries is None else entries
    baseline = json.loads(BASELINE.read_text())
    r = evaluate(ROOT, entries)
    rising = [x for x in ratchet(r["open_by_owner"], baseline) if "rose" in x]
    if rising:
        raise SystemExit("refusing to tighten while counts rose:\n" + "\n".join(rising))
    baseline["dangerous_open_by_owner"] = {k: v for k, v in r["open_by_owner"].items() if v}
    BASELINE.write_text(json.dumps(baseline, indent=1, sort_keys=True) + "\n")
    return baseline


def cutover_check(entries: list[dict] | None = None) -> list[str]:
    entries = load_registry() if entries is None else entries
    return [f"{e.get('census_id') or e['fp']} {e['file']}:{e['line']} owner={e['owner']}" for e in entries
            if e["classification"] == DANGEROUS and e.get("status") == "OPEN" and is_r2_owned(e["owner"])]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=["check", "report", "tighten", "cutover-check"])
    args = ap.parse_args(argv)
    entries = load_registry()
    if args.command == "report":
        print(json.dumps(summary(entries, evaluate(ROOT, entries)), indent=1))
        return 0
    if args.command == "tighten":
        print(json.dumps(tighten(entries), indent=1))
        return 0
    errs = check(ROOT, entries) if args.command == "check" else cutover_check(entries)
    for e in errs:
        print(e)
    label = "fallback gate" if args.command == "check" else "R2 cutover fallback gate"
    print(f"{label}: {'FAIL' if errs else 'PASS'} ({len(errs)} problem(s))")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
