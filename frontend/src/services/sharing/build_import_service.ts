/**
 * UI+2 — Build Import via URL
 * Load shared builds from encoded URLs.
 */

import { BuildShareService, ShareableBuild } from "./build_share_service";

export type ImportStatus = "idle" | "loading" | "success" | "error";

export interface ImportResult {
  status: ImportStatus;
  build: ShareableBuild | null;
  error?: string;
}

export interface ImportOptions {
  /** Validate required fields before accepting the build. */
  validate?: boolean;
  /** Override the URL to import from (defaults to current window URL). */
  sourceUrl?: string;
}

const REQUIRED_FIELDS: (keyof ShareableBuild)[] = [
  "name",
  "characterClass",
  "mastery",
];

function validateBuild(build: ShareableBuild): string | null {
  for (const field of REQUIRED_FIELDS) {
    if (!build[field]) return `Missing required field: ${field}`;
  }
  if (build.version !== 1) {
    return `Unsupported build version: ${build.version}`;
  }
  return null;
}

export const BuildImportService = {
  /**
   * Attempt to import a build from the current page URL.
   * Returns a result object with status and build data.
   */
  importFromCurrentUrl(options: ImportOptions = {}): ImportResult {
    const { validate = true, sourceUrl } = options;

    let code: string | null;
    if (sourceUrl) {
      code = BuildShareService.extractCode(sourceUrl);
    } else {
      code = BuildShareService.readShareCode();
    }

    if (!code) {
      return { status: "idle", build: null };
    }

    return this.importFromCode(code, { validate });
  },

  /**
   * Import a build from a raw share code.
   */
  importFromCode(code: string, options: { validate?: boolean } = {}): ImportResult {
    const { validate = true } = options;
    const build = BuildShareService.decode(code);

    if (!build) {
      return {
        status: "error",
        build: null,
        error: "Invalid share code — could not decode build data.",
      };
    }

    if (validate) {
      const validationError = validateBuild(build);
      if (validationError) {
        return { status: "error", build: null, error: validationError };
      }
    }

    return { status: "success", build };
  },

  /**
   * Import a build from a full share URL.
   */
  importFromUrl(url: string, options: { validate?: boolean } = {}): ImportResult {
    const code = BuildShareService.extractCode(url);
    if (!code) {
      return {
        status: "error",
        build: null,
        error: "No build code found in URL.",
      };
    }
    return this.importFromCode(code, options);
  },

  /**
   * Check whether the current URL has an importable build.
   */
  hasPendingImport(): boolean {
    return BuildShareService.hasShareCode();
  },

  /**
   * Consume the pending import from the URL and clear the code.
   * Returns the import result and removes the param from the URL.
   */
  consumeImport(options: ImportOptions = {}): ImportResult {
    const result = this.importFromCurrentUrl(options);
    if (result.status === "success" || result.status === "error") {
      BuildShareService.clearShareCode();
    }
    return result;
  },
};
