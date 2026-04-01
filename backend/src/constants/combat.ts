/**
 * Combat mechanic constants — hit, crit, and ailment formulas.
 * Update when LE patches change ailment ratios, durations, or crit caps.
 */

/** Player crit chance hard cap */
export const CRIT_CHANCE_CAP = 0.95 as const;

/** BuildStats defaults */
export const BASE_CRIT_CHANCE = 0.05 as const;
export const BASE_CRIT_MULTIPLIER = 1.5 as const;

/** Ailment DoT — Last Epoch baseline values, pre-modifier */
export const BLEED_BASE_RATIO = 0.70 as const;  // 70% of hit damage spread over duration per stack
export const BLEED_DURATION = 4.0 as const;      // seconds

export const IGNITE_DPS_RATIO = 0.20 as const;   // 20% of hit damage per second per stack
export const IGNITE_DURATION = 3.0 as const;     // seconds

export const POISON_DPS_RATIO = 0.30 as const;   // 30% of hit damage per second per stack
export const POISON_DURATION = 3.0 as const;     // seconds
