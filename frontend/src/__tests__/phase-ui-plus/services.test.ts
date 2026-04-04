/**
 * UI+9, UI+10, UI+11, UI+12 — Service tests
 * PresetManager, FavoriteManager, SessionRestore, ShortcutManager
 * 85 tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ─── Mock localStorage ────────────────────────────────────────────────────────

const store: Record<string, string> = {};
vi.stubGlobal("localStorage", {
  getItem: (k: string) => store[k] ?? null,
  setItem: (k: string, v: string) => { store[k] = v; },
  removeItem: (k: string) => { delete store[k]; },
  clear: () => { Object.keys(store).forEach(k => delete store[k]); },
});

async function fresh<T>(path: string, key: string): Promise<T> {
  vi.resetModules();
  Object.keys(store).forEach(k => delete store[k]);
  const mod = await import(path);
  return mod[key] as T;
}

// ─── PresetManager ────────────────────────────────────────────────────────────

describe("PresetManager — save & retrieve", () => {
  it("saves a preset and returns it", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const p = pm.save_preset("My Preset", { key: "value" });
    expect(p.name).toBe("My Preset");
    expect(p.data).toEqual({ key: "value" });
  });

  it("assigns unique ids", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const a = pm.save_preset("A", {});
    const b = pm.save_preset("B", {});
    expect(a.id).not.toBe(b.id);
  });

  it("getAll returns all presets", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    pm.save_preset("X", {});
    pm.save_preset("Y", {});
    expect(pm.getAll()).toHaveLength(2);
  });

  it("getById returns the correct preset", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const p = pm.save_preset("Find Me", { a: 1 });
    expect(pm.getById(p.id)?.name).toBe("Find Me");
  });

  it("getById returns null for unknown id", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(pm.getById("nope")).toBeNull();
  });

  it("getByCategory filters correctly", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    pm.save_preset("Build", {}, { category: "build" });
    pm.save_preset("Craft", {}, { category: "craft" });
    const builds = pm.getByCategory("build");
    expect(builds).toHaveLength(1);
    expect(builds[0].name).toBe("Build");
  });

  it("search finds by name", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    pm.save_preset("Fire Build", {});
    pm.save_preset("Ice Build", {});
    expect(pm.search("fire")).toHaveLength(1);
  });

  it("search finds by description", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    pm.save_preset("X", {}, { description: "high damage setup" });
    expect(pm.search("high damage")).toHaveLength(1);
  });

  it("search finds by tag", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    pm.save_preset("Y", {}, { tags: ["speedrun", "ssf"] });
    expect(pm.search("speedrun")).toHaveLength(1);
  });

  it("apply returns a copy of preset data", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const p = pm.save_preset("Apply Me", { val: 42 });
    const data = pm.apply(p.id);
    expect(data).toEqual({ val: 42 });
  });

  it("apply returns null for unknown id", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(pm.apply("nope")).toBeNull();
  });

  it("delete removes the preset", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const p = pm.save_preset("Deletable", {});
    pm.delete(p.id);
    expect(pm.getById(p.id)).toBeNull();
  });

  it("delete returns false for unknown id", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(pm.delete("nope")).toBe(false);
  });

  it("export produces a string", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const p = pm.save_preset("Exportable", { x: 1 });
    const exported = pm.export(p.id);
    expect(typeof exported).toBe("string");
    expect(exported!.length).toBeGreaterThan(0);
  });

  it("import round-trips a preset", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const p = pm.save_preset("Round Trip", { val: 99 });
    const exported = pm.export(p.id);
    pm.clear();
    const imported = pm.import(exported!);
    expect(imported?.data).toEqual({ val: 99 });
  });

  it("import returns null for garbage", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(pm.import("not_base64!!!")).toBeNull();
  });

  it("count returns correct number", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    pm.save_preset("A", {});
    pm.save_preset("B", {});
    expect(pm.count()).toBe(2);
  });

  it("clear empties all presets", async () => {
    const pm = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    pm.save_preset("X", {});
    pm.clear();
    expect(pm.count()).toBe(0);
  });
});

// ─── FavoriteManager ──────────────────────────────────────────────────────────

describe("FavoriteManager — add & query", () => {
  it("add returns a favorite object", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    const fav = fm.add("build", "build-1", "My Lich");
    expect(fav.type).toBe("build");
    expect(fav.referenceId).toBe("build-1");
    expect(fav.label).toBe("My Lich");
  });

  it("has returns true after adding", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("item", "sword-1", "Sword");
    expect(fm.has("item", "sword-1")).toBe(true);
  });

  it("has returns false before adding", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    expect(fm.has("skill", "fireball")).toBe(false);
  });

  it("remove returns true on success", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("skill", "ice-bolt", "Ice Bolt");
    expect(fm.remove("skill", "ice-bolt")).toBe(true);
  });

  it("remove returns false for non-existent", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    expect(fm.remove("skill", "nope")).toBe(false);
  });

  it("toggle adds when not favorited", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    const added = fm.toggle("build", "x", "X");
    expect(added).toBe(true);
    expect(fm.has("build", "x")).toBe(true);
  });

  it("toggle removes when favorited", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("build", "x", "X");
    const added = fm.toggle("build", "x", "X");
    expect(added).toBe(false);
    expect(fm.has("build", "x")).toBe(false);
  });

  it("getByType filters correctly", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("build", "b1", "B1");
    fm.add("item", "i1", "I1");
    fm.add("skill", "s1", "S1");
    expect(fm.getByType("build")).toHaveLength(1);
    expect(fm.getByType("item")).toHaveLength(1);
  });

  it("count returns total across all types", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("build", "b1", "B1");
    fm.add("skill", "s1", "S1");
    expect(fm.count()).toBe(2);
  });

  it("countByType returns count for that type", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("item", "i1", "I1");
    fm.add("item", "i2", "I2");
    expect(fm.countByType("item")).toBe(2);
    expect(fm.countByType("skill")).toBe(0);
  });

  it("clearByType only removes that type", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("build", "b1", "B1");
    fm.add("item", "i1", "I1");
    fm.clearByType("item");
    expect(fm.countByType("build")).toBe(1);
    expect(fm.countByType("item")).toBe(0);
  });

  it("clear empties all", async () => {
    const fm = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    fm.add("build", "b1", "B1");
    fm.add("skill", "s1", "S1");
    fm.clear();
    expect(fm.count()).toBe(0);
  });
});

// ─── SessionRestore ───────────────────────────────────────────────────────────

describe("SessionRestore", () => {
  it("hasSession returns false on fresh start", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    expect(sr.hasSession()).toBe(false);
  });

  it("setActivePage / getActivePage round-trips", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.setActivePage("/crafting");
    expect(sr.getActivePage()).toBe("/crafting");
  });

  it("setActiveBuildId / getActiveBuildId round-trips", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.setActiveBuildId("build-42");
    expect(sr.getActiveBuildId()).toBe("build-42");
  });

  it("setActiveBuildId accepts null", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.setActiveBuildId(null);
    expect(sr.getActiveBuildId()).toBeNull();
  });

  it("saveScrollPosition / getScrollPosition round-trips", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.saveScrollPosition("gear-panel", 350);
    expect(sr.getScrollPosition("gear-panel")).toBe(350);
  });

  it("getScrollPosition returns 0 for unknown key", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    expect(sr.getScrollPosition("never-set")).toBe(0);
  });

  it("openPanel / isPanelOpen tracks open panels", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.openPanel("settings");
    expect(sr.isPanelOpen("settings")).toBe(true);
  });

  it("closePanel removes panel", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.openPanel("debug");
    sr.closePanel("debug");
    expect(sr.isPanelOpen("debug")).toBe(false);
  });

  it("openPanel is idempotent", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.openPanel("dup");
    sr.openPanel("dup");
    expect(sr.get().openPanels.filter((p: string) => p === "dup")).toHaveLength(1);
  });

  it("saveDraft / getDraft round-trips", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.saveDraft("craft-form", { item: "sword", fp: 20 });
    const draft = sr.getDraft("craft-form");
    expect(draft).toEqual({ item: "sword", fp: 20 });
  });

  it("getDraft returns null for missing key", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    expect(sr.getDraft("nope")).toBeNull();
  });

  it("clearDraft removes the draft", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.saveDraft("form", { x: 1 });
    sr.clearDraft("form");
    expect(sr.getDraft("form")).toBeNull();
  });

  it("patch updates multiple fields at once", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.patch({ activePage: "/profile", activeBuildId: "b1" });
    const s = sr.get();
    expect(s.activePage).toBe("/profile");
    expect(s.activeBuildId).toBe("b1");
  });

  it("clear resets to defaults", async () => {
    const sr = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    sr.setActivePage("/deep/path");
    sr.clear();
    expect(sr.getActivePage()).toBe("/");
    expect(sr.hasSession()).toBe(false);
  });
});

// ─── ShortcutManager ─────────────────────────────────────────────────────────

describe("ShortcutManager", () => {
  it("registers a shortcut and returns unregister function", async () => {
    const { ShortcutManager } = await import("../../services/keyboard/shortcut_manager");
    const handler = vi.fn();
    const unregister = ShortcutManager.register(
      "test-1",
      { key: "x", ctrl: true, description: "Test" },
      handler
    );
    expect(typeof unregister).toBe("function");
    unregister();
  });

  it("getAll returns registered bindings", async () => {
    vi.resetModules();
    const { ShortcutManager } = await import("../../services/keyboard/shortcut_manager");
    const handler = vi.fn();
    const unregister = ShortcutManager.register(
      "test-2",
      { key: "q", ctrl: true, description: "Q" },
      handler
    );
    const all = ShortcutManager.getAll();
    expect(all.some(b => b.id === "test-2")).toBe(true);
    unregister();
  });

  it("setEnabled disables a shortcut", async () => {
    vi.resetModules();
    const { ShortcutManager } = await import("../../services/keyboard/shortcut_manager");
    const handler = vi.fn();
    const unregister = ShortcutManager.register(
      "test-3",
      { key: "w", ctrl: true, description: "W" },
      handler
    );
    ShortcutManager.setEnabled("test-3", false);
    const binding = ShortcutManager.getAll().find(b => b.id === "test-3");
    expect(binding?.enabled).toBe(false);
    unregister();
  });

  it("formatShortcut formats Ctrl+S correctly", async () => {
    vi.resetModules();
    const { ShortcutManager } = await import("../../services/keyboard/shortcut_manager");
    const result = ShortcutManager.formatShortcut({ key: "s", ctrl: true, description: "Save" });
    expect(result).toBe("Ctrl+S");
  });

  it("formatShortcut formats Ctrl+Shift+Z correctly", async () => {
    vi.resetModules();
    const { ShortcutManager } = await import("../../services/keyboard/shortcut_manager");
    const result = ShortcutManager.formatShortcut({ key: "z", ctrl: true, shift: true, description: "Redo" });
    expect(result).toBe("Ctrl+Shift+Z");
  });

  it("getByGroup returns only matching group", async () => {
    vi.resetModules();
    const { ShortcutManager } = await import("../../services/keyboard/shortcut_manager");
    const u1 = ShortcutManager.register("nav-1", { key: "h", description: "Home", group: "navigation" }, vi.fn());
    const u2 = ShortcutManager.register("bld-1", { key: "n", ctrl: true, description: "New", group: "build" }, vi.fn());
    const navBindings = ShortcutManager.getByGroup("navigation");
    expect(navBindings.some(b => b.id === "nav-1")).toBe(true);
    expect(navBindings.some(b => b.id === "bld-1")).toBe(false);
    u1(); u2();
  });

  it("DEFAULT_SHORTCUTS contains SAVE, UNDO, SEARCH", async () => {
    vi.resetModules();
    const { DEFAULT_SHORTCUTS } = await import("../../services/keyboard/shortcut_manager");
    expect(DEFAULT_SHORTCUTS.SAVE).toBeDefined();
    expect(DEFAULT_SHORTCUTS.UNDO).toBeDefined();
    expect(DEFAULT_SHORTCUTS.SEARCH).toBeDefined();
  });

  it("notifies subscribers when shortcut is registered", async () => {
    vi.resetModules();
    const { ShortcutManager } = await import("../../services/keyboard/shortcut_manager");
    const listener = vi.fn();
    const unsub = ShortcutManager.subscribe(listener);
    const unregister = ShortcutManager.register("notify-test", { key: "j", description: "J" }, vi.fn());
    expect(listener).toHaveBeenCalled();
    unregister(); unsub();
  });
});
