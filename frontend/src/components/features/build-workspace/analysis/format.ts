/**
 * Shared number formatting helpers for the phase-3 analysis components.
 *
 * Kept in one place so that "Total DPS" on the score card, the offense card,
 * and the skills table all render the same glyph count for the same
 * underlying number. Every helper returns a string so callers do not need to
 * know whether the value is missing/infinite.
 */

export function fmtNumber(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return numberWithThousands(Math.round(n));
}

export function fmtPct(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "—";
  return `${n.toFixed(1)}%`;
}

export function fmtPctFromFraction(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "—";
  return `${(n * 100).toFixed(1)}%`;
}

export function fmtPerSecond(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "—";
  return `${n.toFixed(2)}/s`;
}

function numberWithThousands(n: number): string {
  // `Intl.NumberFormat` would respect locale, but the project's UI is
  // English-only today and we want deterministic comma separators in
  // snapshot / DOM tests.
  const sign = n < 0 ? "-" : "";
  const abs = String(Math.abs(n));
  const parts: string[] = [];
  for (let i = abs.length; i > 0; i -= 3) {
    parts.unshift(abs.slice(Math.max(0, i - 3), i));
  }
  return sign + parts.join(",");
}
