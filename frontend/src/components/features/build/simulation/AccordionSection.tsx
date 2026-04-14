/**
 * AccordionSection — collapsible wrapper used to tuck away advanced
 * simulation panels (boss encounter, corruption scaling, gear upgrade,
 * Monte Carlo variance) so they don't dominate the page on first load.
 *
 * Open / closed state is persisted in localStorage under the key passed
 * as `storageKey`. Expansion uses a CSS max-height transition rather
 * than display:none so the motion is smooth rather than jarring.
 */

import { useEffect, useRef, useState, type ReactNode } from "react";

interface AccordionSectionProps {
  title: string;
  storageKey: string;
  defaultOpen?: boolean;
  children: ReactNode;
}

function readInitial(storageKey: string, defaultOpen: boolean): boolean {
  if (typeof window === "undefined") return defaultOpen;
  try {
    const raw = window.localStorage.getItem(storageKey);
    if (raw === "true")  return true;
    if (raw === "false") return false;
  } catch {
    // Private mode / disabled storage — fall through
  }
  return defaultOpen;
}

export default function AccordionSection({
  title, storageKey, defaultOpen = false, children,
}: AccordionSectionProps) {
  const [open, setOpen] = useState(() => readInitial(storageKey, defaultOpen));
  const contentRef = useRef<HTMLDivElement>(null);
  const [measuredHeight, setMeasuredHeight] = useState<number>(0);

  // Measure on content change so expanded max-height grows with content.
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

  // Persist to localStorage whenever open changes.
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      window.localStorage.setItem(storageKey, String(open));
    } catch {
      /* ignore */
    }
  }, [open, storageKey]);

  return (
    <div className="rounded border border-forge-border bg-forge-surface overflow-hidden min-w-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={`${storageKey}-panel`}
        className="flex w-full items-center justify-between gap-3 bg-forge-surface2 px-4 py-3 text-left cursor-pointer border-0 border-b border-forge-border hover:bg-forge-surface2/70 transition-colors"
      >
        <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
          {title}
        </span>
        <span
          aria-hidden="true"
          className="text-forge-dim font-mono text-xs transition-transform duration-300"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
        >
          ▼
        </span>
      </button>
      <div
        id={`${storageKey}-panel`}
        role="region"
        aria-hidden={!open}
        style={{
          maxHeight: open ? `${measuredHeight}px` : "0px",
          transition: "max-height 350ms ease-in-out",
          overflow: "hidden",
        }}
      >
        <div ref={contentRef} className="p-4 flex flex-col gap-4 min-w-0">
          {children}
        </div>
      </div>
    </div>
  );
}
