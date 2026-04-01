"""
Cache TTL constants (seconds).

Only values that appear as anonymous magic numbers in multiple places belong here.
Route-specific named TTLs (_LIST_CACHE_TTL, _SIM_CACHE_TTL, etc.) stay local.
"""

# Reference data — static game content, changes only on game patch
REF_STATIC_CACHE_TTL: int = 86400       # 24 hours

# Reference data — semi-static content (affixes, passives)
REF_SEMISTATIC_CACHE_TTL: int = 3600    # 1 hour
