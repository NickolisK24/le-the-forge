/**
 * ClassesPage — displays all character classes from the backend API.
 *
 * Reference template for all data-driven UI components.
 *
 * Pattern:
 *   1. Fetch via shared API client (useClasses hook)
 *   2. Handle loading / error / empty states explicitly
 *   3. Validate loaded count against expected count
 *   4. Render data using reusable card components
 */

import { useClasses } from "@/hooks";
import ClassCard from "@/components/classes/ClassCard";

const EXPECTED_CLASS_COUNT = 5;

// One-liner flavour descriptions. Keyed by class name.
const CLASS_DESCRIPTIONS: Record<string, string> = {
  Sentinel:  "Heavy-armoured melee champion — stand your ground, swing hard, and punish anything that gets close.",
  Mage:      "Elemental caster — trade defences for devastating ranged spells and board-wide AoE.",
  Primalist: "Nature-aligned brute with wolves, totems, and shape-shifts — versatile across melee, ranged, and summons.",
  Rogue:     "Agile hit-and-run specialist — stack crit and movement, strike before the enemy reacts.",
  Acolyte:   "Master of death magic — minions, damage-over-time, and curses that grind down tough targets.",
};

// Per-mastery colours. Falls back to the class colour for unknown names.
const MASTERY_COLORS: Record<string, string> = {
  // Sentinel
  Paladin:     "#f5d060",
  "Forge Guard": "#e06030",
  "Void Knight": "#b870ff",
  // Mage
  Sorcerer:    "#00d4f5",
  Spellblade:  "#ff7070",
  Runemaster:  "#f0a020",
  // Primalist
  Beastmaster: "#c07a3c",
  Druid:       "#3dca74",
  Shaman:      "#5ab0ff",
  // Rogue
  Bladedancer: "#ff5050",
  Marksman:    "#c0f030",
  Falconer:    "#5ab0ff",
  // Acolyte
  Necromancer: "#3dca74",
  Lich:        "#b870ff",
  Warlock:     "#ff5090",
};

export default function ClassesPage() {
  const { data: classesRes, isLoading, isError, error } = useClasses();

  // Unwrap ApiResponse envelope
  const classesData = classesRes?.data ?? null;
  const apiErrors = classesRes?.errors ?? null;

  // Derive class list from the dict response
  const classList = classesData
    ? Object.entries(classesData).map(([name, meta]) => ({
        name,
        color: (meta as any).color ?? "#888",
        masteries: (meta as any).masteries ?? [],
        skills: (meta as any).skills ?? [],
      }))
    : [];

  const classCount = classList.length;
  const countMismatch = classCount > 0 && classCount !== EXPECTED_CLASS_COUNT;

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-forge-amber mb-4">Classes</h1>
        <div className="flex items-center gap-3 text-forge-dim">
          <span className="animate-spin text-lg">&#x21BB;</span>
          <span className="font-mono text-sm">Loading class data...</span>
        </div>
      </div>
    );
  }

  // --- Error state ---
  if (isError || apiErrors) {
    const message =
      apiErrors?.[0]?.message ??
      (error instanceof Error ? error.message : "Failed to load class data");
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-forge-amber mb-4">Classes</h1>
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3">
          <p className="text-sm text-red-400 font-medium">Error loading classes</p>
          <p className="text-xs text-red-400/70 mt-1">{message}</p>
        </div>
      </div>
    );
  }

  // --- Empty state ---
  if (classCount === 0) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-forge-amber mb-4">Classes</h1>
        <div className="rounded-lg border border-forge-border bg-forge-surface px-4 py-6 text-center">
          <p className="text-sm text-forge-dim">No class data available.</p>
          <p className="text-xs text-forge-dim/60 mt-1">
            The backend may not have class definitions loaded.
          </p>
        </div>
      </div>
    );
  }

  // --- Data loaded ---
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold text-forge-amber">Classes</h1>
        <p className="mt-1 font-body text-sm text-forge-muted">
          Character classes and their mastery specializations.
        </p>
      </div>

      {/* Validation badge */}
      <div className="mb-4 flex items-center gap-3">
        <span
          className={`rounded px-2.5 py-1 font-mono text-xs font-semibold ${
            countMismatch
              ? "bg-yellow-500/15 text-yellow-400"
              : "bg-green-500/15 text-green-400"
          }`}
        >
          Classes Loaded: {classCount}
        </span>
        {countMismatch && (
          <span className="text-xs text-yellow-400">
            Expected {EXPECTED_CLASS_COUNT} — count mismatch
          </span>
        )}
      </div>

      {/* Class cards */}
      <div className="space-y-4">
        {classList.map((cls) => (
          <ClassCard
            key={cls.name}
            name={cls.name}
            color={cls.color}
            masteries={cls.masteries}
            skills={cls.skills}
            description={CLASS_DESCRIPTIONS[cls.name]}
            masteryColors={MASTERY_COLORS}
            to={`/build?class=${encodeURIComponent(cls.name)}`}
          />
        ))}
      </div>
    </div>
  );
}
