import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ITEM_TYPES_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "items",
    "item_types.json"
)

ITEMS_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "items",
    "items.json"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "src",
    "constants",
    "SUBTYPE_ID_TO_ITEM_TYPE_ID.ts"
)


# -------------------------
# Load item types
# -------------------------

with open(ITEM_TYPES_PATH) as f:
    item_types = json.load(f)

type_ids = [t["id"] for t in item_types]


# -------------------------
# Load items
# -------------------------

with open(ITEMS_PATH) as f:
    data = json.load(f)

# Find list automatically
items = None

if isinstance(data, list):
    items = data

elif isinstance(data, dict):
    for v in data.values():
        if isinstance(v, list):
            items = v
            break

if not items:
    raise Exception("Could not locate items list")


# -------------------------
# Match subtype → type
# -------------------------

def find_type_from_name(name):
    name_lower = name.lower()

    for type_id in type_ids:
        if type_id in name_lower:
            return type_id

    return None


mapping = {}

matched = 0
skipped = 0

for item in items:
    name = item.get("name")
    subtype = item.get("subTypeID")

    if name is None or subtype is None:
        continue

    type_id = find_type_from_name(name)

    if type_id:
        mapping[subtype] = type_id
        matched += 1
    else:
        skipped += 1


# -------------------------
# Write TypeScript file
# -------------------------

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w") as f:
    f.write("export const SUBTYPE_ID_TO_ITEM_TYPE_ID = {\n\n")

    for subtype in sorted(mapping.keys()):
        f.write(
            f'  {subtype}: "{mapping[subtype]}",\n'
        )

    f.write("\n} as const;\n\n")

    f.write(
        "export type SubTypeId = "
        "keyof typeof SUBTYPE_ID_TO_ITEM_TYPE_ID;\n"
    )


# -------------------------
# Report results
# -------------------------

print("Done.")

print("Matched:", matched)
print("Skipped:", skipped)

print("\nOutput file:")
print(OUTPUT_PATH)