/**
 * R0 regression: API URL composition (FE-1).
 *
 * The committed render.yaml sets VITE_API_BASE_URL to the API origin
 * (https://api.epochforge.gg) while every backend route lives under /api.
 * Whatever form the deployed value takes, requests must reach /api/...
 */
import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

import { joinApiPath, resolveApiBase } from "@/lib/apiBase";

describe("resolveApiBase", () => {
  it.each([
    ["https://api.epochforge.gg", "https://api.epochforge.gg/api"],
    ["https://api.epochforge.gg/", "https://api.epochforge.gg/api"],
    ["https://api.epochforge.gg/api", "https://api.epochforge.gg/api"],
    ["https://api.epochforge.gg/api/", "https://api.epochforge.gg/api"],
    ["http://backend:5000/api", "http://backend:5000/api"],
    ["/api", "/api"],
    ["", "/api"],
    ["   ", "/api"],
    [undefined, "/api"],
    [null, "/api"],
  ])("%s -> %s", (raw, expected) => {
    expect(resolveApiBase(raw as string | undefined)).toBe(expected);
  });
});

describe("API URL composition", () => {
  it.each([
    ["https://api.epochforge.gg", "/auth/discord", "https://api.epochforge.gg/api/auth/discord"],
    ["https://api.epochforge.gg/api", "/auth/discord", "https://api.epochforge.gg/api/auth/discord"],
    ["https://api.epochforge.gg", "/import/build", "https://api.epochforge.gg/api/import/build"],
    ["https://api.epochforge.gg", "builds", "https://api.epochforge.gg/api/builds"],
    [undefined, "/builds", "/api/builds"],
  ])("base %s + %s", (raw, p, expected) => {
    expect(joinApiPath(resolveApiBase(raw as string | undefined), p)).toBe(expected);
  });

  it("the committed render.yaml value composes to /api URLs", () => {
    const blueprint = fs.readFileSync(path.resolve(__dirname, "../../../../render.yaml"), "utf8");
    const match = blueprint.match(/key:\s*VITE_API_BASE_URL\s*\n\s*value:\s*(\S+)/);
    expect(match).not.toBeNull();
    const url = joinApiPath(resolveApiBase(match![1]), "/auth/discord");
    expect(url).toMatch(/^https:\/\/[^/]+\/api\/auth\/discord$/);
  });

  it("no component composes the API base from raw env vars", () => {
    const srcRoot = path.resolve(__dirname, "../..");
    const offenders: string[] = [];
    const walk = (dir: string) => {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (entry.name !== "__tests__") walk(full);
        } else if (/\.(ts|tsx)$/.test(entry.name) && !full.endsWith(path.join("lib", "apiBase.ts"))) {
          if (fs.readFileSync(full, "utf8").includes("VITE_API_BASE_URL ??")) offenders.push(full);
        }
      }
    };
    walk(srcRoot);
    expect(offenders).toEqual([]);
  });
});
