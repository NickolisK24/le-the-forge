import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "node:path";

// Read project VERSION file at build/dev-server start so the app version is
// available synchronously in the client bundle. This lets us render the
// version badge on cold load without waiting for /api/version to resolve.
function readProjectVersion(): string {
  try {
    const versionPath = path.resolve(__dirname, "..", "VERSION");
    return fs.readFileSync(versionPath, "utf8").trim() || "0.0.0";
  } catch {
    return "0.0.0";
  }
}

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": new URL("./src", import.meta.url).pathname,
      "@constants": new URL("../backend/src/constants", import.meta.url).pathname,
    },
  },
  define: {
    __APP_VERSION__: JSON.stringify(readProjectVersion()),
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:5050",
        changeOrigin: true,
      },
    },
  },
});
