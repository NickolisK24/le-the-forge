/**
 * Build Definition API client.
 *
 * Calls POST /api/simulate/encounter-build and returns typed encounter results.
 */

import type { ApiResponse } from "@/types";
import type { EncounterResult } from "@/services/encounterApi";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type CharacterClass = "Acolyte" | "Mage" | "Primalist" | "Sentinel" | "Rogue";

export type EnemyTemplateOpt =
  | "TRAINING_DUMMY"
  | "STANDARD_BOSS"
  | "SHIELDED_BOSS"
  | "ADD_FIGHT"
  | "MOVEMENT_BOSS";

export interface GearAffix {
  name: string;
  tier: number;
}

export interface GearItem {
  slot: string;
  affixes: GearAffix[];
  rarity: "normal" | "magic" | "rare" | "exalted";
}

export interface BuffDef {
  buff_id: string;
  modifiers: Record<string, number>;
  duration: number | null;
}

export interface BuildDefinition {
  character_class: CharacterClass;
  mastery: string;
  skill_id: string;
  skill_level: number;
  gear: GearItem[];
  passive_ids: number[];
  buffs: BuffDef[];
}

export interface EncounterOverride {
  enemy_template?: EnemyTemplateOpt;
  fight_duration?: number;
  tick_size?: number;
  distribution?: "SINGLE" | "CLEAVE" | "SPLIT" | "CHAIN";
}

export interface BuildSimRequest {
  build: BuildDefinition;
  encounter?: EncounterOverride;
}

export const CLASS_MASTERIES: Record<CharacterClass, string[]> = {
  Acolyte:   ["Necromancer", "Lich", "Warlock"],
  Mage:      ["Runemaster", "Sorcerer", "Spellblade"],
  Primalist: ["Beastmaster", "Shaman", "Druid"],
  Sentinel:  ["Paladin", "Void Knight", "Forge Guard"],
  Rogue:     ["Bladedancer", "Marksman", "Falconer"],
};

export const CLASSES: CharacterClass[] = Object.keys(CLASS_MASTERIES) as CharacterClass[];

export const GEAR_SLOTS = [
  "weapon", "offhand", "head", "body", "hands",
  "feet", "ring_1", "ring_2", "amulet", "waist",
] as const;

export const TEMPLATE_LABELS: Record<EnemyTemplateOpt, string> = {
  TRAINING_DUMMY: "Training Dummy",
  STANDARD_BOSS:  "Standard Boss",
  SHIELDED_BOSS:  "Shielded Boss",
  ADD_FIGHT:      "Add Fight",
  MOVEMENT_BOSS:  "Movement Boss",
};

export async function simulateBuild(
  req: BuildSimRequest,
  signal?: AbortSignal
): Promise<EncounterResult> {
  const res = await fetch(`${BASE_URL}/simulate/encounter-build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  });

  if (!res.ok) {
    const body: ApiResponse<null> = await res.json().catch(() => ({
      data: null, meta: null, errors: [{ message: `HTTP ${res.status}` }],
    }));
    const msg = body.errors?.[0]?.message ?? `Request failed (${res.status})`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }

  const body: ApiResponse<EncounterResult> = await res.json();
  if (!body.data) throw new Error("Empty response from server");
  return body.data;
}
