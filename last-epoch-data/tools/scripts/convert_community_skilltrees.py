"""
convert_community_skilltrees.py
================================
Downloads and converts the community datamined skillTrees.ts from
  https://github.com/prowner/last-epoch-data
into our standard JSON format.

The TypeScript file is essentially a large object literal — we strip the
type declarations and export statement then evaluate it with a JS-compatible
JSON parser (demarshalling via regex + json5 or a custom transformer).

Output: exports_json/community_skill_trees.json
"""

import os
import re
import json

ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TS_FILE  = os.path.join(ROOT, "extracted_raw", "community_skilltrees.ts")
OUT_FILE = os.path.join(ROOT, "exports_json", "community_skill_trees.json")


def ts_to_json_text(raw: str) -> str:
    """Transform TypeScript object literal to valid JSON."""

    # 1. Remove everything before 'export const skillTrees: ... = {'
    match = re.search(r'export const skillTrees\s*:\s*\{[^}]+\}\s*=\s*\{', raw)
    if not match:
        raise ValueError("Could not find 'export const skillTrees' declaration")
    start = match.end() - 1  # include the opening {
    raw = raw[start:]

    # 2. Remove trailing semicolon and whitespace
    raw = raw.rstrip()
    if raw.endswith(';'):
        raw = raw[:-1].rstrip()

    # 3. Remove TypeScript type casts (e.g., `as SomeType`)
    raw = re.sub(r'\s+as\s+\w+', '', raw)

    # 4. Convert single-quoted strings to double-quoted
    # Handle escaped quotes inside: ' -> "  but preserve \' -> \'
    def fix_quotes(text):
        result = []
        i = 0
        in_string = False
        string_char = None
        while i < len(text):
            c = text[i]
            if not in_string:
                if c == '"':
                    in_string = True
                    string_char = '"'
                    result.append(c)
                elif c == "'":
                    in_string = True
                    string_char = "'"
                    result.append('"')
                else:
                    result.append(c)
            else:
                if c == '\\' and i + 1 < len(text):
                    next_c = text[i + 1]
                    if string_char == "'" and next_c == "'":
                        result.append("\\'")
                        i += 2
                        continue
                    else:
                        result.append(c)
                        result.append(next_c)
                        i += 2
                        continue
                elif c == string_char:
                    in_string = False
                    result.append('"')
                else:
                    # Escape unescaped double quotes inside single-quoted strings
                    if string_char == "'" and c == '"':
                        result.append('\\"')
                    else:
                        result.append(c)
            i += 1
        return ''.join(result)

    raw = fix_quotes(raw)

    # 5. Remove trailing commas before } and ]
    raw = re.sub(r',(\s*[}\]])', r'\1', raw)

    # 6. Quote unquoted keys (JS object keys don't need quotes, JSON requires them)
    raw = re.sub(r'(?<=[{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', lambda m: f'"{m.group(1)}"{m.group(2)}', raw)
    # Also handle keys at start of line
    raw = re.sub(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', lambda m: f'"{m.group(1).strip()}"{m.group(2)}', raw, flags=re.MULTILINE)

    # 7. Remove single-line comments
    raw = re.sub(r'//[^\n]*', '', raw)

    # 8. Remove multi-line comments
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)

    return raw


def parse_with_json5_fallback(text: str) -> dict:
    """Try json.loads, fall back to json5 if available."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  json.loads failed: {e}")
        print("  Trying json5...")
        try:
            import json5
            return json5.loads(text)
        except ImportError:
            raise RuntimeError("Install json5: pip install json5") from e


def restructure(trees: dict) -> dict:
    """
    Restructure the raw tree dict into a cleaner format:
    {
      "meta": {...},
      "skillTrees": [
        {
          "id": "mush9",
          "ability": "...",
          "nodes": [
            {
              "id": 0,
              "name": "...",
              "description": "...",
              "maxPoints": 1,
              "mastery": 0,
              "stats": [...],
              "requirements": [...],
              "transform": {...}
            }
          ]
        }
      ]
    }
    """
    out = []
    for tree_id, tree_data in trees.items():
        nodes_raw = tree_data.get("nodes", {})
        nodes = []
        for node_id, node in nodes_raw.items():
            nodes.append({
                "id": int(node_id) if node_id.isdigit() else node_id,
                "name": node.get("nodeName", ""),
                "description": node.get("description", ""),
                "loreText": node.get("loreText", ""),
                "altText": node.get("altText", ""),
                "maxPoints": node.get("maxPoints", 1),
                "mastery": node.get("mastery", 0),
                "masteryRequirement": node.get("masteryRequirement", 0),
                "pointBonusDescription": node.get("pointBonusDescription", ""),
                "stats": node.get("stats", []),
                "requirements": node.get("requirements", []),
                "transform": node.get("transform", {}),
                "icon": node.get("icon"),
                "abilityGrantedByNode": node.get("abilityGrantedByNode"),
            })

        entry = {
            "id": tree_id,
            "ability": tree_data.get("ability", ""),
            "nodes": nodes,
        }
        if "masteries" in tree_data:
            entry["masteries"] = tree_data["masteries"]
        if "unlockableAbilities" in tree_data:
            entry["unlockableAbilities"] = tree_data["unlockableAbilities"]

        out.append(entry)

    return {
        "meta": {
            "source": "https://github.com/prowner/last-epoch-data",
            "note": "Community datamined skill tree data. May not reflect current patch.",
            "treeCount": len(out),
            "totalNodes": sum(len(t["nodes"]) for t in out),
        },
        "skillTrees": out,
    }


def main():
    if not os.path.exists(TS_FILE):
        print(f"ERROR: {TS_FILE} not found.")
        print("Download it first with:")
        print("  Invoke-WebRequest -Uri https://raw.githubusercontent.com/prowner/last-epoch-data/main/datamined/skillTrees.ts -OutFile extracted_raw/community_skilltrees.ts")
        return

    print(f"Reading {os.path.basename(TS_FILE)} ({os.path.getsize(TS_FILE)//1024}KB)...")
    raw = open(TS_FILE, encoding="utf-8").read()

    print("Converting TypeScript to JSON-compatible text...")
    try:
        json_text = ts_to_json5(raw)
    except Exception as e:
        print(f"  Regex transform failed: {e}")
        return

    print("Parsing JSON...")
    try:
        import json5
        trees = json5.loads(json_text)
    except ImportError:
        print("  json5 not available, trying standard json...")
        try:
            trees = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"  Parse failed at position {e.pos}: {e.msg}")
            # Show context
            ctx = json_text[max(0, e.pos-100):e.pos+100]
            print(f"  Context: ...{repr(ctx)}...")
            return

    print(f"  Parsed {len(trees)} skill trees.")

    print("Restructuring...")
    result = restructure(trees)
    print(f"  {result['meta']['treeCount']} trees, {result['meta']['totalNodes']} total nodes")

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Written to {os.path.relpath(OUT_FILE, ROOT)}")


def ts_to_json5(raw: str) -> str:
    """Lighter transform — just strip TS type annotations, leaving valid json5."""
    # Find the object literal after the = sign
    match = re.search(r'export const skillTrees\s*:[^=]+=\s*', raw)
    if not match:
        raise ValueError("Could not find skillTrees declaration")
    raw = raw[match.end():]
    # Remove trailing semicolon
    raw = raw.rstrip().rstrip(';')
    # Remove TypeScript type assertions
    raw = re.sub(r'\bas\s+\w+[\w<>, ]*', '', raw)
    # Remove single-line comments
    raw = re.sub(r'//[^\n]*', '', raw)
    # Remove multi-line comments
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
    return raw


if __name__ == "__main__":
    main()
