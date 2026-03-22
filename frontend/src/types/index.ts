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
  instability_before: number;
  instability_after: number;
  fracture_risk_pct: number;
  roll?: number;
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
  instability: number;
  forge_potential: number;
  affixes: CraftAffix[];
  is_fractured: boolean;
  created_at: string;
  steps: CraftStep[];
}

export interface CraftActionResult {
  success: boolean;
  outcome: CraftOutcome;
  fracture_risk_pct: number;
  roll: number;
  instability: number;
  forge_potential: number;
  is_fractured: boolean;
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
  brick_chance: number;
  perfect_item_chance: number;
  step_survival_curve: number[];
  step_fracture_rates: number[];
  median_instability: number;
  n_simulations: number;
}

export interface StrategyComparison {
  name: string;
  description: string;
  brick_chance: number;
  perfect_item_chance: number;
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
  fractures: number;
  fp_spent: number;
  current_risk_pct: number;
  optimal_path: OptimalPathStep[];
  simulation_result: SimulationResult;
  strategy_comparison: StrategyComparison[];
}

export interface CraftSessionCreatePayload {
  item_type: string;
  item_name?: string;
  item_level?: number;
  rarity?: string;
  instability?: number;
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


// ---------------------------------------------------------------------------
// Simulation API types
// ---------------------------------------------------------------------------

export interface SimulateStatsPayload {
  character_class: string;
  mastery: string;
  allocated_node_ids?: number[];
  gear_affixes?: Array<{ name: string; tier: number }>;
}

export interface BuildStatsResult {
  // Offense
  base_damage: number;
  attack_speed: number;
  crit_chance: number;
  crit_multiplier: number;
  spell_damage_pct: number;
  physical_damage_pct: number;
  fire_damage_pct: number;
  cold_damage_pct: number;
  lightning_damage_pct: number;
  necrotic_damage_pct: number;
  void_damage_pct: number;
  // Defense
  max_health: number;
  armour: number;
  dodge_rating: number;
  block_chance: number;
  ward: number;
  fire_res: number;
  cold_res: number;
  lightning_res: number;
  void_res: number;
  necrotic_res: number;
  // Penetration
  fire_penetration: number;
  cold_penetration: number;
  lightning_penetration: number;
  void_penetration: number;
  necrotic_penetration: number;
  physical_penetration: number;
  // Attributes
  strength: number;
  intelligence: number;
  dexterity: number;
  vitality: number;
  attunement: number;
  [key: string]: number;
}

export interface CombatDPSResult {
  dps: number;
  average_hit: number;
  effective_attack_speed: number;
  increased_damage_pool: number;
  crit_contribution_pct: number;
  ailment_dps: number;
  total_dps: number;
  flat_damage_added: number;
}

export interface MonteCarloDPSResult {
  mean_dps: number;
  min_dps: number;
  max_dps: number;
  std_dev: number;
  percentile_25: number;
  percentile_75: number;
  n_simulations: number;
}

export interface SimulateCombatResult {
  dps: CombatDPSResult;
  monte_carlo: MonteCarloDPSResult;
  skill_name: string;
  skill_level: number;
}

export interface DefenseResult {
  effective_hp: number;
  total_ehp_with_ward: number;
  armor_reduction_pct: number;
  avg_resistance_pct: number;
  dodge_chance_pct: number;
  ward_net_gain_per_sec: number;
  sustain_score: number;
  survivability_score: number;
  block_chance_pct: number;
  endurance_pct: number;
  glancing_blow_pct: number;
  crit_avoidance_pct: number;
  resistances: Record<string, number>;
  weaknesses: string[];
  strengths: string[];
}

export interface StatUpgrade {
  stat: string;
  increment: number;
  dps_gain_pct: number;
  ehp_gain_pct: number;
  combined_score: number;
}

export interface SimulateCombatPayload {
  stats: BuildStatsResult;
  skill_name: string;
  skill_level?: number;
  n_simulations?: number;
}

export interface SimulateDefensePayload {
  stats: BuildStatsResult;
}

export interface SimulateOptimizePayload {
  stats: BuildStatsResult;
  skill_name: string;
  skill_level?: number;
  top_n?: number;
}

export interface SimulateBuildPayload {
  character_class: string;
  mastery: string;
  allocated_node_ids?: number[];
  gear_affixes?: Array<{ name: string; tier: number }>;
  skill_name: string;
  skill_level?: number;
  n_simulations?: number;
}

export interface SimulateBuildResult {
  stats: BuildStatsResult;
  combat: SimulateCombatResult;
  defense: DefenseResult;
  optimization: StatUpgrade[];
}

// ---------------------------------------------------------------------------
// Craft Simulation types
// ---------------------------------------------------------------------------

export interface CraftSimulatePayload {
  instability: number;
  forge_potential: number;
  steps: Array<{ action: string; affix_name?: string }>;
  n_simulations?: number;
}

export interface CraftSimulateResult {
  n_simulations: number;
  fracture_rate: number;
  fp_consumed: { p25: number; p50: number; p75: number };
  steps_completed: { p25: number; p50: number; p75: number };
  final_instability: { p25: number; p50: number; p75: number };
  fracture_severity: { none: number; minor: number; major: number; total: number };
}

// ---------------------------------------------------------------------------
// New reference data types
// ---------------------------------------------------------------------------

export interface EnemyResistances {
  physical: number;
  fire: number;
  cold: number;
  lightning: number;
  void: number;
  necrotic: number;
  poison: number;
}

export interface EnemyProfile {
  id: string;
  name: string;
  category: string;
  description: string;
  health: number;
  armor: number;
  resistances: EnemyResistances;
  crit_chance: number;
  crit_multiplier: number;
  tags: string[];
}

export interface DamageType {
  id: string;
  name: string;
  tags: string[];
  description: string;
  stat_key: string;
  resistance_stat: string;
  penetration_stat: string | null;
}

export interface Rarity {
  id: string;
  name: string;
  max_prefixes: number;
  max_suffixes: number;
  description: string;
  color: string;
  min_fp: number;
  max_fp: number;
}

export interface ImplicitStat {
  stat: string;
  values: { min: number; max: number };
  description: string;
}
