"""
Last Epoch Tools importer — parses builds from lastepochtools.com/planner/ URLs.

LE Tools embeds the full build as a JS assignment in a <script> tag:
    window["buildInfo"] = {...};

Schema (relevant fields):
    bio.level           int
    bio.characterClass  int  (0–4)
    bio.chosenMastery   int  (1–3)
    charTree.selected   {nodeId: pts}
    skillTrees[]        [{treeID, selected, level, slotNumber}]
    hud                 [treeID × 5]  — HUD slot order
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional

import requests as _requests

from app.services.importers.base_importer import BaseImporter, ImportResult

logger = logging.getLogger(__name__)

# LE Tools class/mastery ID maps (same as in import_route.py)
_CLASS_MAP: Dict[int, str] = {
    0: "Primalist",
    1: "Mage",
    2: "Sentinel",
    3: "Acolyte",
    4: "Rogue",
}

_MASTERY_MAP: Dict[str, Dict[int, str]] = {
    "Primalist": {1: "Beastmaster", 2: "Shaman",      3: "Druid"},
    "Mage":      {1: "Sorcerer",    2: "Spellblade",  3: "Runemaster"},
    "Sentinel":  {1: "Void Knight", 2: "Forge Guard", 3: "Paladin"},
    "Acolyte":   {1: "Necromancer", 2: "Lich",        3: "Warlock"},
    "Rogue":     {1: "Bladedancer", 2: "Marksman",    3: "Falconer"},
}

# Skill tree ID → display name (loaded lazily)
_SKILL_ID_TO_NAME: Optional[Dict[str, str]] = None


def _get_skill_id_map() -> Dict[str, str]:
    global _SKILL_ID_TO_NAME
    if _SKILL_ID_TO_NAME is not None:
        return _SKILL_ID_TO_NAME

    try:
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))))
        path = os.path.join(root, "data", "classes", "skills_metadata.json")
        with open(path) as f:
            skills_data = json.load(f)
        _SKILL_ID_TO_NAME = {
            v["id"]: v["name"]
            for v in skills_data.values()
            if isinstance(v, dict) and "id" in v and "name" in v
        }
        logger.info("LET importer: loaded %d skill ID mappings", len(_SKILL_ID_TO_NAME))
    except Exception as exc:
        logger.warning("LET importer: could not load skill ID map: %s", exc)
        _SKILL_ID_TO_NAME = {}

    return _SKILL_ID_TO_NAME


# URL pattern for Last Epoch Tools planner links
URL_PATTERN = re.compile(r"lastepochtools\.com/planner/([A-Za-z0-9_\-]+)")


def _extract_build_info(html: str) -> Optional[dict]:
    """Extract the embedded build JSON from LE Tools HTML."""
    assignment_re = re.search(
        r'window\s*(?:\[\s*["\']buildInfo["\']\s*\]|\.buildInfo)\s*=\s*',
        html,
    )
    if not assignment_re:
        return None

    start = assignment_re.end()
    while start < len(html) and html[start] in " \t\r\n":
        start += 1

    try:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(html, start)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


class LastEpochToolsImporter(BaseImporter):
    source_name = "lastepochtools"

    def parse(self, url: str) -> ImportResult:
        match = URL_PATTERN.search(url)
        if not match:
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message="Invalid URL — expected https://www.lastepochtools.com/planner/[code]",
            )

        code = match.group(1)

        # Fetch the page server-side
        try:
            resp = _requests.get(
                f"https://www.lastepochtools.com/planner/{code}",
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=15,
            )
            resp.raise_for_status()
        except _requests.Timeout:
            return ImportResult(
                success=False, source=self.source_name,
                error_message="Timed out fetching the build page — try again.",
            )
        except _requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 502
            if status == 404:
                return ImportResult(
                    success=False, source=self.source_name,
                    error_message="Build not found — the link may be expired or invalid.",
                )
            return ImportResult(
                success=False, source=self.source_name,
                error_message=f"Last Epoch Tools returned HTTP {status}.",
            )
        except _requests.RequestException as exc:
            return ImportResult(
                success=False, source=self.source_name,
                error_message=f"Network error fetching build: {exc}",
            )

        html = resp.text
        build_info = _extract_build_info(html)

        if build_info is None:
            return ImportResult(
                success=False, source=self.source_name,
                error_message=(
                    "Could not find build data in the page. "
                    "The build code may be invalid, or Last Epoch Tools may have updated their format."
                ),
            )

        if build_info.get("buildLoadError"):
            return ImportResult(
                success=False, source=self.source_name,
                error_message="Build not found or deleted on Last Epoch Tools.",
            )

        # LE Tools sometimes wraps the payload in "data"
        if "data" in build_info and isinstance(build_info["data"], dict):
            build_info = build_info["data"]

        if not build_info.get("bio") and not build_info.get("charTree"):
            return ImportResult(
                success=False, source=self.source_name,
                error_message="Build data is incomplete or in an unexpected format.",
            )

        return self._map(build_info, code)

    def _map(self, build_info: dict, code: str) -> ImportResult:
        """Map LE Tools JSON to Forge build payload."""
        missing_fields: List[str] = []
        bio = build_info.get("bio", {})
        char_class_id = int(bio.get("characterClass", 0))
        mastery_id = int(bio.get("chosenMastery", 0))
        level = int(bio.get("level", 70))

        char_class = _CLASS_MAP.get(char_class_id)
        if not char_class:
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message=f"Unknown class ID {char_class_id} — cannot map to a Forge class.",
                missing_fields=["character_class"],
            )

        mastery = _MASTERY_MAP.get(char_class, {}).get(mastery_id, "")
        if not mastery:
            missing_fields.append("mastery")

        # Passive tree
        char_tree = build_info.get("charTree", {})
        selected_nodes: dict = char_tree.get("selected", {})
        passive_tree: List[int] = []
        for node_id_str, pts in selected_nodes.items():
            try:
                passive_tree.extend([int(node_id_str)] * max(0, int(pts)))
            except (ValueError, TypeError):
                missing_fields.append(f"passive_node:{node_id_str}")

        # Skills
        skill_id_map = _get_skill_id_map()
        skill_trees_raw: List[dict] = build_info.get("skillTrees", [])
        hud: List[str] = build_info.get("hud", [])

        skills: List[dict] = []
        for st in skill_trees_raw:
            tree_id: str = st.get("treeID", "")
            if not tree_id:
                continue

            skill_name = skill_id_map.get(tree_id, tree_id)
            if tree_id not in skill_id_map:
                missing_fields.append(f"skill_id:{tree_id}")

            # Slot from HUD order or fallback
            if tree_id in hud:
                slot = hud.index(tree_id)
            else:
                slot = int(st.get("slotNumber", len(skills)))

            # Spec tree
            selected_spec: dict = st.get("selected", {})
            spec_tree: List[int] = []
            for node_id_str, pts in selected_spec.items():
                try:
                    spec_tree.extend([int(node_id_str)] * max(0, int(pts)))
                except (ValueError, TypeError):
                    missing_fields.append(f"skill_node:{tree_id}:{node_id_str}")

            skills.append({
                "skill_name": skill_name,
                "slot": slot,
                "points_allocated": int(st.get("level", 0)),
                "spec_tree": spec_tree,
            })

        skills.sort(key=lambda s: s["slot"])

        build_data = {
            "name": f"Imported — {char_class} {mastery}".strip(),
            "description": (
                f"Imported from Last Epoch Tools "
                f"(level {level} {char_class}{' — ' + mastery if mastery else ''})"
            ),
            "character_class": char_class,
            "mastery": mastery or _MASTERY_MAP.get(char_class, {}).get(1, ""),
            "level": level,
            "passive_tree": passive_tree,
            "skills": skills,
            "gear": [],
            "_source_code": code,
        }

        result = ImportResult(
            success=True,
            build_data=build_data,
            source=self.source_name,
            missing_fields=missing_fields,
        )
        return self.validate(result)
