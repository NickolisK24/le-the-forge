/**
 * Custom React hooks for data fetching.
 * All built on @tanstack/react-query for caching, deduplication, and
 * background refetching.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { buildsApi, craftApi, refApi } from "@/lib/api";
import type {
  BuildFilters,
  BuildCreatePayload,
  CraftSessionCreatePayload,
} from "@/types";

// ---------------------------------------------------------------------------
// Query key factories
// ---------------------------------------------------------------------------

export const qk = {
  builds: {
    all: ["builds"] as const,
    list: (filters: BuildFilters) => ["builds", "list", filters] as const,
    detail: (slug: string) => ["builds", "detail", slug] as const,
  },
  craft: {
    detail: (slug: string) => ["craft", slug] as const,
    summary: (slug: string) => ["craft", slug, "summary"] as const,
  },
  ref: {
    classes: () => ["ref", "classes"] as const,
    affixes: (params: object) => ["ref", "affixes", params] as const,
    itemTypes: () => ["ref", "item-types"] as const,
  },
};

// ---------------------------------------------------------------------------
// Builds
// ---------------------------------------------------------------------------

export function useBuilds(
  filters: import("@/types").BuildFilters & { page?: number } = {},
) {
  return useQuery({
    queryKey: qk.builds.list(filters),
    queryFn: () => buildsApi.list({ per_page: 20, ...filters }),
  });
}

export function useVote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ slug, direction }: { slug: string; direction: 1 | -1 }) =>
      buildsApi.vote(slug, direction),
    onSuccess: (data, { slug }) => {
      // Update cache directly — do NOT invalidate detail (would re-fetch and increment views)
      if (data.data) {
        qc.setQueryData(qk.builds.detail(slug), (old: any) => {
          if (!old?.data) return old;
          return {
            ...old,
            data: {
              ...old.data,
              vote_count: data.data!.vote_count,
              user_vote: data.data!.user_vote,
              tier: data.data!.tier,
            },
          };
        });
      }
      // Only invalidate list queries — NOT builds.all, which would also match
      // the detail query and trigger a re-fetch that increments view_count.
      qc.invalidateQueries({ queryKey: ["builds", "list"] });
    },
  });
}

export function useBuild(slug: string) {
  return useQuery({
    queryKey: qk.builds.detail(slug),
    queryFn: () => buildsApi.get(slug),
    enabled: Boolean(slug),
  });
}

export function useCreateBuild() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: BuildCreatePayload) => buildsApi.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.builds.all });
    },
  });
}

export function useDeleteBuild() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (slug: string) => buildsApi.delete(slug),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.builds.all });
    },
  });
}

// ---------------------------------------------------------------------------
// Craft
// ---------------------------------------------------------------------------

export function useCraftSession(slug: string) {
  return useQuery({
    queryKey: qk.craft.detail(slug),
    queryFn: () => craftApi.get(slug),
    enabled: Boolean(slug),
    refetchInterval: false,
  });
}

export function useCraftSummary(slug: string) {
  return useQuery({
    queryKey: qk.craft.summary(slug),
    queryFn: () => craftApi.summary(slug),
    enabled: Boolean(slug),
  });
}

export function useCreateCraftSession() {
  return useMutation({
    mutationFn: (payload: CraftSessionCreatePayload) => craftApi.create(payload),
  });
}

export function useCraftAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      slug,
      action,
      affixName,
      targetTier,
    }: {
      slug: string;
      action: string;
      affixName?: string;
      targetTier?: number;
    }) => craftApi.action(slug, action, affixName, targetTier),
    onSuccess: (_data, { slug }) => {
      qc.invalidateQueries({ queryKey: qk.craft.detail(slug) });
      qc.invalidateQueries({ queryKey: qk.craft.summary(slug) });
    },
  });
}

// ---------------------------------------------------------------------------
// Reference data
// ---------------------------------------------------------------------------

export function useClasses() {
  return useQuery({
    queryKey: qk.ref.classes(),
    queryFn: () => refApi.classes(),
    staleTime: Infinity,
  });
}

export function useAffixes(params: { type?: string; slot?: string } = {}) {
  return useQuery({
    queryKey: qk.ref.affixes(params),
    queryFn: () => refApi.affixes(params),
    staleTime: Infinity,
  });
}

export function useItemTypes() {
  return useQuery({
    queryKey: qk.ref.itemTypes(),
    queryFn: () => refApi.itemTypes(),
    staleTime: Infinity,
  });
}

// ---------------------------------------------------------------------------
// Profile
// ---------------------------------------------------------------------------

import { profileApi } from "@/lib/api";

export function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: () => profileApi.get(),
    staleTime: 30_000,
  });
}

export function useProfileBuilds(page = 1) {
  return useQuery({
    queryKey: ["profile", "builds", page],
    queryFn: () => profileApi.builds(page),
    staleTime: 30_000,
  });
}

export function useProfileSessions(page = 1) {
  return useQuery({
    queryKey: ["profile", "sessions", page],
    queryFn: () => profileApi.sessions(page),
    staleTime: 30_000,
  });
}