/**
 * API base URL resolution.
 *
 * Every backend route is mounted under /api, and client paths are written
 * relative to it ("/builds", "/auth/discord"). VITE_API_BASE_URL may be set
 * either as the API origin (https://api.epochforge.gg — the value committed in
 * render.yaml) or with the /api prefix (https://api.epochforge.gg/api). Both
 * resolve to the same base, so neither form can silently drop the /api prefix.
 */

export function resolveApiBase(raw: string | null | undefined): string {
  const value = (raw ?? "").trim().replace(/\/+$/, "");
  if (!value) return "/api";
  return /\/api$/i.test(value) ? value : `${value}/api`;
}

export function joinApiPath(base: string, path: string): string {
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export const API_BASE = resolveApiBase(
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
    (import.meta.env.VITE_API_URL as string | undefined),
);

export function apiUrl(path: string): string {
  return joinApiPath(API_BASE, path);
}
