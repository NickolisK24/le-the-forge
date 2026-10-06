/**
 * Decides how a pasted planner URL is imported.
 *
 * Last Epoch Tools planner pages render client-side and are not fetchable by
 * our server (production returned HTTP 403), so LET URLs are never sent to the
 * server-side importer. The user is routed to the JSON tab, where the
 * bookmarklet captures the build from their own browser session.
 */

export type ImportSource = "lastepochtools" | "maxroll";

export type UrlImportDecision =
  | { kind: "empty" }
  | { kind: "unsupported" }
  | { kind: "server_import"; source: ImportSource; url: string }
  | { kind: "let_json_required"; source: "lastepochtools"; url: string };

const LET_PLANNER = /lastepochtools\.com\/planner\//i;
const MAXROLL_PLANNER = /maxroll\.gg\/last-epoch\/planner\//i;

export function detectImportSource(url: string): ImportSource | null {
  if (LET_PLANNER.test(url)) return "lastepochtools";
  if (MAXROLL_PLANNER.test(url)) return "maxroll";
  return null;
}

export function decideUrlImport(rawUrl: string): UrlImportDecision {
  const url = rawUrl.trim();
  if (!url) return { kind: "empty" };
  const source = detectImportSource(url);
  if (source === "lastepochtools") return { kind: "let_json_required", source, url };
  if (source === "maxroll") return { kind: "server_import", source, url };
  return { kind: "unsupported" };
}

/** Error code the backend returns if a LET URL reaches the server importer. */
export const LET_SERVER_FETCH_UNSUPPORTED = "LET_SERVER_FETCH_UNSUPPORTED";
