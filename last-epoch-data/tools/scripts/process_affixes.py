"""
process_affixes.py
==================
Extracts and processes all affix data for Last Epoch.

Sources:
  1. extracted_raw/MasterAffixesList.json — equipment affixes parsed from
     resources.assets (509 single-property + 437 multi-property affixes)
  2. extracted_raw/AffixImport.csv       — idol affixes (115 rows)
  3. extracted_raw/enums/enums.json      — SP, AT, EquipmentType enum tables

Output:
  exports_json/affixes.json

Run from repo root or via run_all.py.
"""

import csv
import json
import os
import struct

# ── paths ────────────────────────────────────────────────────────────────────
ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DIR   = os.path.join(ROOT, "extracted_raw")
OUT_DIR   = os.path.join(ROOT, "exports_json")
OUT_FILE  = os.path.join(OUT_DIR, "affixes.json")

MASTER_JSON   = os.path.join(RAW_DIR, "MasterAffixesList.json")
IDOL_CSV      = os.path.join(RAW_DIR, "AffixImport.csv")
ENUMS_FILE    = os.path.join(RAW_DIR, "enums", "enums.json")

# resources.assets path — only needed if MasterAffixesList.json is missing
RESOURCES_ASSETS = r"D:\SteamLibrary\steamapps\common\Last Epoch\Last Epoch_Data\resources.assets"


# ── enum tables hardcoded from AffixList nested types (Mono.Cecil) ───────────
AFFIX_TYPE = {0: "PREFIX", 1: "SUFFIX", 2: "SPECIAL"}

AFFIX_DISPLAY_CATEGORY = {
    0: "ATTRIBUTES", 1: "OFF_MELEE", 2: "OFF_SPELL", 3: "OFF_TYPE_SPECIFIC",
    4: "OFF_GEN", 5: "OFF_THROW", 6: "DEF_HEALTH", 7: "DEF_BLOCK",
    8: "DEF_RESISTANCE", 9: "DEF_POTION", 10: "DEF_DODGE", 11: "DEF_GLANCING",
    12: "DEF_HEALING", 13: "DEF_WARD", 14: "DEF_STUN", 15: "DEF_CRIT",
    16: "DEF_DAMAGE_TO_MANA", 17: "DEF_LEECH", 18: "MOVEMENT", 19: "COOLDOWN",
    20: "REFLECT", 21: "MANA", 22: "MINION", 23: "AILMENTS", 24: "ACOLYTE",
    25: "MAGE", 26: "PRIMALIST", 27: "SENTINEL", 28: "ROGUE",
    29: "IDOL_GENERAL", 30: "IDOL_ACOLYTE", 31: "IDOL_MAGE",
    32: "IDOL_PRIMALIST", 33: "IDOL_SENTINEL", 34: "IDOL_ROGUE",
    35: "OFF_BOW", 36: "EXPERIMENTAL", 37: "PERSONAL", 38: "DEF_PARRY",
    39: "SET", 40: "IDOL_WEAVER", 41: "IDOL_ENCHANTED",
}

AFFIX_MORPHOLOGY = {0: "PrefixNoun", 1: "PrefixClassNoun", 2: "PrefixAdjective", 3: "Suffix"}
ROLLS_ON = {0: "Equipment", 1: "Idols"}
SPECIAL_AFFIX_TYPE = {
    0: "Standard", 1: "Experimental", 2: "Personal",
    3: "Set", 4: "IdolEnchantment", 5: "IdolWeaver",
}
CLASS_SPECIFICITY_FLAGS = {
    0: "None", 1: "NonSpecific", 2: "Primalist",
    4: "Mage", 8: "Sentinel", 16: "Acolyte", 32: "Rogue",
}
AFFIX_GROUP = {
    0: "PassiveDefense", 1: "ActiveDefense", 2: "OffensiveIncrease",
    3: "OffensiveAddition", 4: "Hybrid", 5: "DefensiveAbility",
    6: "OffensiveAbility", 7: "Retaliation",
}
T6_COMPAT = {0: "Normal", 1: "Incompatible", 2: "MaximumAffixEffectModifier"}
AFFIX_TITLE_TYPE = {0: "Custom", 1: "Class", 2: "Experimental"}
MOD_TYPE = {0: "ADDED", 1: "INCREASED", 2: "MORE", 3: "QUOTIENT"}


def decode_flags(value: int, flag_map: dict) -> list[str]:
    """Decode an integer bitmask against a flags enum dict."""
    if value == 0:
        return [flag_map.get(0, "None")]
    return [name for bit, name in sorted(flag_map.items()) if bit > 0 and (value & bit) == bit]


def decode_at_tags(value: int, at_enum: dict[int, str]) -> list[str]:
    """Decode AT (affix tags) bitmask into list of tag names."""
    if value == 0:
        return ["None"]
    return [name for bit, name in sorted(at_enum.items()) if bit > 0 and (value & bit) == bit]


# ── binary extractor (used only when MasterAffixesList.json is absent) ───────
def extract_master_affixes_list(resources_path: str) -> dict:
    """Parse MasterAffixesList MonoBehaviour from resources.assets."""
    try:
        import UnityPy
    except ImportError:
        raise RuntimeError("UnityPy is required for binary extraction: pip install UnityPy")

    print("  Loading resources.assets (939 MB) …", flush=True)
    env = UnityPy.load(resources_path)
    sf = list(env.files.values())[0]

    AFFIX_LIST_PID = 254574
    if AFFIX_LIST_PID not in sf.objects:
        raise RuntimeError(f"MasterAffixesList (path_id={AFFIX_LIST_PID}) not found in resources.assets")

    raw = sf.objects[AFFIX_LIST_PID].get_raw_data()
    print(f"  Parsing {len(raw):,} bytes …", flush=True)

    def align4(o):  return (o + 3) & ~3
    def r32(o):     return struct.unpack_from("<i", raw, o)[0], o + 4
    def u32(o):     return struct.unpack_from("<I", raw, o)[0], o + 4
    def f32(o):     v = struct.unpack_from("<f", raw, o)[0]; return round(v, 6), o + 4
    def u8(o):      return raw[o], align4(o + 1)
    def u16(o):     return struct.unpack_from("<H", raw, o)[0], align4(o + 2)
    def bool_(o):   return bool(raw[o]), align4(o + 1)

    def str_(o):
        o = align4(o)
        n = struct.unpack_from("<I", raw, o)[0]; o += 4
        s = raw[o:o + n].decode("utf-8", errors="replace"); o += n
        return s, align4(o)

    def read_tier(o):
        mn, o = f32(o); mx, o = f32(o)
        count, o = u32(o)
        pairs = []
        for _ in range(count):
            r1, o = f32(o); r2, o = f32(o)
            pairs.append({"min": r1, "max": r2})
        # isMultiAffix / checkedIfMultiAffix are runtime flags — not serialized
        return {"minRoll": mn, "maxRoll": mx, "extraRolls": pairs}, o

    def read_affix_base(o):
        a = {}
        a["affixName"],                  o = str_(o)
        a["affixDisplayName"],           o = str_(o)
        a["affixLootFilterOverrideName"],o = str_(o)
        a["titleType"],                  o = u8(o)
        a["affixTitle"],                 o = str_(o)
        a["affixMorphology"],            o = r32(o)
        a["affixId"],                    o = r32(o)
        a["levelRequirement"],           o = r32(o)
        a["rollsOn"],                    o = u8(o)
        a["specialAffixType"],           o = r32(o)
        a["classSpecificity"],           o = r32(o)
        a["uniqueId"],                   o = u16(o)
        a["type"],                       o = r32(o)
        a["standardAffixEffectModifier"],o = f32(o)
        a["rerollChance"],               o = f32(o)
        a["weaponEffect"],               o = r32(o)
        a["group"],                      o = r32(o)
        a["shardHueShift"],              o = f32(o)
        a["shardSaturationModifier"],    o = f32(o)
        n, o = u32(o)
        a["canRollOn"] = list(struct.unpack_from(f"<{n}i", raw, o)); o += n * 4
        n2, o = u32(o)
        rerolls = []
        for _ in range(n2):
            et, o = r32(o); ch, o = f32(o)
            rerolls.append({"equipmentType": et, "chance": ch})
        a["specificRerollChances"] = rerolls
        a["convertOnIncompatibleItemType"], o = bool_(o)
        a["affixIDToConvertTo"],            o = u16(o)
        n3, o = u32(o)
        tiers = []
        for _ in range(n3):
            t, o = read_tier(o); tiers.append(t)
        a["tiers"]                         = tiers
        a["t6Compatibility"],              o = r32(o)
        a["maximumAffixEffectModifierForT6"], o = f32(o)
        a["displayCategory"],              o = r32(o)
        return a, o

    def read_single(o):
        a, o = read_affix_base(o)
        a["property"],                     o = u8(o)
        a["specialTag"],                   o = u8(o)
        a["tags"],                         o = r32(o)
        a["modifierType"],                 o = r32(o)
        a["setProperty"],                  o = bool_(o)
        a["useGeneratedNameForDisplayName"],o = bool_(o)
        return a, o

    def read_affix_property(o):
        p = {}
        p["modDisplayName"],               o = str_(o)
        p["property"],                     o = u8(o)
        p["specialTag"],                   o = u8(o)
        p["tags"],                         o = r32(o)
        p["modifierType"],                 o = r32(o)
        p["setProperty"],                  o = bool_(o)
        p["useGeneratedNameForDisplayName"],o = bool_(o)
        return p, o

    def read_multi(o):
        a, o = read_affix_base(o)
        n, o = u32(o)
        props = []
        for _ in range(n):
            p, o = read_affix_property(o); props.append(p)
        a["affixProperties"] = props
        return a, o

    # Parse header to find data start
    name_len = struct.unpack_from("<I", raw, 28)[0]
    off = align4(32 + name_len)

    sa_count, off = u32(off)
    singles = []
    for _ in range(sa_count):
        a, off = read_single(off)
        singles.append(a)

    ma_count, off = u32(off)
    multis = []
    for _ in range(ma_count):
        a, off = read_multi(off)
        multis.append(a)

    print(f"  Extracted {sa_count} single + {ma_count} multi affixes", flush=True)
    return {"singleAffixes": singles, "multiAffixes": multis}


# ── idol affix CSV parser ─────────────────────────────────────────────────────
def parse_idol_csv(path: str) -> list[dict]:
    """
    Parse AffixImport.csv (115 idol affixes, no header row).

    Column layout (0-indexed):
      0   internal name
      1   display name
      2   shard name
      3   type int
      4   affixId
      5   unknown
      6   levelRequirement (may be a range like '29-30-31-32-33'; use minimum)
      7   unknown
      8   tier count (int)
      9   property (SP enum int)
      10  unknown
      11  unknown
      12  tags (AT bitmask int)
      13  modifierType (int: 0=ADDED 1=INCREASED 2=MORE 3=QUOTIENT)
      14  second property (SP, for multi-stat affixes; -1 if none)
      15+ float values: tier_count pairs per property (min, max alternating)
    """
    affixes = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue
            try:
                affix_id = int(row[4])
            except (IndexError, ValueError):
                continue

            # Level requirement: take minimum if range (e.g. '29-30-31-32-33')
            level_raw = row[6].strip() if len(row) > 6 else "0"
            try:
                level_req = int(level_raw.split("-")[0]) if level_raw else 0
            except ValueError:
                level_req = 0

            # Tier count and properties
            try:
                tier_count = int(row[8])
            except (IndexError, ValueError):
                tier_count = 0

            # Parse float columns starting at col 15
            float_cols: list[float] = []
            for v in row[15:]:
                try:
                    float_cols.append(float(v))
                except ValueError:
                    float_cols.append(0.0)

            # Build tiers for the first property (each tier = min, max)
            tiers = []
            for i in range(tier_count):
                idx = i * 2
                if idx + 1 < len(float_cols):
                    tiers.append({"minRoll": float_cols[idx], "maxRoll": float_cols[idx + 1]})

            # Second property tiers (multi-stat affixes)
            tiers2: list[dict] = []
            if len(row) > 14 and row[14].strip() not in ("", "-1"):
                offset = tier_count * 2
                for i in range(tier_count):
                    idx = offset + i * 2
                    if idx + 1 < len(float_cols):
                        tiers2.append({"minRoll": float_cols[idx], "maxRoll": float_cols[idx + 1]})

            affixes.append({
                "id":              affix_id,
                "name":            row[0].strip(),
                "displayName":     row[1].strip(),
                "shardName":       row[2].strip(),
                "levelRequirement": level_req,
                "rollsOn":         "Idols",
                "tiers":           [{"tier": i + 1, **t} for i, t in enumerate(tiers)],
                **({"tiers2": [{"tier": i + 1, **t} for i, t in enumerate(tiers2)]} if tiers2 else {}),
            })
    return affixes


# ── enum decode helpers ───────────────────────────────────────────────────────
def load_enums(path: str) -> dict:
    """Load enums.json and return name→{value: label} dicts for SP, AT, EquipmentType, WeaponEffect."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for e in data["enums"]:
        out[e["name"]] = {v: k for k, v in e["values"].items()}
    return out


def decode_equipment_types(values: list[int], et_map: dict) -> list[str]:
    return [et_map.get(v, str(v)) for v in values]


def build_affix_record(raw: dict, sp_map: dict, at_map: dict, et_map: dict,
                       we_map: dict, is_multi: bool) -> dict:
    """Convert a raw affix dict to a clean, decoded record."""
    a = raw
    rec = {
        "id":           a["affixId"],
        "name":         a["affixName"],
        "displayName":  a["affixDisplayName"],
    }

    if a.get("affixLootFilterOverrideName"):
        rec["lootFilterName"] = a["affixLootFilterOverrideName"]

    rec["type"]             = AFFIX_TYPE.get(a["type"], str(a["type"]))
    rec["morphology"]       = AFFIX_MORPHOLOGY.get(a["affixMorphology"], str(a["affixMorphology"]))
    rec["titleType"]        = AFFIX_TITLE_TYPE.get(a["titleType"], str(a["titleType"]))
    if a.get("affixTitle"):
        rec["title"]        = a["affixTitle"]

    rec["levelRequirement"] = a["levelRequirement"]
    rec["rollsOn"]          = ROLLS_ON.get(a["rollsOn"], str(a["rollsOn"]))
    rec["specialAffixType"] = SPECIAL_AFFIX_TYPE.get(a["specialAffixType"], str(a["specialAffixType"]))
    rec["classSpecificity"] = decode_flags(a["classSpecificity"], CLASS_SPECIFICITY_FLAGS)
    rec["displayCategory"]  = AFFIX_DISPLAY_CATEGORY.get(a["displayCategory"], str(a["displayCategory"]))
    rec["group"]            = AFFIX_GROUP.get(a["group"], str(a["group"]))
    rec["t6Compatibility"]  = T6_COMPAT.get(a["t6Compatibility"], str(a["t6Compatibility"]))
    rec["uniqueId"]         = a["uniqueId"]
    rec["weaponEffect"]     = we_map.get(a["weaponEffect"], str(a["weaponEffect"]))
    rec["canRollOn"]        = decode_equipment_types(a["canRollOn"], et_map)
    rec["rerollChance"]     = a["rerollChance"]

    if a.get("specificRerollChances"):
        rec["specificRerollChances"] = [
            {"equipmentType": et_map.get(r["equipmentType"], str(r["equipmentType"])),
             "chance": r["chance"]}
            for r in a["specificRerollChances"]
        ]

    if a.get("convertOnIncompatibleItemType"):
        rec["convertOnIncompatibleItemType"] = True
        rec["affixIDToConvertTo"] = a["affixIDToConvertTo"]

    if a.get("maximumAffixEffectModifierForT6", 0.0) != 0.0:
        rec["maximumAffixEffectModifierForT6"] = a["maximumAffixEffectModifierForT6"]

    # Tiers
    tiers = []
    for i, t in enumerate(a["tiers"], 1):
        entry: dict = {"tier": i, "minRoll": t["minRoll"], "maxRoll": t["maxRoll"]}
        if t.get("extraRolls"):
            entry["extraRolls"] = t["extraRolls"]
        tiers.append(entry)
    rec["tiers"] = tiers

    if is_multi:
        rec["affixProperties"] = [
            {
                "displayName": p.get("modDisplayName", ""),
                "property":    sp_map.get(p["property"], str(p["property"])),
                "tags":        decode_at_tags(p["tags"], at_map),
                "modifierType": MOD_TYPE.get(p["modifierType"], str(p["modifierType"])),
            }
            for p in a.get("affixProperties", [])
        ]
    else:
        rec["property"]     = sp_map.get(a["property"], str(a["property"]))
        rec["tags"]         = decode_at_tags(a["tags"], at_map)
        rec["modifierType"] = MOD_TYPE.get(a["modifierType"], str(a["modifierType"]))

    return rec


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Load or extract MasterAffixesList
    if os.path.exists(MASTER_JSON):
        print("Loading MasterAffixesList.json …")
        with open(MASTER_JSON, encoding="utf-8") as f:
            master = json.load(f)
    else:
        print("MasterAffixesList.json not found — extracting from resources.assets …")
        if not os.path.exists(RESOURCES_ASSETS):
            raise FileNotFoundError(f"resources.assets not found: {RESOURCES_ASSETS}")
        master = extract_master_affixes_list(RESOURCES_ASSETS)
        with open(MASTER_JSON, "w", encoding="utf-8") as f:
            json.dump(master, f, indent=2, ensure_ascii=False)
        print(f"  Cached to {MASTER_JSON}")

    # 2. Load enums
    print("Loading enums …")
    enum_maps = load_enums(ENUMS_FILE)
    sp_map = enum_maps.get("SP", {})
    at_map = enum_maps.get("AT", {})
    et_map = enum_maps.get("EquipmentType", {})
    we_map = enum_maps.get("WeaponEffect", {})

    # 3. Build equipment affix records
    print(f"Decoding equipment affixes …")
    equipment: list[dict] = []
    for raw in master["singleAffixes"]:
        equipment.append(build_affix_record(raw, sp_map, at_map, et_map, we_map, is_multi=False))
    for raw in master["multiAffixes"]:
        equipment.append(build_affix_record(raw, sp_map, at_map, et_map, we_map, is_multi=True))
    equipment.sort(key=lambda x: x["id"])
    print(f"  {len(equipment)} equipment affixes")

    # 4. Parse idol affixes
    print("Parsing idol affixes from AffixImport.csv …")
    idol: list[dict] = []
    if os.path.exists(IDOL_CSV):
        idol = parse_idol_csv(IDOL_CSV)
        idol.sort(key=lambda x: x["id"])
        print(f"  {len(idol)} idol affixes")
    else:
        print(f"  WARNING: {IDOL_CSV} not found — idol affixes skipped")

    # 5. Write output
    out = {
        "_meta": {
            "equipment_count": len(equipment),
            "idol_count": len(idol),
        },
        "equipment": equipment,
        "idol": idol,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Wrote {len(equipment)} equipment + {len(idol)} idol affixes → {OUT_FILE}")


if __name__ == "__main__":
    main()
