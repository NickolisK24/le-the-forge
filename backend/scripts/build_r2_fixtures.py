"""Build the R2 canonical contract fixtures from an R1 checkout (AUDIT-R2 P17).

Slices real R1 canonical outputs (last-epoch-data) into a small tree that has
the same layout as an R1 checkout:

    exports_canonical/{affixes,passive_trees,skill_trees,weaver_tree,property_definitions}.json
    exports_canonical/TRUST_MANIFEST.json        (canonical family entries only)
    docs/generated/r1_certification_report.json (unchanged)
    snapshots/runs/1.4.6_22986002.retroactive.json (unchanged; proves 1.4.6 is rejected)
    FIXTURE_PROVENANCE.json

Slicing keeps whole records only (never trims fields) and is deterministic.
The 1.4.6 data has no raw snapshot, so it can never form a valid bundle by
itself; tests add a clearly labelled synthetic snapshot/run manifest at test
time. ``FIXTURE_PROVENANCE.json`` records the source commit, the original file
hashes, the slice rules, and R1's own content hash of every sliced file (a
cross-implementation check of ``app.canonical_data.hashing``).

Usage:
    python backend/scripts/build_r2_fixtures.py --r1-root ../last-epoch-data
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "canonical" / "r1_1.4.6_slice"

AFFIX_SINGLE = 25
AFFIX_MULTI = 25
AFFIX_EXTRA_IDS = (14,)                      # second property with its own rolls (REL-7)
PASSIVE_TREES = ("AcolyteTree", "MageTree")  # DEFECTIVE (missing nodes) + mastery-bearing trees
SKILL_TREES = ("wo42", "bl5st", "er6no", "flur3", "fb8fe", "an0my", "fi9", "rf1azz")
PD_PER_FAMILY = 25


def _dump(path: Path, doc) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(r1: Path, out: Path) -> dict:
    sys.path.insert(0, str(r1 / "tools" / "scripts"))
    import r1_snapshot  # the R1 implementation, for the cross-check hashes
    if out.exists():
        shutil.rmtree(out)
    prov = {"source_repository": "last-epoch-data",
            "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=r1, capture_output=True,
                                            text=True, check=True).stdout.strip(),
            "notice": "Real 1.4.6 canonical records, sliced (whole records only). 1.4.6 has no raw snapshot: "
                      "these files never form a valid bundle without the synthetic snapshot tests add.",
            "originals": {}, "slices": {}, "r1_content_sha256": {}}

    def orig(rel):
        prov["originals"][rel] = _sha(r1 / rel)
        return json.loads((r1 / rel).read_text(encoding="utf-8"))

    a = orig("exports_canonical/affixes.json")
    singles = [x for x in a["affixes"] if x["structure"] == "SINGLE_PROPERTY"][:AFFIX_SINGLE]
    multis = [x for x in a["affixes"] if x["structure"] != "SINGLE_PROPERTY"][:AFFIX_MULTI]
    extra = [x for x in a["affixes"] if x["affix_id"] in AFFIX_EXTRA_IDS]
    keep = {x["affix_id"]: x for x in singles + multis + extra}
    a["affixes"] = [keep[k] for k in sorted(keep)]
    prov["slices"]["affixes"] = f"first {AFFIX_SINGLE} single-property, first {AFFIX_MULTI} multi-property, " \
                                f"plus affix ids {list(AFFIX_EXTRA_IDS)}"
    _dump(out / "exports_canonical/affixes.json", a)

    p = orig("exports_canonical/passive_trees.json")
    p["trees"] = [t for t in p["trees"] if t["tree_class"] in PASSIVE_TREES]
    prov["slices"]["passive_trees"] = f"trees {list(PASSIVE_TREES)}"
    _dump(out / "exports_canonical/passive_trees.json", p)

    s = orig("exports_canonical/skill_trees.json")
    s["trees"] = [t for t in s["trees"] if t["tree_id"] in SKILL_TREES]
    prov["slices"]["skill_trees"] = f"trees {list(SKILL_TREES)} (multi-prerequisite, NULL/UNRESOLVED edges, " \
                                    f"name-collision and wrong-metadata cases)"
    _dump(out / "exports_canonical/skill_trees.json", s)

    w = orig("exports_canonical/weaver_tree.json")
    prov["slices"]["weaver_tree"] = "unsliced"
    _dump(out / "exports_canonical/weaver_tree.json", w)

    d = orig("exports_canonical/property_definitions.json")
    for k, v in d["families"].items():
        if isinstance(v, list):
            d["families"][k] = v[:PD_PER_FAMILY]
    prov["slices"]["property_definitions"] = f"first {PD_PER_FAMILY} records of each family"
    _dump(out / "exports_canonical/property_definitions.json", d)

    t = orig("exports_canonical/TRUST_MANIFEST.json")
    t["families"] = [f for f in t["families"] if f.get("kind") == "canonical"]
    t.pop("domains_without_export", None)
    prov["slices"]["TRUST_MANIFEST"] = "canonical family entries only; domains_without_export removed"
    _dump(out / "exports_canonical/TRUST_MANIFEST.json", t)

    for rel in ("docs/generated/r1_certification_report.json", "snapshots/runs/1.4.6_22986002.retroactive.json"):
        prov["originals"][rel] = _sha(r1 / rel)
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(r1 / rel, out / rel)
        prov["slices"][Path(rel).stem] = "unchanged copy"

    for f in sorted((out / "exports_canonical").glob("*.json")):
        prov["r1_content_sha256"][f"exports_canonical/{f.name}"] = r1_snapshot.json_content_hash(f)
    _dump(out / "FIXTURE_PROVENANCE.json", prov)
    return prov


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--r1-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    prov = build(args.r1_root.resolve(), args.out)
    print(f"fixtures from last-epoch-data {prov['source_commit'][:10]} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
