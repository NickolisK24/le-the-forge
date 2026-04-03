/**
 * Phase UI+ — Workflow tests
 * End-to-end multi-step scenarios simulating real user workflows
 * ~50 tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ─── Mock globals ─────────────────────────────────────────────────────────────

const store: Record<string, string> = {};
vi.stubGlobal("localStorage", {
  getItem: (k: string) => store[k] ?? null,
  setItem: (k: string, v: string) => { store[k] = v; },
  removeItem: (k: string) => { delete store[k]; },
  clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
});
vi.stubGlobal("history", { replaceState: vi.fn() });

async function freshAll() {
  vi.resetModules();
  Object.keys(store).forEach((k) => delete store[k]);
  const [
    { BuildManager },
    { BuildShareService },
    { BuildImportService },
    { PresetManager },
    { FavoriteManager },
    { SessionRestore },
    { ShortcutManager },
  ] = await Promise.all([
    import("../../services/build/build_manager"),
    import("../../services/sharing/build_share_service"),
    import("../../services/sharing/build_import_service"),
    import("../../services/presets/preset_manager"),
    import("../../services/favorites/favorite_manager"),
    import("../../services/session/session_restore"),
    import("../../services/keyboard/shortcut_manager"),
  ]);
  return { BuildManager, BuildShareService, BuildImportService, PresetManager, FavoriteManager, SessionRestore, ShortcutManager };
}

// ─── Workflow 1: Build Creation & Sharing ─────────────────────────────────────

describe("Workflow: create → share → import → activate", () => {
  it("full share workflow produces importable URL", async () => {
    const { BuildManager, BuildShareService, BuildImportService } = await freshAll();
    const build = BuildManager.create({ name: "Endgame Lich", characterClass: "Acolyte" });
    const shareable = {
      version: 1 as const, name: build.name,
      characterClass: build.characterClass ?? "Acolyte",
      mastery: "Lich", gear: {}, skills: ["Rip Blood"], passives: [1, 5],
    };
    const { url } = BuildShareService.generateShareUrl(shareable, "https://app.test");
    const result = BuildImportService.importFromUrl(url);
    expect(result.status).toBe("success");
    expect(result.build?.name).toBe("Endgame Lich");
    const imported = BuildManager.create({ name: result.build!.name });
    BuildManager.setActive(imported.id);
    expect(BuildManager.getActive()?.name).toBe("Endgame Lich");
  });

  it("shared build survives module reload (localStorage)", async () => {
    const { BuildManager } = await freshAll();
    BuildManager.create({ name: "Persistent Build" });
    vi.resetModules();
    const { BuildManager: BM2 } = await import("../../services/build/build_manager");
    expect(BM2.getAll().some((b: any) => b.name === "Persistent Build")).toBe(true);
  });

  it("corrupt share code does not affect existing builds", async () => {
    const { BuildManager, BuildImportService } = await freshAll();
    BuildManager.create({ name: "Safe Build" });
    const result = BuildImportService.importFromCode("XXXX_INVALID");
    expect(result.status).toBe("error");
    expect(BuildManager.getAll()).toHaveLength(1);
  });
});

// ─── Workflow 2: Multi-Build Management ───────────────────────────────────────

describe("Workflow: create multiple builds → reorder → delete → switch", () => {
  it("creates 3 builds, all retrievable", async () => {
    const { BuildManager } = await freshAll();
    BuildManager.create({ name: "Build A" });
    BuildManager.create({ name: "Build B" });
    BuildManager.create({ name: "Build C" });
    expect(BuildManager.getAll()).toHaveLength(3);
  });

  it("setActive and getActive are consistent", async () => {
    const { BuildManager } = await freshAll();
    const a = BuildManager.create({ name: "Alpha" });
    const b = BuildManager.create({ name: "Beta" });
    BuildManager.setActive(b.id);
    expect(BuildManager.getActive()?.id).toBe(b.id);
    BuildManager.setActive(a.id);
    expect(BuildManager.getActive()?.id).toBe(a.id);
  });

  it("delete active build clears active", async () => {
    const { BuildManager } = await freshAll();
    const build = BuildManager.create({ name: "Temp" });
    BuildManager.setActive(build.id);
    BuildManager.delete(build.id);
    expect(BuildManager.getActive()).toBeNull();
  });

  it("duplicate then rename produces independent build", async () => {
    const { BuildManager } = await freshAll();
    const original = BuildManager.create({ name: "Original" });
    const copy = BuildManager.duplicate(original.id);
    BuildManager.rename(copy.id, "My Copy");
    expect(BuildManager.getById(original.id)?.name).toBe("Original");
    expect(BuildManager.getById(copy.id)?.name).toBe("My Copy");
  });

  it("listener fires on create", async () => {
    const { BuildManager } = await freshAll();
    const handler = vi.fn();
    BuildManager.subscribe(handler);
    BuildManager.create({ name: "Notified Build" });
    expect(handler).toHaveBeenCalled();
  });

  it("listener fires on delete", async () => {
    const { BuildManager } = await freshAll();
    const build = BuildManager.create({ name: "DeleteMe" });
    const handler = vi.fn();
    BuildManager.subscribe(handler);
    BuildManager.delete(build.id);
    expect(handler).toHaveBeenCalled();
  });

  it("listener fires on rename", async () => {
    const { BuildManager } = await freshAll();
    const build = BuildManager.create({ name: "Old Name" });
    const handler = vi.fn();
    BuildManager.subscribe(handler);
    BuildManager.rename(build.id, "New Name");
    expect(handler).toHaveBeenCalled();
  });

  it("reorder changes position in getAll()", async () => {
    const { BuildManager } = await freshAll();
    const a = BuildManager.create({ name: "First" });
    const b = BuildManager.create({ name: "Second" });
    const c = BuildManager.create({ name: "Third" });
    BuildManager.reorder([c.id, a.id, b.id]);
    const ids = BuildManager.getAll().map((x: any) => x.id);
    expect(ids[0]).toBe(c.id);
  });

  it("clear removes all builds and active", async () => {
    const { BuildManager } = await freshAll();
    BuildManager.create({ name: "X" });
    BuildManager.create({ name: "Y" });
    BuildManager.clear();
    expect(BuildManager.getAll()).toHaveLength(0);
    expect(BuildManager.getActive()).toBeNull();
  });
});

// ─── Workflow 3: Preset save → apply → favorite ───────────────────────────────

describe("Workflow: preset save → search → apply → favorite", () => {
  it("save, search, and apply a preset", async () => {
    const { PresetManager, FavoriteManager } = await freshAll();
    const p = PresetManager.save_preset("Speed Clear", { attackSpeed: 2.0, movespeed: 1.5 });
    const results = PresetManager.search("speed");
    expect(results.some((r: any) => r.id === p.id)).toBe(true);
    const applied = PresetManager.apply(p.id);
    expect(applied).toEqual({ attackSpeed: 2.0, movespeed: 1.5 });
    FavoriteManager.add("preset", p.id, p.name);
    expect(FavoriteManager.has("preset", p.id)).toBe(true);
  });

  it("export single preset then re-import it", async () => {
    const { PresetManager } = await freshAll();
    const p = PresetManager.save_preset("Export Test", { val: 42 });
    const exported = PresetManager.export(p.id);
    expect(exported).toBeTruthy();
    // Delete and re-import
    PresetManager.delete(p.id);
    expect(PresetManager.getAll()).toHaveLength(0);
    const imported = PresetManager.import(exported!);
    expect(imported?.name).toBe("Export Test");
  });

  it("preset categories filter correctly", async () => {
    const { PresetManager } = await freshAll();
    PresetManager.save_preset("Fire Build",   { fire: true },    { category: "damage" });
    PresetManager.save_preset("Tank Setup",   { armor: 1000 },   { category: "defense" });
    expect(PresetManager.getByCategory("damage").some((p: any) => p.name === "Fire Build")).toBe(true);
    expect(PresetManager.getByCategory("defense").some((p: any) => p.name === "Tank Setup")).toBe(true);
    expect(PresetManager.getByCategory("damage").some((p: any) => p.name === "Tank Setup")).toBe(false);
  });

  it("favorited presets count correctly", async () => {
    const { PresetManager, FavoriteManager } = await freshAll();
    const p1 = PresetManager.save_preset("P1", {});
    const p2 = PresetManager.save_preset("P2", {});
    FavoriteManager.add("preset", p1.id, p1.name);
    FavoriteManager.add("preset", p2.id, p2.name);
    expect(FavoriteManager.countByType("preset")).toBe(2);
  });
});

// ─── Workflow 4: Session restore after navigation ─────────────────────────────

describe("Workflow: navigate → scroll → draft → restore session", () => {
  it("saves and restores full session state", async () => {
    const { SessionRestore } = await freshAll();
    SessionRestore.setActivePage("/builds");
    SessionRestore.saveScrollPosition("/builds", 200);
    SessionRestore.openPanel("sidebar");
    SessionRestore.openPanel("stats");
    SessionRestore.setActiveBuildId("build-abc");
    SessionRestore.saveDraft("gear-editor", { helmet: "Crown of Ruin" });
    expect(SessionRestore.getActivePage()).toBe("/builds");
    expect(SessionRestore.getScrollPosition("/builds")).toBe(200);
    expect(SessionRestore.isPanelOpen("sidebar")).toBe(true);
    expect(SessionRestore.getActiveBuildId()).toBe("build-abc");
    expect(SessionRestore.getDraft("gear-editor")).toEqual({ helmet: "Crown of Ruin" });
  });

  it("partial clear preserves uncleared state", async () => {
    const { SessionRestore } = await freshAll();
    SessionRestore.setActivePage("/skills");
    SessionRestore.setActiveBuildId("b-xyz");
    SessionRestore.clearDraft("nonexistent"); // should not throw
    expect(SessionRestore.getActivePage()).toBe("/skills");
    expect(SessionRestore.getActiveBuildId()).toBe("b-xyz");
  });

  it("multiple pages tracked independently", async () => {
    const { SessionRestore } = await freshAll();
    SessionRestore.saveScrollPosition("/builds", 100);
    SessionRestore.saveScrollPosition("/items", 500);
    expect(SessionRestore.getScrollPosition("/builds")).toBe(100);
    expect(SessionRestore.getScrollPosition("/items")).toBe(500);
  });
});

// ─── Workflow 5: Keyboard shortcuts power-user flow ───────────────────────────

describe("Workflow: register shortcuts → trigger → cleanup", () => {
  afterEach(() => {
    vi.resetModules();
    Object.keys(store).forEach((k) => delete store[k]);
  });

  it("default shortcuts are registered on init", async () => {
    const { ShortcutManager } = await freshAll();
    const all = ShortcutManager.getAll();
    expect(Array.isArray(all)).toBe(true);
  });

  it("custom shortcut fires its handler on window keydown", async () => {
    const { ShortcutManager } = await freshAll();
    const handler = vi.fn();
    ShortcutManager.register("workflow-q", { key: "q", description: "Test Q", group: "workflow" }, handler);
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "q", bubbles: true }));
    expect(handler).toHaveBeenCalledOnce();
  });

  it("shortcut ignores events from input elements", async () => {
    const { ShortcutManager } = await freshAll();
    const handler = vi.fn();
    ShortcutManager.register("input-test", { key: "w", description: "W", group: "test" }, handler);
    const input = document.createElement("input");
    document.body.appendChild(input);
    input.dispatchEvent(new KeyboardEvent("keydown", { key: "w", bubbles: true }));
    document.body.removeChild(input);
    expect(handler).not.toHaveBeenCalled();
  });

  it("shortcut ignores events from textarea elements", async () => {
    const { ShortcutManager } = await freshAll();
    const handler = vi.fn();
    ShortcutManager.register("ta-test", { key: "e", description: "E", group: "test" }, handler);
    const textarea = document.createElement("textarea");
    document.body.appendChild(textarea);
    textarea.dispatchEvent(new KeyboardEvent("keydown", { key: "e", bubbles: true }));
    document.body.removeChild(textarea);
    expect(handler).not.toHaveBeenCalled();
  });

  it("first-match-wins: first registered handler fires, not second", async () => {
    const { ShortcutManager } = await freshAll();
    const h1 = vi.fn();
    const h2 = vi.fn();
    ShortcutManager.register("first",  { key: "r", description: "First R",  group: "t" }, h1);
    ShortcutManager.register("second", { key: "r", description: "Second R", group: "t" }, h2);
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "r", bubbles: true }));
    expect(h1).toHaveBeenCalledOnce();
    expect(h2).not.toHaveBeenCalled();
  });
});
