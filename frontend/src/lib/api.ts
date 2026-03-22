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
  CraftSimulatePayload,
  CraftSimulateResult,
  SimulateStatsPayload,
  BuildStatsResult,
  SimulateCombatPayload,
  SimulateCombatResult,
  SimulateDefensePayload,
  DefenseResult,
  SimulateOptimizePayload,
  StatUpgrade,
  SimulateBuildPayload,
  SimulateBuildResult,
  EnemyProfile,
  DamageType,
  Rarity,
  ImplicitStat,
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

export async function request<T>(
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

  const json = await res.json();

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
    instability: number;
    forge_potential: number;
    affixes: CraftAffix[];
    n_simulations?: number;
  }) => post<CraftPredictResult>("/craft/predict", state),

  simulate: (payload: CraftSimulatePayload) =>
    post<CraftSimulateResult>("/craft/simulate", payload),

  delete: (slug: string) => del<null>(`/craft/${slug}`),
};

// ---------------------------------------------------------------------------
// Simulation (stateless engine endpoints)
// ---------------------------------------------------------------------------

export const simulateApi = {
  stats: (payload: SimulateStatsPayload) =>
    post<BuildStatsResult>("/simulate/stats", payload),

  combat: (payload: SimulateCombatPayload) =>
    post<SimulateCombatResult>("/simulate/combat", payload),

  defense: (payload: SimulateDefensePayload) =>
    post<DefenseResult>("/simulate/defense", payload),

  optimize: (payload: SimulateOptimizePayload) =>
    post<StatUpgrade[]>("/simulate/optimize", payload),

  build: (payload: SimulateBuildPayload) =>
    post<SimulateBuildResult>("/simulate/build", payload),
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
  baseItems: () => get<Record<string, { min_fp: number; max_fp: number; implicit: string | null; armor: number }>>("/ref/base-items"),
  fpRanges: () => get<Record<string, { min_fp: number; max_fp: number }>>("/ref/fp-ranges"),
  enemyProfiles: () => get<EnemyProfile[]>("/ref/enemy-profiles"),
  enemyProfile: (id: string) => get<EnemyProfile>(`/ref/enemy-profiles/${id}`),
  damageTypes: () => get<DamageType[]>("/ref/damage-types"),
  rarities: () => get<Rarity[]>("/ref/rarities"),
  implicitStats: () => get<Record<string, ImplicitStat | null>>("/ref/implicit-stats"),
  implicitStat: (itemType: string) => get<ImplicitStat | null>(`/ref/implicit-stats/${itemType}`),
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
// Admin — affix editor
// ---------------------------------------------------------------------------

export interface AdminAffixTier {
  tier: number;
  min: number;
  max: number;
}

export interface AdminAffix {
  id: string;
  name: string;
  type: "prefix" | "suffix";
  tags: string[];
  applicable_to: string[];
  class_requirement: string | null;
  tiers: AdminAffixTier[];
  stat_key: string | null;
}

export interface AdminAffixFilters {
  q?: string;
  type?: string;
  tag?: string;
  slot?: string;
}

export const adminApi = {
  affixes: (filters: AdminAffixFilters = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== undefined && v !== "") as [string, string][]
      )
    ).toString();
    return get<AdminAffix[]>(`/admin/affixes${qs ? "?" + qs : ""}`);
  },
  updateAffix: (id: string, patch: Partial<Omit<AdminAffix, "id">>) =>
    request<AdminAffix>("PATCH", `/admin/affixes/${id}`, patch),
};