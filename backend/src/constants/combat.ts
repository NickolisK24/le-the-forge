/**
 * Combat mechanic constants — hit, crit, and ailment formulas.
 * Update when LE patches change ailment ratios, durations, or crit caps.
 */

/** Player crit chance hard cap */
export const CRIT_CHANCE_CAP = 0.95 as const;

/** BuildStats defaults */
export const BASE_CRIT_CHANCE = 0.05 as const;
export const BASE_CRIT_MULTIPLIER = 1.5 as const;

/** Ailment DoT — Last Epoch baseline durations per stack.
 * VERIFIED: 1.4.3 spec §4 — each ailment has flat base DPS per stack (see
 * BLEED_BASE_DPS / IGNITE_BASE_DPS / POISON_BASE_DPS in the Python constants).
 * The old legacy ratio constants (BLEED_BASE_RATIO etc.) were incorrect and
 * have been removed.
 */
export const BLEED_DURATION = 4.0 as const;      // seconds
export const IGNITE_DURATION = 3.0 as const;     // seconds
export const POISON_DURATION = 3.0 as const;     // seconds
