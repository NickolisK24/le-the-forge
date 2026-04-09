/**
 * buff.ts — Type definitions for the buff/debuff system.
 *
 * Buffs are temporary stat modifiers with duration and optional stacking.
 * They integrate with the runtime context and conditional stat system.
 */

import type { PassiveStatModifier } from "@/types/passiveEffects";

// ---------------------------------------------------------------------------
// Buff definition (template)
// ---------------------------------------------------------------------------

export interface BuffDefinition {
  /** Unique buff identifier */
  id: string;
  /** Display name */
  name: string;
  /** Stat modifiers applied while active (per stack) */
  modifiers: PassiveStatModifier[];
  /** Duration in seconds (0 = permanent until removed) */
  durationSeconds: number;
  /** Maximum number of stacks (default 1) */
  maxStacks: number;
  /** Categorization tags */
  tags: string[];
  /** Whether this is a debuff (negative effect) */
  isDebuff: boolean;
  /** Optional description */
  description?: string;
}

// ---------------------------------------------------------------------------
// Active buff instance (runtime state)
// ---------------------------------------------------------------------------

export interface ActiveBuff {
  /** Reference to the buff definition */
  definition: BuffDefinition;
  /** Remaining duration in seconds (0 = expired, -1 = permanent) */
  remainingSeconds: number;
  /** Current stack count */
  stacks: number;
  /** When this buff was applied (for deterministic ordering) */
  appliedAt: number;
}

// ---------------------------------------------------------------------------
// Example buff definitions
// ---------------------------------------------------------------------------

export const EXAMPLE_BUFFS: Record<string, BuffDefinition> = {
  berserk: {
    id: "berserk",
    name: "Berserk",
    modifiers: [
      { statId: "Damage", type: "percent", value: 30 },
      { statId: "Attack Speed", type: "percent", value: 15 },
    ],
    durationSeconds: 8,
    maxStacks: 1,
    tags: ["melee", "self"],
    isDebuff: false,
    description: "+30% Damage, +15% Attack Speed for 8s",
  },
  frenzy: {
    id: "frenzy",
    name: "Frenzy",
    modifiers: [
      { statId: "Attack Speed", type: "percent", value: 5 },
    ],
    durationSeconds: 4,
    maxStacks: 5,
    tags: ["self", "stackable"],
    isDebuff: false,
    description: "+5% Attack Speed per stack (max 5, 4s)",
  },
  chill: {
    id: "chill",
    name: "Chill",
    modifiers: [
      { statId: "Movement Speed", type: "percent", value: -20 },
    ],
    durationSeconds: 3,
    maxStacks: 1,
    tags: ["cold", "ailment"],
    isDebuff: true,
    description: "-20% Movement Speed for 3s",
  },
  haste: {
    id: "haste",
    name: "Haste",
    modifiers: [
      { statId: "Movement Speed", type: "percent", value: 20 },
      { statId: "Cast Speed", type: "percent", value: 10 },
    ],
    durationSeconds: 5,
    maxStacks: 1,
    tags: ["self", "speed"],
    isDebuff: false,
    description: "+20% Movement Speed, +10% Cast Speed for 5s",
  },
};
