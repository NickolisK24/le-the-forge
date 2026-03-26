"""
process_classes.py
==================
Reads all class MonoBehaviour JSON files and writes classes.json.

Output: exports_json/classes.json

Requirements:
    - Run classify.py first
"""

import os
import json

ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MANIFEST   = os.path.join(ROOT, "extracted_raw", "manifest.json")
OUT_DIR    = os.path.join(ROOT, "exports_json")
OUT_FILE   = os.path.join(OUT_DIR, "classes.json")

# Mage's MonoBehaviour asset fails to deserialize in AssetStudio (one of the
# "failed to read" assets). All values confirmed from CharacterClassID enum
# (classID=1), passive_trees.json (treeID="mg-1"), and game knowledge.
# Masteries: Mage (base), Sorcerer, Spellblade, Runemaster.
KNOWN_FALLBACKS = {
    "Mage": {
        "classID": 1,
        "className": "Mage",
        "treeID": "mg-1",
        "baseHealth": 100,
        "baseMana": 50,
        "hideThirdMasterySkillsInPanel": 0,
        "specialTagForClassSpecificLevelOfSkillsStats": 3,
        "healthBarHeightOffset": 0.0,
        "masteries": [
            {"name": "Mage",       "localizationKey": "Class_Mage"},
            {"name": "Sorcerer",   "localizationKey": "Mastery_Sorcerer"},
            {"name": "Spellblade", "localizationKey": "Mastery_Spellblade"},
            {"name": "Runemaster", "localizationKey": "Mastery_Runemaster"},
        ],
        "_fallback": True,
    },
}


def process_class(data: dict) -> dict:
    masteries = []
    for m in data.get("masteries", []):
        if isinstance(m, dict):
            masteries.append({
                "name": m.get("name", ""),
                "localizationKey": m.get("localizationKey", ""),
            })
    result = {
        "id":            data.get("classID", ""),
        "name":          data.get("className") or data.get("m_Name", ""),
        "treeID":        data.get("treeID", ""),
        "baseHealth":    data.get("baseHealth", 0),
        "baseMana":      data.get("baseMana", 0),
        "hideThirdMasterySkillsInPanel": bool(data.get("hideThirdMasterySkillsInPanel", 0)),
        "specialTagForClassSpecificStats": data.get("specialTagForClassSpecificLevelOfSkillsStats", 0),
        "healthBarHeightOffset": data.get("healthBarHeightOffset", 0.0),
        "masteries":     masteries,
    }
    if data.get("_fallback"):
        result["_fallback"] = True
    return result


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(MANIFEST):
        print("[ERROR] manifest.json not found. Run classify.py first.")
        return
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)

    class_files = [r for r in manifest["files"] if r["type"] == "class"]
    print(f"  Classes found in manifest: {len(class_files)}")

    classes = []
    for record in class_files:
        fpath = os.path.join(ROOT, record["file"])
        try:
            data = json.load(open(fpath, encoding="utf-8"))
            classes.append(process_class(data))
        except Exception as e:
            print(f"  [WARN] {record['file']}: {e}")

    # Inject known fallbacks for any class missing from extracted assets
    extracted_names = {c["name"] for c in classes}
    for name, fallback_data in KNOWN_FALLBACKS.items():
        if name not in extracted_names:
            classes.append(process_class(fallback_data))
            print(f"  [FALLBACK] Injected {name} (asset not extractable from AssetStudio)")

    classes.sort(key=lambda c: c["name"])

    output = {"meta": {"total": len(classes)}, "classes": classes}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done — {len(classes)} classes written to:\n   {OUT_FILE}")


if __name__ == "__main__":
    main()
