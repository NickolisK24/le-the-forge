/**
 * P27 — Craft Debug Page
 *
 * Route: /craft-debug
 *
 * Terminal-style log viewer for crafting simulation events.
 * Generates mock log runs, supports filtering by event type, and
 * tracks entry counts.
 */

import { useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type LogLevel = "CRAFT" | "FRACTURE" | "SUCCESS";

interface LogEntry {
  id: number;
  timestamp: string;
  level: LogLevel;
  message: string;
}

// ---------------------------------------------------------------------------
// Mock log generator
// ---------------------------------------------------------------------------

let globalId = 0;

function nowTs(): string {
  return new Date().toISOString().replace("T", " ").slice(0, 23);
}

const ITEM_ID = "item_001";

function generateTestRun(): LogEntry[] {
  const entries: LogEntry[] = [];

  let fp = 60 + Math.floor(Math.random() * 10);
  let crafts = 0;

  for (let i = 0; i < 10; i++) {
    const roll = Math.random();

    if (roll < 0.15 && fp > 30) {
      // Fracture event
      entries.push({
        id: ++globalId,
        timestamp: nowTs(),
        level: "FRACTURE",
        message: `[FRACTURE] ${ITEM_ID}: minor fracture at FP=${fp}`,
      });
      fp = Math.max(fp - 10, 0);
    } else if (roll < 0.25 && crafts >= 5) {
      // Success event
      const score = (0.7 + Math.random() * 0.25).toFixed(2);
      const fpSpent = 60 - fp;
      entries.push({
        id: ++globalId,
        timestamp: nowTs(),
        level: "SUCCESS",
        message: `[SUCCESS] score=${score} fp_spent=${fpSpent} crafts=${crafts}`,
      });
      crafts = 0;
      fp = 60 + Math.floor(Math.random() * 10);
    } else {
      // Craft event
      const affix = ["max_life", "resistances", "crit_chance", "flat_fire_damage"][
        Math.floor(Math.random() * 4)
      ];
      const action = ["upgrade_affix", "add_affix"][Math.floor(Math.random() * 2)];
      const instability = Math.floor(Math.random() * 30);
      const fpPrev = fp;
      fp = Math.max(fp - Math.floor(Math.random() * 5 + 1), 0);
      crafts++;
      entries.push({
        id: ++globalId,
        timestamp: nowTs(),
        level: "CRAFT",
        message: `[CRAFT] ${ITEM_ID}: ${action} | affix=${affix} | FP: ${fpPrev}→${fp} | Instability: ${instability}`,
      });
    }
  }

  return entries;
}

// ---------------------------------------------------------------------------
// Colour helpers
// ---------------------------------------------------------------------------

function levelColor(level: LogLevel): string {
  switch (level) {
    case "CRAFT":    return "text-green-400";
    case "FRACTURE": return "text-orange-400";
    case "SUCCESS":  return "text-[#22d3ee]";
  }
}

// ---------------------------------------------------------------------------
// Filter buttons
// ---------------------------------------------------------------------------

type FilterType = "All" | LogLevel;
const FILTERS: FilterType[] = ["All", "CRAFT", "FRACTURE", "SUCCESS"];

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function CraftDebugPage() {
  const [log,    setLog]    = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<FilterType>("All");

  function handleGenerate() {
    setLog((prev) => [...prev, ...generateTestRun()]);
  }

  function handleClear() {
    setLog([]);
  }

  const filtered =
    filter === "All" ? log : log.filter((e) => e.level === filter);

  return (
    <div className="mx-auto max-w-4xl space-y-5 p-6">
      {/* Header */}
      <div>
        <h1 className="font-display text-2xl text-[#f5a623]">Craft Debug</h1>
        <p className="font-body text-sm text-gray-400 mt-1">
          Inspect crafting simulation events in real-time with a terminal-style log viewer.
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={handleGenerate}
          className="rounded bg-[#f5a623] px-4 py-1.5 text-sm font-semibold text-[#10152a] transition hover:bg-[#f5a623cc]"
        >
          Generate Test Run
        </button>
        <button
          onClick={handleClear}
          className="rounded border border-[#2a3050] px-4 py-1.5 text-sm text-gray-400 transition hover:text-gray-100 hover:border-gray-500"
        >
          Clear Log
        </button>

        {/* Filter buttons */}
        <div className="flex gap-1 ml-auto">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={[
                "rounded px-2.5 py-1 text-xs font-medium transition-colors",
                filter === f
                  ? "bg-[#f5a623] text-[#10152a]"
                  : "bg-[#1a2035] text-gray-400 hover:text-[#f5a623]",
              ].join(" ")}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Entry count badge */}
        <span className="rounded bg-[#22d3ee22] px-2 py-0.5 text-[11px] text-[#22d3ee]">
          {filtered.length} {filtered.length === 1 ? "entry" : "entries"}
        </span>
      </div>

      {/* Terminal panel */}
      <div className="rounded-lg border border-[#1a2a1a] bg-[#060a06] p-4 font-mono text-xs">
        <div className="h-[480px] overflow-y-auto space-y-0.5">
          {filtered.length === 0 ? (
            <span className="text-green-700">
              {log.length === 0
                ? "// Press 'Generate Test Run' to begin."
                : "// No entries match the current filter."}
            </span>
          ) : (
            filtered.map((entry) => (
              <div key={entry.id} className="flex gap-2 leading-5">
                <span className="text-gray-600 shrink-0 select-none">
                  {entry.timestamp}
                </span>
                <span className={`${levelColor(entry.level)} break-all`}>
                  {entry.message}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
