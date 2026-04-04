/**
 * UI+11 — Session Restore
 * Save and restore full UI state across page refreshes.
 */

export interface SessionState {
  version: number;
  activePage: string;
  activeBuildId: string | null;
  scrollPositions: Record<string, number>;
  openPanels: string[];
  formDrafts: Record<string, unknown>;
  lastSaved: number;
}

const STORAGE_KEY = "forge_session";
const SESSION_VERSION = 1;
/** How long a saved session remains valid (24 hours). */
const SESSION_TTL_MS = 24 * 60 * 60 * 1000;

function defaultSession(): SessionState {
  return {
    version: SESSION_VERSION,
    activePage: "/",
    activeBuildId: null,
    scrollPositions: {},
    openPanels: [],
    formDrafts: {},
    lastSaved: 0,
  };
}

class SessionRestoreClass {
  private state: SessionState = defaultSession();

  constructor() {
    this.load();
  }

  private load(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as SessionState;
      if (parsed.version !== SESSION_VERSION) return;
      if (Date.now() - parsed.lastSaved > SESSION_TTL_MS) return;
      this.state = parsed;
    } catch {
      this.state = defaultSession();
    }
  }

  private persist(): void {
    try {
      this.state.lastSaved = Date.now();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
    } catch {
      // ignore
    }
  }

  // ─── Session Snapshot ───────────────────────────────────────────────────────

  get(): SessionState {
    return { ...this.state };
  }

  /** Update multiple fields at once and persist. */
  patch(changes: Partial<SessionState>): void {
    Object.assign(this.state, changes);
    this.persist();
  }

  // ─── Page Tracking ──────────────────────────────────────────────────────────

  setActivePage(page: string): void {
    this.state.activePage = page;
    this.persist();
  }

  getActivePage(): string {
    return this.state.activePage;
  }

  // ─── Build Tracking ─────────────────────────────────────────────────────────

  setActiveBuildId(id: string | null): void {
    this.state.activeBuildId = id;
    this.persist();
  }

  getActiveBuildId(): string | null {
    return this.state.activeBuildId;
  }

  // ─── Scroll Positions ───────────────────────────────────────────────────────

  saveScrollPosition(key: string, position: number): void {
    this.state.scrollPositions[key] = position;
    this.persist();
  }

  getScrollPosition(key: string): number {
    return this.state.scrollPositions[key] ?? 0;
  }

  // ─── Panel State ────────────────────────────────────────────────────────────

  openPanel(id: string): void {
    if (!this.state.openPanels.includes(id)) {
      this.state.openPanels.push(id);
      this.persist();
    }
  }

  closePanel(id: string): void {
    this.state.openPanels = this.state.openPanels.filter((p) => p !== id);
    this.persist();
  }

  isPanelOpen(id: string): boolean {
    return this.state.openPanels.includes(id);
  }

  // ─── Form Drafts ────────────────────────────────────────────────────────────

  saveDraft(key: string, data: unknown): void {
    this.state.formDrafts[key] = data;
    this.persist();
  }

  getDraft<T>(key: string): T | null {
    return (this.state.formDrafts[key] as T) ?? null;
  }

  clearDraft(key: string): void {
    delete this.state.formDrafts[key];
    this.persist();
  }

  // ─── Lifecycle ──────────────────────────────────────────────────────────────

  /** Check whether a valid session exists to restore. */
  hasSession(): boolean {
    return this.state.lastSaved > 0;
  }

  /** Reset session to defaults and clear storage. */
  clear(): void {
    this.state = defaultSession();
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  }
}

export const SessionRestore = new SessionRestoreClass();
