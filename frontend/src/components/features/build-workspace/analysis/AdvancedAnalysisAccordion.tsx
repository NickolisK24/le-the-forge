/**
 * AdvancedAnalysisAccordion — phase 3 collapsible wrapper for the advanced
 * analysis panels.
 *
 * Wraps the existing leaf panels — `BossEncounterPanel`,
 * `CorruptionScalingPanel`, and `GearUpgradePanel` — inside a single
 * accordion so they don't dominate the right rail on first paint.
 *
 * Behaviour (prompt §7):
 *   - Header: "Advanced Analysis — Boss Encounters, Corruption Scaling,
 *     Gear Upgrades".
 *   - Collapsed by default.
 *   - Open/close state persists in localStorage under the namespaced key
 *     `epochforge.unifiedPlanner.advancedExpanded` so power users do not
 *     have to re-expand on every visit.
 *   - Smooth CSS `max-height` expand/collapse — matches the legacy
 *     `AccordionSection` behaviour, no new animation library.
 *
 * The leaf panels all require a saved-build slug (they hit slug-scoped
 * endpoints). When the workspace holds no slug — e.g. `/workspace/new`
 * before save — the accordion renders a short explainer so the power-user
 * affordance isn't silently hidden.
 */

import { useEffect, useRef, useState, type ReactNode } from "react";

import BossEncounterPanel from "@/components/features/build/BossEncounterPanel";
import CorruptionScalingPanel from "@/components/features/build/CorruptionScalingPanel";
import GearUpgradePanel from "@/components/features/build/GearUpgradePanel";

// ---------------------------------------------------------------------------
// localStorage key — namespaced per phase-3 prompt.
// ---------------------------------------------------------------------------

export const ADVANCED_EXPANDED_KEY = "epochforge.unifiedPlanner.advancedExpanded";

function readStoredOpen(defaultOpen: boolean): boolean {
  if (typeof window === "undefined") return defaultOpen;
  try {
    const raw = window.localStorage.getItem(ADVANCED_EXPANDED_KEY);
    if (raw === "true") return true;
    if (raw === "false") return false;
  } catch {
    /* private mode / disabled storage */
  }
  return defaultOpen;
}

function writeStoredOpen(open: boolean): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(ADVANCED_EXPANDED_KEY, String(open));
  } catch {
    /* ignore */
  }
}

// ---------------------------------------------------------------------------
// Generic accordion shell — local to this file so we can hold the
// min-h-[44px] / wrap-friendly header constraints from the phase-3 mobile
// verification.
// ---------------------------------------------------------------------------

interface AccordionShellProps {
  title: string;
  defaultOpen?: boolean;
  children: ReactNode;
}

function AccordionShell({ title, defaultOpen = false, children }: AccordionShellProps) {
  const [open, setOpen] = useState(() => readStoredOpen(defaultOpen));
  const contentRef = useRef<HTMLDivElement>(null);
  const [measuredHeight, setMeasuredHeight] = useState<number>(0);

  useEffect(() => {
    const el = contentRef.current;
    if (!el) return;
    const measure = () => setMeasuredHeight(el.scrollHeight);
    measure();
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [children]);

  useEffect(() => {
    writeStoredOpen(open);
  }, [open]);

  return (
    <div
      data-testid="advanced-analysis-accordion"
      data-open={open}
      className="rounded border border-forge-border bg-forge-surface overflow-hidden min-w-0"
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="advanced-analysis-accordion-panel"
        data-testid="advanced-analysis-toggle"
        className="flex w-full items-center justify-between gap-3 bg-forge-surface2 px-4 py-3 text-left cursor-pointer border-0 border-b border-forge-border hover:bg-forge-surface2/70 transition-colors min-h-[44px]"
      >
        <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan leading-snug whitespace-normal break-words">
          {title}
        </span>
        <span
          aria-hidden="true"
          className="text-forge-dim font-mono text-xs transition-transform duration-300 shrink-0"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
        >
          ▼
        </span>
      </button>
      <div
        id="advanced-analysis-accordion-panel"
        role="region"
        aria-hidden={!open}
        style={{
          maxHeight: open ? `${measuredHeight}px` : "0px",
          transition: "max-height 350ms ease-in-out",
          overflow: "hidden",
        }}
      >
        <div
          ref={contentRef}
          data-testid="advanced-analysis-body"
          className="p-4 flex flex-col gap-4 min-w-0"
        >
          {children}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Public component
// ---------------------------------------------------------------------------

export interface AdvancedAnalysisAccordionProps {
  /** Persisted build slug. When null, the advanced panels cannot query the
   *  slug-scoped backend endpoints and an explainer renders instead. */
  slug: string | null;
}

export default function AdvancedAnalysisAccordion({
  slug,
}: AdvancedAnalysisAccordionProps) {
  return (
    <AccordionShell
      title="Advanced Analysis — Boss Encounters, Corruption Scaling, Gear Upgrades"
      defaultOpen={false}
    >
      {slug ? (
        <>
          <div className="grid gap-4 lg:grid-cols-2 min-w-0">
            <BossEncounterPanel slug={slug} />
            <CorruptionScalingPanel slug={slug} />
          </div>
          <GearUpgradePanel slug={slug} />
        </>
      ) : (
        <p
          data-testid="advanced-analysis-unsaved-note"
          className="font-body text-sm text-forge-dim italic"
        >
          Save the build to enable boss encounter analysis, corruption
          scaling, and gear-upgrade candidates.
        </p>
      )}
    </AccordionShell>
  );
}
