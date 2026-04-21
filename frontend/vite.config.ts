import { defineConfig, loadEnv } from "vite";
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

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  // VITE_API_BASE_URL is the canonical variable. In production this is the
  // full URL (https://api.epochforge.gg); in dev it's left unset so the
  // server proxy below forwards /api to the local Flask backend.
  // VITE_API_URL is kept as a legacy alias for local workflows.
  const apiBaseUrl = env.VITE_API_BASE_URL || env.VITE_API_URL || "";
  const devProxyTarget = apiBaseUrl.startsWith("http")
    ? apiBaseUrl.replace(/\/api\/?$/, "")
    : "http://localhost:5050";

  return {
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
          target: devProxyTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
