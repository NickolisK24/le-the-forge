/**
 * Phase UI+ — Edge case tests
 * Additional coverage for boundary conditions, error paths, and persistence
 * ~55 tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { BuildShareService } from "../../services/sharing/build_share_service";
import type { ShareableBuild } from "../../services/sharing/build_share_service";
import { BuildImportService } from "../../services/sharing/build_import_service";

// ─── Mock globals ─────────────────────────────────────────────────────────────

const store: Record<string, string> = {};
vi.stubGlobal("localStorage", {
  getItem: (k: string) => store[k] ?? null,
  setItem: (k: string, v: string) => { store[k] = v; },
  removeItem: (k: string) => { delete store[k]; },
  clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
});
vi.stubGlobal("history", { replaceState: vi.fn() });

async function fresh<T>(path: string, key: string): Promise<T> {
  vi.resetModules();
  Object.keys(store).forEach((k) => delete store[k]);
  const mod = await import(path);
  return mod[key] as T;
}

// ─── ShareService edge cases ──────────────────────────────────────────────────

describe("BuildShareService — edge cases", () => {
  const base: ShareableBuild = { version: 1, name: "X", characterClass: "Rogue", mastery: "", gear: {}, skills: [], passives: [] };

  it("handles empty gear object", () => {
    const { code } = BuildShareService.generateShareUrl({ ...base, gear: {} }, "https://x.test");
    expect(BuildShareService.decode(code)?.gear).toEqual({});
  });

  it("handles 100 passives", () => {
    const passives = Array.from({ length: 100 }, (_, i) => i + 1);
    const { code } = BuildShareService.generateShareUrl({ ...base, passives }, "https://x.test");
    expect(BuildShareService.decode(code)?.passives).toHaveLength(100);
  });

  it("handles special characters in build name", () => {
    const { code } = BuildShareService.generateShareUrl({ ...base, name: "Über Héro & <Build>" }, "https://x.test");
    expect(BuildShareService.decode(code)?.name).toBe("Über Héro & <Build>");
  });

  it("returns null for empty string decode", () => {
    expect(BuildShareService.decode("")).toBeNull();
  });

  it("returns null for whitespace-only code", () => {
    expect(BuildShareService.decode("   ")).toBeNull();
  });

  it("extractCode returns null for URL without share param", () => {
    expect(BuildShareService.extractCode("https://app.test/noparam")).toBeNull();
  });

  it("generated code is non-empty", () => {
    const { code } = BuildShareService.generateShareUrl(base, "https://app.test");
    expect(code.length).toBeGreaterThan(10);
  });

  it("url includes the code verbatim", () => {
    const { url, code } = BuildShareService.generateShareUrl(base, "https://app.test");
    expect(url).toContain(code);
  });

  it("different base URLs produce same code", () => {
    const { code: c1 } = BuildShareService.generateShareUrl(base, "https://app.test");
    const { code: c2 } = BuildShareService.generateShareUrl(base, "https://other.test");
    expect(c1).toBe(c2);
  });

  it("build notes field survives round-trip", () => {
    const withNotes = { ...base, notes: "Special notes here" };
    const { code } = BuildShareService.generateShareUrl(withNotes, "https://app.test");
    expect(BuildShareService.decode(code)?.notes).toBe("Special notes here");
  });

  it("version is always 1 in generated share", () => {
    const { code } = BuildShareService.generateShareUrl({ ...base, version: 99 }, "https://app.test");
    expect(BuildShareService.decode(code)?.version).toBe(1);
  });

  it("base URL without trailing slash gets ?b= appended", () => {
    const { url } = BuildShareService.generateShareUrl(base, "https://app.test/path");
    expect(url).toContain("?b=");
  });
});

// ─── BuildImportService edge cases ────────────────────────────────────────────

describe("BuildImportService — validation", () => {
  it("returns error status for corrupt code", () => {
    expect(BuildImportService.importFromCode("XXXX").status).toBe("error");
  });

  it("hasPendingImport returns boolean", () => {
    expect(typeof BuildImportService.hasPendingImport()).toBe("boolean");
  });

  it("importFromUrl with no code returns error", () => {
    expect(BuildImportService.importFromUrl("https://app.test/noparam").status).toBe("error");
  });

  it("importFromCode empty string returns error", () => {
    expect(BuildImportService.importFromCode("").status).toBe("error");
  });
});

// ─── BuildManager edge cases ──────────────────────────────────────────────────

describe("BuildManager — edge cases", () => {
  it("getById returns null for unknown id", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    expect(BM.getById("nonexistent")).toBeNull();
  });

  it("delete nonexistent id does not throw", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    expect(() => BM.delete("ghost-id")).not.toThrow();
  });

  it("rename nonexistent id does not throw", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    expect(() => BM.rename("ghost-id", "New Name")).not.toThrow();
  });

  it("duplicate nonexistent id returns null", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    expect(BM.duplicate("ghost-id")).toBeNull();
  });

  it("setActive nonexistent id does not crash", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    expect(() => BM.setActive("ghost-id")).not.toThrow();
  });

  it("unsubscribe removes listener", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    const handler = vi.fn();
    const unsub = BM.subscribe(handler);
    unsub();
    BM.create({ name: "Silent Build" });
    expect(handler).not.toHaveBeenCalled();
  });

  it("update applies partial changes", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    const build = BM.create({ name: "Before" });
    BM.update(build.id, { name: "After" });
    expect(BM.getById(build.id)?.name).toBe("After");
  });

  it("creates builds with unique ids", async () => {
    const BM = await fresh<any>("../../services/build/build_manager", "BuildManager");
    const builds = Array.from({ length: 5 }, (_, i) => BM.create({ name: `B${i}` }));
    expect(new Set(builds.map((b: any) => b.id)).size).toBe(5);
  });
});

// ─── FavoriteManager edge cases ───────────────────────────────────────────────

describe("FavoriteManager — edge cases", () => {
  it("add same item twice uses map key (deduplicated)", async () => {
    const FM = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    FM.add("item", "sword-1", "Sword");
    FM.add("item", "sword-1", "Sword");
    expect(FM.getByType("item")).toHaveLength(1);
  });

  it("remove returns false for nonexistent item", async () => {
    const FM = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    expect(FM.remove("item", "ghost-item")).toBe(false);
  });

  it("countByType returns 0 for empty type", async () => {
    const FM = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    expect(FM.countByType("skill")).toBe(0);
  });

  it("getByType returns empty array for unknown type", async () => {
    const FM = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    expect(FM.getByType("unknown_type")).toEqual([]);
  });

  it("persists favorites to localStorage on add", async () => {
    const FM = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    FM.add("build", "b-persist", "Persist Build");
    const saved = Object.values(store).some((v) => v.includes("b-persist"));
    expect(saved).toBe(true);
  });

  it("toggle returns true when adding", async () => {
    const FM = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    expect(FM.toggle("build", "b1", "B1")).toBe(true);
  });

  it("toggle returns false when removing", async () => {
    const FM = await fresh<any>("../../services/favorites/favorite_manager", "FavoriteManager");
    FM.add("build", "b1", "B1");
    expect(FM.toggle("build", "b1", "B1")).toBe(false);
  });
});

// ─── PresetManager edge cases ─────────────────────────────────────────────────

describe("PresetManager — edge cases", () => {
  it("delete returns false for nonexistent preset", async () => {
    const PM = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(PM.delete("ghost-preset")).toBe(false);
  });

  it("apply nonexistent preset returns null", async () => {
    const PM = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(PM.apply("ghost-id")).toBeNull();
  });

  it("search with no matches returns empty array", async () => {
    const PM = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    PM.save_preset("Fire Build", {});
    expect(PM.search("xyznotfound")).toEqual([]);
  });

  it("getByCategory with no matches returns empty array", async () => {
    const PM = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(PM.getByCategory("nonexistent-category")).toEqual([]);
  });

  it("import with invalid JSON does not throw", async () => {
    const PM = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(() => PM.import("not valid json")).not.toThrow();
    expect(PM.import("not valid json")).toBeNull();
  });

  it("export of nonexistent id returns null", async () => {
    const PM = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    expect(PM.export("ghost")).toBeNull();
  });

  it("preset has createdAt timestamp on creation", async () => {
    const PM = await fresh<any>("../../services/presets/preset_manager", "PresetManager");
    const p = PM.save_preset("Timed", {});
    expect(p.createdAt).toBeGreaterThan(0);
  });
});

// ─── SessionRestore edge cases ────────────────────────────────────────────────

describe("SessionRestore — edge cases", () => {
  it("getDraft returns null for nonexistent key", async () => {
    const SR = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    expect(SR.getDraft("nonexistent")).toBeNull();
  });

  it("clearDraft does not throw for nonexistent key", async () => {
    const SR = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    expect(() => SR.clearDraft("ghost")).not.toThrow();
  });

  it("getScrollPosition returns 0 for unvisited route", async () => {
    const SR = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    expect(SR.getScrollPosition("/never-visited")).toBe(0);
  });

  it("closePanel removes it from open panels", async () => {
    const SR = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    SR.openPanel("panel1");
    SR.closePanel("panel1");
    expect(SR.isPanelOpen("panel1")).toBe(false);
  });

  it("getActivePage returns default / before any set", async () => {
    const SR = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    expect(SR.getActivePage()).toBe("/");
  });

  it("persists to localStorage on setActivePage", async () => {
    const SR = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    SR.setActivePage("/test-route");
    const persisted = Object.values(store).some((v) => v.includes("test-route"));
    expect(persisted).toBe(true);
  });

  it("patch applies changes to session state", async () => {
    const SR = await fresh<any>("../../services/session/session_restore", "SessionRestore");
    SR.patch({ activeBuildId: "patch-b1" });
    expect(SR.getActiveBuildId()).toBe("patch-b1");
  });
});
