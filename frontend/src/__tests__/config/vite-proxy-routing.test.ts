import fs from "node:fs";

import { describe, expect, it } from "vitest";

describe("Vite proxy routing", () => {
  it("keeps frontend debug routes out of the backend proxy", () => {
    const viteConfig = fs.readFileSync("vite.config.ts", "utf8");

    expect(viteConfig).toContain('"/api"');
    expect(viteConfig).not.toContain('"/debug"');
  });
});
