/**
 * Zustand global state stores.
 *
 * Two slices:
 *   useAuthStore  — current user + JWT token lifecycle
 *   useCraftStore — active craft session UI state (not persisted to DB yet)
 */

import { create } from "zustand";
import { setToken } from "@/lib/api";
import type { User, CraftAffix } from "@/types";

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
  instability: number;
  forgePotential: number;
  affixes: CraftAffix[];
  sessionSlug: string | null;
  isFractured: boolean;

  setItemType: (v: string) => void;
  setItemName: (v: string) => void;
  setItemLevel: (v: number) => void;
  setRarity: (v: string) => void;
  setInstability: (v: number) => void;
  setForgePotential: (v: number) => void;
  setAffixes: (v: CraftAffix[]) => void;
  addAffix: (affix: CraftAffix) => void;
  removeAffix: (name: string) => void;
  updateAffix: (name: string, updates: Partial<CraftAffix>) => void;
  setSessionSlug: (slug: string | null) => void;
  setFractured: (v: boolean) => void;
  resetSession: () => void;
}

const DEFAULT_CRAFT: Omit<
  CraftUIState,
  | "setItemType" | "setItemName" | "setItemLevel" | "setRarity"
  | "setInstability" | "setForgePotential" | "setAffixes"
  | "addAffix" | "removeAffix" | "updateAffix"
  | "setSessionSlug" | "setFractured" | "resetSession"
> = {
  itemType: "Wand",
  itemName: "",
  itemLevel: 84,
  rarity: "Exalted",
  instability: 0,
  forgePotential: 28,
  affixes: [],
  sessionSlug: null,
  isFractured: false,
};

export const useCraftStore = create<CraftUIState>((set) => ({
  ...DEFAULT_CRAFT,

  setItemType: (itemType) => set({ itemType }),
  setItemName: (itemName) => set({ itemName }),
  setItemLevel: (itemLevel) => set({ itemLevel }),
  setRarity: (rarity) => set({ rarity }),
  setInstability: (instability) => set({ instability }),
  setForgePotential: (forgePotential) => set({ forgePotential }),
  setAffixes: (affixes) => set({ affixes }),

  addAffix: (affix) =>
    set((state) => {
      if (state.affixes.length >= 4) return state;
      return { affixes: [...state.affixes, affix] };
    }),

  removeAffix: (name) =>
    set((state) => ({
      affixes: state.affixes.filter((a) => a.name !== name),
    })),

  updateAffix: (name, updates) =>
    set((state) => ({
      affixes: state.affixes.map((a) =>
        a.name === name ? { ...a, ...updates } : a
      ),
    })),

  setSessionSlug: (sessionSlug) => set({ sessionSlug }),
  setFractured: (isFractured) => set({ isFractured }),

  resetSession: () =>
    set({
      ...DEFAULT_CRAFT,
      affixes: [],
      sessionSlug: null,
      isFractured: false,
    }),
}));
