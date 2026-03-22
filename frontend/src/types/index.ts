// ============================================================
// Shared TypeScript types for The Forge frontend
// These mirror the Marshmallow schemas on the backend.
// ============================================================

// ---------------------------------------------------------------------------
// API envelope
// ---------------------------------------------------------------------------

export interface ApiResponse<T> {
  data: T | null;
  meta: PaginationMeta | null;
  errors: ApiError[] | null;
}

export interface ApiError {
  field?: string;
  message: string;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface User {
  id: string;
  discord_id: string;
  username: string;
  discriminator?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Builds
// ---------------------------------------------------------------------------

export type CharacterClass = "Acolyte" | "Mage" | "Primalist" | "Sentinel" | "Rogue";
export type BuildTier = "S" | "A" | "B" | "C";
export type VoteDirection = 1 | -1 | 0;

export interface BuildSkill {
  id: string;
  slot: number;
  skill_name: string;
  points_allocated: number;
  spec_tree: number[];
}

export interface Build {
  id: string;
  slug: string;
  name: string;
  description?: string;
  character_class: CharacterClass;
  mastery: string;
  level: number;
  passive_tree: number[];
  gear: GearSlot[];
  skills: BuildSkill[];
  is_ssf: boolean;
  is_hc: boolean;
  is_ladder_viable: boolean;
  is_budget: boolean;
  patch_version: string;
  cycle: string;
  tier?: BuildTier;
  vote_count: number;
  view_count: number;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  author?: Pick<User, "id" | "username" | "avatar_url">;
  user_vote?: VoteDirection;
}

export interface BuildListItem
  extends Pick<
    Build,
    | "id" | "slug" | "name" | "character_class" | "mastery" | "tier"
    | "vote_count" | "is_ssf" | "is_hc" | "is_ladder_viable" | "is_budget"
    | "patch_version" | "cycle" | "created_at" | "description"
  > {
  author?: Pick<User, "id" | "username">;
}

export interface GearSlot {
  slot: string;
  item_name?: string;
  rarity?: string;
  affixes?: AffixOnItem[];
}

export interface AffixOnItem {
  name: string;
  tier: number;
  sealed: boolean;
}

export interface BuildFilters {
  character_class?: CharacterClass;
  mastery?: string;
  tier?: BuildTier;
  is_ssf?: boolean;
  is_hc?: boolean;
  is_ladder_viable?: boolean;
  is_budget?: boolean;
  cycle?: string;
  sort?: "votes" | "new" | "tier" | "views";
  q?: string;
}

export interface BuildCreatePayload {
  name: string;
  description?: string;
  character_class: CharacterClass;
  mastery: string;
  level?: number;
  passive_tree?: number[];
  gear?: GearSlot[];
  skills?: Partial<BuildSkill>[];
  is_ssf?: boolean;
  is_hc?: boolean;
  is_ladder_viable?: boolean;
  is_budget?: boolean;
  patch_version?: string;
  cycle?: string;
  is_public?: boolean;
}

export interface VoteResult {
  vote_count: number;
  user_vote: VoteDirection;
  tier: BuildTier;
}

// ---------------------------------------------------------------------------
// Craft
// ---------------------------------------------------------------------------

export type CraftAction =
  | "add_affix"
  | "upgrade_affix"
  | "seal_affix"
  | "unseal_affix"
  | "remove_affix";

export type CraftOutcome = "success" | "perfect" | "fracture";

export interface CraftAffix {
  name: string;
  tier: number;
  sealed: boolean;
  type?: "prefix" | "suffix";
}

export interface CraftStep {
  id: string;
  step_number: number;
  timestamp: string;
  action: CraftAction;
  affix_name?: string;
  tier_before?: number;
  tier_after?: number;
  roll?: number | null;
  outcome: CraftOutcome;
  fp_before: number;
  fp_after: number;
}

export interface CraftSession {
  id: string;
  slug: string;
  item_type: string;
  item_name?: string;
  item_level: number;
  rarity: string;
  forge_potential: number;
  affixes: CraftAffix[];
  created_at: string;
  steps: CraftStep[];
}

export interface CraftActionResult {
  success: boolean;
  outcome: CraftOutcome;
  roll: number | null;
  forge_potential: number;
  message: string;
  step_number: number;
  error?: string;
}

export interface OptimalPathStep {
  action: CraftAction;
  affix: string;
  risk_pct: number;
  note: string;
  cumulative_survival_pct: number;
  sealed_count_at_step: number;
}

export interface SimulationResult {
  completion_chance: number;
  step_survival_curve: number[];
  n_simulations: number;
}

export interface LocalSimulationResult {
  fp_consumed: { p25: number; p50: number; p75: number };
  steps_completed: { p25: number; p50: number; p75: number };
  n_simulations: number;
}

export interface StrategyComparison {
  name: string;
  description: string;
  completion_chance: number;
  expected_steps: number;
  expected_fp_cost: number;
}

export interface CraftPredictResult {
  optimal_path: OptimalPathStep[];
  simulation_result: SimulationResult;
  strategy_comparison: StrategyComparison[];
}

export interface CraftSummary {
  total_actions: number;
  successes: number;
  perfects: number;
  fp_spent: number;
  optimal_path: OptimalPathStep[];
  simulation_result: SimulationResult;
  strategy_comparison: StrategyComparison[];
}

export interface CraftSessionCreatePayload {
  item_type: string;
  item_name?: string;
  item_level?: number;
  rarity?: string;
  forge_potential?: number;
  fp_mode?: "random" | "manual" | "fixed";
  manual_fp?: number;
  affixes?: CraftAffix[];
}

// ---------------------------------------------------------------------------
// Reference data
// ---------------------------------------------------------------------------

export interface ClassMeta {
  color: string;
  masteries: string[];
  skills: string[];
}

export interface AffixTier {
  tier: number;
  min: number;
  max: number;
}

export interface AffixDef {
  id: string;
  name: string;
  type: "prefix" | "suffix";
  applicable_to: string[];
  tiers: AffixTier[];
  tags?: string[];
  class_requirement?: string | null;
}

