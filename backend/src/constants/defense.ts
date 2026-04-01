/**
 * Defense mechanic constants — Last Epoch formulas.
 * Update when LE patches change caps or formula divisors.
 */

/** Resistance cap — all elemental, physical, and poison resist capped at 75% */
export const RES_CAP = 75 as const;

/** Ward decay: base fraction of current ward lost per second before retention mods */
export const WARD_BASE_DECAY_RATE = 0.25 as const;

/** Endurance stat hard cap */
export const ENDURANCE_CAP = 60 as const;

/**
 * Diminishing-returns divisors for stat / (stat + DIVISOR) formulas.
 * Named separately so a patch to one mechanic doesn't silently affect others.
 */
export const ARMOR_DIVISOR = 1000 as const;
export const DODGE_DIVISOR = 1000 as const;
export const BLOCK_DIVISOR = 1000 as const;
export const STUN_AVOIDANCE_DIVISOR = 1000 as const;

/** Enemy baseline model used for EHP projections */
export const ENEMY_CRIT_RATE = 0.35 as const;
export const ENEMY_CRIT_MULTIPLIER = 1.5 as const;
