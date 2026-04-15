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
export { type BaseClass, type Mastery, type DamageType, type EquipmentSlot, type ItemRarity } from "@constants";
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
  blessings: import("./blessings").SelectedBlessing[];
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
  blessings?: import("./blessings").SelectedBlessing[];
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

export type CraftOutcome = "success" | "perfect" | "fracture" | "error";

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
  completion_rate: number;
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

// ---------------------------------------------------------------------------
// Phase 4 — Optimization (sensitivity + ranking + efficiency)
// ---------------------------------------------------------------------------

export type OptimizeMode = "balanced" | "offense" | "defense";

export interface StatRankingEntry {
  stat_key: string;
  label: string;
  dps_gain_pct: number;
  ehp_gain_pct: number;
  impact_score: number;
  rank: number;
}

export interface UpgradeCandidate {
  affix_id: string;
  label: string;
  dps_gain_pct: number;
  ehp_gain_pct: number;
  fp_cost: number;
  efficiency_score: number;
  rank: number;
}

export interface OptimizeResponse {
  stat_rankings: StatRankingEntry[];
  top_upgrade_candidates: UpgradeCandidate[];
  mode: OptimizeMode;
  offense_weight: number;
  defense_weight: number;
  base_dps: number;
  base_ehp: number;
  generated_at: string;
}

// ---------------------------------------------------------------------------
// Phase 5 — Skill Tree API
// ---------------------------------------------------------------------------

export interface SkillNodeStat {
  statName: string;
  value: string;
  noScaling: boolean;
  downside: boolean;
}

export interface SkillNodeRequirement {
  node: number;
  requirement: number;
}

export interface SkillNodeTransform {
  x: number;
  y: number;
  scale?: number;
  rotation?: number;
}

export interface SkillNode {
  id: number;
  name: string;
  description: string;
  maxPoints: number;
  stats: SkillNodeStat[];
  requirements: SkillNodeRequirement[];
  transform: SkillNodeTransform;
  icon: string | number | null;
  abilityGrantedByNode: string | null;
}

export interface SkillTreeResponse {
  skill_id: string;
  skill_name: string;
  nodes: SkillNode[];
  root_node_id: number;
}

export interface SkillAllocation {
  skill_id: string;
  skill_name: string;
  slot: number;
  allocated_nodes: Record<string, number>;
  total_points: number;
}

export interface SkillAllocationsResponse {
  skills: SkillAllocation[];
}

// ---------------------------------------------------------------------------
// Phase 6 — Build Import
// ---------------------------------------------------------------------------

export interface ImportBuildRequest {
  url: string;
}

export interface ImportBuildResponse {
  slug: string;
  build_name: string;
  source: string;
  imported_fields: string[];
  missing_fields: string[];
  warnings: string[];
}

export interface ImportFailure {
  id: string;
  source: string;
  raw_url: string;
  missing_fields: string[];
  partial_data: Record<string, unknown> | null;
  user_id: string | null;
  error_message: string | null;
  created_at: string | null;
}

// ---------------------------------------------------------------------------
// Phase 7 — Advanced Analysis
// ---------------------------------------------------------------------------

export interface BossPhaseResult {
  phase: number;
  health_threshold: number;
  dps: number;
  ttk_seconds: number;
  survival_score: number;
  mana_sustainable: boolean;
  warnings: string[];
}

export interface BossSummary {
  total_ttk_seconds: number;
  can_kill_before_enrage: boolean;
  overall_survival_score: number;
  weakest_phase: number;
}

export interface BossAnalysisResponse {
  boss_id: string;
  boss_name: string;
  corruption: number;
  phases: BossPhaseResult[];
  summary: BossSummary;
  warnings: string[];
}

export interface CorruptionDataPoint {
  corruption: number;
  dps_efficiency: number;
  survivability_score: number;
}

export interface CorruptionAnalysisResponse {
  boss_id: string;
  recommended_max_corruption: number;
  curve: CorruptionDataPoint[];
}

export interface GearUpgradeCandidate {
  item_name: string;
  base_type: string;
  slot: string;
  affixes: Record<string, unknown>[];
  dps_delta_pct: number;
  ehp_delta_pct: number;
  fp_cost: number;
  efficiency_score: number;
  rank: number;
}

export interface SlotUpgradeResult {
  slot: string;
  candidates: GearUpgradeCandidate[];
}

export interface GearUpgradeResponse {
  slots: SlotUpgradeResult[];
  top_10_overall: GearUpgradeCandidate[];
}

export interface BossListItem {
  id: string;
  name: string;
  category: string;
}

// ---------------------------------------------------------------------------
// Phase 8 — Community Tools
// ---------------------------------------------------------------------------

// Build Comparison
export interface DPSComparisonData {
  raw_dps_a: number;
  raw_dps_b: number;
  crit_contribution_a: number;
  crit_contribution_b: number;
  ailment_dps_a: number;
  ailment_dps_b: number;
  total_dps_a: number;
  total_dps_b: number;
  winner: "a" | "b" | "tie";
}

export interface EHPComparisonData {
  max_health_a: number;
  max_health_b: number;
  effective_hp_a: number;
  effective_hp_b: number;
  armor_reduction_pct_a: number;
  armor_reduction_pct_b: number;
  avg_resistance_a: number;
  avg_resistance_b: number;
  survivability_score_a: number;
  survivability_score_b: number;
  winner: "a" | "b" | "tie";
}

export interface StatDelta {
  stat_key: string;
  value_a: number;
  value_b: number;
  delta: number;
}

export interface SkillComparisonData {
  skills_a: Array<{ skill_name: string; points_allocated: number; slot: number }>;
  skills_b: Array<{ skill_name: string; points_allocated: number; slot: number }>;
  shared: string[];
  unique_to_a: string[];
  unique_to_b: string[];
}

export interface GearSlotComparisonData {
  slot: string;
  item_a: string | null;
  rarity_a: string | null;
  item_b: string | null;
  rarity_b: string | null;
}

export interface ComparisonResult {
  slug_a: string;
  slug_b: string;
  name_a: string;
  name_b: string;
  dps: DPSComparisonData;
  ehp: EHPComparisonData;
  stat_deltas: StatDelta[];
  overall_winner: "a" | "b" | "tie";
  overall_score_a: number;
  overall_score_b: number;
  skill_comparison: SkillComparisonData;
  gear_comparison: GearSlotComparisonData[];
}

// Meta Analytics
export interface ClassDistEntry {
  class: string;
  count: number;
  percentage: number;
}

export interface MasteryDistEntry {
  mastery: string;
  count: number;
  percentage: number;
}

export interface PopularSkillEntry {
  skill_name: string;
  usage_count: number;
}

export interface PopularAffixEntry {
  affix_name: string;
  usage_count: number;
}

export interface TrendingBuild {
  id: string;
  slug: string;
  name: string;
  character_class: string;
  mastery: string;
  tier: string | null;
  vote_count: number;
  view_count: number;
  trending_score: number;
  author: string | null;
}

export interface FullMetaSnapshot {
  class_distribution: ClassDistEntry[];
  mastery_distribution: Record<string, MasteryDistEntry[]>;
  popular_skills: PopularSkillEntry[];
  popular_affixes: PopularAffixEntry[];
  average_stats_by_class: Array<{
    class: string;
    build_count: number;
    avg_votes: number;
    avg_views: number;
  }>;
  patch_breakdown: Array<{ patch_version: string; count: number }>;
  last_updated: string;
  current_patch: string;
}

// Build Report
export interface BuildReportIdentity {
  name: string;
  character_class: string;
  mastery: string;
  level: number;
  patch_version: string;
  author: string | null;
  slug: string;
}

export interface BuildReport {
  identity: BuildReportIdentity;
  stat_summary: Record<string, number>;
  dps_summary: {
    total_dps: number;
    raw_dps: number;
    crit_contribution_pct: number;
    ailment_dps: number;
    hit_damage: number;
    average_hit: number;
  };
  ehp_summary: {
    effective_hp: number;
    max_health: number;
    armor_reduction_pct: number;
    avg_resistance: number;
    survivability_score: number;
    dodge_chance_pct: number;
    block_chance_pct: number;
  };
  top_upgrades: Array<{
    stat: string;
    label: string;
    dps_gain_pct: number;
    ehp_gain_pct: number;
    explanation?: string;
  }>;
  skills: Array<{
    skill_name: string;
    slot: number;
    points_allocated: number;
    node_count: number;
  }>;
  gear: Array<{
    slot: string;
    item_name: string | null;
    rarity: string | null;
    affix_count: number;
  }>;
  generated_at: string;
  og_title: string;
  og_description: string;
  og_url: string;
}

export interface OpenGraphMeta {
  og_title: string;
  og_description: string;
  og_url: string;
}

