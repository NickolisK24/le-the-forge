/**
 * UI+12 — Keyboard Shortcut Manager
 * Register and dispatch global keyboard shortcuts.
 */

export interface ShortcutDef {
  key: string;           // e.g. "s", "z", "f"
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  description: string;
  group?: string;
}

export interface ShortcutBinding extends ShortcutDef {
  id: string;
  handler: () => void;
  enabled: boolean;
}

type ShortcutListener = (bindings: ShortcutBinding[]) => void;

function shortcutKey(def: Pick<ShortcutDef, "key" | "ctrl" | "shift" | "alt" | "meta">): string {
  const parts: string[] = [];
  if (def.ctrl) parts.push("ctrl");
  if (def.meta) parts.push("meta");
  if (def.alt) parts.push("alt");
  if (def.shift) parts.push("shift");
  parts.push(def.key.toLowerCase());
  return parts.join("+");
}

function eventKey(e: KeyboardEvent): string {
  const parts: string[] = [];
  if (e.ctrlKey) parts.push("ctrl");
  if (e.metaKey) parts.push("meta");
  if (e.altKey) parts.push("alt");
  if (e.shiftKey) parts.push("shift");
  parts.push(e.key.toLowerCase());
  return parts.join("+");
}

class ShortcutManagerClass {
  private bindings: Map<string, ShortcutBinding[]> = new Map();
  private listeners: Set<ShortcutListener> = new Set();
  private attached = false;

  constructor() {
    if (typeof window !== "undefined") {
      this.attach();
    }
  }

  private attach(): void {
    if (this.attached) return;
    window.addEventListener("keydown", this.handleKeyDown);
    this.attached = true;
  }

  private detach(): void {
    window.removeEventListener("keydown", this.handleKeyDown);
    this.attached = false;
  }

  private handleKeyDown = (e: KeyboardEvent): void => {
    // Ignore when typing in inputs
    const target = e.target as HTMLElement;
    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
      return;
    }

    const key = eventKey(e);
    const handlers = this.bindings.get(key);
    if (!handlers) return;

    for (const binding of handlers) {
      if (!binding.enabled) continue;
      e.preventDefault();
      binding.handler();
      break; // First matching enabled handler wins
    }
  };

  private notify(): void {
    const all = this.getAll();
    this.listeners.forEach((fn) => fn(all));
  }

  subscribe(listener: ShortcutListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  register(
    id: string,
    def: ShortcutDef,
    handler: () => void
  ): () => void {
    const key = shortcutKey(def);
    const binding: ShortcutBinding = { ...def, id, handler, enabled: true };

    const existing = this.bindings.get(key) ?? [];
    this.bindings.set(key, [...existing, binding]);
    this.notify();

    return () => this.unregister(id, def);
  }

  unregister(id: string, def: ShortcutDef): void {
    const key = shortcutKey(def);
    const existing = this.bindings.get(key) ?? [];
    const filtered = existing.filter((b) => b.id !== id);
    if (filtered.length === 0) {
      this.bindings.delete(key);
    } else {
      this.bindings.set(key, filtered);
    }
    this.notify();
  }

  setEnabled(id: string, enabled: boolean): void {
    for (const bindings of this.bindings.values()) {
      for (const b of bindings) {
        if (b.id === id) b.enabled = enabled;
      }
    }
    this.notify();
  }

  getAll(): ShortcutBinding[] {
    return [...this.bindings.values()].flat();
  }

  getByGroup(group: string): ShortcutBinding[] {
    return this.getAll().filter((b) => b.group === group);
  }

  formatShortcut(def: ShortcutDef): string {
    const parts: string[] = [];
    if (def.ctrl) parts.push("Ctrl");
    if (def.meta) parts.push("⌘");
    if (def.alt) parts.push("Alt");
    if (def.shift) parts.push("Shift");
    parts.push(def.key.toUpperCase());
    return parts.join("+");
  }

  destroy(): void {
    this.detach();
    this.bindings.clear();
    this.listeners.clear();
  }
}

export const ShortcutManager = new ShortcutManagerClass();

// Built-in default shortcuts (registered by components that handle the action)
export const DEFAULT_SHORTCUTS: Record<string, ShortcutDef> = {
  SAVE:   { key: "s", ctrl: true, description: "Save current build", group: "build" },
  UNDO:   { key: "z", ctrl: true, description: "Undo last action", group: "build" },
  REDO:   { key: "z", ctrl: true, shift: true, description: "Redo action", group: "build" },
  SEARCH: { key: "f", ctrl: true, description: "Open global search", group: "navigation" },
  NEW:    { key: "n", ctrl: true, description: "New build", group: "build" },
  CLOSE:  { key: "Escape", description: "Close panel/modal", group: "navigation" },
};
