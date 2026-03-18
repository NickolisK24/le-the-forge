# The Forge -- Affix System & Data Layer Guide

This document explains how to properly structure and integrate affix
data into The Forge so the system becomes scalable, accurate, and
simulation-ready.

------------------------------------------------------------------------

# Goal

Move from:

-   Hardcoded stat logic
-   Inconsistent data usage

To:

-   Fully data-driven stat system
-   Scalable simulation architecture
-   Clean engine integration

------------------------------------------------------------------------

# 1. Normalize Your Affix Data

## Problem

Unstructured data like:

{ "name": "Crit Chance", "value": 25 }

This cannot scale and breaks engine logic.

------------------------------------------------------------------------

## Solution

Every affix must follow a standardized schema:

``` json
{
  "name": "Increased Critical Strike Chance",
  "stat": "crit_chance",
  "type": "increased",
  "tiers": [
    { "tier": 1, "value": 10 },
    { "tier": 2, "value": 20 }
  ],
  "tags": ["crit", "offensive"]
}
```

------------------------------------------------------------------------

# 2. Stat Bucketing System

## Problem

Mixing all stat values together leads to incorrect calculations.

------------------------------------------------------------------------

## Solution

Create stat buckets:

``` python
stats = {
    "flat": {},
    "increased": {},
    "more": {}
}
```

Example usage:

``` python
stats["increased"]["damage"] += 25
stats["more"]["damage"] *= 1.20
```

Final calculation:

``` python
final_damage = base_damage * (1 + total_increased) * total_more
```

------------------------------------------------------------------------

# 3. Affix Tags

Tags allow flexible filtering and scaling.

Example:

``` json
{
  "tags": ["crit", "offensive"]
}
```

Use cases:

-   Optimization targeting
-   Filtering
-   Scaling rules

------------------------------------------------------------------------

# 4. Apply Affixes in Engine

Create a function:

``` python
def apply_affix(stats, affix, tier):
    value = affix["tiers"][tier]["value"]
    stat = affix["stat"]
    type_ = affix["type"]

    if type_ == "flat":
        stats["flat"][stat] += value
    elif type_ == "increased":
        stats["increased"][stat] += value
    elif type_ == "more":
        stats["more"][stat] *= (1 + value / 100)
```

------------------------------------------------------------------------

# 5. Aggregate Stats

``` python
def aggregate_stats(build):
    stats = create_empty_stat_pool()

    for item in build["items"]:
        for affix in item["affixes"]:
            apply_affix(stats, affix, affix["tier"])

    return stats
```

------------------------------------------------------------------------

# 6. Replace Hardcoded Logic

Avoid:

``` python
damage = 100
```

Use:

``` python
damage = stats["flat"]["damage"]
```

------------------------------------------------------------------------

# 7. Add Item Context (Next Step)

Example:

``` json
{
  "item_type": "helmet",
  "allowed_affixes": ["health", "armor", "resistance"]
}
```

------------------------------------------------------------------------

# 8. Implementation Checklist

-   [x] Normalize affix schema
-   [x] Implement stat buckets
-   [x] Create apply_affix()
-   [x] Build aggregate_stats()
-   [x] Remove hardcoded values
-   [x] Test with sample build

------------------------------------------------------------------------

# Final Note

This system is the foundation of The Forge.

If done correctly, your engine will:

-   Scale easily
-   Support all builds
-   Enable advanced simulations
