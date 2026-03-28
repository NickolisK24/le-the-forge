"""
Import Blueprint — /api/import

POST /api/import/url   → Proxy-fetch a Last Epoch Tools build URL and return
                         a mapped build payload ready to be reviewed / saved.
"""

import json as json_lib
import re

import requests as _requests
from flask import Blueprint, current_app, jsonify, request

from app import limiter

import_bp = Blueprint("import", __name__)

# ---------------------------------------------------------------------------
# Last Epoch class / mastery ID maps
# These mirror the internal game enum values used by Last Epoch Tools.
# Verified against community tooling and game data exports.
# ---------------------------------------------------------------------------
_CLASS_MAP: dict[int, str] = {
    1: "Acolyte",
    2: "Primalist",
    3: "Mage",
    4: "Sentinel",
    5: "Rogue",
}

_MASTERY_MAP: dict[str, dict[int, str]] = {
    "Acolyte":   {1: "Necromancer", 2: "Lich",        3: "Warlock"},
    "Primalist": {1: "Beastmaster", 2: "Druid",        3: "Shaman"},
    "Mage":      {1: "Sorcerer",    2: "Runemaster",   3: "Spellblade"},
    "Sentinel":  {1: "Forge Guard", 2: "Paladin",      3: "Void Knight"},
    "Rogue":     {1: "Bladedancer", 2: "Marksman",     3: "Falconer"},
}

# ---------------------------------------------------------------------------
# Skill tree ID → display name (built lazily from skills_metadata.json)
# ---------------------------------------------------------------------------
_SKILL_ID_TO_NAME: dict[str, str] | None = None


def _get_skill_id_map() -> dict[str, str]:
    """Return {treeID: skill_name} built from data/skills_metadata.json."""
    global _SKILL_ID_TO_NAME
    if _SKILL_ID_TO_NAME is not None:
        return _SKILL_ID_TO_NAME

    try:
        import os
        data_path = os.path.join(
            os.path.dirname(current_app.root_path), "data", "skills_metadata.json"
        )
        with open(data_path) as f:
            skills_data: dict = json_lib.load(f)
        _SKILL_ID_TO_NAME = {
            v["id"]: v["name"]
            for v in skills_data.values()
            if isinstance(v, dict) and "id" in v and "name" in v
        }
    except Exception as exc:
        current_app.logger.warning(f"import: could not load skill ID map: {exc}")
        _SKILL_ID_TO_NAME = {}

    return _SKILL_ID_TO_NAME


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------

def _map_let_build(build_info: dict) -> dict:
    """
    Map a Last Epoch Tools build JSON object to The Forge BuildCreatePayload
    format. Returns the mapped dict (not yet saved).

    LE Tools schema (relevant fields):
        bio.level           int
        bio.characterClass  int  (1–5)
        bio.chosenMastery   int  (1–3)
        charTree.selected   {nodeId: pts}
        skillTrees[]        [{treeID, selected, level, slotNumber}]
        hud                 [treeID × 5]   — HUD slot order
    """
    bio = build_info.get("bio", {})
    char_class_id = bio.get("characterClass", 0)
    mastery_id = bio.get("chosenMastery", 0)
    level = int(bio.get("level", 70))

    char_class = _CLASS_MAP.get(char_class_id, "Acolyte")
    mastery = _MASTERY_MAP.get(char_class, {}).get(mastery_id, "")

    # ---- Passive tree -------------------------------------------------------
    # charTree.selected = {"nodeId": pointsSpent, ...}
    # Our format: flat array of nodeIds (repeated for multi-point allocation)
    char_tree = build_info.get("charTree", {})
    selected_nodes: dict = char_tree.get("selected", {})
    passive_tree: list[int] = []
    for node_id_str, pts in selected_nodes.items():
        try:
            passive_tree.extend([int(node_id_str)] * max(0, int(pts)))
        except (ValueError, TypeError):
            pass

    # ---- Skills -------------------------------------------------------------
    # skillTrees[].treeID   = skill code matching our skills_metadata.json id
    # skillTrees[].level    = skill level (points_allocated)
    # skillTrees[].slotNumber = HUD slot 0–4
    # skillTrees[].selected  = {nodeId: pts} for the skill specialisation tree
    skill_id_map = _get_skill_id_map()
    skill_trees_raw: list[dict] = build_info.get("skillTrees", [])
    hud: list[str] = build_info.get("hud", [])

    skills: list[dict] = []
    for st in skill_trees_raw:
        tree_id: str = st.get("treeID", "")
        if not tree_id:
            continue

        skill_name = skill_id_map.get(tree_id, tree_id)  # fallback to raw ID

        # Determine slot from HUD order, or fall back to slotNumber field
        slot = st.get("slotNumber", 0)
        if tree_id in hud:
            slot = hud.index(tree_id)

        # Spec tree: same flat-array format as passive tree
        selected_spec: dict = st.get("selected", {})
        spec_tree: list[int] = []
        for node_id_str, pts in selected_spec.items():
            try:
                spec_tree.extend([int(node_id_str)] * max(0, int(pts)))
            except (ValueError, TypeError):
                pass

        skills.append({
            "skill_name": skill_name,
            "slot": slot,
            "points_allocated": int(st.get("level", 0)),
            "spec_tree": spec_tree,
        })

    # Sort skills by slot
    skills.sort(key=lambda s: s["slot"])

    return {
        "name": f"Imported — {char_class} {mastery}".strip(),
        "description": f"Imported from Last Epoch Tools (level {level} {char_class} — {mastery})",
        "character_class": char_class,
        "mastery": mastery,
        "level": level,
        "passive_tree": passive_tree,
        "skills": skills,
        # Gear mapping is not yet implemented — LE Tools item IDs require
        # a separate lookup against their database. Returning empty gear
        # so the user can fill it in manually.
        "gear": [],
        "_import_meta": {
            "source": "lastepochtools",
            "char_class_id": char_class_id,
            "mastery_id": mastery_id,
            "skill_count": len(skills),
            "passive_nodes": len(selected_nodes),
            "gear_note": "Gear not imported — Last Epoch Tools item IDs require additional lookup",
        },
    }


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@import_bp.post("/url")
@limiter.limit("20 per minute")
def import_from_url():
    """
    POST /api/import/url
    Body: { "url": "https://www.lastepochtools.com/planner/kB5dyWvQ" }

    Proxy-fetches the LE Tools page, extracts the embedded build JSON,
    maps it to our format, and returns it for user review before saving.
    """
    body = request.get_json(silent=True) or {}
    url: str = body.get("url", "").strip()

    if not url:
        return jsonify({"error": "url is required"}), 400

    # Validate URL format
    match = re.search(r"lastepochtools\.com/planner/([A-Za-z0-9_\-]+)", url)
    if not match:
        return jsonify({
            "error": "Invalid URL. Expected: https://www.lastepochtools.com/planner/[code]"
        }), 400

    code = match.group(1)

    # Fetch the LE Tools page server-side (browser can't due to CORS)
    try:
        resp = _requests.get(
            f"https://www.lastepochtools.com/planner/{code}",
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; TheForge/1.0; "
                    "+https://github.com/NickolisK24/le-the-forge)"
                ),
                "Accept": "text/html,application/xhtml+xml",
            },
            timeout=12,
        )
        resp.raise_for_status()
    except _requests.Timeout:
        return jsonify({"error": "Timed out fetching the build page. Try again."}), 504
    except _requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 502
        if status == 404:
            return jsonify({"error": "Build not found. The link may be expired or invalid."}), 404
        return jsonify({"error": f"Last Epoch Tools returned HTTP {status}"}), 502
    except _requests.RequestException as exc:
        return jsonify({"error": f"Failed to fetch build: {exc}"}), 502

    html = resp.text

    # Extract window["buildInfo"] = {...}; from the HTML
    # LE Tools embeds the full build JSON as a JS assignment in a <script> tag
    bi_match = re.search(
        r'window\s*\[\s*["\']buildInfo["\']\s*\]\s*=\s*(\{.*?\})\s*;',
        html,
        re.DOTALL,
    )
    if not bi_match:
        # Also try window.buildInfo = {...}
        bi_match = re.search(
            r'window\.buildInfo\s*=\s*(\{.*?\})\s*;',
            html,
            re.DOTALL,
        )

    if not bi_match:
        return jsonify({
            "error": (
                "Could not find build data in page. "
                "The build code may be invalid, or the build was deleted."
            )
        }), 404

    try:
        build_info = json_lib.loads(bi_match.group(1))
    except json_lib.JSONDecodeError as exc:
        current_app.logger.warning(f"import/url: JSON parse error for code={code}: {exc}")
        return jsonify({"error": "Failed to parse build data from Last Epoch Tools page."}), 502

    # Check for server-side error flag (LE Tools sets buildLoadError=1 for invalid codes)
    if build_info.get("buildLoadError") or build_info.get("data") is None and not build_info.get("bio"):
        return jsonify({
            "error": "Build not found or has been deleted on Last Epoch Tools."
        }), 404

    # LE Tools sometimes wraps the real payload in a "data" key
    if "data" in build_info and isinstance(build_info["data"], dict):
        build_info = build_info["data"]

    mapped = _map_let_build(build_info)
    return jsonify({"build": mapped, "source_code": code})
