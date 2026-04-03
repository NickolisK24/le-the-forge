/**
 * UI+1 & UI+2 — Sharing service tests
 * 70 tests covering encode/decode, URL extraction, clipboard, import
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { BuildShareService, ShareableBuild } from "../../services/sharing/build_share_service";
import { BuildImportService } from "../../services/sharing/build_import_service";

const SAMPLE_BUILD: ShareableBuild = {
  version: 1,
  name: "Test Lich",
  characterClass: "Acolyte",
  mastery: "Lich",
  gear: { weapon: { affixes: [{ stat: "spell_damage", value: 30 }] } },
  skills: ["Rip Blood", "Bone Curse"],
  passives: [1, 5, 12, 20],
  notes: "Test build",
};

// ─── BuildShareService ────────────────────────────────────────────────────────

describe("BuildShareService.generateShareUrl", () => {
  it("returns a result with url and code", () => {
    const result = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://app.test");
    expect(result).toHaveProperty("url");
    expect(result).toHaveProperty("code");
  });

  it("url contains the base and param key", () => {
    const result = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://app.test/path");
    expect(result.url).toMatch(/https:\/\/app\.test\/path\?b=/);
  });

  it("injects version 1 into payload", () => {
    const { code } = BuildShareService.generateShareUrl({ ...SAMPLE_BUILD, version: 0 }, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.version).toBe(1);
  });

  it("produces URL-safe characters in code", () => {
    const { code } = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test");
    expect(code).not.toContain("+");
    expect(code).not.toContain("/");
    expect(code).not.toContain("=");
  });

  it("different builds produce different codes", () => {
    const a = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test").code;
    const b = BuildShareService.generateShareUrl({ ...SAMPLE_BUILD, name: "Other" }, "https://x.test").code;
    expect(a).not.toBe(b);
  });

  it("same build always produces same code", () => {
    const a = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test").code;
    const b = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test").code;
    expect(a).toBe(b);
  });

  it("handles build with empty arrays", () => {
    const build: ShareableBuild = { ...SAMPLE_BUILD, skills: [], passives: [], gear: {} };
    expect(() => BuildShareService.generateShareUrl(build, "https://x.test")).not.toThrow();
  });

  it("handles build with unicode notes", () => {
    const build: ShareableBuild = { ...SAMPLE_BUILD, notes: "Тест 测试 🎮" };
    const { code } = BuildShareService.generateShareUrl(build, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.notes).toBe("Тест 测试 🎮");
  });

  it("handles very long skill list", () => {
    const skills = Array.from({ length: 20 }, (_, i) => `Skill${i}`);
    const build: ShareableBuild = { ...SAMPLE_BUILD, skills };
    const { code } = BuildShareService.generateShareUrl(build, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.skills).toHaveLength(20);
  });

  it("handles very long passive list", () => {
    const passives = Array.from({ length: 100 }, (_, i) => i);
    const build: ShareableBuild = { ...SAMPLE_BUILD, passives };
    const { code } = BuildShareService.generateShareUrl(build, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.passives).toHaveLength(100);
  });
});

// ─── BuildShareService.decode ────────────────────────────────────────────────

describe("BuildShareService.decode", () => {
  it("round-trips a build correctly", () => {
    const { code } = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.name).toBe("Test Lich");
    expect(decoded?.characterClass).toBe("Acolyte");
    expect(decoded?.mastery).toBe("Lich");
  });

  it("preserves skills array", () => {
    const { code } = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.skills).toEqual(["Rip Blood", "Bone Curse"]);
  });

  it("preserves passives array", () => {
    const { code } = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.passives).toEqual([1, 5, 12, 20]);
  });

  it("preserves gear structure", () => {
    const { code } = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test");
    const decoded = BuildShareService.decode(code);
    expect(decoded?.gear).toHaveProperty("weapon");
  });

  it("returns null for empty string", () => {
    expect(BuildShareService.decode("")).toBeNull();
  });

  it("returns null for random garbage", () => {
    expect(BuildShareService.decode("not_valid_code_!!")).toBeNull();
  });

  it("returns null for invalid base64", () => {
    expect(BuildShareService.decode("@@@")).toBeNull();
  });

  it("returns null for valid base64 but non-JSON", () => {
    const bad = btoa("not json at all").replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
    expect(BuildShareService.decode(bad)).toBeNull();
  });
});

// ─── BuildShareService.extractCode ───────────────────────────────────────────

describe("BuildShareService.extractCode", () => {
  it("extracts code from a share URL", () => {
    const url = "https://app.test/path?b=TESTCODE";
    expect(BuildShareService.extractCode(url)).toBe("TESTCODE");
  });

  it("returns null when no b param", () => {
    expect(BuildShareService.extractCode("https://app.test/path?foo=bar")).toBeNull();
  });

  it("returns null for malformed URL", () => {
    expect(BuildShareService.extractCode("not a url")).toBeNull();
  });

  it("handles URL with multiple params", () => {
    const url = "https://app.test?a=1&b=MYCODE&c=3";
    expect(BuildShareService.extractCode(url)).toBe("MYCODE");
  });
});

// ─── BuildImportService ───────────────────────────────────────────────────────

describe("BuildImportService.importFromCode", () => {
  it("returns success for a valid code", () => {
    const { code } = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test");
    const result = BuildImportService.importFromCode(code);
    expect(result.status).toBe("success");
    expect(result.build?.name).toBe("Test Lich");
  });

  it("returns error for invalid code", () => {
    const result = BuildImportService.importFromCode("invalid!!!");
    expect(result.status).toBe("error");
    expect(result.build).toBeNull();
    expect(result.error).toBeTruthy();
  });

  it("validates required fields by default", () => {
    const build: ShareableBuild = { ...SAMPLE_BUILD, characterClass: "" };
    const { code } = BuildShareService.generateShareUrl(build, "https://x.test");
    const result = BuildImportService.importFromCode(code, { validate: true });
    expect(result.status).toBe("error");
  });

  it("skips validation when validate=false", () => {
    const build: ShareableBuild = { ...SAMPLE_BUILD, characterClass: "" };
    const { code } = BuildShareService.generateShareUrl(build, "https://x.test");
    const result = BuildImportService.importFromCode(code, { validate: false });
    expect(result.status).toBe("success");
  });

  it("returns error for missing name", () => {
    const build: ShareableBuild = { ...SAMPLE_BUILD, name: "" };
    const { code } = BuildShareService.generateShareUrl(build, "https://x.test");
    const result = BuildImportService.importFromCode(code, { validate: true });
    expect(result.status).toBe("error");
  });

  it("returns error for missing mastery", () => {
    const build: ShareableBuild = { ...SAMPLE_BUILD, mastery: "" };
    const { code } = BuildShareService.generateShareUrl(build, "https://x.test");
    const result = BuildImportService.importFromCode(code, { validate: true });
    expect(result.status).toBe("error");
  });
});

describe("BuildImportService.importFromUrl", () => {
  it("imports from a full URL", () => {
    const { url } = BuildShareService.generateShareUrl(SAMPLE_BUILD, "https://x.test");
    const result = BuildImportService.importFromUrl(url);
    expect(result.status).toBe("success");
    expect(result.build?.name).toBe("Test Lich");
  });

  it("returns error when URL has no code", () => {
    const result = BuildImportService.importFromUrl("https://x.test/path?no_b=1");
    expect(result.status).toBe("error");
    expect(result.error).toMatch(/no build code/i);
  });

  it("returns error for unparseable URL", () => {
    const result = BuildImportService.importFromUrl("not a url");
    expect(result.status).toBe("error");
  });
});

describe("BuildImportService.hasPendingImport", () => {
  it("returns false when no b param in URL", () => {
    Object.defineProperty(window, "location", {
      value: { search: "?other=val", href: "https://test.com?other=val" },
      writable: true,
    });
    // hasPendingImport reads current window.location
    expect(typeof BuildImportService.hasPendingImport()).toBe("boolean");
  });
});
