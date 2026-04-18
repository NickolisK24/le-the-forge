"""
Merge scraped passive-tree edges into ``data/classes/passives.json``.

Input: a directory containing one JSON file per class, each in the shape
emitted by the LET-browser scraper:

    {
      "class": "primalist",        # lowercased class name
      "node_count": 111,
      "edge_count": 40,
      "edges": [
        {"parent": "pr_0", "child": "pr_5", "points_required": 1},
        ...
      ]
    }

For every class present in the input directory the merge rebuilds that
class's ``connections`` field from scratch and populates a new ``requires``
field that carries the directed parent threshold relationship used by the
BFS allocation validator (0E-3):

    connections: [child_id, ...]                    # symmetric, renderer-friendly
    requires:    [{"parent_id": id, "points": int}] # directed, one per parent

Classes not present in the input directory are left untouched, so the
merge can be staged per-class as each scrape lands.

Usage:
    python backend/scripts/merge_passive_edges.py \\
        --input /tmp/passive_edges \\
        --passives data/classes/passives.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CLASS_PREFIX = {
    "acolyte":   "ac_",
    "mage":      "mg_",
    "primalist": "pr_",
    "rogue":     "rg_",
    "sentinel":  "sn_",
}


def _load_edge_files(input_dir: Path) -> dict[str, dict]:
    """Return {class_name_lower: payload_dict} for every *.json in input_dir."""
    payloads: dict[str, dict] = {}
    for path in sorted(input_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        cls = (raw.get("class") or "").lower()
        if cls not in CLASS_PREFIX:
            raise SystemExit(
                f"{path.name}: class field {raw.get('class')!r} is not one of "
                f"{sorted(CLASS_PREFIX)}"
            )
        if cls in payloads:
            raise SystemExit(f"duplicate payload for class {cls!r}")
        if not isinstance(raw.get("edges"), list):
            raise SystemExit(f"{path.name}: 'edges' must be a list")
        payloads[cls] = raw
    return payloads


def _validate_edges(class_name: str, payload: dict, class_ids: set[str]) -> None:
    """Raise if any edge endpoint is missing from the class's node set."""
    declared_edges = payload.get("edge_count")
    edges = payload["edges"]
    if declared_edges is not None and declared_edges != len(edges):
        raise SystemExit(
            f"{class_name}: edge_count={declared_edges} but edges list has "
            f"{len(edges)} entries"
        )
    prefix = CLASS_PREFIX[class_name]
    for i, edge in enumerate(edges):
        parent, child = edge.get("parent"), edge.get("child")
        req = edge.get("points_required")
        if not (isinstance(parent, str) and isinstance(child, str)):
            raise SystemExit(
                f"{class_name} edge #{i}: parent/child must be strings"
            )
        if not (isinstance(req, int) and req >= 1):
            raise SystemExit(
                f"{class_name} edge #{i}: points_required must be a positive int"
            )
        if parent == child:
            raise SystemExit(
                f"{class_name} edge #{i}: self-loop {parent!r}->{child!r}"
            )
        for role, nid in (("parent", parent), ("child", child)):
            if not nid.startswith(prefix):
                raise SystemExit(
                    f"{class_name} edge #{i}: {role} {nid!r} does not start "
                    f"with expected prefix {prefix!r}"
                )
            if nid not in class_ids:
                raise SystemExit(
                    f"{class_name} edge #{i}: {role} {nid!r} not found in "
                    f"passives.json for that class"
                )


def _apply_edges(
    class_name: str,
    payload: dict,
    nodes_by_id: dict[str, dict],
) -> tuple[int, int]:
    """
    Rebuild connections[] and populate requires[] for every node in the class.

    Returns (touched_nodes, dropped_junk_endpoints) for the summary.
    """
    prefix = CLASS_PREFIX[class_name]
    class_ids = {nid for nid in nodes_by_id if nid.startswith(prefix)}

    # Reset: strip every existing entry for the class so junk pseudo-edges
    # and garbage pointer-hash ids don't survive the merge.
    dropped = 0
    for nid in class_ids:
        node = nodes_by_id[nid]
        before = len(node.get("connections", []))
        node["connections"] = []
        node["requires"] = []
        dropped += before

    # Rebuild.
    for edge in payload["edges"]:
        parent, child, req = edge["parent"], edge["child"], edge["points_required"]
        parent_node = nodes_by_id[parent]
        child_node = nodes_by_id[child]
        if child not in parent_node["connections"]:
            parent_node["connections"].append(child)
        if parent not in child_node["connections"]:
            child_node["connections"].append(parent)
        child_node["requires"].append({"parent_id": parent, "points": req})

    # Stable ordering: connections sorted by raw_node_id for deterministic diffs.
    for nid in class_ids:
        node = nodes_by_id[nid]
        node["connections"].sort(
            key=lambda cid: nodes_by_id[cid].get("raw_node_id", 0)
        )
        node["requires"].sort(
            key=lambda r: nodes_by_id[r["parent_id"]].get("raw_node_id", 0)
        )

    return len(class_ids), dropped


def merge(input_dir: Path, passives_path: Path, *, dry_run: bool = False) -> None:
    payloads = _load_edge_files(input_dir)
    if not payloads:
        print(f"no edge files found in {input_dir}", file=sys.stderr)
        return

    nodes = json.loads(passives_path.read_text(encoding="utf-8"))
    if not isinstance(nodes, list):
        raise SystemExit(f"{passives_path}: expected a list of nodes")

    nodes_by_id = {n["id"]: n for n in nodes}

    summary: list[str] = []
    for class_name, payload in payloads.items():
        prefix = CLASS_PREFIX[class_name]
        class_ids = {nid for nid in nodes_by_id if nid.startswith(prefix)}
        if not class_ids:
            raise SystemExit(
                f"{class_name}: no nodes with prefix {prefix!r} in passives.json"
            )
        declared = payload.get("node_count")
        if declared is not None and declared != len(class_ids):
            print(
                f"warn: {class_name} node_count={declared} but passives.json "
                f"has {len(class_ids)} nodes with prefix {prefix!r}",
                file=sys.stderr,
            )
        _validate_edges(class_name, payload, class_ids)
        touched, dropped = _apply_edges(class_name, payload, nodes_by_id)
        summary.append(
            f"  {class_name:10s}  nodes={touched:3d}  "
            f"edges={len(payload['edges']):3d}  "
            f"old_endpoints_cleared={dropped}"
        )

    print("merge summary:")
    for line in summary:
        print(line)

    if dry_run:
        print("dry-run: not writing file")
        return

    passives_path.write_text(
        json.dumps(nodes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {passives_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", required=True, type=Path,
        help="Directory containing per-class edge JSON files",
    )
    parser.add_argument(
        "--passives", required=True, type=Path,
        help="Path to data/classes/passives.json",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate and report but do not write passives.json",
    )
    args = parser.parse_args(argv)
    merge(args.input, args.passives, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
