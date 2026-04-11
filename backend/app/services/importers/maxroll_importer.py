"""
Maxroll importer — parses builds from maxroll.gg/last-epoch/planner/ URLs.

Maxroll embeds build data in __NEXT_DATA__ (Next.js hydration) or serves it
via an API endpoint. The planner slug (e.g. "zge0t60e") maps to server-stored
data.

Maxroll's planner JSON schema (relevant fields):
    data.class          str  ("Acolyte", "Mage", etc.)
    data.mastery        str  ("Lich", "Sorcerer", etc.)
    data.level          int
    data.passives       {nodeId: pts, ...}
    data.skills         [{id, name, nodes: {nodeId: pts}, level, slot}, ...]
    data.equipment      [{slot, itemId, baseType, affixes: [...], ...}, ...]

The #2 hash fragment in URLs selects a specific tab/variant but the build
data is the same for the base slug.
"""

import json
import logging
import re
from typing import Dict, List, Optional

import requests as _requests

from app.services.importers.base_importer import BaseImporter, ImportResult

logger = logging.getLogger(__name__)

# Same class/mastery maps for numeric IDs (Maxroll sometimes uses them)
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

# Canonical gear slot names (Maxroll may use various formats)
_SLOT_NORMALISE: Dict[str, str] = {
    "helm": "Helmet",
    "helmet": "Helmet",
    "head": "Helmet",
    "chest": "Body Armour",
    "body": "Body Armour",
    "body armour": "Body Armour",
    "body armor": "Body Armour",
    "gloves": "Gloves",
    "hands": "Gloves",
    "boots": "Boots",
    "feet": "Boots",
    "belt": "Belt",
    "waist": "Belt",
    "amulet": "Amulet",
    "neck": "Amulet",
    "ring 1": "Ring 1",
    "ring1": "Ring 1",
    "ring 2": "Ring 2",
    "ring2": "Ring 2",
    "weapon": "Weapon",
    "mainhand": "Weapon",
    "main hand": "Weapon",
    "offhand": "Off Hand",
    "off hand": "Off Hand",
    "shield": "Off Hand",
    "relic": "Relic",
    "idol 1": "Idol 1",
    "idol 2": "Idol 2",
    "idol 3": "Idol 3",
    "idol 4": "Idol 4",
}

URL_PATTERN = re.compile(
    r"maxroll\.gg/last-epoch/planner/([A-Za-z0-9_\-]+)"
)

# Possible API endpoints Maxroll uses for planner data.
# Ordered by likelihood — first hit wins.
_API_URLS = [
    "https://planners.maxroll.gg/last-epoch/api/save/{code}",
    "https://maxroll.gg/last-epoch/api/planner/{code}",
    "https://planners.maxroll.gg/api/last-epoch/save/{code}",
]


def _extract_next_data(html: str) -> Optional[dict]:
    """Extract build data from __NEXT_DATA__ script tag."""
    match = re.search(
        r'<script\s+id="__NEXT_DATA__"\s+type="application/json">\s*(.*?)\s*</script>',
        html,
        re.DOTALL,
    )
    if not match:
        return None

    try:
        data = json.loads(match.group(1))
        # Navigate Next.js page props structure
        page_props = data.get("props", {}).get("pageProps", {})
        return page_props.get("build") or page_props.get("data") or page_props
    except (json.JSONDecodeError, AttributeError):
        return None


def _unwrap_build_data(payload: dict) -> Optional[dict]:
    """
    Unwrap the build data from various Maxroll response wrappers.

    Maxroll's API has used different envelope formats over time:
      {"data": {...build fields...}}
      {"build": {...build fields...}}
      {"plannerData": {...build fields...}}
      {...build fields directly...}
    """
    # Direct build data (has class or className)
    if payload.get("class") or payload.get("className") or payload.get("characterClass"):
        return payload

    # Nested under a key
    for key in ("data", "build", "plannerData"):
        inner = payload.get(key)
        if isinstance(inner, dict) and (
            inner.get("class") or inner.get("className") or inner.get("characterClass")
        ):
            return inner

    return None


def _normalise_slot(raw_slot: str) -> str:
    """Normalise gear slot name to canonical form."""
    return _SLOT_NORMALISE.get(raw_slot.lower().strip(), raw_slot)


class MaxrollImporter(BaseImporter):
    source_name = "maxroll"

    def parse(self, url: str) -> ImportResult:
        match = URL_PATTERN.search(url)
        if not match:
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message="Invalid URL — expected https://maxroll.gg/last-epoch/planner/[code]",
            )

        code = match.group(1)
        # Strip hash fragment if present (e.g. #2)
        code = code.split("#")[0]

        build_data = self._fetch_build_data(code)
        if build_data is None:
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message=(
                    "Could not fetch build data from Maxroll. "
                    "The build may be expired, or Maxroll may have changed their format."
                ),
            )

        return self._map(build_data, code)

    def _fetch_build_data(self, code: str) -> Optional[dict]:
        """Try multiple strategies to get the build data."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Strategy 1: Try API endpoints
        for url_template in _API_URLS:
            api_url = url_template.format(code=code)
            try:
                resp = _requests.get(api_url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict):
                        unwrapped = _unwrap_build_data(data)
                        if unwrapped:
                            logger.info("Maxroll: got build data from API %s", api_url)
                            return unwrapped
            except Exception:
                continue

        # Strategy 2: Fetch HTML and extract __NEXT_DATA__
        try:
            resp = _requests.get(
                f"https://maxroll.gg/last-epoch/planner/{code}",
                headers={**headers, "Accept": "text/html,application/xhtml+xml"},
                timeout=15,
            )
            if resp.status_code == 200:
                build_data = _extract_next_data(resp.text)
                if build_data:
                    logger.info("Maxroll: extracted build from __NEXT_DATA__")
                    return build_data
        except Exception as exc:
            logger.warning("Maxroll: HTML fetch failed: %s", exc)

        return None

    def _map(self, raw: dict, code: str) -> ImportResult:
        """Map Maxroll planner data to Forge build payload."""
        missing_fields: List[str] = []

        # Class resolution — Maxroll uses string names or numeric IDs
        # Use explicit None checks since 0 is a valid numeric class ID
        char_class = raw.get("class")
        if char_class is None:
            char_class = raw.get("className")
        if char_class is None:
            char_class = raw.get("characterClass")
        if isinstance(char_class, int):
            char_class = _CLASS_MAP.get(char_class)
        if not char_class:
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message="Could not determine character class from Maxroll data.",
                missing_fields=["character_class"],
                build_data={"_raw_keys": list(raw.keys())},
            )

        # Mastery resolution — 0 is not a valid mastery ID so `or` is safe here
        mastery = raw.get("mastery") or raw.get("masteryName") or ""
        if isinstance(mastery, int):
            mastery = _MASTERY_MAP.get(char_class, {}).get(mastery, "")
        if not mastery:
            missing_fields.append("mastery")

        level = int(raw.get("level", 70))

        # Passive tree
        passives_raw = raw.get("passives") or raw.get("charTree", {}).get("selected", {})
        passive_tree: List[int] = []
        if isinstance(passives_raw, dict):
            for node_id_str, pts in passives_raw.items():
                try:
                    passive_tree.extend([int(node_id_str)] * max(0, int(pts)))
                except (ValueError, TypeError):
                    missing_fields.append(f"passive_node:{node_id_str}")
        elif isinstance(passives_raw, list):
            # Some formats use a flat list
            for item in passives_raw:
                if isinstance(item, dict):
                    nid = item.get("id") or item.get("nodeId")
                    pts = item.get("points", 1)
                    if nid is not None:
                        try:
                            passive_tree.extend([int(nid)] * max(0, int(pts)))
                        except (ValueError, TypeError):
                            missing_fields.append(f"passive_node:{nid}")

        # Skills
        skills_raw = raw.get("skills") or raw.get("skillTrees") or []
        skills: List[dict] = []
        for idx, sk in enumerate(skills_raw):
            if isinstance(sk, dict):
                skill_name = sk.get("name") or sk.get("skill_name") or sk.get("id", "")
                slot = sk.get("slot", idx)

                # Node allocations
                nodes = sk.get("nodes") or sk.get("selected") or {}
                spec_tree: List[int] = []
                if isinstance(nodes, dict):
                    for node_id_str, pts in nodes.items():
                        try:
                            spec_tree.extend([int(node_id_str)] * max(0, int(pts)))
                        except (ValueError, TypeError):
                            missing_fields.append(f"skill_node:{skill_name}:{node_id_str}")

                skills.append({
                    "skill_name": skill_name,
                    "slot": slot,
                    "points_allocated": int(sk.get("level", 0)),
                    "spec_tree": spec_tree,
                })

        skills.sort(key=lambda s: s["slot"])

        # Gear (best-effort mapping)
        gear_raw = raw.get("equipment") or raw.get("gear") or raw.get("items") or []
        gear: List[dict] = []
        if isinstance(gear_raw, list):
            for item in gear_raw:
                if isinstance(item, dict):
                    raw_slot = str(item.get("slot", ""))
                    slot = _normalise_slot(raw_slot) if raw_slot else ""
                    item_name = (
                        item.get("name")
                        or item.get("baseType")
                        or item.get("itemName")
                        or ""
                    )
                    rarity = item.get("rarity", "Rare")

                    affixes = []
                    for aff in (item.get("affixes") or []):
                        if isinstance(aff, dict):
                            affixes.append({
                                "name": aff.get("name") or aff.get("id", ""),
                                "tier": aff.get("tier", 1),
                                "sealed": aff.get("sealed", False),
                            })

                    if item_name:
                        gear.append({
                            "slot": slot,
                            "item_name": item_name,
                            "rarity": rarity,
                            "affixes": affixes,
                        })
                    else:
                        missing_fields.append(f"gear_slot:{slot or raw_slot}")
        elif isinstance(gear_raw, dict):
            # Some Maxroll formats use {slot_name: item_data, ...}
            for slot_key, item in gear_raw.items():
                if isinstance(item, dict):
                    slot = _normalise_slot(slot_key)
                    item_name = (
                        item.get("name")
                        or item.get("baseType")
                        or item.get("itemName")
                        or ""
                    )
                    rarity = item.get("rarity", "Rare")

                    affixes = []
                    for aff in (item.get("affixes") or []):
                        if isinstance(aff, dict):
                            affixes.append({
                                "name": aff.get("name") or aff.get("id", ""),
                                "tier": aff.get("tier", 1),
                                "sealed": aff.get("sealed", False),
                            })

                    if item_name:
                        gear.append({
                            "slot": slot,
                            "item_name": item_name,
                            "rarity": rarity,
                            "affixes": affixes,
                        })
                    else:
                        missing_fields.append(f"gear_slot:{slot}")

        build_data = {
            "name": f"Imported — {char_class} {mastery}".strip(),
            "description": (
                f"Imported from Maxroll "
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
            partial_data={
                "character_class": char_class,
                "mastery": mastery,
                "level": level,
                "skills_count": len(skills),
                "passives_count": len(passive_tree),
                "gear_count": len(gear),
                "missing_count": len(missing_fields),
            } if missing_fields else None,
        )
        return self.validate(result)
