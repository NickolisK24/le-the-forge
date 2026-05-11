/**
 * Zustand global state stores.
 *
 * Slices:
 *   useAuthStore            — current user + JWT token lifecycle
 *   useCraftStore           — active craft session UI state (not persisted to DB yet)
 *   useBuildWorkspaceStore  — unified build workspace working copy (phase 1)
 */

import { create } from "zustand";
import { setToken } from "@/lib/api";
import type { User, CraftAffix } from "@/types";

export { useBuildWorkspaceStore } from "./buildWorkspace";
export type {
  AnalysisStatus,
  BuildWorkspaceBuild,
  BuildWorkspaceIdentity,
  BuildWorkspaceState,
  WorkspaceMetaPatch,
  WorkspaceStatus,
} from "./buildWorkspace";

// ---------------------------------------------------------------------------
// Auth store
// ---------------------------------------------------------------------------

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,

  setUser: (user) => set({ user }),

  setToken: (token) => {
    setToken(token);
    set({ token });
  },

  login: (token, user) => {
    setToken(token);
    set({ token, user, isLoading: false });
  },

  logout: () => {
    setToken(null);
    set({ user: null, token: null, isLoading: false });
  },
}));

// ---------------------------------------------------------------------------
// Craft session store (local UI state before saving to backend)
// ---------------------------------------------------------------------------

interface CraftUIState {
  itemType: string;
  itemName: string;
  itemLevel: number;
  rarity: string;
  forgePotential: number;
  affixes: CraftAffix[];
  sessionSlug: string | null;

  setItemType: (v: string) => void;
  setItemName: (v: string) => void;
  setItemLevel: (v: number) => void;
  setRarity: (v: string) => void;
  setForgePotential: (v: number) => void;
  setAffixes: (v: CraftAffix[]) => void;
  addAffix: (affix: CraftAffix) => void;
  removeAffix: (name: string) => void;
  updateAffix: (name: string, updates: Partial<CraftAffix>) => void;
  setSessionSlug: (slug: string | null) => void;
  resetSession: () => void;
}

const DEFAULT_CRAFT: Omit<
  CraftUIState,
  | "setItemType" | "setItemName" | "setItemLevel" | "setRarity"
  | "setForgePotential" | "setAffixes"
  | "addAffix" | "removeAffix" | "updateAffix"
  | "setSessionSlug" | "resetSession"
> = {
  itemType: "Wand",
  itemName: "",
  itemLevel: 84,
  rarity: "Exalted",
  forgePotential: 28,
  affixes: [],
  sessionSlug: null,
};

export const useCraftStore = create<CraftUIState>((set) => ({
  ...DEFAULT_CRAFT,

  setItemType: (itemType) => set({ itemType }),
  setItemName: (itemName) => set({ itemName }),
  setItemLevel: (itemLevel) => set({ itemLevel }),
  setRarity: (rarity) => set({ rarity }),
  setForgePotential: (forgePotential) => set({ forgePotential }),
  setAffixes: (affixes) => set({ affixes }),

  addAffix: (affix) =>
    set((state) => {
      const existing = state.affixes;
      // Only unsealed affixes count toward prefix/suffix limits; sealed is a separate slot (max 1)
      const prefixCount = existing.filter((a) => a.type === "prefix" && !a.sealed).length;
      const suffixCount = existing.filter((a) => a.type === "suffix" && !a.sealed).length;
      if (affix.type === "prefix" && prefixCount >= 2) return state;
      if (affix.type === "suffix" && suffixCount >= 2) return state;
      if (!affix.type && existing.filter((a) => !a.sealed).length >= 4) return state;
      return { affixes: [...existing, affix] };
    }),

  removeAffix: (name) =>
    set((state) => ({
      affixes: state.affixes.filter((a) => a.name !== name),
    })),

  updateAffix: (name, updates) =>
    set((state) => {
      // Enforce max 1 sealed
      if (updates.sealed === true) {
        const alreadySealed = state.affixes.filter((a) => a.name !== name && a.sealed).length;
        if (alreadySealed >= 1) return state;
      }
      return {
        affixes: state.affixes.map((a) =>
          a.name === name ? { ...a, ...updates } : a
        ),
      };
    }),

  setSessionSlug: (sessionSlug) => set({ sessionSlug }),

  resetSession: () =>
    set({
      ...DEFAULT_CRAFT,
      affixes: [],
      sessionSlug: null,
    }),
}));
