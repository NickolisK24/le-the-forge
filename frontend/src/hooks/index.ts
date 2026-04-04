/**
 * Custom React hooks for data fetching.
 * All built on @tanstack/react-query for caching, deduplication, and
 * background refetching.
 */

import { useState, useCallback, useEffect, useRef } from "react";
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

export function useUpdateBuild() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ slug, payload }: { slug: string; payload: Partial<BuildCreatePayload> }) =>
      buildsApi.update(slug, payload),
    onSuccess: (_data, { slug }) => {
      // Update detail cache directly (no re-fetch = no view increment)
      qc.setQueryData(qk.builds.detail(slug), (old: any) => {
        if (!old?.data || !_data.data) return old;
        return { ...old, data: _data.data };
      });
      qc.invalidateQueries({ queryKey: ["builds", "list"] });
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

export function useBaseItems() {
  return useQuery({
    queryKey: ["ref", "base-items"],
    queryFn: () => refApi.baseItems(),
    staleTime: Infinity,
  });
}

export function useFpRanges() {
  return useQuery({
    queryKey: ["ref", "fp-ranges"],
    queryFn: () => refApi.fpRanges(),
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

// ---------------------------------------------------------------------------
// UI24 — Undo / Redo
// ---------------------------------------------------------------------------

interface UndoRedoOptions {
  maxHistory?: number;
}

export function useUndoRedo<T>(initialState: T, options: UndoRedoOptions = {}) {
  const { maxHistory = 50 } = options;
  const [past, setPast] = useState<T[]>([]);
  const [present, setPresent] = useState<T>(initialState);
  const [future, setFuture] = useState<T[]>([]);

  const canUndo = past.length > 0;
  const canRedo = future.length > 0;

  const push = useCallback(
    (newState: T) => {
      setPast((p) => [...p.slice(-(maxHistory - 1)), present]);
      setPresent(newState);
      setFuture([]);
    },
    [present, maxHistory]
  );

  const undo = useCallback(() => {
    if (!canUndo) return;
    const prev = past[past.length - 1];
    setPast((p) => p.slice(0, -1));
    setFuture((f) => [present, ...f]);
    setPresent(prev);
  }, [past, present, canUndo]);

  const redo = useCallback(() => {
    if (!canRedo) return;
    const next = future[0];
    setFuture((f) => f.slice(1));
    setPast((p) => [...p, present]);
    setPresent(next);
  }, [future, present, canRedo]);

  const reset = useCallback((state: T) => {
    setPast([]);
    setPresent(state);
    setFuture([]);
  }, []);

  return { state: present, push, undo, redo, reset, canUndo, canRedo };
}

// ---------------------------------------------------------------------------
// UI25 — Autosave
// ---------------------------------------------------------------------------

type SaveStatus = "idle" | "saving" | "saved" | "error";

interface AutosaveOptions {
  debounceMs?: number;
  onSave: (data: unknown) => Promise<void>;
  enabled?: boolean;
}

export function useAutosave(
  data: unknown,
  options: AutosaveOptions
): SaveStatus {
  const { debounceMs = 1500, onSave, enabled = true } = options;
  const [status, setStatus] = useState<SaveStatus>("idle");
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dataRef = useRef(data);
  const mountedRef = useRef(true);

  useEffect(() => {
    dataRef.current = data;
  }, [data]);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!enabled) return;

    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(async () => {
      if (!mountedRef.current) return;
      setStatus("saving");
      try {
        await onSave(dataRef.current);
        if (mountedRef.current) setStatus("saved");
        // Reset to idle after 2s
        setTimeout(() => {
          if (mountedRef.current) setStatus("idle");
        }, 2000);
      } catch {
        if (mountedRef.current) setStatus("error");
      }
    }, debounceMs);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [data, debounceMs, onSave, enabled]);

  return status;
}
