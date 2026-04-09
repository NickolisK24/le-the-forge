"""
Skills Blueprint — /api/skills

GET  /api/skills/{skill_id}/tree                              → Full skill tree node graph
GET  /api/builds/{slug}/skills                                → Allocation state for all skills
PATCH /api/builds/{slug}/skills/{skill_id}/nodes/{node_id}   → Allocate/deallocate a node
"""

import json
import os
from collections import Counter

from flask import Blueprint, request
from marshmallow import ValidationError

from app import db, limiter
from app.models import Build, BuildSkill
from app.schemas.skill_tree import (
    NodeAllocateRequestSchema,
)
from app.services import build_service
from app.skills.skill_classifier import classify_skills, detect_primary_skill
from app.utils.responses import ok, error, not_found, validation_error
from app.utils.cache import get as cache_get, set as cache_set, delete_pattern

skills_bp = Blueprint("skills", __name__)

_node_allocate_schema = NodeAllocateRequestSchema()

_TREE_CACHE_TTL = 86400  # 24 hours — tree data only changes on patch
_TREE_CACHE_KEY = "forge:skill_tree"

# ---------------------------------------------------------------------------
# Skill tree data loader — reads community_skill_trees.json once, cached
# ---------------------------------------------------------------------------

_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
)
_COMMUNITY_TREES_PATH = os.path.join(_DATA_DIR, "classes", "community_skill_trees.json")

_tree_cache: dict | None = None


def _load_trees() -> dict:
    """Load and index all skill trees by ID. Cached in-memory after first load."""
    global _tree_cache
    if _tree_cache is not None:
        return _tree_cache

    with open(_COMMUNITY_TREES_PATH, "r") as f:
        raw = json.load(f)

    index = {}
    for entry in raw:
        tree_id = entry.get("id")
        if tree_id:
            index[tree_id] = entry
    _tree_cache = index
    return _tree_cache


def _get_tree(skill_id: str) -> dict | None:
    """Look up a single skill tree by ID."""
    trees = _load_trees()
    return trees.get(skill_id)


# ---------------------------------------------------------------------------
# BFS reachability check
# ---------------------------------------------------------------------------

def _is_reachable_from_root(
    node_id: int,
    nodes: list[dict],
    allocated: dict[int, int],
) -> bool:
    """
    Check if node_id is reachable from the root via allocated prerequisite chains.
    A node is reachable if ALL its requirements are met.
    The root node (id=0, maxPoints=0) is always reachable.
    """
    node_map = {n["id"]: n for n in nodes}
    target = node_map.get(node_id)
    if not target:
        return False

    # Root node is always reachable
    if target.get("maxPoints", 1) == 0 and not target.get("requirements"):
        return True

    # Memoize results to avoid exponential blowup, but allow shared nodes
    memo: dict[int, bool] = {}

    def _check(nid: int, path: frozenset[int]) -> bool:
        if nid in path:
            return False  # cycle guard
        if nid in memo:
            return memo[nid]

        node = node_map.get(nid)
        if not node:
            memo[nid] = False
            return False

        # Root node (maxPoints=0, no requirements) is always reachable
        reqs = node.get("requirements", [])
        if not reqs:
            result = node.get("maxPoints", 1) == 0 or allocated.get(nid, 0) >= 1
            memo[nid] = result
            return result

        # All requirements must be met
        new_path = path | {nid}
        for req in reqs:
            req_node_id = req.get("node", req.get("nodeId"))
            req_points = req.get("requirement", 0)
            if req_node_id is None:
                continue
            pts = allocated.get(req_node_id, 0)
            # Root nodes (maxPoints=0) always count as allocated
            req_node = node_map.get(req_node_id, {})
            if req_node.get("maxPoints", 1) == 0:
                pts = 1
            if pts < max(req_points, 1):
                memo[nid] = False
                return False
            # Requirement node must itself be reachable
            if not _check(req_node_id, new_path):
                memo[nid] = False
                return False

        memo[nid] = True
        return True

    return _check(node_id, frozenset())


def _would_orphan_children(
    node_id: int,
    new_points: int,
    nodes: list[dict],
    allocated: dict[int, int],
) -> bool:
    """
    Check if reducing node_id to new_points would orphan any allocated children.
    """
    for node in nodes:
        reqs = node.get("requirements", [])
        for req in reqs:
            req_node_id = req.get("node", req.get("nodeId"))
            req_points = req.get("requirement", 0)
            if req_node_id == node_id and allocated.get(node["id"], 0) > 0:
                if new_points < max(req_points, 1):
                    return True
    return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _spec_tree_to_alloc_map(spec_tree: list) -> dict[int, int]:
    """Convert flat node-id list (with repeats) to {node_id: points} map."""
    return dict(Counter(spec_tree))


def _alloc_map_to_spec_tree(alloc: dict[int, int]) -> list[int]:
    """Convert {node_id: points} map back to flat list with repeats."""
    result = []
    for node_id, pts in sorted(alloc.items()):
        result.extend([node_id] * pts)
    return result


# ---------------------------------------------------------------------------
# GET /api/skills/{skill_id}/tree
# ---------------------------------------------------------------------------

@skills_bp.get("/skills/<skill_id>/tree")
@limiter.limit("30 per minute")
def get_skill_tree(skill_id: str):
    """Return the full node graph for a skill tree."""
    # Check Redis cache
    cache_key = f"{_TREE_CACHE_KEY}:{skill_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    tree = _get_tree(skill_id)
    if not tree:
        return not_found("Skill tree")

    nodes = tree.get("nodes", [])
    root_id = 0
    for node in nodes:
        if node.get("maxPoints", 1) == 0 and not node.get("requirements"):
            root_id = node["id"]
            break

    result = {
        "skill_id": skill_id,
        "skill_name": tree.get("ability", nodes[0].get("name", skill_id) if nodes else skill_id),
        "nodes": nodes,
        "root_node_id": root_id,
    }

    cache_set(cache_key, result, _TREE_CACHE_TTL)
    return ok(data=result)


# ---------------------------------------------------------------------------
# GET /api/builds/{slug}/skills
# ---------------------------------------------------------------------------

@skills_bp.get("/builds/<slug>/skills")
@limiter.limit("20 per minute")
def get_build_skills(slug: str):
    """Return allocation state for all skills on a build, with classifications and primary detection."""
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    skills_data = []
    for skill in sorted(build.skills, key=lambda s: s.slot):
        alloc_map = _spec_tree_to_alloc_map(skill.spec_tree or [])
        str_map = {str(k): v for k, v in alloc_map.items()}
        total = sum(alloc_map.values())
        skills_data.append({
            "skill_id": _skill_name_to_id(skill.skill_name),
            "skill_name": skill.skill_name,
            "slot": skill.slot,
            "allocated_nodes": str_map,
            "total_points": total,
            "classification": classify_skills([skill.skill_name]).get(skill.skill_name, "damage"),
        })

    # Auto-detect primary skill
    detect_input = [
        {"skill_name": s["skill_name"], "slot": s["slot"], "allocated_nodes": s["total_points"]}
        for s in skills_data
    ]
    primary = detect_primary_skill(detect_input)
    classifications = {s["skill_name"]: s["classification"] for s in skills_data}

    return ok(data={
        "skills": skills_data,
        "primary_skill": primary,
        "skill_classifications": classifications,
    })


def _skill_name_to_id(skill_name: str) -> str:
    """
    Convert a skill name to its tree ID using the same mapping as the frontend.
    Also handles the case where skill_name is already a tree code (from imports).
    Falls back to a slugified version if not found.
    """
    trees = _load_trees()
    name_lower = skill_name.lower().strip()
    # Direct tree code match (imported builds may store codes as names)
    if name_lower in trees:
        return name_lower
    for tree_id, tree in trees.items():
        if tree.get("ability", "").lower().strip() == name_lower:
            return tree_id
        # Also check root node name
        nodes = tree.get("nodes", [])
        if nodes and nodes[0].get("name", "").lower().strip() == name_lower:
            return tree_id
    # Fallback
    return skill_name.lower().replace(" ", "_")


# ---------------------------------------------------------------------------
# PATCH /api/builds/{slug}/skills/{skill_id}/nodes/{node_id}
# ---------------------------------------------------------------------------

@skills_bp.patch("/builds/<slug>/skills/<skill_id>/nodes/<int:node_id>")
@limiter.limit("30 per minute")
def allocate_skill_node(slug: str, skill_id: str, node_id: int):
    """Allocate or deallocate points on a single skill tree node."""
    try:
        data = _node_allocate_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    new_points = data["points"]

    # Load build
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    # Load tree data
    tree = _get_tree(skill_id)
    if not tree:
        return not_found("Skill tree")

    nodes = tree.get("nodes", [])
    node_map = {n["id"]: n for n in nodes}
    target_node = node_map.get(node_id)
    if not target_node:
        return error(f"Node {node_id} not found in skill tree '{skill_id}'", status=404)

    # Validate points within 0 – max_points
    max_pts = target_node.get("maxPoints", 1)
    if max_pts == 0:
        return error("Cannot allocate points on the root node")
    if new_points < 0 or new_points > max_pts:
        return error(f"Points must be between 0 and {max_pts}")

    # Find the BuildSkill for this skill
    skill_name = tree.get("ability", nodes[0].get("name", ""))
    build_skill = None
    for s in build.skills:
        sid = _skill_name_to_id(s.skill_name)
        if sid == skill_id or s.skill_name.lower() == skill_name.lower():
            build_skill = s
            break

    if not build_skill:
        return error(f"Skill '{skill_name}' is not on this build", status=404)

    # Build current allocation map
    alloc = _spec_tree_to_alloc_map(build_skill.spec_tree or [])

    # Calculate what the new allocation would be
    old_points = alloc.get(node_id, 0)
    test_alloc = {**alloc}

    if new_points > old_points:
        # Allocating more points — check reachability and budget
        test_alloc[node_id] = new_points
        if not _is_reachable_from_root(node_id, nodes, test_alloc):
            return error("Node is not reachable — prerequisite nodes must be allocated first")

        total = sum(v for k, v in test_alloc.items() if node_map.get(k, {}).get("maxPoints", 1) > 0)
        # Base cap is 20; gear affixes like "+X to Skill" can raise it
        max_budget = max(20, sum(v for k, v in alloc.items() if node_map.get(k, {}).get("maxPoints", 1) > 0))
        if total > max_budget:
            return error("Cannot exceed 20 skill points")

    elif new_points < old_points:
        # Deallocating — check that no children would be orphaned
        if _would_orphan_children(node_id, new_points, nodes, alloc):
            return error("Cannot deallocate — other allocated nodes depend on this one")
        test_alloc[node_id] = new_points

    else:
        # No change
        pass

    # Clean up zero entries
    test_alloc = {k: v for k, v in test_alloc.items() if v > 0}

    # Persist
    build_skill.spec_tree = _alloc_map_to_spec_tree(test_alloc)
    build_skill.points_allocated = sum(test_alloc.values())
    db.session.commit()

    # Invalidate optimization cache
    delete_pattern(f"forge:optimize:{slug}:*")

    # Return updated allocation
    str_map = {str(k): v for k, v in test_alloc.items()}
    return ok(data={
        "skill_id": skill_id,
        "skill_name": build_skill.skill_name,
        "slot": build_skill.slot,
        "allocated_nodes": str_map,
        "total_points": sum(test_alloc.values()),
    })
