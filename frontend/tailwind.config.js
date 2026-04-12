/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Backgrounds — deep space with blue-black tint
        "forge-bg":       "#06080f",
        "forge-surface":  "#0c0f1c",
        "forge-surface2": "#10152a",
        "forge-surface3": "#161c34",
        // Input/form backgrounds — slightly darker than surface2 for contrast
        "forge-input":    "#10152a",
        // Borders — blue-purple tint
        "forge-border":     "rgba(80,100,210,0.22)",
        "forge-border-hot": "rgba(130,160,255,0.50)",
        // Primary accent — warm gold (crafting / equipment)
        "forge-accent":    "#f0a020",
        "forge-amber":     "#f0a020",
        "forge-amber-hot": "#ffb83f",
        "forge-ember":     "#e06030",
        "forge-gold":      "#f5d060",
        // Secondary accent — cyan (temporal energy)
        "forge-cyan":     "#00d4f5",
        "forge-cyan-hot": "#40ddf5",
        // Text
        "forge-text":  "#eceef8",
        "forge-muted": "#8890b8",
        "forge-dim":   "#4a5480",
        // Status
        "forge-green":  "#3dca74",
        "forge-red":    "#ff5050",
        "forge-blue":   "#5ab0ff",
        "forge-purple": "#b870ff",
      },
      fontFamily: {
        display: ["Cinzel", "serif"],
        body:    ["Exo 2", "system-ui", "sans-serif"],
        mono:    ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        sm:      "3px",
        DEFAULT: "6px",
      },
      boxShadow: {
        "glow-amber": "0 0 14px rgba(240,160,32,0.45), 0 0 28px rgba(240,160,32,0.15)",
        "glow-cyan":  "0 0 14px rgba(0,212,245,0.45),  0 0 28px rgba(0,212,245,0.15)",
        "glow-gold":  "0 0 14px rgba(245,208,96,0.45),  0 0 28px rgba(245,208,96,0.15)",
      },
    },
  },
  plugins: [],
};
