import fs from "node:fs";

import { describe, expect, it } from "vitest";

describe("Vite proxy routing", () => {
  it("keeps frontend debug routes out of the backend proxy", () => {
    const viteConfig = fs.readFileSync("vite.config.ts", "utf8");

    expect(viteConfig).toContain('"/api"');
    expect(viteConfig).not.toContain('"/debug"');
  });

  it("keeps the browser API base path separate from the Docker backend proxy target", () => {
    const viteConfig = fs.readFileSync("vite.config.ts", "utf8");
    const composeConfig = fs.readFileSync("../docker-compose.yml", "utf8");

    expect(viteConfig).toContain("VITE_API_PROXY_TARGET");
    expect(composeConfig).toContain("VITE_API_BASE_URL: /api");
    expect(composeConfig).toContain("VITE_API_PROXY_TARGET: http://backend:5000");
    expect(composeConfig).not.toContain("VITE_API_BASE_URL: http://backend:5000/api");
  });
});
