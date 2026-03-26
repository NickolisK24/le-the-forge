"""
process_ailments.py
===================
Reads all ailment/buff MonoBehaviour JSON files and writes ailments.json.

Output: exports_json/ailments.json

Requirements:
    - Run classify.py first
    - extracted_raw/enums/enums.json (for AilmentID and AT enum decoding)
"""

import os
import json

ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MANIFEST   = os.path.join(ROOT, "extracted_raw", "manifest.json")
ENUMS_FILE = os.path.join(ROOT, "extracted_raw", "enums", "enums.json")
OUT_DIR    = os.path.join(ROOT, "exports_json")
OUT_FILE   = os.path.join(OUT_DIR, "ailments.json")


def load_enum(enums_data: list, name: str) -> dict:
    for e in enums_data:
        if e["name"] == name:
            return {int(v): k for k, v in e["values"].items() if isinstance(v, int)}
    return {}


def process_ailment(data: dict, ailment_id_map: dict) -> dict:
    raw_id  = data.get("id", 0)
    name    = ailment_id_map.get(raw_id, "") or data.get("displayName") or data.get("m_Name", "")
    return {
        "id":           raw_id,
        "name":         name,
        "displayName":  data.get("displayName", ""),
        "instanceName": data.get("instanceName", ""),
        "duration":     data.get("duration", 0.0),
        "maxInstances": data.get("maxInstances", 0),
        "positive":     bool(data.get("positive", 0)),
        "showsInBuffUI": bool(data.get("showsInBuffUI", 0)),
        "tags":         data.get("tags", 0),
        "applyPrefix":  bool(data.get("applyPrefix", 0)),
        "perStackDisplay": data.get("perStackDisplay", ""),
        "modifyingStatDisplay": data.get("modifyingStatDisplay", ""),
        "withAilmentStatDisplay": data.get("withAilmentStatDisplay", ""),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(MANIFEST):
        print("[ERROR] manifest.json not found. Run classify.py first.")
        return
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)

    ailment_id_map = {}
    if os.path.exists(ENUMS_FILE):
        enums_data = json.load(open(ENUMS_FILE, encoding="utf-8"))["enums"]
        ailment_id_map = load_enum(enums_data, "AilmentID")
        print(f"  AilmentID enum loaded: {len(ailment_id_map)} values")

    ailment_files = [r for r in manifest["files"] if r["type"] in ("ailment", "buff")]
    print(f"  Ailment/buff files found: {len(ailment_files)}")

    ailments = []
    for record in ailment_files:
        fpath = os.path.join(ROOT, record["file"])
        try:
            data = json.load(open(fpath, encoding="utf-8"))
            ailments.append(process_ailment(data, ailment_id_map))
        except Exception as e:
            print(f"  [WARN] {record['file']}: {e}")

    ailments.sort(key=lambda a: a["name"].lower())

    output = {"meta": {"total": len(ailments)}, "ailments": ailments}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done — {len(ailments)} ailments written to:\n   {OUT_FILE}")


if __name__ == "__main__":
    main()
