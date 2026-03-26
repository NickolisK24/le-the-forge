"""
extract_enums.py
================
Parses all LE*.dll DummyDll assemblies from Il2CppDumper output and extracts
every enum type with its members and integer values.

Output: extracted_raw/enums/enums.json

Requirements:
    pip install pythonnet
    (Mono.Cecil.dll must exist in tools/AssestStudio/)
"""

import os
import json
import sys

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DUMMY_DIR   = os.path.join(ROOT, "il2cpp_dump", "DummyDll")
CECIL_DIR   = os.path.join(ROOT, "tools", "AssestStudio")
OUT_DIR     = os.path.join(ROOT, "extracted_raw", "enums")
OUT_FILE    = os.path.join(OUT_DIR, "enums.json")

# DLLs that contain game-specific types — parse all of them
LE_DLLS = [
    "LE.dll",
    "LE.Core.dll",
    "LE.PCG.dll",
    "LE.Networking.Core.dll",
    "LE.UI.Controls.dll",
    "LE.Telemetry.dll",
    "LE.Telemetry.Client.dll",
    "Generated.dll",
    "NewAssembly.dll",
]

# High-priority enums for the pipeline (actual names from LE.dll)
PRIORITY_ENUMS = {
    # Core gameplay
    "SP",                       # Stat properties (125 values)
    "AT",                       # Ability/skill tags (30 values)
    "DamageType",               # Damage types (7 values)
    "EquipmentType",            # Equipment slots (40 values)
    "AilmentID",                # All ailments (138 values)
    "AbilityID",                # All abilities/skills (881 values)
    # Classes
    "CharacterClassID",         # Class IDs (was ClassRequirement in plan)
    "BazaarItemClassRequirement",
    "BazaarItemSubClassRequirement",
    # Items
    "NonEquipmentType",         # Non-equippable item types
    "BazaarItemType",           # Item type for trade
    "WearableSlots",            # Equipment slot flags
    "SealedAffixType",          # Affix type (was AffixType in plan)
    "AffixKey",                 # Affix identifier
    "ItemModFlags",             # Item modification flags
    "BazaarItemRarity",         # Item rarity
    # Status / buffs
    "StatusEffectID",           # All status effect IDs
    "NonAilmentUIBuffID",       # Non-ailment buffs shown in UI
    # Factions / progression
    "FactionID",                # Faction IDs (was FactionType in plan)
    "DungeonID",                # Dungeon identifiers
    "TimelineID",               # Timeline/zone IDs
    "MonolithObjectiveType",    # Monolith objectives
    "EchoRewardSource",         # Echo reward types
    # Cosmetics / misc
    "CosmeticType",
    "QuestType",
    "QuestState",
    # Weapon / damage classification
    "Weapon",                   # Weapon types (was WeaponType in plan)
    "WeaponEffect",
    "ResistanceStatType",
    "CritType",
    # Blessings / woven echoes
    "WovenEchoType",
    "WovenEchoContentType",
}


def setup_cecil():
    """Load Mono.Cecil via pythonnet and return the AssemblyDefinition type."""
    try:
        import pythonnet
        pythonnet.load("coreclr")
    except Exception as exc:
        print(f"[ERROR] Could not load coreclr runtime: {exc}")
        print("        Ensure pythonnet is installed: pip install pythonnet")
        sys.exit(1)

    import clr
    sys.path.insert(0, CECIL_DIR)
    try:
        clr.AddReference("Mono.Cecil")
    except Exception as exc:
        print(f"[ERROR] Could not load Mono.Cecil from {CECIL_DIR}: {exc}")
        sys.exit(1)

    from Mono.Cecil import AssemblyDefinition
    return AssemblyDefinition


def extract_enums_from_dll(dll_path: str, AssemblyDefinition) -> list[dict]:
    """
    Open a .NET assembly with Mono.Cecil and return a list of enum descriptors:
        {
            "namespace": str,
            "name": str,
            "fullName": str,
            "source": str,
            "priority": bool,
            "values": {str: int, ...}
        }
    """
    dll_name = os.path.basename(dll_path)
    results = []

    try:
        asm = AssemblyDefinition.ReadAssembly(dll_path)
    except Exception as exc:
        print(f"  [WARN] Could not open {dll_name}: {exc}")
        return results

    for type_def in asm.MainModule.Types:
        if not type_def.IsEnum:
            continue

        type_name = str(type_def.Name)
        type_ns   = str(type_def.Namespace) if type_def.Namespace else ""
        full_name = f"{type_ns}.{type_name}" if type_ns else type_name

        # Collect enum fields — skip the backing "value__" field
        values: dict[str, int] = {}
        for field in type_def.Fields:
            fname = str(field.Name)
            if fname == "value__":
                continue
            if field.HasConstant and field.Constant is not None:
                try:
                    values[fname] = int(field.Constant)
                except Exception:
                    values[fname] = str(field.Constant)

        results.append({
            "namespace": type_ns,
            "name":      type_name,
            "fullName":  full_name,
            "source":    dll_name,
            "priority":  type_name in PRIORITY_ENUMS,
            "values":    values,
        })

    return results


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Loading Mono.Cecil...")
    AssemblyDefinition = setup_cecil()
    print("Ready.\n")

    all_enums: list[dict] = []
    found_dlls = []

    for dll_name in LE_DLLS:
        dll_path = os.path.join(DUMMY_DIR, dll_name)
        if not os.path.exists(dll_path):
            print(f"  [SKIP] {dll_name} not found")
            continue

        found_dlls.append(dll_name)
        print(f"  Parsing {dll_name} ...", end="", flush=True)
        enums = extract_enums_from_dll(dll_path, AssemblyDefinition)
        all_enums.extend(enums)
        print(f" → {len(enums)} enums")

    # Sort: priority enums first, then alphabetically by fullName
    all_enums.sort(key=lambda e: (not e["priority"], e["fullName"].lower()))

    output = {
        "meta": {
            "source_dlls":          found_dlls,
            "total_enums":          len(all_enums),
            "priority_enums_found": [e["name"] for e in all_enums if e["priority"]],
        },
        "enums": all_enums,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done — {len(all_enums)} enums written to:\n   {OUT_FILE}")

    priority_found = [e for e in all_enums if e["priority"]]
    if priority_found:
        print(f"\n⭐ Priority enums captured ({len(priority_found)}):")
        for e in priority_found:
            print(f"   {e['fullName']} ({len(e['values'])} values)")
    else:
        print("\n⚠️  No priority enums found — check DLL paths or enum names.")

    found_names = {e["name"] for e in all_enums}
    missing = PRIORITY_ENUMS - found_names
    if missing:
        print(f"\n⚠️  Priority enums NOT found (may be named differently):")
        for m in sorted(missing):
            print(f"   {m}")


if __name__ == "__main__":
    main()
