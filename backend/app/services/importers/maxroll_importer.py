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
from collections import Counter
from typing import Dict, List, Optional

import requests as _requests

from app.services.importers.base_importer import BaseImporter, ImportResult

logger = logging.getLogger(__name__)

# Cap on how many individual per-item warnings (e.g. `gear_slot:...`) of any
# single prefix we emit in missing_fields. Without this cap, a Maxroll payload
# with hundreds of unnamed items can flood the import UI with warnings.
_MAX_WARNINGS_PER_PREFIX = 5

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

# Reverse lookup: mastery name → base class.
# Maxroll sometimes stores the mastery name in the `class` field (the
# current Maxroll planner treats "Bladedancer" etc. as the character's
# class). We detect this and resolve the real base class.
_MASTERY_TO_CLASS: Dict[str, str] = {
    mastery: base
    for base, masteries in _MASTERY_MAP.items()
    for mastery in masteries.values()
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
# Maxroll has restructured their planner backend several times; we try a
# variety of known patterns. Any 4xx/5xx responses are logged (with status)
# so misses can be traced in production.
_API_URLS = [
    "https://planners.maxroll.gg/profiles/le-planner/{code}",
    "https://planners.maxroll.gg/last-epoch/api/save/{code}",
    "https://planners.maxroll.gg/api/last-epoch/save/{code}",
    "https://planners.maxroll.gg/api/last-epoch/load/{code}",
    "https://planners.maxroll.gg/api/v1/last-epoch/{code}",
    "https://maxroll.gg/last-epoch/api/planner/{code}",
    "https://maxroll.gg/api/last-epoch/planner/{code}",
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


# Signals that a dict actually carries build content (not just a label).
# Used to distinguish a real build payload from a planner *envelope* that
# happens to carry a top-level `class` field (e.g. Maxroll's profile envelope
# wraps the real build under `data` alongside metadata like id/date/name).
_BUILD_CONTENT_KEYS = (
    "passives", "passiveTree", "passiveNodes", "tree", "passive_tree",
    "skills", "skillTrees", "abilities", "abilityTree", "skillSpecializations",
    "equipment", "gear", "items",
    "level", "mastery", "masteryName",
    "nodes", "charTree",
    # Planner workspace markers — a profiles list means we have build
    # data even if other keys live inside profiles[activeProfile].
    "profiles", "mainset",
)


def _has_class_field(d: dict) -> bool:
    v = d.get("class", d.get("className", d.get("characterClass")))
    # Accept 0 (Primalist numeric ID) but reject None/"".
    return v is not None and v != ""


def _is_build_dict(d: dict) -> bool:
    """Return True if *d* looks like a single-build payload.

    Requires both a class signal AND a build-content signal. A bare `class`
    is insufficient because Maxroll's planner envelope also carries a
    top-level `class` label while the real build lives under `data`.
    """
    if not _has_class_field(d):
        return False
    return any(k in d for k in _BUILD_CONTENT_KEYS)


def _maybe_decode_json(value):
    """Return *value* parsed as JSON if it is a string that looks like JSON,
    otherwise return it unchanged. Maxroll's profile envelopes sometimes
    store the build payload as a JSON-encoded string under `data`."""
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                return json.loads(s)
            except (ValueError, json.JSONDecodeError):
                return value
    return value


def _drill_profiles(d: dict, variant: Optional[int] = None) -> dict:
    """If *d* is a Maxroll planner workspace (a dict with a `profiles` list
    and an `activeProfile` index), return the selected profile enriched
    with workspace-level fields (class, mainset, items, name). Otherwise
    return *d* unchanged.

    Maxroll's planner workspace looks like:
        {
          "profiles": [{char/passives/skills}, ...],
          "activeProfile": 0,
          "items": [...],      # item catalog shared across profiles
          "mainset": {...},    # active equipped set
          "class": "Rogue",    # display label
          "name": "..."
        }
    The URL fragment (#N) selects a profile; if *variant* is None we fall
    back to `activeProfile`.
    """
    profiles = d.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        return d

    active = d.get("activeProfile", 0)
    if not isinstance(active, int):
        try:
            active = int(active)
        except (ValueError, TypeError):
            active = 0

    # An explicit URL variant takes precedence if it's in range; otherwise
    # fall back to the workspace's activeProfile setting.
    if variant is not None and 0 <= variant < len(profiles):
        idx = variant
    elif 0 <= active < len(profiles):
        idx = active
    else:
        idx = 0

    profile = profiles[idx]
    if not isinstance(profile, dict):
        return d

    # Enrich the profile with workspace-level fields it lacks, so the
    # mapper can resolve class labels and locate the equipped set.
    enriched = dict(profile)
    for k in ("class", "mainset", "items", "name"):
        if k not in enriched and k in d:
            enriched[k] = d[k]
    return enriched


def _unwrap_build_data(payload: dict, variant: Optional[int] = None) -> Optional[dict]:
    """
    Unwrap the build data from various Maxroll response wrappers.

    Maxroll's API has used different envelope formats over time:
      {"data": {...build fields...}}
      {"data": "<JSON-encoded build>"}
      {"data": [{...build 0...}, {...build 1...}, ...]}
      {"data": {"builds": [{...}, ...]}}
      {"build": {...build fields...}}
      {"plannerData": {...build fields...}}
      {"id": ..., "class": "Rogue", "data": {...real build...}, ...}  (profile envelope)
      {...profiles: [...], activeProfile: N, items, mainset, ...}     (planner workspace)
      {...build fields directly...}

    *variant* is the 0-based index from the URL hash fragment (e.g. #2 → 2).
    The returned dict is always drilled to profile level when a workspace
    is detected.
    """
    result = _do_unwrap_build_data(payload, variant)
    if result is None:
        return None
    return _drill_profiles(result, variant)


def _do_unwrap_build_data(payload: dict, variant: Optional[int] = None) -> Optional[dict]:
    """Inner unwrap logic; see _unwrap_build_data docstring.

    For list-indexed payloads (`{"data": [...]}`, `{"data": {"builds": [...]}}`),
    an unspecified variant is treated as 0 (first entry).
    """
    list_variant = variant if variant is not None else 0
    # Direct build data (has class + real build content)
    if _is_build_dict(payload):
        return payload

    # Nested under a wrapper key
    for key in ("data", "build", "plannerData"):
        inner = _maybe_decode_json(payload.get(key))
        if isinstance(inner, dict):
            # {"data": {"builds": [...]}}
            builds_list = inner.get("builds")
            if isinstance(builds_list, list) and builds_list:
                idx = min(list_variant, len(builds_list) - 1)
                if isinstance(builds_list[idx], dict):
                    # The envelope often has the class label at the top
                    # level; fall back to it if the inner build lacks one.
                    candidate = builds_list[idx]
                    if not _has_class_field(candidate) and _has_class_field(payload):
                        candidate = {**candidate, "class": payload.get("class")}
                    return candidate
            if isinstance(inner, dict) and (
                _is_build_dict(inner)
                or any(k in inner for k in _BUILD_CONTENT_KEYS)
            ):
                # Envelope fallback: inner has build content but no class —
                # borrow the class label from the outer envelope. If neither
                # side has a class, keep looking (don't return a classless dict).
                if not _has_class_field(inner):
                    if not _has_class_field(payload):
                        continue
                    inner = {**inner, "class": payload.get("class")}
                # Merge sibling envelope fields that carry build data.
                # Maxroll's profile envelope puts gear under `mainset`
                # alongside `data`; without this merge we lose the gear.
                for field in ("mainset", "equipment", "gear", "items", "level", "name"):
                    if field in payload and field not in inner:
                        inner = {**inner, field: payload[field]}
                return inner
        # {"data": [{...build...}, ...]}
        if isinstance(inner, list) and inner:
            idx = min(list_variant, len(inner) - 1)
            if isinstance(inner[idx], dict) and _is_build_dict(inner[idx]):
                return inner[idx]

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

        # Extract variant index from the URL hash fragment (e.g. #2 → variant 2).
        # The regex already excludes '#' so it won't appear in *code*, but we
        # still need to pull the fragment from the original URL.
        # None when the URL has no fragment, so workspace unwrap falls
        # back to Maxroll's `activeProfile`. An explicit `#0` pins to 0.
        variant: Optional[int] = None
        frag_match = re.search(r"#(\d+)", url)
        if frag_match:
            variant = int(frag_match.group(1))

        build_data, fetch_diag = self._fetch_build_data(code, variant)
        if build_data is None:
            # Surface the last observed HTTP status (if any) so production
            # operators can tell whether Maxroll is rate-limiting, returning
            # 404s, or returning 200s with an unexpected body shape.
            diag_suffix = f" ({fetch_diag})" if fetch_diag else ""
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message=(
                    "Could not fetch build data from Maxroll. "
                    "The build may be expired, or Maxroll may have changed their format."
                    + diag_suffix
                ),
            )

        return self._map(build_data, code)

    def _fetch_build_data(
        self, code: str, variant: Optional[int] = None
    ) -> tuple[Optional[dict], str]:
        """
        Try multiple strategies to get the build data.

        Returns a tuple of (build_data_or_None, diagnostic_string). The
        diagnostic string summarises what each attempt returned so callers
        can include it in error messages and logs.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://maxroll.gg/last-epoch/planner/",
            "Origin": "https://maxroll.gg",
        }
        attempts: List[str] = []

        # Strategy 1: Try API endpoints
        for url_template in _API_URLS:
            api_url = url_template.format(code=code)
            try:
                resp = _requests.get(api_url, headers=headers, timeout=15)
                status = resp.status_code
                if status == 200:
                    try:
                        data = resp.json()
                    except (ValueError, json.JSONDecodeError) as exc:
                        attempts.append(f"{api_url}: 200 non-JSON ({exc})")
                        logger.warning("Maxroll: %s returned 200 non-JSON: %s", api_url, exc)
                        continue
                    if isinstance(data, dict):
                        unwrapped = _unwrap_build_data(data, variant)
                        if unwrapped:
                            logger.info("Maxroll: got build data from API %s", api_url)
                            return unwrapped, ""
                        attempts.append(f"{api_url}: 200 but unknown shape (keys={list(data.keys())[:5]})")
                        logger.warning(
                            "Maxroll: %s returned 200 with unknown shape, keys=%s",
                            api_url, list(data.keys())[:10],
                        )
                    else:
                        attempts.append(f"{api_url}: 200 non-dict ({type(data).__name__})")
                else:
                    attempts.append(f"{api_url}: HTTP {status}")
                    logger.debug("Maxroll: %s returned HTTP %d", api_url, status)
            except _requests.Timeout:
                attempts.append(f"{api_url}: timeout")
            except _requests.RequestException as exc:
                attempts.append(f"{api_url}: {type(exc).__name__}")
                logger.debug("Maxroll: %s raised %s", api_url, exc)

        # Strategy 2: Fetch HTML and extract __NEXT_DATA__
        html_url = f"https://maxroll.gg/last-epoch/planner/{code}"
        try:
            resp = _requests.get(
                html_url,
                headers={**headers, "Accept": "text/html,application/xhtml+xml"},
                timeout=15,
            )
            html_status = resp.status_code
            if html_status == 200:
                raw = _extract_next_data(resp.text)
                if raw:
                    # __NEXT_DATA__ may also wrap multi-variant builds
                    if isinstance(raw, dict):
                        unwrapped = _unwrap_build_data(raw, variant)
                        if unwrapped:
                            logger.info("Maxroll: extracted build from __NEXT_DATA__")
                            return unwrapped, ""
                        # _extract_next_data already returned a valid build dict
                        if _is_build_dict(raw):
                            logger.info("Maxroll: extracted build from __NEXT_DATA__")
                            return raw, ""
                    attempts.append(f"{html_url}: 200 but __NEXT_DATA__ has no build")
                else:
                    attempts.append(f"{html_url}: 200 but no __NEXT_DATA__ found")
            else:
                attempts.append(f"{html_url}: HTTP {html_status}")
        except _requests.Timeout:
            attempts.append(f"{html_url}: timeout")
        except Exception as exc:
            # Catch broadly — resp.text may raise unexpectedly and we must
            # never let the HTML fallback kill the whole parse.
            attempts.append(f"{html_url}: {type(exc).__name__}")
            logger.warning("Maxroll: HTML fetch failed: %s", exc)

        # Compact diagnostic — only include the HTTP statuses (most useful),
        # not the full attempt list, to keep the user-facing message short.
        statuses = [
            part.split(": ", 1)[1]
            for part in attempts
            if ": " in part
        ]
        diag = f"attempts: {'; '.join(statuses[-3:])}" if statuses else ""
        logger.warning(
            "Maxroll: all fetch strategies failed for code=%s. Attempts: %s",
            code, "; ".join(attempts),
        )
        return None, diag

    def _map(self, raw: dict, code: str) -> ImportResult:
        """Map Maxroll planner data to Forge build payload."""
        missing_fields: List[str] = []
        # Count of per-prefix warnings emitted so we can cap them. After the
        # cap, suppressed entries are summarised as `<prefix>_overflow:N`.
        prefix_counts: Counter = Counter()

        def add_missing(entry: str) -> None:
            """Append to missing_fields, capping entries sharing the same
            colon-delimited prefix so a malformed payload can't flood the UI."""
            prefix = entry.split(":", 1)[0] if ":" in entry else entry
            prefix_counts[prefix] += 1
            if prefix_counts[prefix] <= _MAX_WARNINGS_PER_PREFIX:
                missing_fields.append(entry)

        # Class resolution — Maxroll uses string names or numeric IDs
        # Use explicit None checks since 0 is a valid numeric class ID
        char_class = raw.get("class")
        if char_class is None:
            char_class = raw.get("className")
        if char_class is None:
            char_class = raw.get("characterClass")
        if isinstance(char_class, int):
            char_class = _CLASS_MAP.get(char_class)

        # Mastery resolution — 0 is not a valid mastery ID so `or` is safe here
        mastery = raw.get("mastery") or raw.get("masteryName") or ""
        if isinstance(mastery, int):
            mastery = _MASTERY_MAP.get(char_class, {}).get(mastery, "")

        # Maxroll frequently stores the mastery name in the `class` field
        # (e.g. "Bladedancer" instead of "Rogue"). If what we parsed as the
        # class is actually a known mastery, swap them into the correct slots.
        if char_class in _MASTERY_TO_CLASS:
            # If no mastery was set, use the value as the mastery; otherwise
            # keep the explicit mastery and just correct the base class.
            if not mastery:
                mastery = char_class
            char_class = _MASTERY_TO_CLASS[char_class]

        if not char_class:
            return ImportResult(
                success=False,
                source=self.source_name,
                error_message="Could not determine character class from Maxroll data.",
                missing_fields=["character_class"],
                build_data={"_raw_keys": list(raw.keys())},
            )

        if not mastery:
            add_missing("mastery")

        level = int(raw.get("level", 70))

        # Passive tree — try several candidate keys. Maxroll's planner has
        # used different names over time; newer exports put them under
        # `passiveTree`, `tree`, or `passiveNodes` rather than `passives`.
        passives_raw = (
            raw.get("passives")
            or raw.get("passiveTree")
            or raw.get("passiveNodes")
            or raw.get("tree")
            or raw.get("charTree", {}).get("selected", {})
        )
        passive_tree: List[int] = []
        if isinstance(passives_raw, dict):
            for node_id_str, pts in passives_raw.items():
                try:
                    passive_tree.extend([int(node_id_str)] * max(0, int(pts)))
                except (ValueError, TypeError):
                    add_missing(f"passive_node:{node_id_str}")
        elif isinstance(passives_raw, list):
            # Some formats use a flat list
            for item in passives_raw:
                if isinstance(item, dict):
                    nid = item.get("id") or item.get("nodeId") or item.get("node")
                    pts = item.get("points") or item.get("pts") or item.get("rank") or 1
                    if nid is not None:
                        try:
                            passive_tree.extend([int(nid)] * max(0, int(pts)))
                        except (ValueError, TypeError):
                            add_missing(f"passive_node:{nid}")
                elif isinstance(item, (int, str)):
                    # List of bare node IDs
                    try:
                        passive_tree.append(int(item))
                    except (ValueError, TypeError):
                        add_missing(f"passive_node:{item}")

        # Skills — try several candidate keys
        skills_raw = (
            raw.get("skills")
            or raw.get("skillTrees")
            or raw.get("abilities")
            or raw.get("abilityTree")
            or raw.get("skillSpecializations")
            or []
        )
        skills: List[dict] = []
        if isinstance(skills_raw, list):
            iterable = enumerate(skills_raw)
        elif isinstance(skills_raw, dict):
            # Some formats use {slot: skill_data, ...}
            iterable = enumerate(skills_raw.values())
        else:
            iterable = enumerate([])

        for idx, sk in iterable:
            if isinstance(sk, dict):
                skill_name = (
                    sk.get("name")
                    or sk.get("skill_name")
                    or sk.get("skillName")
                    or sk.get("ability")
                    or sk.get("id", "")
                )
                slot = sk.get("slot", idx)

                # Node allocations — check many candidate keys
                nodes = (
                    sk.get("nodes")
                    or sk.get("selected")
                    or sk.get("tree")
                    or sk.get("specTree")
                    or sk.get("spec_tree")
                    or sk.get("allocations")
                    or {}
                )
                spec_tree: List[int] = []
                if isinstance(nodes, dict):
                    for node_id_str, pts in nodes.items():
                        try:
                            spec_tree.extend([int(node_id_str)] * max(0, int(pts)))
                        except (ValueError, TypeError):
                            add_missing(f"skill_node:{skill_name}:{node_id_str}")
                elif isinstance(nodes, list):
                    for n in nodes:
                        if isinstance(n, dict):
                            nid = n.get("id") or n.get("nodeId") or n.get("node")
                            pts = n.get("points") or n.get("pts") or n.get("rank") or 1
                            if nid is not None:
                                try:
                                    spec_tree.extend([int(nid)] * max(0, int(pts)))
                                except (ValueError, TypeError):
                                    add_missing(f"skill_node:{skill_name}:{nid}")
                        elif isinstance(n, (int, str)):
                            try:
                                spec_tree.append(int(n))
                            except (ValueError, TypeError):
                                add_missing(f"skill_node:{skill_name}:{n}")

                skills.append({
                    "skill_name": skill_name,
                    "slot": slot,
                    "points_allocated": int(
                        sk.get("level") or sk.get("points") or sk.get("points_allocated") or 0
                    ),
                    "spec_tree": spec_tree,
                })

        skills.sort(key=lambda s: s["slot"])

        # Diagnostic — log raw structure when the mapper produced nothing.
        # This is critical for debugging unknown Maxroll data formats since
        # the main payload is not captured anywhere else.
        if not passive_tree and not skills:
            logger.warning(
                "Maxroll: mapper produced no passives/skills for code=%s. "
                "raw top-level keys=%s; sample values=%s",
                code,
                list(raw.keys()),
                {k: type(v).__name__ for k, v in list(raw.items())[:20]},
            )
        elif not passive_tree:
            logger.warning(
                "Maxroll: no passives mapped for code=%s. raw keys=%s",
                code, list(raw.keys()),
            )
        elif not skills:
            logger.warning(
                "Maxroll: no skills mapped for code=%s. raw keys=%s",
                code, list(raw.keys()),
            )

        # Gear (best-effort mapping). Maxroll's planner workspace stores
        # equipped gear under `mainset`. Note: `items` is a shared item
        # CATALOG (all items the user has saved) — NOT equipped gear — so
        # we deliberately exclude it here to avoid importing 100s of stray
        # entries as gear slots.
        gear_raw = (
            raw.get("equipment")
            or raw.get("gear")
            or raw.get("mainset")
            or []
        )
        # `mainset` on Maxroll is sometimes a wrapper dict like
        # {"items": [...]} or {"equipment": {...}}. Descend one level.
        if isinstance(gear_raw, dict):
            for inner_key in ("items", "equipment", "gear"):
                if isinstance(gear_raw.get(inner_key), (list, dict)):
                    gear_raw = gear_raw[inner_key]
                    break

        # Item catalog — used to resolve int/str references in mainset to
        # a concrete item dict (name/type/affixes). Planner format stores
        # the catalog under `items` at the workspace level.
        items_catalog = raw.get("items") if isinstance(raw.get("items"), list) else []

        def _resolve_item_ref(ref):
            """Resolve a gear-slot reference to an item dict.

            Maxroll's mainset often uses integer indices or string IDs that
            point into the items catalog, rather than inline item objects.
            """
            if isinstance(ref, dict):
                return ref
            if isinstance(ref, int) and 0 <= ref < len(items_catalog):
                resolved = items_catalog[ref]
                return resolved if isinstance(resolved, dict) else None
            if isinstance(ref, str):
                for candidate in items_catalog:
                    if isinstance(candidate, dict) and str(candidate.get("id")) == ref:
                        return candidate
            return None

        def _extract_item_name(item: dict) -> str:
            return (
                item.get("name")
                or item.get("baseType")
                or item.get("itemName")
                or item.get("type")
                or item.get("baseTypeName")
                or item.get("baseTypeId")
                or ""
            )

        def _collect_affixes(item: dict) -> list:
            affixes = []
            for aff in (item.get("affixes") or []):
                if isinstance(aff, dict):
                    affixes.append({
                        "name": aff.get("name") or aff.get("id", ""),
                        "tier": aff.get("tier", 1),
                        "sealed": aff.get("sealed", False),
                    })
            return affixes

        gear: List[dict] = []
        if isinstance(gear_raw, list):
            for entry in gear_raw:
                resolved = _resolve_item_ref(entry)
                if resolved is None and isinstance(entry, dict):
                    resolved = entry
                if not isinstance(resolved, dict):
                    continue
                raw_slot = str(
                    (entry.get("slot") if isinstance(entry, dict) else "")
                    or resolved.get("slot", "")
                )
                slot = _normalise_slot(raw_slot) if raw_slot else ""
                item_name = _extract_item_name(resolved)
                rarity = resolved.get("rarity", "Rare")

                if item_name:
                    gear.append({
                        "slot": slot,
                        "item_name": item_name,
                        "rarity": rarity,
                        "affixes": _collect_affixes(resolved),
                    })
                else:
                    add_missing(f"gear_slot:{slot or raw_slot or 'unknown'}")
        elif isinstance(gear_raw, dict):
            # Some Maxroll formats use {slot_name: item_ref, ...} where the
            # value may be an inline dict, an int index into items_catalog,
            # or a string item id.
            for slot_key, entry in gear_raw.items():
                resolved = _resolve_item_ref(entry)
                if resolved is None and isinstance(entry, dict):
                    resolved = entry
                if not isinstance(resolved, dict):
                    continue
                slot = _normalise_slot(slot_key)
                item_name = _extract_item_name(resolved)
                rarity = resolved.get("rarity", "Rare")

                if item_name:
                    gear.append({
                        "slot": slot,
                        "item_name": item_name,
                        "rarity": rarity,
                        "affixes": _collect_affixes(resolved),
                    })
                else:
                    add_missing(f"gear_slot:{slot}")

        # Flag empty passives/skills so the partial import alert captures them.
        # Without this, a build with 0 passives+skills looks "successful" and
        # the failure is only visible in the UI.
        if not passive_tree:
            add_missing("passives:empty")
        if not skills:
            add_missing("skills:empty")

        # Emit overflow summaries for any prefix that exceeded the per-prefix
        # cap, so operators still see the magnitude of the failure without
        # drowning the UI.
        for prefix, count in prefix_counts.items():
            if count > _MAX_WARNINGS_PER_PREFIX:
                overflow = count - _MAX_WARNINGS_PER_PREFIX
                missing_fields.append(f"{prefix}_overflow:+{overflow} more")

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
                # Raw top-level keys — critical for debugging unknown formats
                "raw_keys": list(raw.keys()),
            } if missing_fields else None,
        )
        return self.validate(result)
