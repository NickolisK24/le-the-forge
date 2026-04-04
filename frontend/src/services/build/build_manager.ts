/**
 * UI+5 — Multi-Build Manager
 * Create, rename, duplicate, delete, and switch between builds.
 */

export interface ManagedBuild {
  id: string;
  name: string;
  characterClass: string;
  mastery: string;
  gear: Record<string, unknown>;
  skills: string[];
  passives: number[];
  notes: string;
  createdAt: number;
  updatedAt: number;
}

export type BuildManagerListener = (builds: ManagedBuild[], activeId: string | null) => void;

const STORAGE_KEY = "forge_builds";
const ACTIVE_KEY = "forge_active_build";

function generateId(): string {
  return `build_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

function now(): number {
  return Date.now();
}

function defaultBuild(overrides: Partial<ManagedBuild> = {}): ManagedBuild {
  return {
    id: generateId(),
    name: "Untitled Build",
    characterClass: "Acolyte",
    mastery: "Lich",
    gear: {},
    skills: [],
    passives: [],
    notes: "",
    createdAt: now(),
    updatedAt: now(),
    ...overrides,
  };
}

class BuildManagerClass {
  private builds: ManagedBuild[] = [];
  private activeId: string | null = null;
  private listeners: Set<BuildManagerListener> = new Set();

  constructor() {
    this.load();
  }

  // ─── Persistence ────────────────────────────────────────────────────────────

  private load(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      this.builds = raw ? (JSON.parse(raw) as ManagedBuild[]) : [];
      this.activeId = localStorage.getItem(ACTIVE_KEY) ?? (this.builds[0]?.id ?? null);
    } catch {
      this.builds = [];
      this.activeId = null;
    }
  }

  private save(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.builds));
      if (this.activeId) {
        localStorage.setItem(ACTIVE_KEY, this.activeId);
      } else {
        localStorage.removeItem(ACTIVE_KEY);
      }
    } catch {
      // Ignore storage errors (private/incognito mode)
    }
    this.notify();
  }

  private notify(): void {
    const snapshot = [...this.builds];
    this.listeners.forEach((fn) => fn(snapshot, this.activeId));
  }

  // ─── Subscriptions ──────────────────────────────────────────────────────────

  subscribe(listener: BuildManagerListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // ─── Getters ────────────────────────────────────────────────────────────────

  getAll(): ManagedBuild[] {
    return [...this.builds];
  }

  getById(id: string): ManagedBuild | null {
    return this.builds.find((b) => b.id === id) ?? null;
  }

  getActive(): ManagedBuild | null {
    if (!this.activeId) return null;
    return this.getById(this.activeId);
  }

  getActiveId(): string | null {
    return this.activeId;
  }

  count(): number {
    return this.builds.length;
  }

  // ─── Mutations ──────────────────────────────────────────────────────────────

  create(overrides: Partial<ManagedBuild> = {}): ManagedBuild {
    const build = defaultBuild(overrides);
    this.builds.push(build);
    this.activeId = build.id;
    this.save();
    return build;
  }

  update(id: string, changes: Partial<Omit<ManagedBuild, "id" | "createdAt">>): ManagedBuild | null {
    const idx = this.builds.findIndex((b) => b.id === id);
    if (idx === -1) return null;
    this.builds[idx] = { ...this.builds[idx], ...changes, updatedAt: now() };
    this.save();
    return this.builds[idx];
  }

  rename(id: string, name: string): ManagedBuild | null {
    return this.update(id, { name: name.trim() || "Untitled Build" });
  }

  duplicate(id: string): ManagedBuild | null {
    const source = this.getById(id);
    if (!source) return null;
    const copy = defaultBuild({
      ...source,
      id: generateId(),
      name: `${source.name} (Copy)`,
      createdAt: now(),
      updatedAt: now(),
    });
    const idx = this.builds.findIndex((b) => b.id === id);
    this.builds.splice(idx + 1, 0, copy);
    this.activeId = copy.id;
    this.save();
    return copy;
  }

  delete(id: string): boolean {
    const idx = this.builds.findIndex((b) => b.id === id);
    if (idx === -1) return false;
    this.builds.splice(idx, 1);
    if (this.activeId === id) {
      this.activeId = this.builds[Math.max(0, idx - 1)]?.id ?? null;
    }
    this.save();
    return true;
  }

  setActive(id: string): boolean {
    if (!this.builds.find((b) => b.id === id)) return false;
    this.activeId = id;
    this.save();
    return true;
  }

  reorder(ids: string[]): void {
    const map = new Map(this.builds.map((b) => [b.id, b]));
    this.builds = ids.map((id) => map.get(id)).filter(Boolean) as ManagedBuild[];
    this.save();
  }

  clear(): void {
    this.builds = [];
    this.activeId = null;
    this.save();
  }
}

export const BuildManager = new BuildManagerClass();
