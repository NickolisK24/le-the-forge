/**
 * runtimeContext.ts — Centralized runtime state for conditional evaluation.
 *
 * Provides structured context about the current combat/build state.
 * Immutable during a single evaluation pass. Optional and extensible.
 */

// ---------------------------------------------------------------------------
// Core context
// ---------------------------------------------------------------------------

export type EnemyType = "normal" | "rare" | "boss" | "none";

export interface RuntimeContext {
  // Health state
  currentHealth: number;
  maxHealth: number;

  // Mana state
  currentMana: number;
  maxMana: number;

  // Combat state
  isMoving: boolean;
  wasHitRecently: boolean;
  isChanneling: boolean;

  // Enemy state
  enemyType: EnemyType;
  enemyCount: number;

  // Minion state
  minionCount: number;

  // Build tags (e.g. "melee", "fire", "dual_wield")
  activeTags: Set<string>;

  // Ward
  currentWard: number;
}

// ---------------------------------------------------------------------------
// Derived values
// ---------------------------------------------------------------------------

/** Get health as a percentage (0-100). */
export function getHealthPercent(ctx: RuntimeContext): number {
  if (ctx.maxHealth <= 0) return 0;
  return (ctx.currentHealth / ctx.maxHealth) * 100;
}

/** Get mana as a percentage (0-100). */
export function getManaPercent(ctx: RuntimeContext): number {
  if (ctx.maxMana <= 0) return 0;
  return (ctx.currentMana / ctx.maxMana) * 100;
}

/** Check if character is at "low life" (≤35% health, Last Epoch threshold). */
export function isLowLife(ctx: RuntimeContext): boolean {
  return getHealthPercent(ctx) <= 35;
}

// ---------------------------------------------------------------------------
// Default context for planner mode
// ---------------------------------------------------------------------------

export const DEFAULT_PLANNER_CONTEXT: RuntimeContext = {
  currentHealth: 1000,
  maxHealth: 1000,
  currentMana: 200,
  maxMana: 200,
  isMoving: false,
  wasHitRecently: false,
  isChanneling: false,
  enemyType: "boss",
  enemyCount: 1,
  minionCount: 0,
  activeTags: new Set(),
  currentWard: 0,
};

/**
 * Create a context with custom overrides from the planner defaults.
 */
export function createPlannerContext(overrides: Partial<RuntimeContext> = {}): RuntimeContext {
  return { ...DEFAULT_PLANNER_CONTEXT, ...overrides };
}
