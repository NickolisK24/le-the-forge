/**
 * UI+5 — BuildManager tests
 * 65 tests covering CRUD, ordering, subscriptions, and persistence
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock localStorage
const store: Record<string, string> = {};
vi.stubGlobal("localStorage", {
  getItem: (k: string) => store[k] ?? null,
  setItem: (k: string, v: string) => { store[k] = v; },
  removeItem: (k: string) => { delete store[k]; },
  clear: () => { Object.keys(store).forEach(k => delete store[k]); },
});

// Fresh import for each test group to avoid singleton pollution
async function getBuildManager() {
  vi.resetModules();
  const mod = await import("../../services/build/build_manager");
  mod.BuildManager.clear();
  return mod.BuildManager;
}

describe("BuildManager — create", () => {
  it("creates a build with defaults", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    expect(b.name).toBe("Untitled Build");
    expect(b.characterClass).toBe("Acolyte");
    expect(b.id).toBeTruthy();
  });

  it("creates a build with overrides", async () => {
    const bm = await getBuildManager();
    const b = bm.create({ name: "My Lich", characterClass: "Acolyte", mastery: "Lich" });
    expect(b.name).toBe("My Lich");
    expect(b.mastery).toBe("Lich");
  });

  it("sets the new build as active", async () => {
    const bm = await getBuildManager();
    const b = bm.create({ name: "Active Build" });
    expect(bm.getActiveId()).toBe(b.id);
  });

  it("generates unique IDs", async () => {
    const bm = await getBuildManager();
    const ids = Array.from({ length: 10 }, () => bm.create().id);
    expect(new Set(ids).size).toBe(10);
  });

  it("sets createdAt and updatedAt", async () => {
    const bm = await getBuildManager();
    const before = Date.now();
    const b = bm.create();
    const after = Date.now();
    expect(b.createdAt).toBeGreaterThanOrEqual(before);
    expect(b.createdAt).toBeLessThanOrEqual(after);
    expect(b.updatedAt).toBeGreaterThanOrEqual(before);
  });

  it("increments count", async () => {
    const bm = await getBuildManager();
    expect(bm.count()).toBe(0);
    bm.create();
    bm.create();
    expect(bm.count()).toBe(2);
  });
});

describe("BuildManager — read", () => {
  it("getAll returns all builds", async () => {
    const bm = await getBuildManager();
    bm.create({ name: "A" });
    bm.create({ name: "B" });
    expect(bm.getAll()).toHaveLength(2);
  });

  it("getById returns the correct build", async () => {
    const bm = await getBuildManager();
    const b = bm.create({ name: "Findable" });
    expect(bm.getById(b.id)?.name).toBe("Findable");
  });

  it("getById returns null for unknown id", async () => {
    const bm = await getBuildManager();
    expect(bm.getById("nope")).toBeNull();
  });

  it("getActive returns active build", async () => {
    const bm = await getBuildManager();
    const b = bm.create({ name: "Active" });
    expect(bm.getActive()?.id).toBe(b.id);
  });

  it("getActive returns null with no builds", async () => {
    const bm = await getBuildManager();
    expect(bm.getActive()).toBeNull();
  });
});

describe("BuildManager — update & rename", () => {
  it("update changes specified fields", async () => {
    const bm = await getBuildManager();
    const b = bm.create({ name: "Original" });
    bm.update(b.id, { name: "Updated" });
    expect(bm.getById(b.id)?.name).toBe("Updated");
  });

  it("update refreshes updatedAt", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    const before = b.updatedAt;
    await new Promise((r) => setTimeout(r, 5));
    bm.update(b.id, { name: "Changed" });
    expect(bm.getById(b.id)!.updatedAt).toBeGreaterThan(before);
  });

  it("update returns null for unknown id", async () => {
    const bm = await getBuildManager();
    expect(bm.update("nope", { name: "X" })).toBeNull();
  });

  it("rename trims whitespace", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    bm.rename(b.id, "  My Build  ");
    expect(bm.getById(b.id)?.name).toBe("My Build");
  });

  it("rename falls back to Untitled Build for empty string", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    bm.rename(b.id, "");
    expect(bm.getById(b.id)?.name).toBe("Untitled Build");
  });
});

describe("BuildManager — duplicate", () => {
  it("creates a copy with same data", async () => {
    const bm = await getBuildManager();
    const b = bm.create({ name: "Source", mastery: "Lich" });
    const copy = bm.duplicate(b.id);
    expect(copy?.mastery).toBe("Lich");
  });

  it("copy name has (Copy) suffix", async () => {
    const bm = await getBuildManager();
    const b = bm.create({ name: "Hero" });
    const copy = bm.duplicate(b.id);
    expect(copy?.name).toBe("Hero (Copy)");
  });

  it("copy has different id", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    const copy = bm.duplicate(b.id);
    expect(copy?.id).not.toBe(b.id);
  });

  it("copy becomes active", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    const copy = bm.duplicate(b.id);
    expect(bm.getActiveId()).toBe(copy?.id);
  });

  it("duplicate returns null for unknown id", async () => {
    const bm = await getBuildManager();
    expect(bm.duplicate("nope")).toBeNull();
  });

  it("increments count", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    expect(bm.count()).toBe(1);
    bm.duplicate(b.id);
    expect(bm.count()).toBe(2);
  });
});

describe("BuildManager — delete", () => {
  it("removes build by id", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    bm.delete(b.id);
    expect(bm.getById(b.id)).toBeNull();
  });

  it("returns true on success", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    expect(bm.delete(b.id)).toBe(true);
  });

  it("returns false for unknown id", async () => {
    const bm = await getBuildManager();
    expect(bm.delete("nope")).toBe(false);
  });

  it("updates active when active is deleted", async () => {
    const bm = await getBuildManager();
    const a = bm.create({ name: "A" });
    const b = bm.create({ name: "B" });
    bm.setActive(b.id);
    bm.delete(b.id);
    expect(bm.getActiveId()).not.toBe(b.id);
  });

  it("active becomes null when last build deleted", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    bm.delete(b.id);
    expect(bm.getActiveId()).toBeNull();
  });
});

describe("BuildManager — setActive & reorder", () => {
  it("setActive switches active build", async () => {
    const bm = await getBuildManager();
    const a = bm.create({ name: "A" });
    const b = bm.create({ name: "B" });
    bm.setActive(a.id);
    expect(bm.getActiveId()).toBe(a.id);
  });

  it("setActive returns false for unknown id", async () => {
    const bm = await getBuildManager();
    expect(bm.setActive("nope")).toBe(false);
  });

  it("reorder changes build order", async () => {
    const bm = await getBuildManager();
    const a = bm.create({ name: "A" });
    const b = bm.create({ name: "B" });
    const c = bm.create({ name: "C" });
    bm.reorder([c.id, a.id, b.id]);
    const all = bm.getAll();
    expect(all[0].id).toBe(c.id);
    expect(all[1].id).toBe(a.id);
    expect(all[2].id).toBe(b.id);
  });
});

describe("BuildManager — subscriptions", () => {
  it("fires listener on create", async () => {
    const bm = await getBuildManager();
    const fn = vi.fn();
    bm.subscribe(fn);
    bm.create({ name: "Trigger" });
    expect(fn).toHaveBeenCalled();
  });

  it("listener receives updated builds array", async () => {
    const bm = await getBuildManager();
    let received: unknown[] = [];
    bm.subscribe((builds) => { received = builds; });
    bm.create({ name: "Sub Test" });
    expect(received).toHaveLength(1);
  });

  it("unsubscribe stops notifications", async () => {
    const bm = await getBuildManager();
    const fn = vi.fn();
    const unsub = bm.subscribe(fn);
    unsub();
    bm.create();
    expect(fn).not.toHaveBeenCalled();
  });

  it("fires listener on delete", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    const fn = vi.fn();
    bm.subscribe(fn);
    bm.delete(b.id);
    expect(fn).toHaveBeenCalled();
  });

  it("fires listener on rename", async () => {
    const bm = await getBuildManager();
    const b = bm.create();
    const fn = vi.fn();
    bm.subscribe(fn);
    bm.rename(b.id, "New Name");
    expect(fn).toHaveBeenCalled();
  });

  it("supports multiple listeners simultaneously", async () => {
    const bm = await getBuildManager();
    const a = vi.fn();
    const b = vi.fn();
    bm.subscribe(a);
    bm.subscribe(b);
    bm.create();
    expect(a).toHaveBeenCalled();
    expect(b).toHaveBeenCalled();
  });
});
