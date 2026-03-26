"""
process_timelines.py
====================
Parses MonolithTimeline ScriptableObjects from resources.assets (path_ids 254589–254598).

Extracts per-timeline:
  - timelineID, name, difficulties
  - Per difficulty: level, maxStability, corruption thresholds,
    firstSlotBlessings / otherSlotBlessings / anySlotBlessings (subtype IDs),
    monsterMod key from corruption
  - mods / empoweredMods (monster mod keys + depth ranges)
  - Echo weighting values and tier thresholds

Also builds a blessing lookup table from items.json (Blessing base type).

Output:
  exports_json/timelines.json   — 10 timeline entries
  exports_json/blessings.json   — 224 blessing subtypes with implicit mods

Struct reference (from il2cpp.h):
  MonolithTimeline_Fields (extends ScriptableObject):
    timelineID(u8), displayName(str), difficulties(List<Difficulty>),
    restZone(str), optionRerollCost(i32), optionRerollCostPerDepth(i32),
    addedBlessingPopupDelay(f32), timelineBossLoot(PPtr/12B),
    erasForRandomEncounters(List<i32>),
    questZones/nonQuestZones/arenaZones/empoweredNonQuestZones/empoweredArenaZones
    mods/empoweredMods(List<Mod>),
    minimumModDuration/maximumModDuration(List<ModDurationRequirement>),
    modEffectivenessFormulae(List<ModEffectivenessFormula>),
    [23 int/float tier & weighting fields],
    exclusiveEchoRewardsDescription(str)

  MonolithTimeline_Difficulty_Fields:
    sufficientRequirements(List<Completion>), level(i32), tutorialise(bool/4B),
    modEffectModifier(f32), echoesLostOnDeathModifier(f32), maxStability(i32),
    firstSlotBlessings/otherSlotBlessings/anySlotBlessings(List<i32>),
    minTierForTombsOfTheErased(i32), hasCorruptionMod(bool/4B),
    modFromCorruption(MonsterModRef = key(i32) only),
    minimumCorruption(i32), hasMaxCorruption(bool/4B),
    maximumCorruption(i32), additionalCorruptionEffect(i32),
    corruptionRequiredPerLevel(i32)

  MonolithTimeline_Completion_Fields: timelineID(u8/4B), completionType(u8/4B)
  MonolithTimeline_Zone_Fields:       sceneName(str), minimumDepth(i32)
  MonolithTimeline_QuestZone_Fields:  ...Zone + maximumChance(f32), maximumChanceDepth(i32),
                                       stabilityRequirements(i32[]), requiredQuestCompletion(i32),
                                       requiresBranch(bool/4B), requiredBranch(i32), description(str)
  MonolithTimeline_NonQuestZone_Fields: ...Zone + hasMaximumDepth(bool/4B), maximumDepth(i32)
  MonolithTimeline_Mod_Fields:        monsterMod(MonsterModRef=key(i32)), minimumDepth(i32),
                                       hasMaximumDepth(bool/4B), maximumDepth(i32)
  MonolithTimeline_ModDurationRequirement_Fields: duration(i32), requirement(i32)
  MonolithTimeline_ModEffectivenessFormula_Fields: depthThreshold(i32), baseModifier(f32),
                                                    modifierPerDepthAboveThreshold(f32)
"""

import json
import os
import sys

ROOT             = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DIR          = os.path.join(ROOT, "extracted_raw")
OUT_DIR          = os.path.join(ROOT, "exports_json")
TIMELINES_OUT    = os.path.join(OUT_DIR, "timelines.json")
BLESSINGS_OUT    = os.path.join(OUT_DIR, "blessings.json")
ITEMS_JSON       = os.path.join(OUT_DIR, "items.json")
CACHE_FILE       = os.path.join(RAW_DIR, "MonolithTimelines.json")
MANIFEST_FILE    = os.path.join(RAW_DIR, "resources_manifest.json")
RESOURCES_ASSETS = r"D:\SteamLibrary\steamapps\common\Last Epoch\Last Epoch_Data\resources.assets"

sys.path.insert(0, os.path.dirname(__file__))
from resources_reader import BinaryReader, monobehaviour_data_start


# ── Struct readers ─────────────────────────────────────────────────────────────

def read_completion(r: BinaryReader) -> dict:
    """MonolithTimeline_Completion: timelineID(u8/4B), completionType(u8/4B)"""
    return {
        "timelineID":     r.read_u8_aligned(),
        "completionType": r.read_u8_aligned(),
    }


def read_zone_base(r: BinaryReader) -> dict:
    """MonolithTimeline_Zone_Fields: sceneName(str), minimumDepth(i32)"""
    return {
        "sceneName":    r.read_string(),
        "minimumDepth": r.read_i32(),
    }


def read_quest_zone(r: BinaryReader) -> dict:
    """MonolithTimeline_QuestZone extends Zone_Fields"""
    rec = read_zone_base(r)
    rec["maximumChance"]      = r.read_f32r()
    rec["maximumChanceDepth"] = r.read_i32()
    # stabilityRequirements: int32[] (fixed array with count prefix)
    n = r.read_u32()
    rec["stabilityRequirements"] = [r.read_i32() for _ in range(n)]
    rec["requiredQuestCompletion"] = r.read_i32()
    rec["requiresBranch"]  = r.read_bool()
    rec["requiredBranch"]  = r.read_i32()
    rec["description"]     = r.read_string()
    return rec


def read_non_quest_zone(r: BinaryReader) -> dict:
    """MonolithTimeline_NonQuestZone extends Zone_Fields"""
    rec = read_zone_base(r)
    rec["hasMaximumDepth"] = r.read_bool()
    rec["maximumDepth"]    = r.read_i32()
    return rec


def read_mod(r: BinaryReader) -> dict:
    """MonolithTimeline_Mod: monsterModKey(i32), minimumDepth(i32),
       hasMaximumDepth(bool/4B), maximumDepth(i32)"""
    return {
        "monsterModKey":   r.read_i32(),   # MonsterModRef.key (MonsterMod* not serialized)
        "minimumDepth":    r.read_i32(),
        "hasMaximumDepth": r.read_bool(),
        "maximumDepth":    r.read_i32(),
    }


def read_mod_duration(r: BinaryReader) -> dict:
    """MonolithTimeline_ModDurationRequirement: duration(i32), requirement(i32)"""
    return {"duration": r.read_i32(), "requirement": r.read_i32()}


def read_mod_effectiveness(r: BinaryReader) -> dict:
    """MonolithTimeline_ModEffectivenessFormula"""
    return {
        "depthThreshold":                 r.read_i32(),
        "baseModifier":                   r.read_f32r(),
        "modifierPerDepthAboveThreshold": r.read_f32r(),
    }


def read_difficulty(r: BinaryReader) -> dict:
    """MonolithTimeline_Difficulty_Fields"""
    n_req = r.read_u32()
    requirements = [read_completion(r) for _ in range(n_req)]

    level              = r.read_i32()
    tutorialise        = r.read_bool()
    mod_effect         = r.read_f32r()
    echoes_lost        = r.read_f32r()
    max_stability      = r.read_i32()

    n_first = r.read_u32()
    first_slot_blessings = [r.read_i32() for _ in range(n_first)]
    n_other = r.read_u32()
    other_slot_blessings = [r.read_i32() for _ in range(n_other)]
    n_any = r.read_u32()
    any_slot_blessings   = [r.read_i32() for _ in range(n_any)]

    min_tier_tombs   = r.read_i32()
    has_corruption   = r.read_bool()
    corruption_key   = r.read_i32()   # MonsterModRef.key
    min_corruption   = r.read_i32()
    has_max_corrupt  = r.read_bool()
    max_corruption   = r.read_i32()
    add_corrupt_eff  = r.read_i32()
    corrupt_per_lvl  = r.read_i32()

    rec: dict = {
        "level":       level,
        "maxStability": max_stability,
        "firstSlotBlessings":  first_slot_blessings,
        "otherSlotBlessings":  other_slot_blessings,
        "anySlotBlessings":    any_slot_blessings,
        "minTierForTombsOfTheErased": min_tier_tombs,
    }
    if requirements:
        rec["sufficientRequirements"] = requirements
    if tutorialise:
        rec["tutorialise"] = True
    rec["modEffectModifier"]         = round(mod_effect, 4)
    rec["echoesLostOnDeathModifier"] = round(echoes_lost, 4)
    if has_corruption:
        rec["hasCorruptionMod"]    = True
        rec["corruptionModKey"]    = corruption_key
    rec["minimumCorruption"]       = min_corruption
    if has_max_corrupt:
        rec["hasMaxCorruption"]    = True
        rec["maximumCorruption"]   = max_corruption
    rec["additionalCorruptionEffect"] = add_corrupt_eff
    rec["corruptionRequiredPerLevel"] = corrupt_per_lvl
    return rec


def parse_timeline(raw: bytes, name: str) -> dict:
    """Parse one MonolithTimeline MonoBehaviour blob."""
    _, start = monobehaviour_data_start(raw)
    r = BinaryReader(raw)
    r.pos = start

    timeline_id  = r.read_u8_aligned()
    display_name = r.read_string()

    n_diff = r.read_u32()
    difficulties = [read_difficulty(r) for _ in range(n_diff)]

    rest_zone              = r.read_string()
    option_reroll_cost     = r.read_i32()
    option_reroll_per_dep  = r.read_i32()
    popup_delay            = r.read_f32r()
    r.read_pptr()  # timelineBossLoot (ScriptableObject PPtr, 12 bytes)

    n_eras = r.read_u32()
    eras = [r.read_i32() for _ in range(n_eras)]

    n_qz = r.read_u32()
    quest_zones = [read_quest_zone(r) for _ in range(n_qz)]

    n_nqz = r.read_u32()
    non_quest_zones = [read_non_quest_zone(r) for _ in range(n_nqz)]

    n_az = r.read_u32()
    arena_zones = [read_non_quest_zone(r) for _ in range(n_az)]

    n_eqz = r.read_u32()
    emp_non_quest = [read_non_quest_zone(r) for _ in range(n_eqz)]

    n_eaz = r.read_u32()
    emp_arena = [read_non_quest_zone(r) for _ in range(n_eaz)]

    n_mods = r.read_u32()
    mods = [read_mod(r) for _ in range(n_mods)]

    n_emp_mods = r.read_u32()
    emp_mods = [read_mod(r) for _ in range(n_emp_mods)]

    n_min_dur = r.read_u32()
    min_dur = [read_mod_duration(r) for _ in range(n_min_dur)]

    n_max_dur = r.read_u32()
    max_dur = [read_mod_duration(r) for _ in range(n_max_dur)]

    n_formulas = r.read_u32()
    formulas = [read_mod_effectiveness(r) for _ in range(n_formulas)]

    min_enemy_types   = r.read_i32()
    max_enemy_types   = r.read_i32()
    arena_enemy_types = r.read_i32()
    enemy_similarity  = r.read_f32r()
    enemy_density     = r.read_f32r()

    max_tier_non_shade = r.read_i32()
    min_tier_arena     = r.read_i32()
    min_tier_shade     = r.read_i32()
    min_tier_beacon    = r.read_i32()
    min_tier_voc       = r.read_i32()
    min_tier_vom       = r.read_i32()
    min_tier_treasure  = r.read_i32()
    min_tier_soul      = r.read_i32()
    min_tier_cemetery  = r.read_i32()

    w_normal   = r.read_f32r()
    w_arena    = r.read_f32r()
    w_beacon   = r.read_f32r()
    w_voc      = r.read_f32r()
    w_vom      = r.read_f32r()
    w_treasure = r.read_f32r()
    w_soul     = r.read_f32r()
    w_cemetery = r.read_f32r()

    shade_steepness  = r.read_f32r()
    shade_start      = r.read_f32r()
    extra_shade_cor  = r.read_i32()
    echoes_for_shade = r.read_i32()
    tier_shade_always = r.read_i32()

    exclusive_desc = r.read_string()

    remaining = r.remaining()

    rec: dict = {
        "name":        name,
        "timelineID":  timeline_id,
        "displayName": display_name or name,
        "difficulties": difficulties,
        "restZone":    rest_zone,
        "optionRerollCost":        option_reroll_cost,
        "optionRerollCostPerDepth": option_reroll_per_dep,
    }
    if quest_zones:
        rec["questZones"] = quest_zones
    if non_quest_zones:
        rec["nonQuestZones"] = non_quest_zones
    if arena_zones:
        rec["arenaZones"] = arena_zones
    if emp_non_quest:
        rec["empoweredNonQuestZones"] = emp_non_quest
    if emp_arena:
        rec["empoweredArenaZones"] = emp_arena
    if mods:
        rec["mods"] = mods
    if emp_mods:
        rec["empoweredMods"] = emp_mods
    rec["echoWeights"] = {
        "normal":   round(w_normal,   4),
        "arena":    round(w_arena,    4),
        "beacon":   round(w_beacon,   4),
        "vesselOfChaos":   round(w_voc,    4),
        "vesselOfMemory":  round(w_vom,    4),
        "treasureRoom":    round(w_treasure, 4),
        "soulSealedEcho":  round(w_soul,   4),
        "cemetery":        round(w_cemetery, 4),
    }
    rec["minTiers"] = {
        "arena": min_tier_arena, "shade": min_tier_shade,
        "beacon": min_tier_beacon, "vesselOfChaos": min_tier_voc,
        "vesselOfMemory": min_tier_vom, "treasureRoom": min_tier_treasure,
        "soulSealedEcho": min_tier_soul, "cemetery": min_tier_cemetery,
        "tombsOfTheErased": 0,  # stored per difficulty
    }
    if exclusive_desc:
        rec["exclusiveEchoRewardsDescription"] = exclusive_desc
    print(f"    Remaining bytes: {remaining}", flush=True)
    return rec


# ── Extract ───────────────────────────────────────────────────────────────────

def extract_timelines(manifest: dict) -> list:
    try:
        import UnityPy
    except ImportError:
        raise RuntimeError("pip install UnityPy")

    timeline_entries = manifest.get("MonolithTimeline", [])
    if not timeline_entries:
        raise RuntimeError("MonolithTimeline not found in resources_manifest.json")

    print("  Loading resources.assets …", flush=True)
    env = UnityPy.load(RESOURCES_ASSETS)
    sf  = list(env.files.values())[0]

    results = []
    for entry in timeline_entries:
        pid  = entry["pathId"]
        name = entry["name"]
        print(f"  Parsing '{name}' (pid={pid}) …", flush=True)
        raw = sf.objects[pid].get_raw_data()
        print(f"    Raw size: {len(raw):,} bytes", flush=True)
        rec = parse_timeline(raw, name)
        results.append(rec)

    return results


# ── Blessings from items.json ─────────────────────────────────────────────────

def build_blessings(items_path: str) -> list:
    """Extract the Blessing base type subtypes from items.json."""
    data = json.load(open(items_path, encoding="utf-8"))
    for base in data.get("equippable", []):
        if base.get("name") == "Blessing":
            return base.get("subTypes", [])
    return []


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(MANIFEST_FILE):
        raise FileNotFoundError(f"resources_manifest.json not found: {MANIFEST_FILE}")
    manifest = json.load(open(MANIFEST_FILE, encoding="utf-8"))

    if os.path.exists(CACHE_FILE):
        print("Loading cached MonolithTimelines.json …")
        timelines = json.load(open(CACHE_FILE, encoding="utf-8"))
    else:
        print("Extracting from resources.assets …")
        if not os.path.exists(RESOURCES_ASSETS):
            raise FileNotFoundError(f"resources.assets not found: {RESOURCES_ASSETS}")
        timelines = extract_timelines(manifest)
        json.dump(timelines, open(CACHE_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"  Cached to {CACHE_FILE}")

    # Write timelines.json
    out_timelines = {
        "_meta": {"count": len(timelines)},
        "timelines": timelines,
    }
    json.dump(out_timelines, open(TIMELINES_OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n✅ {len(timelines)} timelines → {TIMELINES_OUT}")

    # Write blessings.json from items.json
    if os.path.exists(ITEMS_JSON):
        blessings = build_blessings(ITEMS_JSON)
        out_blessings = {
            "_meta": {"count": len(blessings), "source": "items.json (Blessing base type)"},
            "blessings": blessings,
        }
        json.dump(out_blessings, open(BLESSINGS_OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"✅ {len(blessings)} blessings → {BLESSINGS_OUT}")
    else:
        print("⚠️  items.json not found — skipping blessings.json (run process_items.py first)")


if __name__ == "__main__":
    main()
