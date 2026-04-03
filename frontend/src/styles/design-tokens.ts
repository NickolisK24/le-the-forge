/**
 * UI27-UI29 — Design System Tokens
 *
 * Centralized design token definitions for the forge theme.
 * These mirror the Tailwind config but as JS constants for use in
 * dynamic styles, recharts, and any non-Tailwind context.
 */

// ---------------------------------------------------------------------------
// UI27 — Typography
// ---------------------------------------------------------------------------

export const typography = {
  family: {
    display: "Cinzel, serif",
    body: "'Exo 2', system-ui, sans-serif",
    mono: "'JetBrains Mono', monospace",
  },
  size: {
    xs: "0.75rem",    // 12px — labels, badges
    sm: "0.875rem",   // 14px — body, table cells
    base: "1rem",     // 16px — default
    lg: "1.125rem",   // 18px — sub-headings
    xl: "1.25rem",    // 20px — headings
    "2xl": "1.5rem",  // 24px — page titles
    "3xl": "1.875rem", // 30px — hero headings
  },
  weight: {
    normal: "400",
    bold: "700",
  },
  tracking: {
    tight: "-0.01em",
    normal: "0em",
    wide: "0.05em",
    wider: "0.1em",
    widest: "0.18em",
  },
} as const;

// ---------------------------------------------------------------------------
// UI28 — Color System
// ---------------------------------------------------------------------------

export const colors = {
  // Backgrounds
  bg:       "#06080f",
  surface:  "#0c0f1c",
  surface2: "#10152a",
  surface3: "#161c34",

  // Borders
  border:    "rgba(80,100,210,0.22)",
  borderHot: "rgba(130,160,255,0.50)",

  // Primary (amber/gold — crafting, equipment)
  amber:    "#f0a020",
  amberHot: "#ffb83f",
  ember:    "#e06030",
  gold:     "#f5d060",

  // Secondary (cyan — simulation, temporal)
  cyan:    "#00d4f5",
  cyanHot: "#40ddf5",

  // Text
  text:  "#eceef8",
  muted: "#8890b8",
  dim:   "#4a5480",

  // Status
  success: "#3dca74",
  error:   "#ff5050",
  info:    "#5ab0ff",
  purple:  "#b870ff",
} as const;

// Semantic aliases
export const semantic = {
  primary:    colors.amber,
  primaryHot: colors.amberHot,
  secondary:  colors.cyan,
  success:    colors.success,
  warning:    colors.amber,
  error:      colors.error,
  info:       colors.info,
  text:       colors.text,
  textMuted:  colors.muted,
  textDim:    colors.dim,
  bgBase:     colors.bg,
  bgPanel:    colors.surface,
  bgPanel2:   colors.surface2,
  bgPanel3:   colors.surface3,
  border:     colors.border,
} as const;

// Recharts-compatible color palette
export const chartColors = {
  primary:   colors.amber,
  secondary: colors.cyan,
  success:   colors.success,
  error:     colors.error,
  info:      colors.info,
  purple:    colors.purple,
  series: [colors.amber, colors.cyan, colors.success, colors.info, colors.purple, colors.ember],
} as const;

// ---------------------------------------------------------------------------
// UI29 — Spacing & Layout
// ---------------------------------------------------------------------------

export const spacing = {
  0:   "0",
  1:   "0.25rem",   // 4px
  2:   "0.5rem",    // 8px
  3:   "0.75rem",   // 12px
  4:   "1rem",      // 16px
  5:   "1.25rem",   // 20px
  6:   "1.5rem",    // 24px
  8:   "2rem",      // 32px
  10:  "2.5rem",    // 40px
  12:  "3rem",      // 48px
  16:  "4rem",      // 64px
} as const;

export const layout = {
  maxWidth:       "80rem",      // 1280px — max page width
  sidebarCollapsed: "3.5rem",  // 56px
  sidebarExpanded:  "12.5rem", // 200px
  topBarHeight:   "3.5rem",    // 56px
  panelPadding:   spacing[4],
  borderRadius:   "6px",
  borderRadiusSm: "3px",
} as const;

export const shadow = {
  amber: "0 0 14px rgba(240,160,32,0.45), 0 0 28px rgba(240,160,32,0.15)",
  cyan:  "0 0 14px rgba(0,212,245,0.45),  0 0 28px rgba(0,212,245,0.15)",
  gold:  "0 0 14px rgba(245,208,96,0.45),  0 0 28px rgba(245,208,96,0.15)",
} as const;
