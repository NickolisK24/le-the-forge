/**
 * API client for The Forge backend.
 *
 * All methods return typed ApiResponse<T> so callers can check
 * data/errors without needing try/catch everywhere.
 *
 * Auth token is stored in module-level memory (not localStorage).
 * The auth store manages the token lifecycle.
 */

import type {
  ApiResponse,
  Build,
  BuildListItem,
  BuildCreatePayload,
  BuildFilters,
  VoteResult,
  CraftSession,
  CraftActionResult,
  CraftSummary,
  CraftSessionCreatePayload,
  CraftPredictResult,
  CraftAffix,
  ClassMeta,
  AffixDef,
  User,
  PaginationMeta,
} from "@/types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

// Token stored in memory — survives page navigation but not hard refresh.
// For "remember me" you'd also persist to sessionStorage.
let _token: string | null = null;

export function setToken(token: string | null) {
  _token = token;
}

export function getToken() {
  return _token;
}

// ---------------------------------------------------------------------------
// Core fetch helper
// ---------------------------------------------------------------------------

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<ApiResponse<T>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (_token) {
    headers["Authorization"] = `Bearer ${_token}`;
  }

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (err) {
    const message =
      err instanceof DOMException && err.name === "AbortError"
        ? "Request cancelled"
        : "Network error — check your connection";
    return { data: null, meta: null, errors: [{ message }] };
  }

  // 204 No Content
  if (res.status === 204) {
    return { data: null, meta: null, errors: null };
  }

  let json: any;
  try {
    json = await res.json();
  } catch {
    return {
      data: null,
      meta: null,
      errors: [{ message: res.ok ? "Invalid response from server" : `Server error (${res.status})` }],
    };
  }

  if (!res.ok) {
    // Backend always returns { errors: [...] } on error
    return {
      data: null,
      meta: null,
      errors: json.errors ?? [{ message: "Unknown error" }],
    };
  }

  return json as ApiResponse<T>;
}

const get = <T>(path: string, signal?: AbortSignal) =>
  request<T>("GET", path, undefined, signal);
const post = <T>(path: string, body?: unknown) => request<T>("POST", path, body);
const patch = <T>(path: string, body?: unknown) => request<T>("PATCH", path, body);
const del = <T>(path: string) => request<T>("DELETE", path);

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export const authApi = {
  me: (signal?: AbortSignal) => get<User>("/auth/me", signal),
  logout: () => post<{ message: string }>("/auth/logout"),
};

// ---------------------------------------------------------------------------
// Builds
// ---------------------------------------------------------------------------

function buildQueryString(filters: BuildFilters & { page?: number; per_page?: number }): string {
  const params = new URLSearchParams();
  const map: Record<string, string | undefined> = {
    class: filters.character_class,
    mastery: filters.mastery,
    tier: filters.tier,
    ssf: filters.is_ssf != null ? String(filters.is_ssf) : undefined,
    hc: filters.is_hc != null ? String(filters.is_hc) : undefined,
    ladder: filters.is_ladder_viable != null ? String(filters.is_ladder_viable) : undefined,
    budget: filters.is_budget != null ? String(filters.is_budget) : undefined,
    cycle: filters.cycle,
    sort: filters.sort,
    q: filters.q,
    page: filters.page != null ? String(filters.page) : undefined,
    per_page: filters.per_page != null ? String(filters.per_page) : undefined,
  };
  for (const [k, v] of Object.entries(map)) {
    if (v !== undefined) params.set(k, v);
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export interface MetaSnapshotEntry {
  class: string;
  count: number;
}

export interface STierBuild {
  id: string;
  slug: string;
  name: string;
  mastery: string;
}

export interface MetaSnapshot {
  total_builds: number;
  most_played_class: string;
  top_mastery: string;
  class_distribution: MetaSnapshotEntry[];
  s_tier_builds: STierBuild[];
}

export const buildsApi = {
  list: (filters: BuildFilters & { page?: number; per_page?: number } = {}) =>
    get<BuildListItem[]>(`/builds${buildQueryString(filters)}`),

  get: (slug: string) => get<Build>(`/builds/${slug}`),

  create: (payload: BuildCreatePayload) => post<Build>("/builds", payload),

  update: (slug: string, payload: Partial<BuildCreatePayload>) =>
    patch<Build>(`/builds/${slug}`, payload),

  delete: (slug: string) => del<null>(`/builds/${slug}`),

  vote: (slug: string, direction: 1 | -1) =>
    post<VoteResult>(`/builds/${slug}/vote`, { direction }),

  metaSnapshot: () => get<MetaSnapshot>("/builds/meta/snapshot"),
};

// ---------------------------------------------------------------------------
// Craft
// ---------------------------------------------------------------------------

export const craftApi = {
  create: (payload: CraftSessionCreatePayload) =>
    post<CraftSession>("/craft", payload),

  get: (slug: string) => get<CraftSession>(`/craft/${slug}`),

  action: (
    slug: string,
    action: string,
    affix_name?: string,
    target_tier?: number,
  ) =>
    post<CraftActionResult>(`/craft/${slug}/action`, {
      action,
      affix_name,
      target_tier,
    }),

  summary: (slug: string) => get<CraftSummary>(`/craft/${slug}/summary`),

  predict: (state: {
    forge_potential: number;
    affixes: CraftAffix[];
    n_simulations?: number;
  }) => post<CraftPredictResult>("/craft/predict", state),

  delete: (slug: string) => del<null>(`/craft/${slug}`),
};

// ---------------------------------------------------------------------------
// Reference data
// ---------------------------------------------------------------------------

export const refApi = {
  classes: () => get<Record<string, ClassMeta>>("/ref/classes"),
  itemTypes: () => get<Array<{ name: string; category: string }>>("/ref/item-types"),
  affixes: (params: { type?: string; slot?: string } = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).filter(([, v]) => v !== undefined) as [string, string][]
      )
    ).toString();
    return get<AffixDef[]>(`/ref/affixes${qs ? "?" + qs : ""}`);
  },
  skills: (charClass?: string) =>
    get<Record<string, string[]>>(`/ref/skills${charClass ? `?class=${charClass}` : ""}`),
  baseItems: () => get<Record<string, BaseItemDef[]>>("/ref/base-items"),
  baseItemsBySlot: (slot: string) => get<BaseItemDef[]>(`/ref/base-items?slot=${encodeURIComponent(slot)}`),
  fpRanges: () => get<Record<string, { min_fp: number; max_fp: number }>>("/ref/fp-ranges"),
};

// ---------------------------------------------------------------------------
// Profile
// ---------------------------------------------------------------------------

export const profileApi = {
  get: () => get<any>("/profile"),
  builds: (page = 1) => get<any>(`/profile/builds?page=${page}&sort=new`),
  sessions: (page = 1) => get<any>(`/profile/sessions?page=${page}`),
};
// ---------------------------------------------------------------------------
// Admin — affix management
// ---------------------------------------------------------------------------

export interface AdminAffixTier {
  tier: number;
  min: number;
  max: number;
}

export interface AdminAffix {
  id: string;
  name: string;
  type: string;
  tags: string[];
  applicable_to: string[];
  class_requirement: string | null;
  stat_key: string | null;
  tiers: AdminAffixTier[];
}

export const adminApi = {
  affixes: (params: { q?: string; type?: string; tag?: string; slot?: string } = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).filter(([, v]) => v !== undefined && v !== "") as [string, string][]
      )
    ).toString();
    return get<AdminAffix[]>(`/admin/affixes${qs ? "?" + qs : ""}`);
  },

  updateAffix: (id: string, payload: Partial<Omit<AdminAffix, "id">>) =>
    patch<AdminAffix>(`/admin/affixes/${id}`, payload),
};

export interface VersionInfo {
  version: string;
  commit: string;
  data_version: string;
  current_patch: string;
}

export const versionApi = {
  get: () => get<VersionInfo>("/version"),
};

// ---------------------------------------------------------------------------
// Simulation results
// ---------------------------------------------------------------------------

export interface DPSResult {
  hit_damage: number;
  average_hit: number;
  dps: number;
  effective_attack_speed: number;
  crit_contribution_pct: number;
  flat_damage_added: number;
  bleed_dps: number;
  ignite_dps: number;
  poison_dps: number;
  ailment_dps: number;
  total_dps: number;
}

export interface MonteCarloDPS {
  mean_dps: number;
  min_dps: number;
  max_dps: number;
  std_dev: number;
  percentile_25: number;
  percentile_75: number;
  n_simulations: number;
}

export interface StatUpgrade {
  stat: string;
  label: string;
  dps_gain_pct: number;
  ehp_gain_pct: number;
  explanation?: string;
}

export interface DefenseResult {
  max_health: number;
  effective_hp: number;
  armor_reduction_pct: number;
  avg_resistance: number;
  fire_res: number;
  cold_res: number;
  lightning_res: number;
  void_res: number;
  necrotic_res: number;
  physical_res: number;
  poison_res: number;
  dodge_chance_pct: number;
  block_chance_pct: number;
  block_mitigation_pct: number;
  endurance_pct: number;
  endurance_threshold_pct: number;
  crit_avoidance_pct: number;
  glancing_blow_pct: number;
  stun_avoidance_pct: number;
  ward_buffer: number;
  total_ehp: number;
  ward_regen_per_second: number;
  ward_decay_per_second: number;
  net_ward_per_second: number;
  leech_pct: number;
  health_on_kill: number;
  mana_on_kill: number;
  ward_on_kill: number;
  health_regen: number;
  mana_regen: number;
  survivability_score: number;
  sustain_score: number;
  weaknesses: string[];
  strengths: string[];
}

export interface SkillDpsEntry {
  skill_name: string;
  skill_level: number;
  slot: number;
  dps: number;
  total_dps: number;
  is_primary: boolean;
}

export interface BuildSimulationResult {
  primary_skill: string;
  skill_level: number;
  stats: Record<string, number>;
  dps: DPSResult;
  monte_carlo: MonteCarloDPS;
  defense: DefenseResult;
  stat_upgrades: StatUpgrade[];
  seed: number | null;
  dps_per_skill: SkillDpsEntry[];
  combined_dps: number;
}

export const simulateApi = {
  build: (slug: string) =>
    post<BuildSimulationResult>(`/builds/${slug}/simulate`),
};

// ---------------------------------------------------------------------------
// Import API
// ---------------------------------------------------------------------------

export interface ImportedBuild {
  name: string;
  description: string;
  character_class: string;
  mastery: string;
  level: number;
  passive_tree: number[];
  skills: Array<{
    skill_name: string;
    slot: number;
    points_allocated: number;
    spec_tree: number[];
  }>;
  gear: unknown[];
  _import_meta?: {
    source: string;
    char_class_id: number;
    mastery_id: number;
    skill_count: number;
    passive_nodes: number;
    gear_note: string;
  };
}

export const importApi = {
  fromUrl: (url: string) =>
    post<{ build: ImportedBuild; source_code: string }>("/import/url", { url }),
};

// ---------------------------------------------------------------------------
// Unique items reference
// ---------------------------------------------------------------------------

export interface BaseItemDef {
  name: string;
  level_req: number;
  min_fp: number;
  max_fp: number;
  armor: number;
  implicit: string | null;
  tags: string[];
}

export interface UniqueItem {
  id: string;
  name: string;
  slot: string;
  base: string;
  level_req?: number;
  implicit: string | null;
  affixes: string[];
  unique_effects: string[];
  tags: string[];
  lore?: string;
}

/** Meta-slot categories understood by the backend */
export const WEAPON_META_SLOT  = "weapon";   // sword/axe/mace/dagger/sceptre/wand/staff/bow/spear
export const OFFHAND_META_SLOT = "offhand";  // shield/quiver/catalyst
export const IDOL_META_SLOT    = "idol";     // all idol sizes

export const uniquesApi = {
  list: (params: { slot?: string; q?: string } = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).filter(([, v]) => v !== undefined && v !== "") as [string, string][]
      )
    ).toString();
    return get<UniqueItem[]>(`/ref/uniques${qs ? "?" + qs : ""}`);
  },
  get: (slug: string) => get<UniqueItem>(`/ref/uniques/${slug}`),
};

