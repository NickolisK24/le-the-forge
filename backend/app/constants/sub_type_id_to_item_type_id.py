"""
Maps subTypeID values to item type ID slugs.

NOTE: subTypeID values are NOT globally unique — they restart at 0 for each
baseTypeID. Populate this only if a use case requires subTypeID-based lookup
within a known baseTypeID context. Prefer BASE_TYPE_ID_TO_ITEM_TYPE_ID for
general item type resolution.
"""

SUBTYPE_ID_TO_ITEM_TYPE_ID: dict[int, str] = {}
