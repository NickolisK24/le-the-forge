"""
process_all_uniques.py
======================
Auto-generates data/uniques.json from the full set of uniques in
exports_json/uniques.json (403 items).

Replaces the old hand-curated data/uniques.json (which only contained 66
items) with a complete, auto-generated version that covers every unique in
the game.

Output:
  data/uniques.json

Notes:
  - affixes: auto-formatted from raw mod values. Ranges show min–max.
  - implicit: resolved from the base item's subType implicits in items.json.
  - unique_effects: list of special tooltip lines from tooltipDescriptions
    (these describe the unique's special mechanic, e.g. "You have no ward").
  - tags: inferred from mod tags (lowercased, deduplicated).
  - class_req: omitted — subType class affinity is unreliable for uniques.
    Requires manual curation if needed.
  - PlayerProperty / AbilityProperty: internal engine generics with no clean
    display string. Affixes using these will show the raw property name.
    The actual effect is described in unique_effects (tooltipDescriptions).
"""

import json
import os
import re

ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UNIQUES_IN = os.path.join(ROOT, "exports_json", "uniques.json")
ITEMS_IN   = os.path.join(ROOT, "exports_json", "items.json")
DATA_DIR   = os.path.join(ROOT, "..", "data")
OUT_FILE   = os.path.join(DATA_DIR, "uniques.json")


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

FLAT_PROPS = {
    "Health", "Mana", "Armour", "HealthRegen", "DodgeRating",
    "StunAvoidance", "EnduranceThreshold", "HealthGain",
    "Strength", "Dexterity", "Intelligence", "Attunement",
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

    is_percent = prop not in FLAT_PROPS and abs(value) <= 5.0

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
        # Filter to numeric entries only
        numeric = []
        for n in nums:
            try:
                numeric.append(float(n))
            except ValueError:
                pass  # skip non-numeric like 'c'
        if len(numeric) >= 2:
            lo, hi = fmt_val(numeric[0]), fmt_val(numeric[1])
            return f"{lo}–{hi}" if lo != hi else lo
        elif len(numeric) == 1:
            return fmt_val(numeric[0])
        return m.group(0)  # leave unchanged if no numerics found
    return re.sub(r"\[([^\]]+)\]", replace, text)


# ── Name helpers ──────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[''`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


# ── Item index ────────────────────────────────────────────────────────────────

def build_item_index(items_data: dict) -> dict:
    """Return {equippable_name: {subTypeID: {name, implicits}}}."""
    idx = {}
    for bt in items_data.get("equippable", []):
        bt_name = bt["name"]
        idx[bt_name] = {}
        for st in bt.get("subTypes", []):
            idx[bt_name][st["subTypeID"]] = {
                "name":      st.get("displayName") or st.get("name", ""),
                "implicits": st.get("implicits", []),
            }
    return idx


def lookup_base_info(item: dict, item_idx: dict) -> tuple[str | None, list]:
    """Return (base_name, implicits_list) for a raw unique."""
    equip_name = BASETYPE_TO_EQUIPPABLE.get(item["baseType"])
    if not equip_name:
        return None, []
    sub_type_ids = item.get("subTypes", [])
    if not sub_type_ids:
        return None, []
    st = item_idx.get(equip_name, {}).get(sub_type_ids[0], {})
    return st.get("name") or None, st.get("implicits", [])


def format_implicit(implicits: list) -> str | None:
    """Summarise implicit mods into a single string, or None."""
    if not implicits:
        return None
    parts = []
    for imp in implicits:
        value   = imp.get("value", 0)
        max_val = imp.get("maxValue")
        prop    = imp.get("property", "")
        tags    = [t for t in imp.get("tags", []) if t != "None"]
        mod_type = imp.get("modifierType", "ADDED")

        is_percent = prop not in FLAT_PROPS and abs(value) <= 5.0

        if is_percent:
            lo = fmt_val(value * 100)
            hi = fmt_val(max_val * 100) if max_val is not None and max_val != value else None
        else:
            lo = fmt_val(value)
            hi = fmt_val(max_val) if max_val is not None and max_val != value else None

        val_str   = f"{lo}–{hi}" if hi else lo
        prop_name = camel_to_words(prop)
        tag_str   = " ".join(tags) + " " if tags else ""
        sign      = "+" if value >= 0 else ""
        pct       = "%" if is_percent else ""

        if mod_type == "INCREASED":
            parts.append(f"{sign}{val_str}{pct} increased {tag_str}{prop_name}".strip())
        elif mod_type == "MORE":
            parts.append(f"{sign}{val_str}{pct} more {tag_str}{prop_name}".strip())
        else:
            parts.append(f"{sign}{val_str}{pct} {tag_str}{prop_name}".strip())

    return "; ".join(parts) if parts else None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading source data …")
    with open(UNIQUES_IN, encoding="utf-8") as f:
        uniques_data = json.load(f)
    with open(ITEMS_IN, encoding="utf-8") as f:
        items_data = json.load(f)

    raw_uniques: list[dict] = uniques_data.get("uniques", [])
    print(f"  Found {len(raw_uniques)} uniques")

    item_idx = build_item_index(items_data)

    output: dict = {}
    seen_slugs: dict[str, int] = {}

    for item in raw_uniques:
        display = item.get("displayName") or item["name"]
        slug_base = slugify(display)

        # Deduplicate slugs (rare, but two items can share a display name)
        if slug_base in seen_slugs:
            seen_slugs[slug_base] += 1
            slug = f"{slug_base}_{seen_slugs[slug_base]}"
        else:
            seen_slugs[slug_base] = 1
            slug = slug_base

        slot                    = BASETYPE_TO_SLOT.get(item["baseType"], item["baseType"].lower())
        base_name, raw_implicits = lookup_base_info(item, item_idx)

        visible_mods = [m for m in item.get("mods", []) if not m.get("hideInTooltip")]
        affixes      = [format_affix(m) for m in visible_mods]

        implicit = format_implicit(raw_implicits)

        # Unique effects: non-set tooltip lines describe the special mechanic
        unique_effects = [
            format_tooltip(tt["text"])
            for tt in item.get("tooltipDescriptions", [])
            if not tt.get("setMod")
        ]

        tag_set = set()
        for m in item.get("mods", []):
            for t in m.get("tags", []):
                if t != "None":
                    tag_set.add(t.lower())
        tags = sorted(tag_set)

        entry: dict = {
            "name": display,
            "slot": slot,
        }
        if base_name:
            entry["base"] = base_name
        if item.get("levelRequirement"):
            entry["level_req"] = item["levelRequirement"]
        entry["implicit"]       = implicit
        entry["affixes"]        = affixes
        entry["unique_effects"] = unique_effects
        entry["tags"]           = tags
        if item.get("loreText"):
            entry["lore"] = item["loreText"]

        output[slug] = entry

    # ── Write ─────────────────────────────────────────────────────────────────
    os.makedirs(DATA_DIR, exist_ok=True)

    final = {
        "_meta": {
            "description": "Last Epoch unique item reference data for The Forge build planner.",
            "note": (
                "Auto-generated from exports_json/uniques.json. "
                "Affix ranges reflect raw game values. "
                "PlayerProperty/AbilityProperty affixes show internal engine names — "
                "see unique_effects for the human-readable description."
            ),
            "total": len(output),
        },
        **output,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(output)} uniques → {OUT_FILE}")


if __name__ == "__main__":
    main()
