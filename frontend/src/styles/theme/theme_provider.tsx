/**
 * UI+13 — Theme System
 * Dark mode / light mode toggle with CSS variable injection.
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";

export type Theme = "dark" | "light";

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isDark: boolean;
  isLight: boolean;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: "dark",
  setTheme: () => undefined,
  toggleTheme: () => undefined,
  isDark: true,
  isLight: false,
});

const STORAGE_KEY = "forge_theme";
const DEFAULT_THEME: Theme = "dark";

const DARK_VARS: Record<string, string> = {
  "--color-bg":          "#06080f",
  "--color-surface":     "#0d1117",
  "--color-surface2":    "#161b22",
  "--color-surface3":    "#1c2230",
  "--color-border":      "#2d3748",
  "--color-text":        "#e2e8f0",
  "--color-text-muted":  "#8899aa",
  "--color-text-dim":    "#556677",
  "--color-amber":       "#f0a020",
  "--color-amber-hot":   "#ffb83f",
  "--color-cyan":        "#00d4f5",
  "--color-cyan-hot":    "#40ddf5",
  "--color-success":     "#3dca74",
  "--color-error":       "#ff5050",
  "--color-info":        "#5ab0ff",
};

const LIGHT_VARS: Record<string, string> = {
  "--color-bg":          "#f8f9fa",
  "--color-surface":     "#ffffff",
  "--color-surface2":    "#f1f3f5",
  "--color-surface3":    "#e9ecef",
  "--color-border":      "#ced4da",
  "--color-text":        "#212529",
  "--color-text-muted":  "#6c757d",
  "--color-text-dim":    "#adb5bd",
  "--color-amber":       "#d4870a",
  "--color-amber-hot":   "#e8960f",
  "--color-cyan":        "#0598b0",
  "--color-cyan-hot":    "#0aaac5",
  "--color-success":     "#198754",
  "--color-error":       "#dc3545",
  "--color-info":        "#0d6efd",
};

function applyTheme(theme: Theme): void {
  const vars = theme === "dark" ? DARK_VARS : LIGHT_VARS;
  const root = document.documentElement;
  for (const [key, value] of Object.entries(vars)) {
    root.style.setProperty(key, value);
  }
  root.setAttribute("data-theme", theme);
  document.body.classList.toggle("theme-dark", theme === "dark");
  document.body.classList.toggle("theme-light", theme === "light");
}

function readStoredTheme(): Theme {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "dark" || stored === "light") return stored;
    // Respect OS preference
    if (window.matchMedia?.("(prefers-color-scheme: light)").matches) return "light";
  } catch {
    // ignore
  }
  return DEFAULT_THEME;
}

export function ThemeProvider({ children }: { children: ReactNode }): React.JSX.Element {
  const [theme, setThemeState] = useState<Theme>(() =>
    typeof window !== "undefined" ? readStoredTheme() : DEFAULT_THEME
  );

  useEffect(() => {
    applyTheme(theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // ignore
    }
  }, [theme]);

  const setTheme = useCallback((t: Theme) => setThemeState(t), []);
  const toggleTheme = useCallback(
    () => setThemeState((t) => (t === "dark" ? "light" : "dark")),
    []
  );

  return (
    <ThemeContext.Provider
      value={{ theme, setTheme, toggleTheme, isDark: theme === "dark", isLight: theme === "light" }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  return useContext(ThemeContext);
}

/** Standalone helper: get the current CSS variable value. */
export function getThemeVar(variable: string): string {
  if (typeof document === "undefined") return "";
  return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
}

export { DARK_VARS, LIGHT_VARS };
