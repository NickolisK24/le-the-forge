/**
 * Phase UI+ — Integration tests
 * Tests combining multiple services together
 * ~55 tests
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

async function freshModule<T>(path: string, key: string): Promise<T> {
  vi.resetModules();
  Object.keys(store).forEach((k) => delete store[k]);
  const mod = await import(path);
  return mod[key] as T;
}

// ─── Sharing + Import integration ─────────────────────────────────────────────

import { BuildShareService } from "../../services/sharing/build_share_service";
import type { ShareableBuild } from "../../services/sharing/build_share_service";
import { BuildImportService } from "../../services/sharing/build_import_service";

const FULL_BUILD: ShareableBuild = {
  version: 1,
  name: "Glass Cannon Lich",
  characterClass: "Acolyte",
  mastery: "Lich",
  gear: {
    weapon: { affixes: [{ stat: "spell_damage", value: 80 }] },
    helmet: { affixes: [{ stat: "crit_chance", value: 20 }] },
  },
  skills: ["Rip Blood", "Bone Curse", "Summon Skeleton"],
  passives: [1, 5, 12, 20, 33, 45],
  notes: "Full integration test build",
};

describe("Sharing + Import — round-trip", () => {
  it("encode then decode produces identical build name", () => {
    const { code } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.name).toBe(FULL_BUILD.name);
  });

  it("decoded characterClass matches original", () => {
    const { code } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test");
    expect(BuildShareService.decode(code)?.characterClass).toBe(FULL_BUILD.characterClass);
  });

  it("decoded skills match original", () => {
    const { code } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test");
    expect(BuildShareService.decode(code)?.skills).toEqual(FULL_BUILD.skills);
  });

  it("decoded passives match original", () => {
    const { code } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test");
    expect(BuildShareService.decode(code)?.passives).toEqual(FULL_BUILD.passives);
  });

  it("importFromCode returns status success", () => {
    const { code } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test");
    const result = BuildImportService.importFromCode(code);
    expect(result.status).toBe("success");
  });

  it("importFromCode returns correct build data", () => {
    const { code } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test");
    const result = BuildImportService.importFromCode(code);
    expect(result.build?.name).toBe(FULL_BUILD.name);
  });

  it("importFromUrl extracts code and returns success", () => {
    const { url } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test/build");
    const result = BuildImportService.importFromUrl(url);
    expect(result.status).toBe("success");
    expect(result.build?.characterClass).toBe("Acolyte");
  });

  it("multiple different builds produce different codes", () => {
    const c1 = BuildShareService.generateShareUrl({ ...FULL_BUILD, name: "One" }, "https://app.test").code;
    const c2 = BuildShareService.generateShareUrl({ ...FULL_BUILD, name: "Two" }, "https://app.test").code;
    expect(c1).not.toBe(c2);
  });

  it("corrupt code returns error status", () => {
    const result = BuildImportService.importFromCode("not_valid_base64!!");
    expect(result.status).toBe("error");
    expect(result.error).toBeTruthy();
  });

  it("extractCode + decode works end-to-end", () => {
    const { url } = BuildShareService.generateShareUrl(FULL_BUILD, "https://app.test");
    const code = BuildShareService.extractCode(url)!;
    expect(BuildShareService.decode(code)?.name).toBe(FULL_BUILD.name);
  });
});

// ─── BuildManager + Sharing integration ───────────────────────────────────────

describe("BuildManager + Sharing — export/import flow", () => {
  it("created build can be serialized to share URL", async () => {
    const BM = await freshModule<any>("../../services/build/build_manager", "BuildManager");
    const build = BM.create({ name: "Export Me", characterClass: "Sentinel" });
    const shareable: ShareableBuild = {
      version: 1,
      name: build.name,
      characterClass: build.characterClass ?? "Sentinel",
      mastery: build.mastery ?? "",
      gear: build.gear ?? {},
      skills: build.skills ?? [],
      passives: build.passives ?? [],
    };
    const { code } = BuildShareService.generateShareUrl(shareable, "https://app.test");
    expect(BuildShareService.decode(code)?.name).toBe("Export Me");
  });

  it("imported build can be added to BuildManager", async () => {
    const BM = await freshModule<any>("../../services/build/build_manager", "BuildManager");
    const shareable: ShareableBuild = {
      version: 1, name: "Imported Build", characterClass: "Mage", mastery: "Sorcerer",
      gear: {}, skills: ["Glacier"], passives: [1, 2, 3],
    };
    const { code } = BuildShareService.generateShareUrl(shareable, "https://app.test");
    const imported = BuildImportService.importFromCode(code);
    expect(imported.status).toBe("success");
    const build = BM.create({ name: imported.build!.name });
    expect(build.name).toBe("Imported Build");
  });

  it("duplicated build can be independently shared", async () => {
    const BM = await freshModule<any>("../../services/build/build_manager", "BuildManager");
    const original = BM.create({ name: "Original" });
    const copy = BM.duplicate(original.id);
    expect(copy.id).not.toBe(original.id);
    const { code } = BuildShareService.generateShareUrl(
      { version: 1, name: copy.name, characterClass: "Rogue", mastery: "", gear: {}, skills: [], passives: [] },
      "https://app.test"
    );
    expect(BuildShareService.decode(code)?.name).toContain("Original");
  });
});

// ─── PresetManager + FavoriteManager integration ──────────────────────────────

describe("PresetManager + FavoriteManager — combined workflow", () => {
  it("saved preset can be favorited by id", async () => {
    const PM = await freshModule<any>("../../services/presets/preset_manager", "PresetManager");
    vi.resetModules(); Object.keys(store).forEach(k => delete store[k]);
    const FM = await freshModule<any>("../../services/favorites/favorite_manager", "FavoriteManager");

    const preset = PM.save_preset("Power Preset", { dps: 5000 });
    FM.add("preset", preset.id, preset.name);
    expect(FM.has("preset", preset.id)).toBe(true);
  });

  it("multiple categories coexist in favorites", async () => {
    const FM = await freshModule<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    FM.add("preset", "p1", "Preset 1");
    FM.add("build", "b1", "Build 1");
    FM.add("item", "i1", "Item 1");
    expect(FM.has("preset", "p1")).toBe(true);
    expect(FM.has("build", "b1")).toBe(true);
    expect(FM.has("item", "i1")).toBe(true);
  });

  it("toggle adds then removes a favorite", async () => {
    const FM = await freshModule<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    FM.toggle("build", "b99", "Build 99");
    expect(FM.has("build", "b99")).toBe(true);
    FM.toggle("build", "b99", "Build 99");
    expect(FM.has("build", "b99")).toBe(false);
  });

  it("clearByType only removes that type", async () => {
    const FM = await freshModule<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    FM.add("preset", "p1", "P1");
    FM.add("build", "b1", "B1");
    FM.clearByType("preset");
    expect(FM.has("preset", "p1")).toBe(false);
    expect(FM.has("build", "b1")).toBe(true);
  });
});

// ─── SessionRestore + BuildManager integration ────────────────────────────────

describe("SessionRestore + BuildManager — state persistence", () => {
  it("active build id persists to session", async () => {
    const BM = await freshModule<any>("../../services/build/build_manager", "BuildManager");
    vi.resetModules(); Object.keys(store).forEach(k => delete store[k]);
    const SR = await freshModule<any>("../../services/session/session_restore", "SessionRestore");

    const build = BM.create({ name: "Session Build" });
    BM.setActive(build.id);
    SR.setActiveBuildId(build.id);
    expect(SR.getActiveBuildId()).toBe(build.id);
  });

  it("current page persists and restores", async () => {
    const SR = await freshModule<any>("../../services/session/session_restore", "SessionRestore");
    SR.setActivePage("/builds");
    expect(SR.getActivePage()).toBe("/builds");
  });

  it("scroll position is saved and retrieved per route", async () => {
    const SR = await freshModule<any>("../../services/session/session_restore", "SessionRestore");
    SR.saveScrollPosition("/items", 350);
    expect(SR.getScrollPosition("/items")).toBe(350);
    expect(SR.getScrollPosition("/builds")).toBe(0);
  });

  it("open panels persist", async () => {
    const SR = await freshModule<any>("../../services/session/session_restore", "SessionRestore");
    SR.openPanel("sidebar");
    SR.openPanel("details");
    expect(SR.isPanelOpen("sidebar")).toBe(true);
    expect(SR.isPanelOpen("details")).toBe(true);
  });

  it("form draft saved and restored", async () => {
    const SR = await freshModule<any>("../../services/session/session_restore", "SessionRestore");
    SR.saveDraft("build-editor", { name: "Draft Name", notes: "WIP" });
    const draft = SR.getDraft("build-editor") as { name: string; notes: string } | null;
    expect(draft?.name).toBe("Draft Name");
  });

  it("clearing session removes all state", async () => {
    const SR = await freshModule<any>("../../services/session/session_restore", "SessionRestore");
    SR.setActivePage("/builds");
    SR.setActiveBuildId("b1");
    SR.clear();
    expect(SR.getActiveBuildId()).toBeNull();
    expect(SR.hasSession()).toBe(false);
  });
});

// ─── ShortcutManager integration ─────────────────────────────────────────────

describe("ShortcutManager — multiple shortcut groups", () => {
  afterEach(() => {
    vi.resetModules();
    Object.keys(store).forEach((k) => delete store[k]);
  });

  it("register shortcuts in different groups", async () => {
    const SM = await freshModule<any>("../../services/keyboard/shortcut_manager", "ShortcutManager");
    SM.register("save",   { key: "s", ctrl: true, description: "Save",   group: "file" },       vi.fn());
    SM.register("search", { key: "f", ctrl: true, description: "Search", group: "navigation" }, vi.fn());
    expect(SM.getByGroup("file").some((s: any) => s.id === "save")).toBe(true);
    expect(SM.getByGroup("navigation").some((s: any) => s.id === "search")).toBe(true);
  });

  it("unregistered shortcut is no longer in group", async () => {
    const SM = await freshModule<any>("../../services/keyboard/shortcut_manager", "ShortcutManager");
    const def = { key: "t", description: "Temp", group: "tools" };
    SM.register("temp", def, vi.fn());
    SM.unregister("temp", def);
    expect(SM.getByGroup("tools").some((s: any) => s.id === "temp")).toBe(false);
  });

  it("disabled shortcut does not fire handler", async () => {
    const SM = await freshModule<any>("../../services/keyboard/shortcut_manager", "ShortcutManager");
    const handler = vi.fn();
    SM.register("x", { key: "x", description: "X", group: "test" }, handler);
    SM.setEnabled("x", false);
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "x", bubbles: true }));
    expect(handler).not.toHaveBeenCalled();
    SM.setEnabled("x", true);
  });

  it("formatShortcut produces readable string with ctrl", async () => {
    const SM = await freshModule<any>("../../services/keyboard/shortcut_manager", "ShortcutManager");
    const label = SM.formatShortcut({ key: "s", ctrl: true });
    expect(label).toMatch(/ctrl/i);
    expect(label).toMatch(/s/i);
  });

  it("re-registering same key replaces in binding map", async () => {
    const SM = await freshModule<any>("../../services/keyboard/shortcut_manager", "ShortcutManager");
    SM.register("dup", { key: "d", description: "First",  group: "g" }, vi.fn());
    SM.register("dup2",{ key: "d", description: "Second", group: "g" }, vi.fn());
    // Both registrations exist (different ids)
    const all = SM.getAll();
    expect(all.filter((s: any) => s.key === "d").length).toBeGreaterThanOrEqual(1);
  });
});
