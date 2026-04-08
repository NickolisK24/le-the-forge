/**
 * UI+10 — Favorites System
 * Bookmark commonly used objects (items, skills, builds, affixes).
 */

export type FavoriteType = "build" | "item" | "skill" | "affix" | "enemy" | "preset";

export interface Favorite {
  id: string;
  type: FavoriteType;
  referenceId: string;
  label: string;
  meta: Record<string, unknown>;
  addedAt: number;
}

const STORAGE_KEY = "forge_favorites";

type FavoriteListener = (favorites: Favorite[]) => void;

function makeId(type: FavoriteType, referenceId: string): string {
  return `${type}::${referenceId}`;
}

class FavoriteManagerClass {
  private favorites: Map<string, Favorite> = new Map();
  private listeners: Set<FavoriteListener> = new Set();

  constructor() {
    this.load();
  }

  private load(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const arr = JSON.parse(raw) as Favorite[];
        this.favorites = new Map(arr.map((f) => [makeId(f.type, f.referenceId), f]));
      }
    } catch {
      this.favorites = new Map();
    }
  }

  private save(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...this.favorites.values()]));
    } catch {
      // ignore
    }
    this.notify();
  }

  private notify(): void {
    const snapshot = [...this.favorites.values()];
    this.listeners.forEach((fn) => fn(snapshot));
  }

  subscribe(listener: FavoriteListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  add(
    type: FavoriteType,
    referenceId: string,
    label: string,
    meta: Record<string, unknown> = {}
  ): Favorite {
    const key = makeId(type, referenceId);
    const favorite: Favorite = {
      id: key,
      type,
      referenceId,
      label,
      meta,
      addedAt: Date.now(),
    };
    this.favorites.set(key, favorite);
    this.save();
    return favorite;
  }

  remove(type: FavoriteType, referenceId: string): boolean {
    const key = makeId(type, referenceId);
    const existed = this.favorites.has(key);
    if (existed) {
      this.favorites.delete(key);
      this.save();
    }
    return existed;
  }

  toggle(
    type: FavoriteType,
    referenceId: string,
    label: string,
    meta: Record<string, unknown> = {}
  ): boolean {
    if (this.has(type, referenceId)) {
      this.remove(type, referenceId);
      return false;
    }
    this.add(type, referenceId, label, meta);
    return true;
  }

  has(type: FavoriteType, referenceId: string): boolean {
    return this.favorites.has(makeId(type, referenceId));
  }

  get(type: FavoriteType, referenceId: string): Favorite | null {
    return this.favorites.get(makeId(type, referenceId)) ?? null;
  }

  getAll(): Favorite[] {
    return [...this.favorites.values()].sort((a, b) => b.addedAt - a.addedAt);
  }

  getByType(type: FavoriteType): Favorite[] {
    return this.getAll().filter((f) => f.type === type);
  }

  count(): number {
    return this.favorites.size;
  }

  countByType(type: FavoriteType): number {
    return this.getByType(type).length;
  }

  clear(): void {
    this.favorites.clear();
    this.save();
  }

  clearByType(type: FavoriteType): void {
    for (const [key, fav] of this.favorites) {
      if (fav.type === type) this.favorites.delete(key);
    }
    this.save();
  }
}

export const FavoriteManager = new FavoriteManagerClass();
