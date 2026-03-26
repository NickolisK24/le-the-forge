"""
process_skills.py
=================
Reads all skill/ability MonoBehaviour JSON files from raw_bundles,
decodes bitmask tags using the extracted enums, and writes skills.json.

Output: exports_json/skills.json

Requirements:
    - Run classify.py first (uses manifest.json to find skill files)
    - extracted_raw/enums/enums.json must exist (from extract_enums.py)
"""

import os
import json

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MANIFEST    = os.path.join(ROOT, "extracted_raw", "manifest.json")
ENUMS_FILE  = os.path.join(ROOT, "extracted_raw", "enums", "enums.json")
OUT_DIR     = os.path.join(ROOT, "exports_json")
OUT_FILE    = os.path.join(OUT_DIR, "skills.json")


def load_enum(enums_data: list[dict], name: str) -> dict[int, str]:
    """Return a value→name dict for the named enum."""
    for e in enums_data:
        if e["name"] == name:
            return {int(v): k for k, v in e["values"].items() if isinstance(v, int)}
    return {}


def decode_bitmask(value: int, enum_map: dict[int, str]) -> list[str]:
    """Decode an integer bitmask into a list of enum member names."""
    if not value:
        return []
    result = []
    for bit_val in sorted(enum_map.keys()):
        if bit_val > 0 and (value & bit_val) == bit_val:
            result.append(enum_map[bit_val])
    return result


def decode_attribute_scaling(entries: list) -> list[dict]:
    """
    Parse the attributeScaling array.
    Each entry: {attribute: int, stats: [{property, specialTag, tags, addedValue, increasedValue, moreValues}]}
    attribute: 0=Str, 1=Dex, 2=Int, 3=Att, 4=Vit
    """
    attr_names = {0: "Strength", 1: "Dexterity", 2: "Intelligence", 3: "Attunement", 4: "Vitality"}
    result = []
    for entry in (entries or []):
        attr = entry.get("attribute", -1)
        stats = entry.get("stats", [])
        if not stats:
            continue
        result.append({
            "attribute": attr_names.get(attr, f"attr_{attr}"),
            "stats": [
                {
                    "property":     s.get("property", 0),
                    "addedValue":   s.get("addedValue", 0.0),
                    "increasedValue": s.get("increasedValue", 0.0),
                    "moreValues":   s.get("moreValues", []),
                    "tags":         s.get("tags", 0),
                    "specialTag":   s.get("specialTag", 0),
                }
                for s in stats
            ],
        })
    return result


def process_skill(data: dict, at_map: dict, ability_id_map: dict) -> dict:
    """Convert a raw ability MonoBehaviour dict into a clean skill record."""
    name = data.get("abilityName") or data.get("m_Name", "")
    pid  = data.get("playerAbilityID", "")

    tags_raw      = data.get("tags", 0)
    fake_tags_raw = data.get("fakeTags", 0)
    conv_tags_raw = data.get("skillTreeConversionDamageTags", 0)

    tags_decoded      = decode_bitmask(tags_raw,      at_map)
    conv_tags_decoded = decode_bitmask(conv_tags_raw, at_map)

    # Shared cooldown ability refs (PathID based — names only if we can map them)
    shared_cd_ids = []
    for ref in data.get("sharedCooldownAbilities", []):
        pid_ref = ref.get("m_PathID", 0)
        if pid_ref and pid_ref != 0:
            shared_cd_ids.append(str(pid_ref))

    return {
        # ── identity ───────────────────────────────────────────────────────────
        "id":           pid,
        "name":         name,
        "description":  data.get("description", ""),
        "lore":         data.get("skillLore", ""),
        "altText":      data.get("altText", ""),

        # ── tags ───────────────────────────────────────────────────────────────
        "tags":               tags_raw,
        "tagsDecoded":        tags_decoded,
        "fakeTags":           fake_tags_raw,
        "conversionDamageTagsDecoded": conv_tags_decoded,

        # ── costs ──────────────────────────────────────────────────────────────
        "manaCost":           data.get("manaCost", 0.0),
        "minimumManaCost":    data.get("minimumManaCost", 0.0),
        "manaCostPerDistance": data.get("manaCostPerDistance", 0.0),
        "freeWhenOutOfMana":  bool(data.get("freeWhenOutOfMana", 0)),
        "channelCost":        data.get("channelCost", 0.0),

        # ── timing ─────────────────────────────────────────────────────────────
        "useDelay":           data.get("useDelay", 0.0),
        "useDuration":        data.get("useDuration", 0.0),
        "minimumUseDuration": data.get("minimumUseDuration", 0.0),
        "channelTimeLimit":   data.get("channelTimeLimit", 0.0),

        # ── charges ────────────────────────────────────────────────────────────
        "maxCharges":         data.get("maxCharges", 0.0),
        "chargesPerSecond":   data.get("chargesGainedPerSecond", 0.0),

        # ── cooldown ───────────────────────────────────────────────────────────
        "sharedCooldown":           bool(data.get("sharedCooldown", 0)),
        "sharedCooldownCanBeMutated": bool(data.get("sharedCooldownCanBeMutated", 0)),
        "sharedCooldownAbilityRefs": shared_cd_ids,
        "cannotResetCooldown":      bool(data.get("cannotResetCooldown", 0)),

        # ── flags ──────────────────────────────────────────────────────────────
        "channelled":         bool(data.get("channelled", 0)),
        "isZoneAbility":      bool(data.get("isZoneAbility", 0)),
        "traversalSkill":     bool(data.get("traversalSkill", 0)),
        "evadeSkill":         bool(data.get("evadeSkill", 0)),
        "countsAsMovement":   bool(data.get("countsAsMovementAbility", 0)),
        "isTransform":        bool(data.get("isTransform", 0)),
        "comboAbility":       bool(data.get("comboAbility", 0)),
        "instantCast":        bool(data.get("instantCastForPlayer", 0)),
        "stunImmuneDuringUse": bool(data.get("stunImmuneDuringUse", 0)),
        "overridePrimary":    bool(data.get("overridePrimaryAbility", 0)),
        "minionsUseAbility":  bool(data.get("minionsUseAbility", 0)),

        # ── requirements ───────────────────────────────────────────────────────
        "requireWeaponType":  bool(data.get("requireWeaponType", 0)),
        "permittedWeaponTypes": data.get("permittedWeaponTypes", []),
        "requiresShield":     bool(data.get("requiresSheild", 0)),
        "requiresDualWield":  bool(data.get("requiresDualWielding", 0)),

        # ── targeting ──────────────────────────────────────────────────────────
        "maxTargetDistance":  data.get("maxTargetDistance", 0.0),
        "stopRange":          data.get("stopRange", 0.0),
        "rangeLimitForPlayers": data.get("rangeLimitForPlayers", 0.0),
        "targetsAllies":      bool(data.get("targetsAllies", 0)),
        "targetsSelfOnly":    bool(data.get("targetsSelfOnly", 0)),
        "onlyTargetMinions":  bool(data.get("onlyTargetMinions", 0)),

        # ── movement ───────────────────────────────────────────────────────────
        "movementDuringUse":  bool(data.get("movementDuringUse", 0)),
        "baseMovementDuration": data.get("baseMovementDuration", 0.0),
        "dashDistance":       data.get("fixedDistanceDashDistance", 0.0),

        # ── scaling ────────────────────────────────────────────────────────────
        "attributeScaling":   decode_attribute_scaling(data.get("attributeScaling", [])),
        "levelScaling":       data.get("levelScaling", []),

        # ── speed ──────────────────────────────────────────────────────────────
        "speedScaler":        data.get("speedScaler", 0),
        "speedMultiplier":    data.get("speedMultiplier", 1.0),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load manifest
    if not os.path.exists(MANIFEST):
        print(f"[ERROR] manifest.json not found. Run classify.py first.")
        return
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)

    # Load enums
    at_map = {}
    ability_id_map = {}
    if os.path.exists(ENUMS_FILE):
        with open(ENUMS_FILE, encoding="utf-8") as f:
            enums_data = json.load(f)["enums"]
        at_map         = load_enum(enums_data, "AT")
        ability_id_map = load_enum(enums_data, "AbilityID")
        print(f"  Enums loaded: AT ({len(at_map)} values), AbilityID ({len(ability_id_map)} values)")
    else:
        print("  [WARN] enums.json not found — tags will not be decoded")

    # Find all skill files
    skill_files = [r for r in manifest["files"] if r["type"] == "skill"]
    print(f"  Skills found in manifest: {len(skill_files)}")

    skills_by_id: dict[str, tuple[dict, dict]] = {}  # id → (skill, raw_data)
    errors = []

    for record in skill_files:
        fpath = os.path.join(ROOT, record["file"])
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            skill = process_skill(data, at_map, ability_id_map)
            sid = skill["id"]
            m_name = data.get("m_Name", "")
            ability_name = data.get("abilityName", "")

            if sid not in skills_by_id:
                skills_by_id[sid] = (skill, m_name, ability_name)
            else:
                # Prefer the file where m_Name == abilityName (canonical MonoBehaviour)
                _, existing_m, existing_ab = skills_by_id[sid]
                current_is_canonical  = (m_name == ability_name)
                existing_is_canonical = (existing_m == existing_ab)
                if current_is_canonical and not existing_is_canonical:
                    skills_by_id[sid] = (skill, m_name, ability_name)
                elif not existing_is_canonical and not current_is_canonical:
                    # Both non-canonical — keep shorter m_Name (less likely to be a sub-ability)
                    if len(m_name) < len(existing_m):
                        skills_by_id[sid] = (skill, m_name, ability_name)
        except Exception as e:
            errors.append({"file": record["file"], "error": str(e)})

    skills = [entry[0] for entry in skills_by_id.values()]

    # Sort by name
    skills.sort(key=lambda s: s["name"].lower())

    output = {
        "meta": {
            "total":  len(skills),
            "rawFiles": len(skill_files),
            "deduplicated": len(skill_files) - len(skills),
            "errors": len(errors),
        },
        "skills": skills,
    }
    if errors:
        output["errors"] = errors

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done — {len(skills)} skills written to:\n   {OUT_FILE}")
    if errors:
        print(f"   ⚠️  {len(errors)} files had errors")


if __name__ == "__main__":
    main()
