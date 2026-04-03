/**
 * UI+1 — Shareable Build Links
 * Serialize → Compress → Encode → Append to URL
 */

export interface ShareableBuild {
  version: number;
  name: string;
  characterClass: string;
  mastery: string;
  gear: Record<string, unknown>;
  skills: string[];
  passives: number[];
  notes?: string;
}

export interface ShareResult {
  url: string;
  code: string;
}

const SHARE_VERSION = 1;
const PARAM_KEY = "b";

/** Encode build data to a URL-safe base64 string. */
function encodeBuild(build: ShareableBuild): string {
  const json = JSON.stringify(build);
  const bytes = new TextEncoder().encode(json);
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

/** Decode a URL-safe base64 string back to build data. */
function decodeBuild(code: string): ShareableBuild {
  const padded = code.replace(/-/g, "+").replace(/_/g, "/");
  const pad = padded.length % 4 === 0 ? "" : "=".repeat(4 - (padded.length % 4));
  const binary = atob(padded + pad);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  const json = new TextDecoder().decode(bytes);
  return JSON.parse(json) as ShareableBuild;
}

export const BuildShareService = {
  /**
   * Generate a shareable URL for a build.
   * @param build The build data to share.
   * @param baseUrl Optional base URL (defaults to current location).
   */
  generateShareUrl(build: ShareableBuild, baseUrl?: string): ShareResult {
    const payload: ShareableBuild = { ...build, version: SHARE_VERSION };
    const code = encodeBuild(payload);
    const base = baseUrl ?? `${window.location.origin}${window.location.pathname}`;
    const url = `${base}?${PARAM_KEY}=${code}`;
    return { url, code };
  },

  /** Copy the share URL to the clipboard. Returns true on success. */
  async copyToClipboard(build: ShareableBuild, baseUrl?: string): Promise<boolean> {
    const { url } = this.generateShareUrl(build, baseUrl);
    try {
      await navigator.clipboard.writeText(url);
      return true;
    } catch {
      // Fallback for environments without clipboard API
      const el = document.createElement("textarea");
      el.value = url;
      el.style.position = "fixed";
      el.style.opacity = "0";
      document.body.appendChild(el);
      el.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(el);
      return ok;
    }
  },

  /**
   * Decode a share code back to build data.
   * Returns null if the code is invalid or from an incompatible version.
   */
  decode(code: string): ShareableBuild | null {
    try {
      const build = decodeBuild(code);
      if (typeof build !== "object" || build === null) return null;
      return build;
    } catch {
      return null;
    }
  },

  /** Extract the share code from a URL string. */
  extractCode(url: string): string | null {
    try {
      const u = new URL(url);
      return u.searchParams.get(PARAM_KEY);
    } catch {
      return null;
    }
  },

  /** Check whether the current page URL contains a share code. */
  hasShareCode(): boolean {
    return new URLSearchParams(window.location.search).has(PARAM_KEY);
  },

  /** Read the share code from the current page URL. */
  readShareCode(): string | null {
    return new URLSearchParams(window.location.search).get(PARAM_KEY);
  },

  /** Remove the share code from the current URL without reloading. */
  clearShareCode(): void {
    const url = new URL(window.location.href);
    url.searchParams.delete(PARAM_KEY);
    window.history.replaceState({}, "", url.toString());
  },
};
