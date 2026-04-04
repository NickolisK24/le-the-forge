"""
Canonical API Response Schemas — the single source of truth for API contracts.

Every API endpoint MUST return data matching these schemas exactly.
Both DB and JSON fallback paths must produce identical field sets.

Used by:
  - API route handlers (serialization)
  - Contract tests (validation)
  - Frontend type definitions (should mirror these)
"""

# ---------------------------------------------------------------------------
# Affix Definition (GET /api/ref/affixes)
# ---------------------------------------------------------------------------
# Each affix returned by the API must contain exactly these fields.
AFFIX_FIELDS = {
    "id":                str,    # Unique identifier (string)
    "name":              str,    # Display name
    "type":              str,    # "prefix" or "suffix" (normalized)
    "stat_key":          str,    # Internal stat identifier
    "applicable_to":     list,   # List of slot names
    "tiers":             list,   # [{tier: int, min: float, max: float}, ...]
    "tags":              list,   # Tag strings
    "class_requirement": (str, type(None)),  # Class name or null
}

# ---------------------------------------------------------------------------
# Passive Node (GET /api/passives/<class>)
# ---------------------------------------------------------------------------
PASSIVE_NODE_FIELDS = {
    "id":                  str,    # Namespaced ID (e.g. "ac_0")
    "raw_node_id":         int,    # Game-internal node ID
    "character_class":     str,    # Class name
    "mastery":             (str, type(None)),  # Mastery name or null (base nodes)
    "mastery_index":       int,    # 0=base, 1/2/3=masteries
    "mastery_requirement": int,    # Points needed to unlock
    "name":                str,    # Display name
    "description":         (str, type(None)),  # Tooltip text
    "node_type":           str,    # "core" or "notable"
    "x":                   (int, float),  # Position X
    "y":                   (int, float),  # Position Y
    "max_points":          int,    # Max allocatable points
    "connections":         list,   # Connected node IDs
    "stats":               list,   # [{key: str, value: str|num}, ...]
    "ability_granted":     (str, type(None)),  # Granted ability name
    "icon":                (str, type(None)),  # Icon asset ID (e.g. "a-r-528")
}

# ---------------------------------------------------------------------------
# Item Type (GET /api/ref/item-types)
# ---------------------------------------------------------------------------
ITEM_TYPE_FIELDS = {
    "id":             int,
    "name":           str,
    "category":       str,
    "base_implicit":  (str, type(None)),
}

# ---------------------------------------------------------------------------
# Base Item (GET /api/ref/base-items — items within each slot)
# ---------------------------------------------------------------------------
BASE_ITEM_FIELDS = {
    "name":      str,
    "level_req": int,
    "min_fp":    int,
    "max_fp":    int,
    "armor":     int,
    "implicit":  (str, type(None)),
    "tags":      list,
}

# ---------------------------------------------------------------------------
# Build (GET /api/builds)
# ---------------------------------------------------------------------------
BUILD_LIST_FIELDS = {
    "id":               str,
    "slug":             str,
    "name":             str,
    "description":      (str, type(None)),
    "character_class":  str,
    "mastery":          (str, type(None)),
    "tier":             (str, type(None)),
    "vote_count":       int,
    "is_ssf":           bool,
    "is_hc":            bool,
    "is_ladder_viable": bool,
    "is_budget":        bool,
    "patch_version":    (str, type(None)),
    "cycle":            (str, type(None)),
    "created_at":       str,
    "author":           (dict, type(None)),
}

# ---------------------------------------------------------------------------
# Class Meta (GET /api/ref/classes)
# ---------------------------------------------------------------------------
CLASS_META_FIELDS = {
    "color":     str,
    "masteries": list,
    "skills":    list,
}

# ---------------------------------------------------------------------------
# Enemy Profile (GET /api/ref/enemy-profiles)
# ---------------------------------------------------------------------------
ENEMY_PROFILE_FIELDS = {
    "id":              str,
    "category":        str,
    "description":     str,
    "health":          (int, float),
    "armor":           (int, float),
    "crit_chance":     (int, float),
    "crit_multiplier": (int, float),
    "data_version":    str,
}

# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def validate_record(record: dict, schema: dict, context: str = "") -> list[str]:
    """Validate a single record against a schema. Returns list of errors."""
    errors = []
    for field, expected_type in schema.items():
        if field not in record:
            errors.append(f"[{context}] Missing field: {field}")
            continue
        value = record[field]
        if isinstance(expected_type, tuple):
            if not isinstance(value, expected_type):
                errors.append(
                    f"[{context}] Field '{field}': expected {expected_type}, got {type(value).__name__} ({value!r})"
                )
        else:
            if not isinstance(value, expected_type):
                errors.append(
                    f"[{context}] Field '{field}': expected {expected_type.__name__}, got {type(value).__name__} ({value!r})"
                )
    # Extra fields (warning, not error)
    extra = set(record.keys()) - set(schema.keys())
    if extra:
        errors.append(f"[{context}] Extra fields: {extra}")
    return errors


def validate_dataset(records: list[dict], schema: dict, label: str, sample_size: int = 10) -> list[str]:
    """Validate a list of records. Checks first `sample_size` records and reports."""
    if not records:
        return [f"[{label}] Empty dataset"]
    errors = []
    checked = min(sample_size, len(records))
    for i in range(checked):
        errs = validate_record(records[i], schema, f"{label}[{i}]")
        errors.extend(errs)
    return errors
