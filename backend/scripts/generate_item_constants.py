import json
import os
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ITEM_TYPES_PATH = os.path.join(
    BASE_DIR,
    "..",
    "..",
    "data",
    "items",
    "item_types.json"
)

ITEMS_PATH = os.path.join(
    BASE_DIR,
    "..",
    "..",
    "data",
    "items",
    "items.json"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "src",
    "constants"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -----------------------------------------
# Utility writer
# -----------------------------------------

def write_ts_file(filename, content):

    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w") as f:
        f.write(content)

    print(f"✓ Generated {filename}")


# -----------------------------------------
# Load Data
# -----------------------------------------

with open(ITEM_TYPES_PATH) as f:
    item_types = json.load(f)

with open(ITEMS_PATH) as f:
    raw_items_data = json.load(f)


# Find real item list inside items.json
def extract_items_list(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for v in data.values():

            if isinstance(v, list):
                return v

    return []


items_list = extract_items_list(raw_items_data)


# -----------------------------------------
# Generate equipmentSlots.ts
# -----------------------------------------

def generate_equipment_slots():

    slots = sorted({
        item["slot"]
        for item in item_types
    })

    slots_ts = f"""export const EQUIPMENT_SLOTS = [
{chr(10).join([f'  "{slot}",' for slot in slots])}
] as const;

export type EquipmentSlot =
  typeof EQUIPMENT_SLOTS[number];
"""

    write_ts_file(
        "equipmentSlots.ts",
        slots_ts
    )


# -----------------------------------------
# Generate itemTypeIds.ts
# -----------------------------------------

def generate_item_type_ids():

    ids = sorted({
        item["id"]
        for item in item_types
    })

    ids_ts = f"""export const ITEM_TYPE_IDS = [
{chr(10).join([f'  "{id_}",' for id_ in ids])}
] as const;

export type ItemTypeId =
  typeof ITEM_TYPE_IDS[number];
"""

    write_ts_file(
        "itemTypeIds.ts",
        ids_ts
    )


# -----------------------------------------
# Generate itemTypeToSlot.ts
# -----------------------------------------

def generate_item_type_to_slot():

    mapping = OrderedDict()

    for item in sorted(
        item_types,
        key=lambda x: x["id"]
    ):
        mapping[item["id"]] = item["slot"]

    mapping_lines = [
        f'  "{k}": "{v}",'
        for k, v in mapping.items()
    ]

    mapping_ts = f"""import type {{ EquipmentSlot }} from "./equipmentSlots";
import type {{ ItemTypeId }} from "./itemTypeIds";

export const ITEM_TYPE_TO_SLOT: Record<
  ItemTypeId,
  EquipmentSlot
> = {{
{chr(10).join(mapping_lines)}
}};
"""

    write_ts_file(
        "itemTypeToSlot.ts",
        mapping_ts
    )


# -----------------------------------------
# Generate subTypeIdToItemTypeId.ts
# -----------------------------------------

def generate_subtype_to_item_type_id():

    # Build lookup from subtypeID → itemTypeId
    mapping = {}

    for item in items_list:

        sub_type_id = item.get("subTypeID")

        if sub_type_id is None:
            continue

        # Match subtype to item type
        for item_type in item_types:

            subtype_ids = item_type.get(
                "subTypeIDs",
                []
            )

            if sub_type_id in subtype_ids:

                mapping[sub_type_id] = item_type["id"]

    # Sort mapping
    mapping = dict(sorted(mapping.items()))

    lines = [
        f"  {k}: \"{v}\","
        for k, v in mapping.items()
    ]

    mapping_ts = f"""export const SUBTYPE_ID_TO_ITEM_TYPE_ID = {{
{chr(10).join(lines)}
}} as const;

export type SubTypeId =
  keyof typeof SUBTYPE_ID_TO_ITEM_TYPE_ID;
"""

    write_ts_file(
        "subTypeIdToItemTypeId.ts",
        mapping_ts
    )


# -----------------------------------------
# Run All Generators
# -----------------------------------------

generate_equipment_slots()

generate_item_type_ids()

generate_item_type_to_slot()

generate_subtype_to_item_type_id()

print("\n✓ All item constants generated successfully.")