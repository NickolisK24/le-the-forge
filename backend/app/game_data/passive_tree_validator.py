"""
Passive tree allocation validator (CSV task 0E-3).

Given a passive tree (a list of node dicts with ``id``, ``max_points``, and
``requires`` populated by the 0E-2 merge script) and a proposed allocation
(``{node_id: points}``), return a list of human-readable errors. An empty
list means the allocation is valid.

The validator enforces five rules, in order:

  1. Every allocated id exists in the node set.
  2. Every allocated point count is in ``[1, max_points]``.
  3. For every allocated node, every parent declared in ``requires`` is also
     allocated **and** its allocated points are ``>= points_required``.
  4. Every allocated node is reachable from an entry node (a node with no
     ``requires`` entries) via a BFS traversal that only walks through other
     allocated nodes whose thresholds are satisfied — no isolated islands.
  5. The total points allocated does not exceed ``max_total_points`` (if
     supplied). This is a class-agnostic budget check; the CSV gate for the
     live 106-point Last Epoch cap lives upstream of the validator.

The validator never mutates its inputs.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable


def validate_allocation(
    nodes: Iterable[dict],
    allocations: dict[str, int],
    *,
    max_total_points: int | None = None,
) -> list[str]:
    """Return a list of error strings. Empty list means the allocation is valid."""
    errors: list[str] = []

    nodes_by_id = {n["id"]: n for n in nodes}

    # ---- Rule 1: unknown ids --------------------------------------------
    unknown = sorted(nid for nid in allocations if nid not in nodes_by_id)
    for nid in unknown:
        errors.append(f"unknown node id: {nid!r}")

    # ---- Rule 2: point range --------------------------------------------
    for nid, pts in allocations.items():
        if nid not in nodes_by_id:
            continue
        max_pts = nodes_by_id[nid].get("max_points", 0)
        if not isinstance(pts, int) or pts < 1:
            errors.append(f"{nid}: allocated points must be a positive integer, got {pts!r}")
        elif pts > max_pts:
            errors.append(f"{nid}: allocated {pts} exceeds max_points {max_pts}")

    # If rules 1-2 failed, downstream rules will produce noisy follow-up
    # errors. Keep going so the caller sees the full picture.

    # ---- Rule 3: parent thresholds --------------------------------------
    for nid, pts in allocations.items():
        node = nodes_by_id.get(nid)
        if node is None:
            continue
        for req in node.get("requires", []) or []:
            parent_id = req["parent_id"]
            needed = req["points"]
            parent_pts = allocations.get(parent_id, 0)
            if parent_pts < needed:
                errors.append(
                    f"{nid}: requires parent {parent_id} to have >= {needed} points "
                    f"(has {parent_pts})"
                )

    # ---- Rule 4: BFS reachability from entry nodes ----------------------
    entry_ids = {
        nid for nid, n in nodes_by_id.items()
        if not (n.get("requires") or [])
    }
    # The BFS frontier starts from allocated entry nodes.
    allocated_set = {nid for nid in allocations if nid in nodes_by_id}
    reachable: set[str] = set()
    queue: deque[str] = deque(sorted(allocated_set & entry_ids))
    reachable.update(queue)

    # Pre-build a child lookup: parent -> set of children that list it in requires.
    children_of: dict[str, list[str]] = {}
    for nid, n in nodes_by_id.items():
        for req in n.get("requires", []) or []:
            children_of.setdefault(req["parent_id"], []).append(nid)

    while queue:
        current = queue.popleft()
        for child in children_of.get(current, []):
            if child in reachable or child not in allocated_set:
                continue
            reqs = nodes_by_id[child].get("requires") or []
            if all(
                allocations.get(r["parent_id"], 0) >= r["points"]
                and r["parent_id"] in reachable
                for r in reqs
            ):
                reachable.add(child)
                queue.append(child)

    orphans = sorted(allocated_set - reachable)
    for nid in orphans:
        errors.append(
            f"{nid}: not reachable from any entry node through the allocated subtree"
        )

    # ---- Rule 5: total point budget -------------------------------------
    if max_total_points is not None:
        total = sum(p for p in allocations.values() if isinstance(p, int) and p > 0)
        if total > max_total_points:
            errors.append(
                f"total allocated points {total} exceeds budget {max_total_points}"
            )

    return errors
