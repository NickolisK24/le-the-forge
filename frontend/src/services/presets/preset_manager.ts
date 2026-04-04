/**
 * UI+9 — Preset System
 * Save and load reusable workflow setups.
 */

export interface Preset {
  id: string;
  name: string;
  description: string;
  category: "build" | "craft" | "sim" | "general";
  data: Record<string, unknown>;
  createdAt: number;
  updatedAt: number;
  tags: string[];
}

const STORAGE_KEY = "forge_presets";

type PresetListener = (presets: Preset[]) => void;

function generateId(): string {
  return `preset_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

class PresetManagerClass {
  private presets: Preset[] = [];
  private listeners: Set<PresetListener> = new Set();

  constructor() {
    this.load();
  }

  private load(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      this.presets = raw ? (JSON.parse(raw) as Preset[]) : [];
    } catch {
      this.presets = [];
    }
  }

  private save(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.presets));
    } catch {
      // ignore
    }
    this.notify();
  }

  private notify(): void {
    const snapshot = [...this.presets];
    this.listeners.forEach((fn) => fn(snapshot));
  }

  subscribe(listener: PresetListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  getAll(): Preset[] {
    return [...this.presets];
  }

  getById(id: string): Preset | null {
    return this.presets.find((p) => p.id === id) ?? null;
  }

  getByCategory(category: Preset["category"]): Preset[] {
    return this.presets.filter((p) => p.category === category);
  }

  search(query: string): Preset[] {
    const q = query.toLowerCase();
    return this.presets.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.tags.some((t) => t.toLowerCase().includes(q))
    );
  }

  save_preset(
    name: string,
    data: Record<string, unknown>,
    options: Partial<Pick<Preset, "description" | "category" | "tags">> = {}
  ): Preset {
    const preset: Preset = {
      id: generateId(),
      name: name.trim() || "Unnamed Preset",
      description: options.description ?? "",
      category: options.category ?? "general",
      data,
      tags: options.tags ?? [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    this.presets.unshift(preset);
    this.save();
    return preset;
  }

  update(id: string, changes: Partial<Omit<Preset, "id" | "createdAt">>): Preset | null {
    const idx = this.presets.findIndex((p) => p.id === id);
    if (idx === -1) return null;
    this.presets[idx] = { ...this.presets[idx], ...changes, updatedAt: Date.now() };
    this.save();
    return this.presets[idx];
  }

  delete(id: string): boolean {
    const idx = this.presets.findIndex((p) => p.id === id);
    if (idx === -1) return false;
    this.presets.splice(idx, 1);
    this.save();
    return true;
  }

  apply(id: string): Record<string, unknown> | null {
    const preset = this.getById(id);
    return preset ? { ...preset.data } : null;
  }

  export(id: string): string | null {
    const preset = this.getById(id);
    if (!preset) return null;
    return btoa(JSON.stringify(preset));
  }

  import(encoded: string): Preset | null {
    try {
      const preset = JSON.parse(atob(encoded)) as Preset;
      if (!preset.name || !preset.data) return null;
      preset.id = generateId();
      preset.createdAt = Date.now();
      preset.updatedAt = Date.now();
      this.presets.unshift(preset);
      this.save();
      return preset;
    } catch {
      return null;
    }
  }

  count(): number {
    return this.presets.length;
  }

  clear(): void {
    this.presets = [];
    this.save();
  }
}

export const PresetManager = new PresetManagerClass();
