"""
process_skill_trees.py
======================
Cross-references community skill tree node data with our extracted skills.json,
producing:

  exports_json/skills_with_trees.json   — Each skill enriched with its tree nodes
  exports_json/passive_trees.json       — Class passive trees (all 5 classes)
  exports_json/unmatched_trees.json     — Community trees we couldn't link to a skill

Matching strategy (most → least precise):
  1. Exact: ability name (spaces stripped, lowercased) == skill name
  2. Stripped: remove class prefix words (Rogue, Warlock, Falconer, etc.)
  3. Suffix: strip trailing digits / numbers
  4. Token overlap: ≥2 matching tokens
"""

import os
import re
import json

ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TREES_FILE = os.path.join(ROOT, "exports_json", "community_skill_trees.json")
SKILLS_FILE= os.path.join(ROOT, "exports_json", "skills.json")
OUT_DIR    = os.path.join(ROOT, "exports_json")

CLASS_PREFIXES = r'^(rogue|mage|sentinel|primalist|acolyte|falconer|warlock|runemaster|spellblade|sorcerer|forgeguard|voidknight|paladin|beastmaster|shaman|druid|necromancer|bladedancer|marksman)\s*\d*\s*'
PASSIVE_IDS = {"pr-1", "mg-1", "rg-1", "ac-1", "kn-1"}  # class passive trees


def normalise(s: str) -> str:
    s = s.replace(" ", "").lower()
    s = re.sub(r'\d+$', '', s)   # strip trailing digits
    return s


def strip_prefix(s: str) -> str:
    return re.sub(CLASS_PREFIXES, '', s, flags=re.IGNORECASE).strip()


def tokens(s: str) -> set[str]:
    return set(re.split(r'(?=[A-Z])|[\s_\-]+', s)) - {'', 'the', 'of', 'a'}


def match_trees_to_skills(trees: list[dict], skills: list[dict]) -> tuple[dict, list, list]:
    """
    Returns:
      matched   : {skill_id: tree}
      passives  : [tree, ...]      — class passive trees
      unmatched : [tree, ...]
    """
    # Build lookup maps for our skills
    by_exact   = {normalise(s["name"]): s for s in skills}           # 'abyssalechoes' → skill
    by_id      = {s["id"]: s for s in skills}

    matched   : dict[str, dict] = {}   # skill_id → tree
    passives  : list[dict]      = []
    unmatched : list[dict]      = []

    for tree in trees:
        tree_id = tree["id"]
        ability = tree.get("ability", "")

        # Passive trees are always separated out
        if tree_id in PASSIVE_IDS:
            passives.append(tree)
            continue

        # --- Attempt 1: exact normalised match ---
        key = normalise(ability)
        skill = by_exact.get(key)

        # --- Attempt 2: strip class prefix ---
        if not skill:
            stripped = normalise(strip_prefix(ability))
            skill = by_exact.get(stripped)

        # --- Attempt 3: strip trailing numbers then try again ---
        if not skill:
            key2 = re.sub(r'\d', '', key)
            skill = by_exact.get(key2)

        # --- Attempt 4: token overlap (≥2 tokens, ignoring short/common ones) ---
        if not skill:
            STOP_TOKENS = {'summon', 'form', 'strike', 'the', 'and', 'for'}
            toks = {t.lower() for t in tokens(ability) if len(t) > 3 and t.lower() not in STOP_TOKENS}
            if len(toks) >= 2:
                best_score = 0
                best_skill = None
                for s in skills:
                    s_toks = {t.lower() for t in tokens(s["name"]) if len(t) > 3 and t.lower() not in STOP_TOKENS}
                    overlap = len(toks & s_toks)
                    if overlap >= 2 and overlap > best_score:
                        best_score = overlap
                        best_skill = s
                skill = best_skill

        if skill:
            sid = skill["id"]
            if sid not in matched:
                matched[sid] = tree
            else:
                # Already matched — keep the one whose ability is a closer string match
                existing_ability = matched[sid].get("ability", "")
                if len(ability) < len(existing_ability):
                    matched[sid] = tree
        else:
            unmatched.append(tree)

    return matched, passives, unmatched


def merge_skill_with_tree(skill: dict, tree: dict) -> dict:
    out = dict(skill)
    out["skillTree"] = {
        "sourceId":   tree["id"],
        "ability":    tree.get("ability", ""),
        "nodes":      tree["nodes"],
    }
    if tree.get("unlockableAbilities"):
        out["skillTree"]["unlockableAbilities"] = tree["unlockableAbilities"]
    return out


def build_passive_trees(passives: list[dict]) -> list[dict]:
    CLASS_MAP = {"pr-1": "Primalist", "mg-1": "Mage", "rg-1": "Rogue", "ac-1": "Acolyte", "kn-1": "Sentinel"}
    result = []
    for tree in passives:
        tree_id = tree["id"]
        entry = {
            "class":      CLASS_MAP.get(tree_id, tree_id),
            "treeId":     tree_id,
            "nodes":      tree["nodes"],
            "masteries":  tree.get("masteries", []),
        }
        if tree.get("unlockableAbilities"):
            entry["unlockableAbilities"] = tree["unlockableAbilities"]
        result.append(entry)
    return sorted(result, key=lambda x: x["class"])


def write(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    count = len(data) if isinstance(data, (list, dict)) else "?"
    print(f"  -> {os.path.relpath(path, ROOT)}  ({count})")


def main():
    print("Loading data...")
    trees_data = json.load(open(TREES_FILE, encoding="utf-8"))
    trees      = trees_data["skillTrees"]
    skills_data= json.load(open(SKILLS_FILE, encoding="utf-8"))
    skills     = skills_data["skills"]

    skill_trees = [t for t in trees if t["id"] not in PASSIVE_IDS]
    print(f"  {len(skills)} skills, {len(skill_trees)} community skill trees, {len(PASSIVE_IDS)} passive trees")

    print("\nMatching trees to skills...")
    matched, passives, unmatched = match_trees_to_skills(trees, skills)
    print(f"  Matched:   {len(matched)}/{len(skill_trees)} trees -> skills")
    print(f"  Passives:  {len(passives)}")
    print(f"  Unmatched: {len(unmatched)}")

    # Build skills_with_trees — ALL skills, enriched where possible
    print("\nBuilding skills_with_trees.json...")
    enriched_skills = []
    enriched_count = 0
    for skill in skills:
        sid = skill["id"]
        tree = matched.get(sid)
        if tree:
            enriched_skills.append(merge_skill_with_tree(skill, tree))
            enriched_count += 1
        else:
            out = dict(skill)
            out["skillTree"] = None
            enriched_skills.append(out)

    result = {
        "meta": {
            **skills_data.get("meta", {}),
            "skillTreeSource": "https://github.com/prowner/last-epoch-data",
            "skillsWithTree":  enriched_count,
            "skillsWithoutTree": len(skills) - enriched_count,
        },
        "skills": enriched_skills,
    }
    write(os.path.join(OUT_DIR, "skills_with_trees.json"), result)

    # Build passive_trees.json
    print("\nBuilding passive_trees.json...")
    passive_result = {
        "meta": {
            "source": "https://github.com/prowner/last-epoch-data",
            "note": "Class passive trees. May not reflect current patch.",
            "classCount": len(passives),
        },
        "passiveTrees": build_passive_trees(passives),
    }
    write(os.path.join(OUT_DIR, "passive_trees.json"), passive_result)

    # Write unmatched for reference
    print("\nWriting unmatched_trees.json...")
    write(
        os.path.join(OUT_DIR, "unmatched_trees.json"),
        [{"id": t["id"], "ability": t.get("ability"), "nodeCount": len(t["nodes"])} for t in unmatched]
    )

    print("\nMatched trees:")
    for sid, tree in sorted(matched.items(), key=lambda x: x[1].get("ability","")):
        skill_name = next(s["name"] for s in skills if s["id"] == sid)
        print(f"  {tree['ability']:40s} -> {skill_name}")

    print("\nUnmatched community trees (no skill found):")
    for t in unmatched:
        print(f"  {t['id']:12s}  {t.get('ability','')}")

    print(f"\nDone. {enriched_count}/{len(skills)} skills enriched with tree nodes.")


if __name__ == "__main__":
    main()
