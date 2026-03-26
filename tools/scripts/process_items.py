"""
process_items.py
================
Parses ItemList from resources.assets (MasterItemsList, path_id=254575).

Extracts:
  - All equippable base item types (weapons, armor, jewelry, idols, lenses)
  - All non-equippable items (crafting materials: shards, glyphs, runes,
    catalysts, blessings, etc.)
  - Implicits per sub-type (fixed stats on item base types)
  - Unique items linked per sub-type

Output:
  exports_json/items.json

Struct reference (from il2cpp.h):
  ItemList_BaseItem: BaseTypeName, displayName, lootFilterNameOverride,
      baseTypeID, maximumAffixes, maxSockets, affixEffectModifier, gridSize
  ItemList_BaseEquipmentItem extends BaseItem:
      type(EquipmentType), isWeapon, minimumDropLevel, goldCostModifier,
      minimumSellValue, addedGambleCost, rerollChance, classAffinity,
      affinityRerollChance, subTypeDropUpgradeChance*, weaponSwingSound,
      subTypeClassSpecificity, subItems(List<EquipmentItem>),
      filteredSubItems(runtime), usePreClassIncompatibilityDropLists,
      preClassIncompatibilityDropLists
  ItemList_EquipmentItem extends SubItem:
      implicits(List<EquipmentImplicit>), classRequirement, subClassRequirement,
      cannotBeUpgradedOnDrop, uniquesList(List<UniqueItem_in_list>),
      hitSoundType, uiItemSoundType, addedWeaponRange, attackRate,
      IMSetTier, IMSetOverrides
  ItemList_EquipmentImplicit:
      property(SP byte), specialTag(byte), tags(AT i32), type(ModType i32),
      implicitValue(f32), implicitMaxValue(f32)
  ItemList_SubItem: name, displayName, subTypeID, levelRequirement,
      cannotDrop, itemTags, hideSubTypeInLootFilter,
      forceAllClassesCategoryInLootFilter, isLegacySubType
  ItemList_BaseNonEquipmentItem extends BaseItem:
      subItems(List<NonEquipmentItem>)
  ItemList_NonEquipmentItem extends SubItem:
      rerollChance, description, uiItemSoundType
"""

import json
import os
import struct

ROOT             = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DIR          = os.path.join(ROOT, "extracted_raw")
OUT_DIR          = os.path.join(ROOT, "exports_json")
OUT_FILE         = os.path.join(OUT_DIR, "items.json")
CACHE_FILE       = os.path.join(RAW_DIR, "MasterItemsList.json")
ENUMS_FILE       = os.path.join(RAW_DIR, "enums", "enums.json")
RESOURCES_ASSETS = r"D:\SteamLibrary\steamapps\common\Last Epoch\Last Epoch_Data\resources.assets"
ITEM_LIST_PID    = 254575

# ── Import shared binary reader ───────────────────────────────────────────────
import sys
sys.path.insert(0, os.path.dirname(__file__))
from resources_reader import BinaryReader, monobehaviour_data_start

# ── Enums decoded inline (matches il2cpp.h) ───────────────────────────────────
SP_MAP: dict[int, str] = {}   # populated from enums.json
AT_MAP: dict[int, str] = {}
ET_MAP: dict[int, str] = {}
MOD_TYPE = {0: "ADDED", 1: "INCREASED", 2: "MORE", 3: "QUOTIENT"}
CLASS_REQ = {0: "Any", 1: "Primalist", 2: "Mage", 3: "Sentinel", 4: "Acolyte", 5: "Rogue", 6: "Weaver"}
SUBCLASS_REQ = {0: "Any", 1: "Beastmaster", 2: "Druid", 3: "Shaman",
                4: "Sorcerer", 5: "Runemaster", 6: "SpellBlade",
                7: "Paladin", 8: "VoidKnight", 9: "ForgeMaster",
                10: "Necromancer", 11: "WarLock", 12: "Lich",
                13: "Bladedancer", 14: "Falconer", 15: "Marksman",
                16: "ThreadWeaver", 17: "Invoker", 18: "Chronomancer"}


def decode_at_tags(val: int) -> list[str]:
    if val == 0: return ["None"]
    return [name for bit, name in sorted(AT_MAP.items()) if bit > 0 and (val & bit) == bit]


def load_enums(path: str):
    global SP_MAP, AT_MAP, ET_MAP
    data = json.load(open(path, encoding="utf-8"))["enums"]
    for e in data:
        if e["name"] == "SP":
            SP_MAP = {v: k for k, v in e["values"].items()}
        elif e["name"] == "AT":
            AT_MAP = {v: k for k, v in e["values"].items()}
        elif e["name"] == "EquipmentType":
            ET_MAP = {v: k for k, v in e["values"].items()}


# ── Binary parsing ────────────────────────────────────────────────────────────

def read_equipment_implicit(r: BinaryReader) -> dict:
    prop     = r.read_u8_aligned()
    spec_tag = r.read_u8_aligned()
    tags     = r.read_i32()
    mod_type = r.read_i32()
    impl_val = r.read_f32r()
    impl_max = r.read_f32r()
    return {
        "property":     SP_MAP.get(prop, str(prop)),
        "specialTag":   spec_tag,
        "tags":         decode_at_tags(tags),
        "modifierType": MOD_TYPE.get(mod_type, str(mod_type)),
        "value":        impl_val,
        "maxValue":     impl_max,
    }


def read_unique_item_in_list(r: BinaryReader) -> dict:
    """ItemList_UniqueItem — a lightweight unique reference embedded in each sub-type."""
    name     = r.read_string()
    disp     = r.read_string()
    override_level = r.read_bool()
    level_req      = r.read_i32()
    unique_id      = r.read_i32()
    set_id         = r.read_i32()
    reroll         = r.read_f32r()
    no_world_drops = r.read_bool()
    is_fracture    = r.read_bool()
    is_set_unique  = r.read_bool()
    is_legendary   = r.read_bool()

    # basicMods: List<UniqueItemStatMod>
    n = r.read_u32()
    mods = []
    for _ in range(n):
        val     = r.read_f32r()
        prop    = r.read_u8_aligned()
        spec    = r.read_u8_aligned()
        tags    = r.read_i32()
        mtype   = r.read_i32()
        hidden  = r.read_bool()
        mods.append({
            "value": val, "property": SP_MAP.get(prop, str(prop)),
            "tags": decode_at_tags(tags),
            "modifierType": MOD_TYPE.get(mtype, str(mtype)),
        })

    # descriptionParts: List<UniqueDescriptionPart>
    n2 = r.read_u32()
    descs = []
    for _ in range(n2):
        desc  = r.read_string()
        alt   = r.read_string()
        is_set_part    = r.read_bool()
        set_item_req   = r.read_i32()
        if desc: descs.append(desc)

    lore = r.read_string()

    rec: dict = {"name": name, "uniqueId": unique_id}
    if disp: rec["displayName"] = disp
    if level_req: rec["levelRequirement"] = level_req
    if set_id:  rec["setId"] = set_id
    rec["mods"] = mods
    if descs:   rec["descriptions"] = descs
    if lore:    rec["loreText"] = lore
    return rec


def read_subitem_base(r: BinaryReader) -> dict:
    """ItemList_SubItem fields."""
    name          = r.read_string()
    display       = r.read_string()
    subtype_id    = r.read_i32()
    level_req     = r.read_i32()
    cannot_drop   = r.read_bool()
    item_tags     = r.read_i32()
    hide_lf       = r.read_bool()
    force_all_cls = r.read_bool()
    is_legacy     = r.read_bool()
    return {
        "name": name, "displayName": display, "subTypeID": subtype_id,
        "levelRequirement": level_req, "cannotDrop": cannot_drop,
        "itemTags": item_tags, "isLegacySubType": is_legacy,
    }


def read_equipment_item(r: BinaryReader) -> dict:
    """ItemList_EquipmentItem (extends SubItem)."""
    rec = read_subitem_base(r)

    # implicits: List<EquipmentImplicit>
    n = r.read_u32()
    implicits = [read_equipment_implicit(r) for _ in range(n)]
    rec["implicits"] = implicits

    rec["classRequirement"]    = CLASS_REQ.get(r.read_i32(), "Any")
    rec["subClassRequirement"] = SUBCLASS_REQ.get(r.read_i32(), "Any")
    rec["cannotBeUpgradedOnDrop"] = r.read_bool()

    # uniquesList: List<UniqueItem>
    n2 = r.read_u32()
    uniques = [read_unique_item_in_list(r) for _ in range(n2)]
    if uniques: rec["uniques"] = uniques

    rec["hitSoundType"]     = r.read_u8_aligned()
    rec["uiItemSoundType"]  = r.read_u8_aligned()
    rec["addedWeaponRange"] = r.read_f32r()
    rec["attackRate"]       = r.read_f32r()
    rec["IMSetTier"]        = r.read_i32()

    # IMSetOverrides: List<IMSetClassOverride>
    n3 = r.read_u32()
    for _ in range(n3):
        r.read_i32()  # classID
        r.read_i32()  # tier override

    return rec


def read_base_item_header(r: BinaryReader) -> dict:
    """ItemList_BaseItem fields."""
    base_name   = r.read_string()
    display     = r.read_string()
    loot_filter = r.read_string()
    base_id     = r.read_i32()
    max_affixes = r.read_i32()
    max_sockets = r.read_u8_aligned()
    affix_mod   = r.read_f32r()
    grid_x, grid_y = r.read_vector2int()
    return {
        "name": base_name, "displayName": display,
        "baseTypeID": base_id, "maximumAffixes": max_affixes,
        "maxSockets": max_sockets, "affixEffectModifier": affix_mod,
        "gridSize": [grid_x, grid_y],
        **({"lootFilterName": loot_filter} if loot_filter else {}),
    }


def read_drop_list(r: BinaryReader):
    """ItemList_DropList: List<int>."""
    return r.read_i32_array()


def read_base_equipment_item(r: BinaryReader) -> dict:
    """ItemList_BaseEquipmentItem (extends BaseItem)."""
    rec = read_base_item_header(r)
    rec["type"]           = ET_MAP.get(r.read_i32(), "UNKNOWN")
    rec["isWeapon"]       = r.read_bool()
    rec["minimumDropLevel"] = r.read_f32r()
    rec["goldCostModifier"] = r.read_f32r()
    rec["minimumSellValue"] = r.read_i32()
    rec["addedGambleCost"]  = r.read_f32r()
    rec["rerollChance"]     = r.read_f32r()
    rec["classAffinity"]    = r.read_i32()
    rec["affinityRerollChance"] = r.read_f32r()
    rec["subTypeDropUpgradeChanceMultiplier"]         = r.read_f32r()
    rec["subTypeDropUpgradeChanceMultiplierPerLevel"] = r.read_f32r()
    rec["weaponSwingSound"]  = r.read_u8_aligned()
    rec["subTypeClassSpecificity"] = r.read_i32()

    # subItems: List<EquipmentItem>
    n = r.read_u32()
    rec["subTypes"] = [read_equipment_item(r) for _ in range(n)]

    # filteredSubItems (runtime): List<EquipmentItem> — skip, it's populated at runtime
    n2 = r.read_u32()
    for _ in range(n2):
        read_equipment_item(r)

    rec["usePreClassIncompatibilityDropLists"] = r.read_bool()

    # preClassIncompatibilityDropLists: List<DropList>
    n3 = r.read_u32()
    drop_lists = [read_drop_list(r) for _ in range(n3)]
    if any(drop_lists): rec["preClassDropLists"] = drop_lists

    return rec


def read_non_equipment_item(r: BinaryReader) -> dict:
    """ItemList_NonEquipmentItem (extends SubItem)."""
    rec = read_subitem_base(r)
    rec["rerollChance"]   = r.read_f32r()
    rec["description"]    = r.read_string()
    rec["uiItemSoundType"] = r.read_u8_aligned()
    return rec


def read_base_non_equipment_item(r: BinaryReader) -> dict:
    """ItemList_BaseNonEquipmentItem (extends BaseItem)."""
    rec = read_base_item_header(r)
    n = r.read_u32()
    rec["subTypes"] = [read_non_equipment_item(r) for _ in range(n)]
    return rec


def parse_item_list(raw: bytes) -> dict:
    """Parse the full ItemList MonoBehaviour binary."""
    name, start = monobehaviour_data_start(raw)
    r = BinaryReader(raw)
    r.pos = start

    # affixList: PPtr (12 bytes) — skip
    r.read_pptr()

    # EquippableItems: BaseEquipmentItem[]
    equip_count = r.read_u32()
    print(f"  Parsing {equip_count} equippable base types …", flush=True)
    equippable = [read_base_equipment_item(r) for _ in range(equip_count)]

    # nonEquippableItems: BaseNonEquipmentItem[]
    non_equip_count = r.read_u32()
    print(f"  Parsing {non_equip_count} non-equippable base types …", flush=True)
    non_equippable = [read_base_non_equipment_item(r) for _ in range(non_equip_count)]

    # Remaining fields are all editor/visual PPtrs — not needed
    print(f"  Bytes remaining: {r.remaining()} / {len(raw)}", flush=True)

    return {"equippable": equippable, "nonEquippable": non_equippable}


def extract_from_resources(path: str) -> dict:
    try:
        import UnityPy
    except ImportError:
        raise RuntimeError("pip install UnityPy")

    print("  Loading resources.assets …", flush=True)
    env = UnityPy.load(path)
    sf  = list(env.files.values())[0]
    if ITEM_LIST_PID not in sf.objects:
        raise RuntimeError(f"ItemList path_id={ITEM_LIST_PID} not found")
    raw = sf.objects[ITEM_LIST_PID].get_raw_data()
    print(f"  Raw size: {len(raw):,} bytes", flush=True)
    return parse_item_list(raw)


# ── Output encoding helpers ───────────────────────────────────────────────────

def clean_equip_item(item: dict) -> dict:
    """Remove runtime/empty fields before export."""
    out = {k: v for k, v in item.items()
           if v not in (None, [], "", 0, 0.0, False) or k in ("baseTypeID", "subTypeID", "levelRequirement")}
    if "subTypes" in item:
        out["subTypes"] = [clean_equip_item(s) for s in item["subTypes"]]
    return out


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    load_enums(ENUMS_FILE)

    if os.path.exists(CACHE_FILE):
        print("Loading cached MasterItemsList.json …")
        with open(CACHE_FILE, encoding="utf-8") as f:
            raw_data = json.load(f)
    else:
        print("Extracting from resources.assets …")
        if not os.path.exists(RESOURCES_ASSETS):
            raise FileNotFoundError(f"resources.assets not found: {RESOURCES_ASSETS}")
        raw_data = extract_from_resources(RESOURCES_ASSETS)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        print(f"  Cached to {CACHE_FILE}")

    equippable    = raw_data["equippable"]
    non_equippable = raw_data["nonEquippable"]

    total_subtypes = sum(len(b.get("subTypes", [])) for b in equippable)
    total_ne       = sum(len(b.get("subTypes", [])) for b in non_equippable)

    print(f"  {len(equippable)} equippable base types, {total_subtypes} sub-types")
    print(f"  {len(non_equippable)} non-equippable base types, {total_ne} sub-types")

    out = {
        "_meta": {
            "equippable_base_types": len(equippable),
            "equippable_subtypes":   total_subtypes,
            "non_equippable_base_types": len(non_equippable),
            "non_equippable_subtypes":   total_ne,
        },
        "equippable":    equippable,
        "nonEquippable": non_equippable,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(equippable)} base types ({total_subtypes} subtypes) + "
          f"{len(non_equippable)} non-equip ({total_ne} subtypes) → {OUT_FILE}")


if __name__ == "__main__":
    main()
