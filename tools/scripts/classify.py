"""
classify.py
===========
Scans all exported MonoBehaviour JSON files across all raw_bundles subfolders,
detects their data type by field signature, and writes a manifest.json that maps
every file path to its detected type and key identifiers.

Output: extracted_raw/manifest.json

Run this first before any process_*.py script.
"""

import os
import json
from collections import defaultdict

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUNDLES_DIR = os.path.join(ROOT, "extracted_raw", "raw_bundles")
OUT_FILE    = os.path.join(ROOT, "extracted_raw", "manifest.json")


# ── type detection rules ───────────────────────────────────────────────────────
# Each rule: (type_name, required_fields, excluded_fields)
# First matching rule wins.
TYPE_RULES: list[tuple[str, set, set]] = [
    # ── skip runtime-only objects ──────────────────────────────────────────────
    ("runtime_component",   {"shouldBeDestoyedAfterUpdate", "autoPool", "getFromParent"}, set()),
    ("runtime_sync",        {"syncCreator", "locationCreatedFrom", "oType", "useType"},   set()),
    ("runtime_movement",    {"reachedTargetLocation", "startLocation", "targetLocationOffset"}, set()),
    ("runtime_age",         {"ageResets", "expireNextUpdate"},                             set()),
    ("runtime_vfx",         {"animatorChanges", "childrenWithParticleSystems", "keepLightsEnabled"}, set()),
    ("runtime_damage",      {"canDamageSameEnemyAgain", "baseDamageStats", "damageTags"}, set()),
    ("runtime_mover",       {"acceleration", "accelerationDelay", "maxSpeed"},             set()),
    ("runtime_audio",       {"AllowFadeout", "Event", "OverrideAttenuation"},              set()),
    ("runtime_sync2",       {"SyncType", "constantRotation", "creationReferences", "faceVelocityDirection"}, set()),

    # ── MTX cosmetics ─────────────────────────────────────────────────────────
    ("mtx_cosmetic",        {"BackendID", "StoreSprite", "BorderlessShopIconInstead"},     set()),
    ("mtx_skill",           {"BackendID", "AbilityRef", "EquipSlot", "Class"},             set()),
    ("mtx_pet",             {"BackendID", "IsFlying", "Key"},                              set()),

    # ── core gameplay data ─────────────────────────────────────────────────────
    ("skill",               {"playerAbilityID", "abilityName", "manaCost"},                set()),
    ("class",               {"classID", "className", "treeID"},                            set()),
    ("ailment",             {"duration", "maxInstances", "showsInBuffUI"},                  set()),
    ("buff",                {"duration", "maxInstances", "positive"},                       set()),
    ("loot_table",          {"lootGroups"},                                                 set()),
    ("passive_node",        {"passiveId"},                                                  set()),
    ("passive_tree",        {"passiveNodes", "startingNode"},                               set()),
    ("skill_tree_node",     {"nodeID", "nodeUnlockRequirements"},                           set()),
    ("affix",               {"affixId"},                                                    set()),
    ("base_item",           {"levelRequirement", "implicitMods"},                           set()),
    ("unique_item",         {"uniqueID", "legendaryType"},                                  set()),
    ("unique_item2",        {"lp_"},                                                        set()),  # LP uniques naming
    ("enemy_actor",         {"actorName", "baseHealth", "baseArmor"},                      set()),
    ("waypoint",            {"waypointID", "sceneName"},                                    set()),
    ("blessing",            {"blessingID"},                                                  set()),
    ("faction",             {"factionID", "reputationThresholds"},                          set()),
    ("ability_visual",      {"Entries"},                                                    set()),
    ("vfx_limiter",         {"_limiterType", "_light"},                                    set()),
    ("wave_spawner",        {"waves", "wavesSpawned", "waveCondition"},                    set()),
    ("drop_rate",           {"baseDropRates", "dropFlags"},                                 set()),
    ("spawner_data",        {"timelinesToEmpower", "difficultyToUnlock"},                  set()),
]


def detect_type(data: dict) -> str:
    """Return the detected type string for a MonoBehaviour data dict."""
    keys = set(data.keys())
    for type_name, required, excluded in TYPE_RULES:
        if required.issubset(keys) and not excluded.intersection(keys):
            return type_name
    return "unknown"


def get_identifier(data: dict, detected_type: str) -> str:
    """Return the primary identifier value for a typed record."""
    id_fields = {
        "skill":        "playerAbilityID",
        "class":        "classID",
        "ailment":      "id",
        "buff":         "id",
        "passive_node": "passiveId",
        "affix":        "affixId",
        "unique_item":  "uniqueID",
        "blessing":     "blessingID",
        "faction":      "factionID",
        "waypoint":     "waypointID",
    }
    field = id_fields.get(detected_type)
    if field and field in data:
        return str(data[field])
    return data.get("m_Name", "")


def scan_bundle(bundle_path: str) -> list[dict]:
    """Scan a single bundle folder (MonoBehaviour subfolder) and classify all files."""
    results = []
    mono_dir = os.path.join(bundle_path, "MonoBehaviour")
    if not os.path.isdir(mono_dir):
        return results

    bundle_name = os.path.basename(bundle_path)

    for fname in sorted(os.listdir(mono_dir)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(mono_dir, fname)
        rel_path = os.path.relpath(fpath, ROOT)

        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            results.append({
                "file":   rel_path,
                "bundle": bundle_name,
                "name":   fname,
                "type":   "parse_error",
                "id":     "",
                "error":  str(e),
            })
            continue

        detected = detect_type(data)
        identifier = get_identifier(data, detected)

        results.append({
            "file":   rel_path,
            "bundle": bundle_name,
            "name":   data.get("m_Name", fname.replace(".json", "")),
            "type":   detected,
            "id":     identifier,
        })

    return results


def main():
    if not os.path.isdir(BUNDLES_DIR):
        print(f"[ERROR] raw_bundles directory not found: {BUNDLES_DIR}")
        print("        Run AssetStudio exports first.")
        return

    all_records: list[dict] = []
    type_counts: dict[str, int] = defaultdict(int)

    bundle_dirs = sorted([
        os.path.join(BUNDLES_DIR, d)
        for d in os.listdir(BUNDLES_DIR)
        if os.path.isdir(os.path.join(BUNDLES_DIR, d))
    ])

    for bundle_path in bundle_dirs:
        bundle_name = os.path.basename(bundle_path)
        records = scan_bundle(bundle_path)
        all_records.extend(records)
        for r in records:
            type_counts[r["type"]] += 1
        print(f"  {bundle_name}: {len(records)} files")

    # Build output
    output = {
        "meta": {
            "total_files":  len(all_records),
            "type_counts":  dict(sorted(type_counts.items(), key=lambda x: -x[1])),
            "bundles":      [os.path.basename(b) for b in bundle_dirs],
        },
        "files": all_records,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Manifest written: {OUT_FILE}")
    print(f"   Total files: {len(all_records)}")
    print("\n📊 Type breakdown:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"   {str(c).rjust(5)}  {t}")


if __name__ == "__main__":
    main()
