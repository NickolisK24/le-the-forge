"""
process_uniques.py
==================
Parses UniqueList from resources.assets (UniqueList, path_id=254583).

Extracts all unique and set items with their:
  - Stats (UniqueItemMod: value, property, tags, modifierType)
  - Tooltip descriptions (set bonus text)
  - Set membership (setID, isSetItem)
  - Legendary potential info
  - Crafting costs (primordial feathers, fangs, etc.)
  - Base type and sub-types they can be

Output:
  exports_json/uniques.json

UniqueList_Fields layout:
  Runtime filter fields (all skipped) + uniques: List<Entry> + filteredList (runtime)
"""

import json
import os
import sys

ROOT             = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DIR          = os.path.join(ROOT, "extracted_raw")
OUT_DIR          = os.path.join(ROOT, "exports_json")
OUT_FILE         = os.path.join(OUT_DIR, "uniques.json")
CACHE_FILE       = os.path.join(RAW_DIR, "UniqueList.json")
ENUMS_FILE       = os.path.join(RAW_DIR, "enums", "enums.json")
RESOURCES_ASSETS = r"D:\SteamLibrary\steamapps\common\Last Epoch\Last Epoch_Data\resources.assets"
UNIQUE_LIST_PID  = 254583

sys.path.insert(0, os.path.dirname(__file__))
from resources_reader import BinaryReader, monobehaviour_data_start

# ── Enums ─────────────────────────────────────────────────────────────────────
SP_MAP: dict[int, str] = {}
AT_MAP: dict[int, str] = {}
ET_MAP: dict[int, str] = {}
MOD_TYPE = {0: "ADDED", 1: "INCREASED", 2: "MORE", 3: "QUOTIENT"}
LEGENDARY_TYPE = {0: "None", 1: "Normal", 2: "Exalted", 3: "Set", 4: "Unique"}
UNIFIED_UNIQUE = {0: "Normal", 1: "Experimental", 2: "Personal", 3: "Set", 4: "Weaver"}


def decode_at(val: int) -> list[str]:
    if val == 0: return ["None"]
    return [name for bit, name in sorted(AT_MAP.items()) if bit > 0 and (val & bit) == bit]


def load_enums(path: str):
    global SP_MAP, AT_MAP, ET_MAP
    data = json.load(open(path, encoding="utf-8"))["enums"]
    for e in data:
        if e["name"] == "SP":    SP_MAP = {v: k for k, v in e["values"].items()}
        elif e["name"] == "AT":  AT_MAP = {v: k for k, v in e["values"].items()}
        elif e["name"] == "EquipmentType": ET_MAP = {v: k for k, v in e["values"].items()}


# ── Binary parsing ────────────────────────────────────────────────────────────

def skip_runtime_filter_fields(r: BinaryReader):
    """
    UniqueList has many runtime-only filter fields before the actual data.
    Layout (from il2cpp.h):
      isRandomDropFilter: i32
      isSetItemFilter: i32
      isPrimordialItemFilter: i32
      filterBySetID: bool (+ pad)
      setID: u8 (+pad)
      minimumLevelRequirement: u8 (+pad)
      maximumLevelRequirement: u8 (+pad)
      filterByBaseType: bool (+pad)
      baseType: i32 (EquipmentType)
      filterByModProperty: bool (+pad)
      modProperty: u8 (+pad)
      filterByModTags: bool (+pad)
      modTags: i32
      includeImplicitsInPropertySearch: bool (+pad)
      filterByLegendaryPotentialLevel: bool (+pad)
      minimumEffectiveLevelForLegendaryPotential: i32
      maximumEffectiveLevelForLegendaryPotential: i32
      filterByLegendaryType: bool (+pad)
      legendaryType: i32
      search: string
      uniques: List<Entry>  <-- this is where we want to be
    """
    r.read_i32()           # isRandomDropFilter
    r.read_i32()           # isSetItemFilter
    r.read_i32()           # isPrimordialItemFilter
    r.read_bool()          # filterBySetID
    r.read_u8_aligned()    # setID
    r.read_u8_aligned()    # minimumLevelRequirement
    r.read_u8_aligned()    # maximumLevelRequirement
    r.read_bool()          # filterByBaseType
    r.read_i32()           # baseType
    r.read_bool()          # filterByModProperty
    r.read_u8_aligned()    # modProperty
    r.read_bool()          # filterByModTags
    r.read_i32()           # modTags
    r.read_bool()          # includeImplicitsInPropertySearch
    r.read_bool()          # filterByLegendaryPotentialLevel
    r.read_i32()           # minimumEffectiveLevelForLegendaryPotential
    r.read_i32()           # maximumEffectiveLevelForLegendaryPotential
    r.read_bool()          # filterByLegendaryType
    r.read_i32()           # legendaryType
    r.read_string()        # search (runtime editor field)


def read_unique_mod(r: BinaryReader) -> dict:
    """UniqueItemMod: value, canRoll, rollID, maxValue, property, specialTag, tags, type, hideInTooltip."""
    value    = r.read_f32r()
    can_roll = r.read_bool()
    roll_id  = r.read_u8_aligned()
    max_val  = r.read_f32r()
    prop     = r.read_u8_aligned()
    spec_tag = r.read_u8_aligned()
    tags     = r.read_i32()
    mod_type = r.read_i32()
    hide     = r.read_bool()

    rec: dict = {
        "value":        value,
        "property":     SP_MAP.get(prop, str(prop)),
        "tags":         decode_at(tags),
        "modifierType": MOD_TYPE.get(mod_type, str(mod_type)),
    }
    if can_roll:
        rec["canRoll"] = True
        rec["rollId"]  = roll_id
        rec["maxValue"] = max_val
    if hide:
        rec["hideInTooltip"] = True
    return rec


def read_tooltip_description(r: BinaryReader) -> dict | None:
    """ItemTooltipDescription: description, altText, setMod, setRequirement."""
    desc    = r.read_string()
    alt     = r.read_string()
    set_mod = r.read_bool()
    set_req = r.read_u8_aligned()
    if not desc:
        return None
    entry: dict = {"text": desc}
    if alt: entry["altText"] = alt
    if set_mod: entry["setMod"] = True; entry["setRequirement"] = set_req
    return entry


def read_unique_entry(r: BinaryReader) -> dict:
    """UniqueList_Entry — one unique/set item."""
    name         = r.read_string()
    display      = r.read_string()
    alt_search   = r.read_string()
    unique_id    = r.read_u16_aligned()
    unified_type = r.read_i32()
    is_set       = r.read_bool()
    set_id       = r.read_u8_aligned()
    is_primordial= r.read_bool()

    feather_cost = r.read_i32()
    fang_cost    = r.read_i32()
    petal_cost   = r.read_i32()
    horn_cost    = r.read_i32()
    crystal_cost = r.read_i32()
    bone_cost    = r.read_i32()

    is_cocooned   = r.read_bool()
    override_lvl  = r.read_bool()
    level_req     = r.read_u8_aligned()
    legendary_type= r.read_i32()
    override_eff  = r.read_bool()
    eff_level_lp  = r.read_u8_aligned()
    can_drop_rnd  = r.read_bool()
    reroll_chance = r.read_f32r()

    # abilityTooltipToShowInAltTooltip: AbilityRef struct {key: i64, ability: Ability*}
    # Only key (int64) is serialized; the raw Ability* pointer is NOT serialized by Unity
    r.skip(8)   # key (i64)

    item_model_type = r.read_i32()
    sub_type_for_im = r.read_i32()
    base_type       = r.read_u8_aligned()

    # subTypes: List<byte>
    n_sub = r.read_u32()
    sub_types = [r.read_u8() for _ in range(n_sub)]
    if n_sub % 4 != 0:
        r.align4()

    # mods: List<UniqueItemMod>
    n_mods = r.read_u32()
    mods = [read_unique_mod(r) for _ in range(n_mods)]

    # tooltipDescriptions: List<ItemTooltipDescription>
    n_tt = r.read_u32()
    tooltips = []
    for _ in range(n_tt):
        tt = read_tooltip_description(r)
        if tt: tooltips.append(tt)

    lore = r.read_string()

    # tooltipEntries: List<UniqueModDisplayListEntry>
    n_te = r.read_u32()
    for _ in range(n_te):
        r.read_u8_aligned()  # modDisplay: byte (padded)

    old_subtype_id = r.read_u8_aligned()
    old_unique_id  = r.read_u8_aligned()

    rec: dict = {
        "id":          unique_id,
        "name":        name,
        "displayName": display,
        "baseType":    ET_MAP.get(base_type, str(base_type)),
        "subTypes":    sub_types,
        "mods":        mods,
    }
    if alt_search: rec["altSearchName"] = alt_search
    if is_set:     rec["isSetItem"] = True; rec["setId"] = set_id
    if is_primordial:
        rec["isPrimordialItem"] = True
        primordial_costs = {}
        if feather_cost: primordial_costs["feathers"] = feather_cost
        if fang_cost:    primordial_costs["fangs"]    = fang_cost
        if petal_cost:   primordial_costs["petals"]   = petal_cost
        if horn_cost:    primordial_costs["horns"]     = horn_cost
        if crystal_cost: primordial_costs["crystals"]  = crystal_cost
        if bone_cost:    primordial_costs["bones"]     = bone_cost
        if primordial_costs: rec["primordialCosts"] = primordial_costs
    if is_cocooned:        rec["isCocoonedItem"] = True
    if level_req:          rec["levelRequirement"] = level_req
    rec["legendaryType"] = LEGENDARY_TYPE.get(legendary_type, str(legendary_type))
    if eff_level_lp:       rec["effectiveLevelForLP"] = eff_level_lp
    rec["canDropRandomly"] = can_drop_rnd
    rec["rerollChance"]    = reroll_chance
    if tooltips:           rec["tooltipDescriptions"] = tooltips
    if lore:               rec["loreText"] = lore
    return rec


def parse_unique_list(raw: bytes) -> list[dict]:
    name, start = monobehaviour_data_start(raw)
    r = BinaryReader(raw)
    r.pos = start
    # NOTE: All "filter" fields in UniqueList are editor/runtime-only and NOT serialized.
    # The binary data starts directly with: uniques count + entries.

    n = r.read_u32()
    print(f"  Parsing {n} unique entries …", flush=True)
    uniques = []
    for i in range(n):
        try:
            entry = read_unique_entry(r)
            uniques.append(entry)
        except Exception as e:
            print(f"  ERROR at entry {i}: {e}, pos={r.pos}")
            break

    print(f"  Bytes remaining: {r.remaining()} / {len(raw)}", flush=True)
    return uniques


def extract_from_resources(path: str) -> list[dict]:
    try:
        import UnityPy
    except ImportError:
        raise RuntimeError("pip install UnityPy")
    print("  Loading resources.assets …", flush=True)
    env = UnityPy.load(path)
    sf  = list(env.files.values())[0]
    raw = sf.objects[UNIQUE_LIST_PID].get_raw_data()
    print(f"  Raw size: {len(raw):,} bytes", flush=True)
    return parse_unique_list(raw)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    load_enums(ENUMS_FILE)

    if os.path.exists(CACHE_FILE):
        print("Loading cached UniqueList.json …")
        with open(CACHE_FILE, encoding="utf-8") as f:
            uniques = json.load(f)
    else:
        print("Extracting from resources.assets …")
        if not os.path.exists(RESOURCES_ASSETS):
            raise FileNotFoundError(f"resources.assets not found: {RESOURCES_ASSETS}")
        uniques = extract_from_resources(RESOURCES_ASSETS)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(uniques, f, indent=2, ensure_ascii=False)
        print(f"  Cached to {CACHE_FILE}")

    # Separate regular uniques from set items
    set_items    = [u for u in uniques if u.get("isSetItem")]
    normal       = [u for u in uniques if not u.get("isSetItem")]

    out = {
        "_meta": {
            "total": len(uniques),
            "unique_count": len(normal),
            "set_item_count": len(set_items),
        },
        "uniques":  sorted(normal,   key=lambda x: x["id"]),
        "setItems": sorted(set_items, key=lambda x: x["id"]),
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(normal)} uniques + {len(set_items)} set items → {OUT_FILE}")


if __name__ == "__main__":
    main()
