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
    equipment[]         [{baseTypeID, affixes: [{affixID, tier}], ...}]
"""

import json
import logging
import os
import re
import traceback
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

# LE Tools equipment slot indices → slot names
_EQUIP_SLOT_MAP: Dict[int, str] = {
    0: "helmet",
    1: "body_armour",
    2: "belt",
    3: "boots",
    4: "gloves",
    5: "weapon",
    6: "off_hand",
    7: "amulet",
    8: "ring_1",
    9: "ring_2",
    10: "relic",
}

# Skill tree ID → display name (loaded lazily)
_SKILL_ID_TO_NAME: Optional[Dict[str, str]] = None

# Base item type ID → base item info (loaded lazily)
_BASE_ITEM_MAP: Optional[Dict[int, dict]] = None

# Affix ID → affix info (loaded lazily)
_AFFIX_MAP: Optional[Dict[str, dict]] = None


def _project_root() -> str:
    """Return project root (4 levels up from this file)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))


def _get_skill_id_map() -> Dict[str, str]:
    global _SKILL_ID_TO_NAME
    if _SKILL_ID_TO_NAME is not None:
        return _SKILL_ID_TO_NAME

    try:
        path = os.path.join(_project_root(), "data", "classes", "skills_metadata.json")
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


def _get_base_item_map() -> Dict[int, dict]:
    """Load base item data keyed by LE Tools integer type ID."""
    global _BASE_ITEM_MAP
    if _BASE_ITEM_MAP is not None:
        return _BASE_ITEM_MAP

    _BASE_ITEM_MAP = {}
    try:
        path = os.path.join(_project_root(), "data", "items", "base_items.json")
        with open(path) as f:
            data = json.load(f)
        # base_items.json is {slot_name: [items...]} — flatten
        idx = 0
        for slot_name, items in data.items():
            for item in items:
                item["_slot"] = slot_name
                _BASE_ITEM_MAP[idx] = item
                idx += 1
        logger.info("LET importer: loaded %d base item entries", len(_BASE_ITEM_MAP))
    except Exception as exc:
        logger.warning("LET importer: could not load base item map: %s", exc)

    return _BASE_ITEM_MAP


def _get_affix_map() -> Dict[str, dict]:
    """Load affix data keyed by affix ID string."""
    global _AFFIX_MAP
    if _AFFIX_MAP is not None:
        return _AFFIX_MAP

    _AFFIX_MAP = {}
    try:
        path = os.path.join(_project_root(), "data", "items", "affixes.json")
        with open(path) as f:
            affixes = json.load(f)
        for affix in affixes:
            affix_id = affix.get("affix_id") or affix.get("id")
            if affix_id is not None:
                _AFFIX_MAP[str(affix_id)] = affix
        logger.info("LET importer: loaded %d affix entries", len(_AFFIX_MAP))
    except Exception as exc:
        logger.warning("LET importer: could not load affix map: %s", exc)

    return _AFFIX_MAP


# URL pattern for Last Epoch Tools planner links
URL_PATTERN = re.compile(r"lastepochtools\.com/planner/([A-Za-z0-9_\-]+)")


def _extract_build_info(html: str) -> Optional[dict]:
    """Extract the embedded build JSON from LE Tools HTML."""
    # Method 1: window["buildInfo"] = {...} or window.buildInfo = {...}
    assignment_re = re.search(
        r'window\s*(?:\[\s*["\']buildInfo["\']\s*\]|\.buildInfo)\s*=\s*',
        html,
    )
    if assignment_re:
        start = assignment_re.end()
        while start < len(html) and html[start] in " \t\r\n":
            start += 1
        try:
            decoder = json.JSONDecoder()
            obj, _ = decoder.raw_decode(html, start)
            if isinstance(obj, dict):
                logger.info("LET importer: extracted buildInfo via window assignment")
                return obj
        except json.JSONDecodeError as exc:
            logger.warning("LET importer: found buildInfo assignment but JSON decode failed: %s", exc)

    # Method 2: Look for __NEXT_DATA__ (Next.js SSR pages embed data here)
    next_data_re = re.search(
        r'<script\s+id="__NEXT_DATA__"\s+type="application/json">\s*',
        html,
    )
    if next_data_re:
        start = next_data_re.end()
        end = html.find("</script>", start)
        if end > start:
            try:
                next_data = json.loads(html[start:end])
                # Navigate to props.pageProps.buildInfo or similar
                page_props = next_data.get("props", {}).get("pageProps", {})
                if "buildInfo" in page_props:
                    logger.info("LET importer: extracted buildInfo via __NEXT_DATA__")
                    return page_props["buildInfo"]
                if "build" in page_props:
                    logger.info("LET importer: extracted build data via __NEXT_DATA__.props.pageProps.build")
                    return page_props["build"]
                # Return entire pageProps if it has bio/charTree
                if page_props.get("bio") or page_props.get("charTree"):
                    logger.info("LET importer: extracted build data from __NEXT_DATA__ pageProps")
                    return page_props
                logger.warning(
                    "LET importer: found __NEXT_DATA__ but no buildInfo. Keys: %s, pageProps keys: %s",
                    list(next_data.keys()),
                    list(page_props.keys()),
                )
            except json.JSONDecodeError as exc:
                logger.warning("LET importer: __NEXT_DATA__ JSON decode failed: %s", exc)

    # Method 3: Look for any large JSON object in script tags that has bio/charTree keys
    for match in re.finditer(r'<script[^>]*>\s*', html):
        script_start = match.end()
        script_end = html.find("</script>", script_start)
        if script_end < 0:
            continue
        script_content = html[script_start:script_end].strip()
        # Look for JSON-like content starting with {
        if not script_content.startswith("{"):
            # Try after an assignment like var x =
            json_match = re.search(r'=\s*(\{)', script_content)
            if not json_match:
                continue
            json_start = json_match.start(1)
            script_content = script_content[json_start:]
        if len(script_content) < 50:
            continue
        try:
            obj, _ = json.JSONDecoder().raw_decode(script_content)
            if isinstance(obj, dict) and ("bio" in obj or "charTree" in obj):
                logger.info("LET importer: extracted build data from script tag via fallback scan")
                return obj
        except (json.JSONDecodeError, ValueError):
            continue

    logger.warning("LET importer: no build data found in HTML (%d bytes)", len(html))
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
        logger.info("LET importer: starting import for code=%s", code)

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
            logger.info(
                "LET importer: fetched page for code=%s status=%d len=%d",
                code, resp.status_code, len(resp.text),
            )
        except _requests.Timeout:
            return ImportResult(
                success=False, source=self.source_name,
                error_message="Timed out fetching the build page — try again.",
            )
        except _requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 502
            logger.warning("LET importer: HTTP %d for code=%s", status, code)
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
            logger.warning("LET importer: network error for code=%s: %s", code, exc)
            return ImportResult(
                success=False, source=self.source_name,
                error_message=f"Network error fetching build: {exc}",
            )

        html = resp.text
        build_info = _extract_build_info(html)

        if build_info is None:
            # Log a snippet for debugging
            logger.warning(
                "LET importer: no buildInfo found for code=%s. "
                "HTML snippet (first 500 chars): %s",
                code, html[:500],
            )
            return ImportResult(
                success=False, source=self.source_name,
                error_message=(
                    "Could not find build data in the page. "
                    "The build code may be invalid, or Last Epoch Tools may have updated their format."
                ),
                partial_data={"html_length": len(html), "code": code},
            )

        if build_info.get("buildLoadError"):
            logger.info("LET importer: buildLoadError flag set for code=%s", code)
            return ImportResult(
                success=False, source=self.source_name,
                error_message="Build not found or deleted on Last Epoch Tools.",
            )

        # LE Tools sometimes wraps the payload in "data"
        if "data" in build_info and isinstance(build_info["data"], dict):
            build_info = build_info["data"]
            logger.info("LET importer: unwrapped 'data' key for code=%s", code)

        if not build_info.get("bio") and not build_info.get("charTree"):
            logger.warning(
                "LET importer: extracted JSON missing bio/charTree for code=%s: keys=%s",
                code, list(build_info.keys()),
            )
            return ImportResult(
                success=False, source=self.source_name,
                error_message="Build data is incomplete or in an unexpected format.",
                partial_data={"keys": list(build_info.keys()), "code": code},
            )

        logger.info(
            "LET importer: extracted build data for code=%s, top-level keys=%s",
            code, list(build_info.keys()),
        )

        try:
            result = self._map(build_info, code)
            logger.info(
                "LET importer: mapping complete for code=%s success=%s missing=%d",
                code, result.success, len(result.missing_fields),
            )
            return result
        except Exception as exc:
            logger.error(
                "LET importer: unexpected error mapping build code=%s: %s\n%s",
                code, exc, traceback.format_exc(),
            )
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message=f"Failed to map build data: {exc}",
                partial_data={"code": code, "keys": list(build_info.keys())},
            )

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

        logger.info(
            "LET importer: bio parsed — class=%s (id=%d) mastery=%s (id=%d) level=%d",
            char_class, char_class_id, mastery or "UNKNOWN", mastery_id, level,
        )

        # Passive tree
        char_tree = build_info.get("charTree", {})
        selected_nodes: dict = char_tree.get("selected", {})
        passive_tree: List[int] = []
        for node_id_str, pts in selected_nodes.items():
            try:
                passive_tree.extend([int(node_id_str)] * max(0, int(pts)))
            except (ValueError, TypeError):
                missing_fields.append(f"passive_node:{node_id_str}")
        logger.info("LET importer: parsed %d passive nodes (%d total points)", len(selected_nodes), len(passive_tree))

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
        logger.info("LET importer: parsed %d skills", len(skills))

        # Gear
        gear = self._parse_gear(build_info, missing_fields)
        logger.info("LET importer: parsed %d gear items", len(gear))

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
            "gear": gear,
            "_source_code": code,
        }

        result = ImportResult(
            success=True,
            build_data=build_data,
            source=self.source_name,
            missing_fields=missing_fields,
        )
        return self.validate(result)

    def _parse_gear(self, build_info: dict, missing_fields: List[str]) -> list:
        """
        Parse gear from LE Tools equipment data.

        LE Tools uses several possible keys: "equipment", "gear", "items".
        Each entry has baseTypeID (int), affixes (list of {affixID, tier}),
        and a slot index.
        """
        raw_equipment = (
            build_info.get("equipment")
            or build_info.get("gear")
            or build_info.get("items")
            or []
        )

        if not raw_equipment:
            logger.info("LET importer: no gear/equipment data in build")
            return []

        logger.info(
            "LET importer: raw equipment entries=%d, sample keys=%s",
            len(raw_equipment),
            list(raw_equipment[0].keys()) if raw_equipment and isinstance(raw_equipment[0], dict) else "N/A",
        )

        base_item_map = _get_base_item_map()
        affix_map = _get_affix_map()
        gear: list = []

        for idx, item_raw in enumerate(raw_equipment):
            if not isinstance(item_raw, dict):
                continue

            # Determine slot
            slot_idx = item_raw.get("equipmentSlot", item_raw.get("slot", idx))
            slot_name = _EQUIP_SLOT_MAP.get(int(slot_idx), f"slot_{slot_idx}")

            # Base type
            base_type_id = item_raw.get("baseTypeID", item_raw.get("baseType", item_raw.get("base_type_id")))
            base_item_name = None
            if base_type_id is not None:
                base_info = base_item_map.get(int(base_type_id))
                if base_info:
                    base_item_name = base_info.get("name")
                else:
                    missing_fields.append(f"gear_base_type:{slot_name}:{base_type_id}")

            # Affixes
            raw_affixes = item_raw.get("affixes", item_raw.get("mods", []))
            parsed_affixes = []
            for affix_raw in (raw_affixes or []):
                if not isinstance(affix_raw, dict):
                    continue
                affix_id = str(affix_raw.get("affixID", affix_raw.get("id", "")))
                tier = affix_raw.get("tier", affix_raw.get("t", 0))
                affix_info = affix_map.get(affix_id) if affix_id else None
                parsed_affixes.append({
                    "id": affix_id,
                    "name": affix_info["name"] if affix_info else None,
                    "tier": tier,
                    "_raw": affix_raw if not affix_info else None,
                })
                if not affix_info and affix_id:
                    missing_fields.append(f"gear_affix:{slot_name}:{affix_id}")

            # Implicit stats
            implicit_value = item_raw.get("implicitValue", item_raw.get("implicit"))

            gear_entry = {
                "slot": slot_name,
                "base_type_id": base_type_id,
                "item_name": base_item_name,
                "affixes": parsed_affixes,
                "implicit": implicit_value,
                "rarity": item_raw.get("rarity", "normal"),
                "_raw": item_raw if not base_item_name else None,
            }

            # Clean up None _raw entries
            if gear_entry["_raw"] is None:
                del gear_entry["_raw"]
            for affix in gear_entry["affixes"]:
                if affix.get("_raw") is None:
                    affix.pop("_raw", None)

            gear.append(gear_entry)

        return gear
