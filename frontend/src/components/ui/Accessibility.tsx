/**
 * UI30-UI32 — Accessibility Utilities
 *
 * UI30: Keyboard navigation support
 * UI31: Screen reader support (SR-only text, ARIA helpers)
 * UI32: Color contrast compliance utilities
 */

import { useEffect, KeyboardEvent } from "react";

// ---------------------------------------------------------------------------
// UI31 — Screen Reader Support
// ---------------------------------------------------------------------------

/** Visually hidden text that is still read by screen readers */
export function ScreenReaderOnly({ children }: { children: React.ReactNode }) {
  return (
    <span className="sr-only">
      {children}
    </span>
  );
}

/** Skip-to-content link for keyboard users */
export function SkipToContent({ targetId = "main-content" }: { targetId?: string }) {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[9999] focus:px-4 focus:py-2 focus:bg-forge-amber focus:text-forge-bg focus:rounded font-mono text-sm font-bold"
    >
      Skip to main content
    </a>
  );
}

/** ARIA live region for dynamic announcements */
export function LiveRegion({
  message,
  politeness = "polite",
}: {
  message: string;
  politeness?: "polite" | "assertive";
}) {
  return (
    <div
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
}

// ---------------------------------------------------------------------------
// UI30 — Keyboard Navigation
// ---------------------------------------------------------------------------

/** Key handler factory for common keyboard patterns */
export function onKeyAction(
  key: string | string[],
  handler: () => void
): (e: KeyboardEvent) => void {
  const keys = Array.isArray(key) ? key : [key];
  return (e: KeyboardEvent) => {
    if (keys.includes(e.key)) {
      e.preventDefault();
      handler();
    }
  };
}

/** Hook: trap focus within a container (for modals/dialogs) */
export function useFocusTrap(ref: React.RefObject<HTMLElement | null>, active: boolean) {
  useEffect(() => {
    if (!active || !ref.current) return;

    const el = ref.current;
    const focusable = el.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    function handleTab(e: globalThis.KeyboardEvent) {
      if (e.key !== "Tab") return;
      if (e.shiftKey) {
        if (document.activeElement === first) {
          last?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === last) {
          first?.focus();
          e.preventDefault();
        }
      }
    }

    document.addEventListener("keydown", handleTab);
    first?.focus();
    return () => document.removeEventListener("keydown", handleTab);
  }, [ref, active]);
}

/** Hook: close on Escape key */
export function useEscapeKey(handler: () => void, active: boolean = true) {
  useEffect(() => {
    if (!active) return;
    function onKeyDown(e: globalThis.KeyboardEvent) {
      if (e.key === "Escape") handler();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [handler, active]);
}

// ---------------------------------------------------------------------------
// UI32 — Color Contrast Compliance
// ---------------------------------------------------------------------------

/** Check if a hex color meets WCAG AA contrast ratio against a background */
function hexToRgb(hex: string): [number, number, number] {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

function relativeLuminance([r, g, b]: [number, number, number]): number {
  const toLinear = (v: number) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

export function contrastRatio(fg: string, bg: string): number {
  const l1 = relativeLuminance(hexToRgb(fg));
  const l2 = relativeLuminance(hexToRgb(bg));
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

/** Returns true if contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large text) */
export function meetsWcagAA(fg: string, bg: string, largeText = false): boolean {
  return contrastRatio(fg, bg) >= (largeText ? 3.0 : 4.5);
}

/** Forge theme contrast checks (design validation) */
export const forgeContrast = {
  amberOnBg:  () => contrastRatio("#f0a020", "#06080f"),
  cyanOnBg:   () => contrastRatio("#00d4f5", "#06080f"),
  textOnBg:   () => contrastRatio("#eceef8", "#06080f"),
  mutedOnBg:  () => contrastRatio("#8890b8", "#06080f"),
} as const;
