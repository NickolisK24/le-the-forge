/**
 * Cache TTL constants (seconds).
 * Only values used in multiple places belong here.
 */

/** Reference data — static game content, changes only on game patch (24 hours) */
export const REF_STATIC_CACHE_TTL = 86400 as const;

/** Reference data — semi-static content, e.g. affixes, passives (1 hour) */
export const REF_SEMISTATIC_CACHE_TTL = 3600 as const;
