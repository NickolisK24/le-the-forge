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

import base64
import json
import logging
import os
import re
import traceback
from typing import Dict, List, Optional, Tuple

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

# Unique items by slot → [{name, base, ...}] (loaded lazily)
_UNIQUE_ITEMS: Optional[Dict[str, List[dict]]] = None


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
    """Load base item data keyed by sequential index."""
    global _BASE_ITEM_MAP
    if _BASE_ITEM_MAP is not None:
        return _BASE_ITEM_MAP

    _BASE_ITEM_MAP = {}
    try:
        path = os.path.join(_project_root(), "data", "items", "base_items.json")
        with open(path) as f:
            data = json.load(f)
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


# (baseTypeID, subTypeID) → item name (from items.json equippable subtypes)
_ITEM_SUBTYPE_MAP: Optional[Dict[Tuple[int, int], str]] = None
# baseTypeID → Forge slot category
_BASE_TYPE_TO_SLOT: Optional[Dict[int, str]] = None


def _get_item_subtype_map() -> Dict[Tuple[int, int], str]:
    """
    Load the (baseTypeID, subTypeID) → displayName lookup from items.json.

    LE Tools encodes items using the game's baseTypeID (equipment category,
    0-39) and subTypeID (specific base within that category). This mapping
    lets us resolve decoded IDs to human-readable item names.
    """
    global _ITEM_SUBTYPE_MAP, _BASE_TYPE_TO_SLOT
    if _ITEM_SUBTYPE_MAP is not None:
        return _ITEM_SUBTYPE_MAP

    _ITEM_SUBTYPE_MAP = {}
    _BASE_TYPE_TO_SLOT = {}
    try:
        path = os.path.join(_project_root(), "data", "items", "items.json")
        with open(path) as f:
            items_data = json.load(f)
        for eq in items_data.get("equippable", []):
            btid = eq.get("baseTypeID")
            if btid is None:
                continue
            slot_type = (eq.get("type") or "").lower()
            _BASE_TYPE_TO_SLOT[btid] = slot_type
            for st in eq.get("subTypes", []):
                stid = st.get("subTypeID")
                name = st.get("displayName") or st.get("name")
                if stid is not None and name:
                    _ITEM_SUBTYPE_MAP[(btid, stid)] = name
        logger.info(
            "LET importer: loaded %d item subtypes from items.json",
            len(_ITEM_SUBTYPE_MAP),
        )
    except Exception as exc:
        logger.warning("LET importer: could not load items.json: %s", exc)

    return _ITEM_SUBTYPE_MAP


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


# Unique item slot names from uniques.json → Forge slot names
_UNIQUE_SLOT_TO_FORGE: Dict[str, str] = {
    "helm": "helmet", "chest": "body_armour",
    "belt": "belt", "boots": "boots", "gloves": "gloves",
    "amulet": "amulet", "ring": "ring",
    "relic": "relic",
    "sword_1h": "weapon", "axe_1h": "weapon", "mace_1h": "weapon",
    "dagger": "weapon", "wand": "weapon", "sceptre": "weapon",
    "sword_2h": "weapon", "axe_2h": "weapon", "mace_2h": "weapon",
    "spear": "weapon", "staff": "weapon", "bow": "weapon",
    "shield": "off_hand", "catalyst": "off_hand", "quiver": "off_hand",
    "idol_1x1_eterra": "idol_altar", "idol_1x3": "idol_altar",
    "idol_1x4": "idol_altar", "idol_2x2": "idol_altar",
}


def _get_unique_items() -> Dict[str, List[dict]]:
    """
    Load unique items from data/items/uniques.json, grouped by Forge slot name.

    Returns { "helmet": [{name, base, slot, ...}], "body_armour": [...], ... }
    """
    global _UNIQUE_ITEMS
    if _UNIQUE_ITEMS is not None:
        return _UNIQUE_ITEMS

    _UNIQUE_ITEMS = {}
    try:
        path = os.path.join(_project_root(), "data", "items", "uniques.json")
        with open(path) as f:
            data = json.load(f)
        count = 0
        for key, item in data.items():
            if key == "_meta" or not isinstance(item, dict):
                continue
            raw_slot = item.get("slot", "")
            forge_slot = _UNIQUE_SLOT_TO_FORGE.get(raw_slot)
            if not forge_slot:
                continue
            _UNIQUE_ITEMS.setdefault(forge_slot, []).append(item)
            count += 1
        logger.info("LET importer: loaded %d unique items", count)
    except Exception as exc:
        logger.warning("LET importer: could not load uniques.json: %s", exc)

    return _UNIQUE_ITEMS


# ---------------------------------------------------------------------------
# Forge slot name → affix registry slot tags (used for slot-validation)
# Forge slot name → list of possible game baseTypeIDs (ordered by likelihood)
# Weapons can be many types, so list all weapon baseTypeIDs.
_SLOT_TO_BASE_TYPE_IDS: Dict[str, List[int]] = {
    "helmet":      [0],
    "body_armour": [1],
    "belt":        [2],
    "boots":       [3],
    "gloves":      [4],
    "weapon1":     [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23],  # all weapon types
    "weapon2":     [5, 6, 7, 8, 9, 10, 11, 18, 19, 17],  # one-hand + shield/catalyst/quiver
    "weapon":      [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23],
    "off_hand":    [18, 19, 17],  # shield, catalyst, quiver
    "amulet":      [20],
    "ring_1":      [21],
    "ring_2":      [21],
    "relic":       [22],
    "idol_altar":  [25, 26, 27, 28, 29, 30, 31, 32, 33],  # all idol sizes
}

# Equipment-only baseTypeIDs (non-idol, non-blessing, non-lens)
_EQUIPMENT_BASE_TYPE_IDS = list(range(0, 24))
# Idol-only baseTypeIDs
_IDOL_BASE_TYPE_IDS = list(range(25, 34))


def _decode_base_item_id(
    encoded: str, slot_name: str,
) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """
    Decode a base64-encoded LE Tools item ID and resolve the base item name.

    Only searches base item subtypes that are valid for the given slot.
    Never crosses slot boundaries (a ring lookup will never return a helmet).

    Returns (item_name, baseTypeID, subTypeID) or (None, None, None).
    """
    raw = _b64_decode_safe(encoded)
    if raw is None:
        logger.debug("LET importer: base item ID '%s' failed base64 decode", encoded)
        return None, None, None

    varints = _decode_varints(raw)
    subtype_map = _get_item_subtype_map()

    # Infer which baseTypeIDs are valid for this slot
    slot_base_ids = _SLOT_TO_BASE_TYPE_IDS.get(slot_name)

    # Extract candidate subTypeIDs from the varints.
    candidates: List[int] = []
    if len(varints) >= 2:
        candidates.append(varints[1])
    for v in varints:
        if 0 <= v <= 200 and v not in candidates:
            candidates.append(v)

    if not candidates:
        return None, (slot_base_ids[0] if slot_base_ids else None), None

    # ONLY search this slot's valid baseTypeIDs — no brute-force cross-slot scan
    if slot_base_ids:
        for btid in slot_base_ids:
            for sub_id in candidates:
                name = subtype_map.get((btid, sub_id))
                if name:
                    return name, btid, sub_id

    return None, (slot_base_ids[0] if slot_base_ids else None), None


def _resolve_unique_for_slot(slot_name: str) -> Optional[str]:
    """
    When we know an item is unique/set (from rarity) but can't decode its
    base64 ID, return "Unknown Unique" as a placeholder.

    In the future this could try to match against unique items by cross-
    referencing decoded varint data with the unique item registry.
    """
    return None


def _b64_decode_safe(encoded: str) -> Optional[bytes]:
    """Decode a base64 string with flexible padding."""
    if not encoded:
        return None
    for pad_len in range(4):
        padded = encoded + "=" * pad_len
        for decoder in [base64.b64decode, base64.urlsafe_b64decode]:
            try:
                return decoder(padded)
            except Exception:
                continue
    return None


# ---------------------------------------------------------------------------

_FORGE_SLOT_TO_AFFIX_TAGS: Dict[str, list] = {
    "helmet":      ["helm"],
    "body_armour": ["chest"],
    "belt":        ["belt"],
    "boots":       ["boots"],
    "gloves":      ["gloves"],
    "weapon":      ["sword", "axe", "mace", "dagger", "wand", "sceptre", "staff",
                    "bow", "polearm", "two_handed_sword", "two_handed_axe",
                    "two_handed_mace", "two_handed_staff", "two_handed_polearm"],
    "weapon1":     ["sword", "axe", "mace", "dagger", "wand", "sceptre", "staff",
                    "bow", "polearm", "two_handed_sword", "two_handed_axe",
                    "two_handed_mace", "two_handed_staff", "two_handed_polearm"],
    "weapon2":     ["sword", "axe", "mace", "dagger", "wand", "sceptre",
                    "shield", "catalyst", "quiver"],
    "off_hand":    ["shield", "catalyst", "quiver"],
    "amulet":      ["amulet"],
    "ring_1":      ["ring"],
    "ring_2":      ["ring"],
    "relic":       ["relic"],
}


# ---------------------------------------------------------------------------
# Base64 affix ID decoder
# ---------------------------------------------------------------------------

def _decode_varints(data: bytes) -> List[int]:
    """Decode a sequence of protobuf-style varints from raw bytes."""
    varints: List[int] = []
    pos = 0
    while pos < len(data):
        result = 0
        shift = 0
        while pos < len(data):
            b = data[pos]
            result |= (b & 0x7f) << shift
            shift += 7
            pos += 1
            if not (b & 0x80):
                break
        varints.append(result)
    return varints


def _decode_let_affix(encoded: str) -> Dict:
    """
    Decode a Last Epoch Tools base64-encoded affix ID.

    LE Tools encodes each affix as a base64 string over a byte sequence
    of protobuf-style varints:
        varint[0] = 0  (padding / version marker)
        varint[1] = category / type flags
        varint[2] = affix identifier (may be the affix_id, or packed with tier)
        varint[3+] = tier, roll value, or other metadata

    Since LE Tools' internal affix IDs may differ from The Forge's, we
    extract multiple candidate IDs and let the caller try each one.

    Returns a dict with:
        raw_bytes: hex string of decoded bytes
        varints: list of decoded varints
        candidates: list of candidate affix_id ints to try (best-guess order)
        tier_guess: best-guess tier (0-7) or None
    """
    raw = _b64_decode_safe(encoded)
    if raw is None:
        return {"raw_bytes": "", "varints": [], "candidates": [], "tier_guess": None}

    varints = _decode_varints(raw)
    candidates: List[int] = []
    tier_guess: Optional[int] = None

    if len(varints) >= 3:
        v2 = varints[2]
        # Strategy 1: varint[2] directly as affix_id (works for small values)
        if 0 <= v2 <= 1110:
            candidates.append(v2)
            # Tier from varint[3] if present
            if len(varints) >= 4:
                t = varints[3]
                if 0 <= t <= 7:
                    tier_guess = t
                else:
                    tier_guess = t & 0x07

        # Strategy 2: for large varint[2], try splitting — low 8 bits as affix_id
        if v2 > 255:
            low8 = v2 & 0xFF
            tier_from_high = (v2 >> 8) & 0x07
            if 0 <= low8 <= 1110 and low8 not in candidates:
                candidates.append(low8)
                if tier_guess is None:
                    tier_guess = tier_from_high

    # Strategy 3: varint[1] as affix_id (fallback for 2-varint entries)
    if len(varints) >= 2 and varints[1] not in candidates:
        v1 = varints[1]
        if 0 <= v1 <= 1110:
            candidates.append(v1)

    # Strategy 4: raw byte[2] (skip varint encoding, just use the third byte)
    if len(raw) >= 3:
        b2 = raw[2]
        if b2 not in candidates and 0 <= b2 <= 255:
            candidates.append(b2)

    return {
        "raw_bytes": raw.hex(),
        "varints": varints,
        "candidates": candidates,
        "tier_guess": tier_guess,
    }


def _resolve_affix(decoded: Dict, slot_name: str) -> Tuple[Optional[dict], Optional[int]]:
    """
    Try to resolve decoded affix candidates against The Forge's affix registry.

    Tries each candidate ID in order, preferring matches whose applicable_to
    list includes the slot.  Returns (affix_info, tier) or (None, None).
    """
    affix_map = _get_affix_map()
    # Build a numeric lookup
    affix_by_num: Dict[int, dict] = {}
    for a in affix_map.values():
        aid = a.get("affix_id")
        if aid is not None:
            affix_by_num[int(aid)] = a

    slot_tags = _FORGE_SLOT_TO_AFFIX_TAGS.get(slot_name, [])
    tier = decoded.get("tier_guess")

    # First pass: find a candidate that matches the slot
    for cid in decoded.get("candidates", []):
        affix = affix_by_num.get(cid)
        if not affix:
            continue
        applicable = affix.get("applicable_to", [])
        if not applicable:
            # No restriction — accept
            return affix, tier
        # Check if any slot tag matches
        if any(tag in applicable for tag in slot_tags):
            return affix, tier

    # Second pass: accept any matching candidate regardless of slot
    for cid in decoded.get("candidates", []):
        affix = affix_by_num.get(cid)
        if affix:
            return affix, tier

    return None, None


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
            # Populate partial_data with whatever we can safely extract from
            # raw build_info so the Discord alert shows what was parsed
            # before the failure point.
            bio = build_info.get("bio", {})
            try:
                cls_id = int(bio.get("characterClass", -1))
            except (ValueError, TypeError):
                cls_id = -1
            cls_name = _CLASS_MAP.get(cls_id)
            mastery_name = None
            if cls_name:
                try:
                    mastery_name = _MASTERY_MAP.get(cls_name, {}).get(
                        int(bio.get("chosenMastery", 0))
                    )
                except (ValueError, TypeError):
                    pass
            partial = {
                "code": code,
                "character_class": cls_name,
                "mastery": mastery_name,
                "level": bio.get("level"),
                "passive_count": len(build_info.get("charTree", {}).get("selected", {})),
                "skill_count": len(build_info.get("skillTrees", [])),
                "gear_attempted": "equipment" in build_info or "gear" in build_info,
                "error": str(exc),
            }
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message=f"Failed to map build data: {exc}",
                partial_data=partial,
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

        # Gear — wrapped so a crash here still returns what was parsed above
        try:
            gear = self._parse_gear(build_info, missing_fields)
        except Exception as exc:
            logger.error("LET importer: gear parsing failed: %s", exc)
            missing_fields.append(f"gear_parse_error:{exc}")
            gear = []

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

        LE Tools stores equipment as a dict keyed by slot name:
          {"helm": {"id": 123, "affixes": [...], "ir": 0, "ur": 0}, ...}

        Field meanings:
          id      — base item type ID (integer)
          affixes — list of affix entries (base64-encoded strings or dicts)
          ir      — item rarity (0=Normal, 1=Magic, 2=Rare, 3=Exalted,
                    4=Legendary, 5=Set, 6=Unique)
          ur      — unique rarity / legendary potential (integer)

        Can also be a list of item dicts with equipmentSlot fields.
        """
        raw_equipment = (
            build_info.get("equipment")
            or build_info.get("gear")
            or build_info.get("items")
        )

        if not raw_equipment:
            logger.info("LET importer: no gear/equipment data in build")
            return []

        # Normalise to a list of (slot_key, item_dict) pairs regardless of shape
        items_iter: List[tuple] = []
        if isinstance(raw_equipment, list):
            items_iter = [(idx, v) for idx, v in enumerate(raw_equipment)]
        elif isinstance(raw_equipment, dict):
            items_iter = list(raw_equipment.items())
        else:
            logger.warning(
                "LET importer: unexpected equipment type %s, skipping gear",
                type(raw_equipment).__name__,
            )
            return []

        # Log the actual structure for diagnostics
        if items_iter:
            first_key, first_val = items_iter[0]
            logger.info(
                "LET importer: equipment — %d slots, slot_names=%s, "
                "first_slot=%s fields=%s",
                len(items_iter),
                [k for k, _ in items_iter],
                first_key,
                list(first_val.keys()) if isinstance(first_val, dict) else type(first_val).__name__,
            )

        base_item_map = _get_base_item_map()
        gear: list = []

        # LE Tools rarity ID → name
        _RARITY_MAP: Dict[int, str] = {
            0: "normal",
            1: "magic",
            2: "rare",
            3: "exalted",
            4: "legendary",
            5: "set",
            6: "unique",
        }

        # LE Tools slot name → Forge slot name
        _LET_SLOT_ALIASES: Dict[str, str] = {
            "helm": "helmet", "helmet": "helmet", "head": "helmet",
            "body": "body_armour", "body_armour": "body_armour",
            "chest": "body_armour", "bodyArmour": "body_armour",
            "belt": "belt", "waist": "belt",
            "boots": "boots", "feet": "boots",
            "gloves": "gloves", "hands": "gloves",
            "weapon": "weapon", "weapon1": "weapon1", "mainHand": "weapon1",
            "weapon2": "weapon2", "offHand": "off_hand", "off_hand": "off_hand",
            "shield": "off_hand",
            "amulet": "amulet", "neck": "amulet",
            "ring1": "ring_1", "ring_1": "ring_1", "leftRing": "ring_1",
            "ring2": "ring_2", "ring_2": "ring_2", "rightRing": "ring_2",
            "relic": "relic",
            "idol_altar": "idol_altar", "idolAltar": "idol_altar",
        }

        affixes_resolved = 0
        affixes_missing = 0

        for slot_key, item_raw in items_iter:
            if not isinstance(item_raw, dict):
                continue

            # Determine slot — try the item's own field first, then the dict key,
            # then fall back to the numeric index via _EQUIP_SLOT_MAP
            explicit_slot = item_raw.get("equipmentSlot", item_raw.get("slot"))
            if explicit_slot is not None:
                try:
                    slot_name = _EQUIP_SLOT_MAP.get(int(explicit_slot), f"slot_{explicit_slot}")
                except (ValueError, TypeError):
                    slot_name = _LET_SLOT_ALIASES.get(str(explicit_slot), str(explicit_slot))
            elif isinstance(slot_key, str) and not slot_key.isdigit():
                slot_name = _LET_SLOT_ALIASES.get(slot_key, slot_key)
            else:
                try:
                    slot_name = _EQUIP_SLOT_MAP.get(int(slot_key), f"slot_{slot_key}")
                except (ValueError, TypeError):
                    slot_name = f"slot_{slot_key}"

            # Base type — LE Tools 'id' field may be:
            #   - An integer base item type ID
            #   - A base64-encoded blob containing baseTypeID + subTypeID
            #   - A string integer ("123")
            raw_item_id = item_raw.get("id",
                          item_raw.get("baseTypeID",
                          item_raw.get("baseType",
                          item_raw.get("base_type_id"))))
            base_item_name = None
            base_type_id = None

            if raw_item_id is not None:
                if isinstance(raw_item_id, int):
                    # Plain integer — try direct lookup
                    base_info = base_item_map.get(raw_item_id)
                    if base_info:
                        base_item_name = base_info.get("name")
                        base_type_id = raw_item_id
                elif isinstance(raw_item_id, str) and raw_item_id.isdigit():
                    # String integer
                    int_id = int(raw_item_id)
                    base_info = base_item_map.get(int_id)
                    if base_info:
                        base_item_name = base_info.get("name")
                        base_type_id = int_id
                elif isinstance(raw_item_id, str):
                    # Base64-encoded — decode and resolve via items.json subtypes
                    name, btid, stid = _decode_base_item_id(raw_item_id, slot_name)
                    if name:
                        base_item_name = name
                        base_type_id = btid

                if not base_item_name:
                    missing_fields.append(f"gear_base:{slot_name}:{raw_item_id}")

            # Rarity — 'ir' field may be:
            #   - A list of bytes e.g. [155, 21, 118] → rarity is byte[0] & 0x07
            #   - An integer (0-6)
            #   - A string integer ("4")
            #   - A base64-encoded string
            ir = item_raw.get("ir", item_raw.get("rarity"))
            rarity = "normal"

            if isinstance(ir, list) and len(ir) >= 1:
                # Byte-list encoding: low 3 bits of first byte = rarity
                try:
                    rarity_code = int(ir[0]) & 0x07
                    rarity = _RARITY_MAP.get(rarity_code, f"rarity_{rarity_code}")
                except (ValueError, TypeError):
                    pass
            elif isinstance(ir, int) and ir > 0:
                rarity = _RARITY_MAP.get(ir, f"rarity_{ir}")
            elif isinstance(ir, str):
                if ir.isdigit() and int(ir) > 0:
                    rarity = _RARITY_MAP.get(int(ir), f"rarity_{ir}")
                elif ir in _RARITY_MAP.values():
                    rarity = ir
                else:
                    ir_bytes = _b64_decode_safe(ir)
                    if ir_bytes:
                        ir_varints = _decode_varints(ir_bytes)
                        for v in ir_varints:
                            if v in _RARITY_MAP and v > 0:
                                rarity = _RARITY_MAP[v]
                                break

            # Legendary potential / unique rarity
            ur_raw = item_raw.get("ur", item_raw.get("legendaryPotential", 0))
            legendary_potential = 0
            if isinstance(ur_raw, list) and len(ur_raw) >= 1:
                try:
                    legendary_potential = int(ur_raw[0])
                except (ValueError, TypeError):
                    pass
            elif isinstance(ur_raw, int):
                legendary_potential = ur_raw
            elif isinstance(ur_raw, str) and ur_raw.isdigit():
                legendary_potential = int(ur_raw)
            elif isinstance(ur_raw, str):
                ur_bytes = _b64_decode_safe(ur_raw)
                if ur_bytes:
                    ur_varints = _decode_varints(ur_bytes)
                    legendary_potential = ur_varints[0] if ur_varints else 0

            # Fallback: infer from affix count when rarity is still "normal"
            raw_affixes = item_raw.get("affixes", item_raw.get("mods", []))
            affix_count = len(raw_affixes) if raw_affixes else 0
            if rarity == "normal" and affix_count > 0:
                if legendary_potential > 0:
                    rarity = "legendary"
                elif affix_count >= 4:
                    rarity = "exalted"
                elif affix_count >= 3:
                    rarity = "rare"
                elif affix_count >= 1:
                    rarity = "magic"

            # For unique/set items where base_id didn't resolve, note the rarity
            if not base_item_name and rarity in ("unique", "set"):
                base_item_name = f"Unknown {rarity.title()}"

            # Affixes — LE Tools encodes affix IDs as base64 strings.
            raw_affixes = item_raw.get("affixes", item_raw.get("mods", []))
            parsed_affixes = []
            for affix_raw in (raw_affixes or []):
                if isinstance(affix_raw, str):
                    encoded_id = affix_raw
                    explicit_tier = None
                elif isinstance(affix_raw, dict):
                    encoded_id = str(affix_raw.get("affixID", affix_raw.get("id", "")))
                    explicit_tier = affix_raw.get("tier", affix_raw.get("t"))
                elif isinstance(affix_raw, (int, float)):
                    # Plain integer affix ID
                    encoded_id = str(int(affix_raw))
                    explicit_tier = None
                else:
                    continue

                if not encoded_id:
                    continue

                # Try direct numeric lookup first (if it looks like an integer)
                affix_info = None
                tier = explicit_tier
                if encoded_id.isdigit():
                    affix_by_num = {int(a.get("affix_id", -1)): a
                                    for a in _get_affix_map().values()
                                    if a.get("affix_id") is not None}
                    affix_info = affix_by_num.get(int(encoded_id))
                    if affix_info:
                        parsed_affixes.append({
                            "id": encoded_id,
                            "name": affix_info["name"],
                            "tier": tier,
                        })
                        affixes_resolved += 1
                        continue

                # Base64 decode and multi-strategy resolution
                decoded = _decode_let_affix(encoded_id)
                affix_info, tier_guess = _resolve_affix(decoded, slot_name)
                if tier is None:
                    tier = tier_guess

                if affix_info:
                    parsed_affixes.append({
                        "id": str(affix_info.get("affix_id", encoded_id)),
                        "name": affix_info["name"],
                        "tier": tier,
                    })
                    affixes_resolved += 1
                else:
                    parsed_affixes.append({
                        "id": encoded_id,
                        "name": None,
                        "tier": tier,
                        "decoded": {
                            "candidates": decoded.get("candidates", []),
                            "varints": decoded.get("varints", []),
                        },
                    })
                    missing_fields.append(
                        f"gear_affix:{slot_name}:{encoded_id}"
                        f"(candidates={decoded.get('candidates', [])})"
                    )
                    affixes_missing += 1

            gear_entry: dict = {
                "slot": slot_name,
                "base_type_id": base_type_id,
                "item_name": base_item_name,
                "rarity": rarity,
                "affixes": parsed_affixes,
            }
            if legendary_potential:
                gear_entry["legendary_potential"] = legendary_potential
            if not base_item_name:
                gear_entry["_raw"] = item_raw

            logger.info(
                "LET importer: parsed %s — %s rarity=%s affixes=%d",
                slot_name,
                base_item_name or f"(base_id={base_type_id})",
                rarity,
                len(parsed_affixes),
            )
            gear.append(gear_entry)

        logger.info(
            "LET importer: gear summary — %d slots, %d affixes resolved, %d unresolved",
            len(gear), affixes_resolved, affixes_missing,
        )
        return gear

        return gear
