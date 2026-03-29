"""
process_set_items.py
====================
Processes set items from exports_json/uniques.json into data/set_items.json.

Reads the setItems array (already extracted by process_uniques.py), resolves
base item names from items.json, formats affix ranges, infers set names from
item name patterns, and writes a structured data file matching the style of
data/uniques.json.

Output:
  data/set_items.json

Notes:
  - PlayerProperty / AbilityProperty: These are internal game-engine generic
    property names used for special unique effects that don't map to a clean
    display string. Items with these properties will show the raw name in their
    affix list (e.g. "+10–20% Physical Cold Necrotic Player Property"). They
    require manual curation to produce human-readable tooltip text — the actual
    effect is described in the item's tooltipDescriptions in the raw export.
"""

import json
import os
import re

ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UNIQUES_IN  = os.path.join(ROOT, "exports_json", "uniques.json")
ITEMS_IN    = os.path.join(ROOT, "exports_json", "items.json")
DATA_DIR    = os.path.join(ROOT, "..", "data")
OUT_FILE    = os.path.join(DATA_DIR, "set_items.json")


# ── Slot mapping ──────────────────────────────────────────────────────────────

BASETYPE_TO_SLOT = {
    "HELMET":            "helmet",
    "BODY_ARMOR":        "body",
    "BELT":              "belt",
    "BOOTS":             "boots",
    "GLOVES":            "gloves",
    "AMULET":            "amulet",
    "RING":              "ring",
    "RELIC":             "relic",
    "WAND":              "wand",
    "SHIELD":            "shield",
    "CATALYST":          "catalyst",
    "QUIVER":            "quiver",
    "ONE_HANDED_SWORD":  "sword",
    "ONE_HANDED_AXE":    "axe",
    "ONE_HANDED_MACES":  "mace",
    "ONE_HANDED_DAGGER": "dagger",
    "ONE_HANDED_SCEPTRE":"sceptre",
    "TWO_HANDED_MACE":   "mace",
    "TWO_HANDED_STAFF":  "staff",
    "TWO_HANDED_SWORD":  "sword",
    "TWO_HANDED_AXE":    "axe",
    "TWO_HANDED_POLEARM":"polearm",
    "BOW":               "bow",
    "CROSSBOW":          "crossbow",
}

BASETYPE_TO_EQUIPPABLE = {
    "HELMET":            "Helmets",
    "BODY_ARMOR":        "Body Armor",
    "BELT":              "Belts",
    "BOOTS":             "Boots",
    "GLOVES":            "Gloves",
    "AMULET":            "Amulet",
    "RING":              "Ring",
    "RELIC":             "Relic",
    "WAND":              "Wands",
    "SHIELD":            "Shield",
    "CATALYST":          "Catalyst",
    "QUIVER":            "Quiver",
    "ONE_HANDED_SWORD":  "1H Swords",
    "ONE_HANDED_AXE":    "1H Axes",
    "ONE_HANDED_MACES":  "1H Maces",
    "ONE_HANDED_DAGGER": "1H Dagger",
    "ONE_HANDED_SCEPTRE":"1H Scepter",
    "TWO_HANDED_MACE":   "2H Maces",
    "TWO_HANDED_STAFF":  "2H Staff",
    "TWO_HANDED_SWORD":  "2H Swords",
    "TWO_HANDED_AXE":    "2H Axes",
    "TWO_HANDED_POLEARM":"2H Polearm",
    "BOW":               "Bows",
    "CROSSBOW":          "Crossbow",
}


# ── Affix formatting ──────────────────────────────────────────────────────────

# Properties whose values are flat numbers, not 0–1 fractions.
FLAT_PROPS = {
    "Health", "Mana", "Armour", "HealthRegen", "DodgeRating",
    "StunAvoidance", "EnduranceThreshold", "HealthGain",
    "Strength", "Dexterity", "Intelligence", "Attunement",
    "LevelOfSkills", "Mana",
}


def camel_to_words(s: str) -> str:
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)


def fmt_val(v: float) -> str:
    rounded = round(v)
    return str(rounded) if abs(v - rounded) < 0.005 else f"{v:.2f}".rstrip("0").rstrip(".")


def format_affix(mod: dict) -> str:
    prop     = mod["property"]
    tags     = [t for t in mod.get("tags", []) if t != "None"]
    mod_type = mod.get("modifierType", "ADDED")
    value    = mod["value"]
    max_val  = mod.get("maxValue")

    # Determine if value is a fraction (percentage display) or flat.
    is_percent = prop not in FLAT_PROPS and abs(value) <= 5.0 and prop != "LevelOfSkills"

    if is_percent:
        lo = fmt_val(value * 100)
        hi = fmt_val(max_val * 100) if max_val is not None else None
    else:
        lo = fmt_val(value)
        hi = fmt_val(max_val) if max_val is not None else None

    val_str = f"{lo}–{hi}" if hi is not None and hi != lo else lo
    prop_name = camel_to_words(prop)
    tag_str   = " ".join(tags) + " " if tags else ""
    sign      = "+" if value >= 0 else ""
    pct       = "%" if is_percent else ""

    if mod_type == "INCREASED":
        return f"{sign}{val_str}{pct} increased {tag_str}{prop_name}".strip()
    if mod_type == "MORE":
        return f"{sign}{val_str}{pct} more {tag_str}{prop_name}".strip()
    return f"{sign}{val_str}{pct} {tag_str}{prop_name}".strip()


def format_tooltip(text: str) -> str:
    """Convert '[36,48,2]% Increased ...' → '36–48% Increased ...'
    Handles scaling patterns like '[1,c,5]' (c = per character level)."""
    def replace(m):
        nums = [n.strip() for n in m.group(1).split(",")]
        numeric = []
        for n in nums:
            try:
                numeric.append(float(n))
            except ValueError:
                pass
        if len(numeric) >= 2:
            lo, hi = fmt_val(numeric[0]), fmt_val(numeric[1])
            return f"{lo}–{hi}" if lo != hi else lo
        elif len(numeric) == 1:
            return fmt_val(numeric[0])
        return m.group(0)
    return re.sub(r"\[([^\]]+)\]", replace, text)


# ── Name helpers ──────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[''`]", "", s)      # drop apostrophes
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def infer_set_name(display_names: list[str]) -> str:
    """Find the longest common word sequence shared by all item names in the set."""
    word_lists = [n.split() for n in display_names]
    common = set(word_lists[0]) & {w for wl in word_lists[1:] for w in wl} if len(word_lists) > 1 else set(word_lists[0])

    # Walk the first name to find the longest consecutive common run.
    best, current = [], []
    for word in word_lists[0]:
        if word in common:
            current.append(word)
        else:
            if len(current) > len(best):
                best = current[:]
            current = []
    if len(current) > len(best):
        best = current

    return " ".join(best) if best else display_names[0]


# ── Base item lookup ──────────────────────────────────────────────────────────

def build_base_item_index(items_data: dict) -> dict:
    """Return {equippable_name: {subTypeID: displayName}}."""
    idx = {}
    for bt in items_data.get("equippable", []):
        bt_name = bt["name"]
        idx[bt_name] = {}
        for st in bt.get("subTypes", []):
            idx[bt_name][st["subTypeID"]] = st.get("displayName") or st.get("name", "")
    return idx


def lookup_base(item: dict, base_idx: dict) -> str | None:
    """Return the base item name for a raw set item."""
    equip_name = BASETYPE_TO_EQUIPPABLE.get(item["baseType"])
    if not equip_name:
        return None
    sub_type_ids = item.get("subTypes", [])
    if not sub_type_ids:
        return None
    return base_idx.get(equip_name, {}).get(sub_type_ids[0])


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading source data …")
    with open(UNIQUES_IN, encoding="utf-8") as f:
        uniques_data = json.load(f)
    with open(ITEMS_IN, encoding="utf-8") as f:
        items_data = json.load(f)

    raw_set_items: list[dict] = uniques_data.get("setItems", [])
    print(f"  Found {len(raw_set_items)} set items")

    base_idx = build_base_item_index(items_data)

    # ── Group items by set ────────────────────────────────────────────────────
    by_set: dict[int, list[dict]] = {}
    for item in raw_set_items:
        sid = item["setId"]
        by_set.setdefault(sid, []).append(item)

    # ── Infer set names ───────────────────────────────────────────────────────
    set_names: dict[int, str] = {}
    for sid, members in sorted(by_set.items()):
        display_names = [m.get("displayName") or m["name"] for m in members]
        set_names[sid] = infer_set_name(display_names)

    # ── Build output ──────────────────────────────────────────────────────────
    output: dict = {}
    sets_index: dict[str, dict] = {}

    for sid, members in sorted(by_set.items()):
        set_name = set_names[sid]
        slugs = []

        for item in sorted(members, key=lambda x: x["id"]):
            display = item.get("displayName") or item["name"]
            slug    = slugify(display)
            slugs.append(slug)

            slot      = BASETYPE_TO_SLOT.get(item["baseType"], item["baseType"].lower())
            base_name = lookup_base(item, base_idx)

            # Visible affixes (skip hidden mods)
            visible_mods = [m for m in item.get("mods", []) if not m.get("hideInTooltip")]
            affixes = [format_affix(m) for m in visible_mods]

            # Set bonuses from tooltip descriptions (setMod=True entries)
            all_tt = item.get("tooltipDescriptions", [])
            set_bonuses = [
                {
                    "pieces": tt["setRequirement"],
                    "text":   format_tooltip(tt["text"]),
                }
                for tt in all_tt if tt.get("setMod")
            ]

            # Gameplay tags from mod tags (lowercased, deduplicated, no "None")
            tag_set = set()
            for m in item.get("mods", []):
                for t in m.get("tags", []):
                    if t != "None":
                        tag_set.add(t.lower())
            tags = sorted(tag_set)

            entry: dict = {
                "name":    display,
                "slot":    slot,
                "set_id":  sid,
                "set":     set_name,
            }
            if base_name:
                entry["base"] = base_name
            if item.get("levelRequirement"):
                entry["level_req"] = item["levelRequirement"]
            entry["affixes"] = affixes
            if set_bonuses:
                entry["set_bonuses"] = set_bonuses
            entry["tags"] = tags
            if item.get("loreText"):
                entry["lore"] = item["loreText"]

            output[slug] = entry

        sets_index[str(sid)] = {"name": set_name, "items": slugs}

    # ── Write ─────────────────────────────────────────────────────────────────
    os.makedirs(DATA_DIR, exist_ok=True)

    final = {
        "_meta": {
            "description": "Last Epoch set item reference data for The Forge build planner.",
            "note":        "Affix ranges are auto-generated from game data. Verify against in-game tooltips.",
            "set_count":   len(sets_index),
            "total_items": len(output),
        },
        "sets": sets_index,
        **output,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(by_set)} sets, {len(output)} items → {OUT_FILE}")
    for sid, members in sorted(by_set.items()):
        names = [m.get("displayName") or m["name"] for m in members]
        print(f"   Set {sid:2d} ({set_names[sid]}): {', '.join(names)}")


if __name__ == "__main__":
    main()
