/**
 * UI+7 — Global Comparison Mode
 * Side-by-side comparison of builds, items, or craft results.
 */

import React, { useState } from "react";

export type ComparisonType = "build" | "item" | "craft";

export interface ComparisonItem {
  id: string;
  label: string;
  data: Record<string, unknown>;
}

export interface ComparisonField {
  key: string;
  label: string;
  format?: (value: unknown) => string;
  higherIsBetter?: boolean;
}

interface GlobalComparisonViewProps {
  type: ComparisonType;
  items: ComparisonItem[];
  fields: ComparisonField[];
  onRemove?: (id: string) => void;
  className?: string;
  maxItems?: number;
}

type DiffDirection = "better" | "worse" | "equal" | "n/a";

function numericValue(v: unknown): number | null {
  if (typeof v === "number") return v;
  if (typeof v === "string") {
    const n = parseFloat(v);
    return isNaN(n) ? null : n;
  }
  return null;
}

function diffClass(dir: DiffDirection, good: boolean): string {
  if (dir === "n/a" || dir === "equal") return "text-gray-400";
  if ((dir === "better") === good) return "text-green-400";
  return "text-red-400";
}

function getDiffMark(dir: DiffDirection, good: boolean): string {
  if (dir === "n/a" || dir === "equal") return "";
  if ((dir === "better") === good) return "▲";
  return "▼";
}

function compareValues(
  a: unknown,
  b: unknown,
  higherIsBetter = true
): DiffDirection {
  const na = numericValue(a);
  const nb = numericValue(b);
  if (na === null || nb === null) return "n/a";
  if (na === nb) return "equal";
  return na > nb ? (higherIsBetter ? "better" : "worse") : (higherIsBetter ? "worse" : "better");
}

function defaultFormat(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return v % 1 === 0 ? String(v) : v.toFixed(2);
  return String(v);
}

export function GlobalComparisonView({
  type,
  items,
  fields,
  onRemove,
  className = "",
  maxItems = 4,
}: GlobalComparisonViewProps): React.JSX.Element {
  const [pinnedId, setPinnedId] = useState<string | null>(items[0]?.id ?? null);
  const visibleItems = items.slice(0, maxItems);
  const pinnedItem = visibleItems.find((i) => i.id === pinnedId) ?? visibleItems[0];

  const typeLabel: Record<ComparisonType, string> = {
    build: "Build",
    item: "Item",
    craft: "Craft",
  };

  return (
    <div
      className={`rounded-lg bg-[#0d1117] border border-[#2d3748] overflow-hidden ${className}`}
      role="region"
      aria-label={`${typeLabel[type]} Comparison`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[#2d3748] bg-[#161b22]">
        <span className="text-xs text-[#f0a020] font-semibold uppercase tracking-wider">
          {typeLabel[type]} Comparison
        </span>
        <span className="text-xs text-gray-600">({visibleItems.length} / {maxItems})</span>
      </div>

      {/* Column Headers */}
      <div
        className="grid border-b border-[#2d3748]"
        style={{ gridTemplateColumns: `140px repeat(${visibleItems.length}, 1fr)` }}
      >
        <div className="px-3 py-2 text-xs text-gray-600 font-medium">Stat</div>
        {visibleItems.map((item) => (
          <div
            key={item.id}
            className={`px-3 py-2 text-center ${
              item.id === pinnedItem?.id ? "bg-[#f0a020]/5" : ""
            }`}
          >
            <div className="flex items-center justify-center gap-1">
              <button
                onClick={() => setPinnedId(item.id)}
                className={`text-xs font-semibold truncate max-w-[80px] ${
                  item.id === pinnedItem?.id
                    ? "text-[#f0a020]"
                    : "text-gray-300 hover:text-white"
                }`}
                title={`Pin "${item.label}" as reference`}
              >
                {item.label}
              </button>
              {onRemove && (
                <button
                  onClick={() => onRemove(item.id)}
                  className="text-gray-600 hover:text-red-400 text-xs ml-1"
                  aria-label={`Remove ${item.label}`}
                >
                  ×
                </button>
              )}
            </div>
            {item.id === pinnedItem?.id && (
              <div className="text-[10px] text-[#f0a020]/60 mt-0.5">reference</div>
            )}
          </div>
        ))}
      </div>

      {/* Stat Rows */}
      <div className="divide-y divide-[#2d3748]/50">
        {fields.map((field) => (
          <div
            key={field.key}
            className="grid hover:bg-white/[0.02] transition-colors"
            style={{ gridTemplateColumns: `140px repeat(${visibleItems.length}, 1fr)` }}
          >
            {/* Field name */}
            <div className="px-3 py-2 text-xs text-gray-500">{field.label}</div>

            {/* Values */}
            {visibleItems.map((item) => {
              const value = item.data[field.key];
              const format = field.format ?? defaultFormat;
              const dir =
                item.id === pinnedItem?.id
                  ? "equal"
                  : compareValues(value, pinnedItem?.data[field.key], field.higherIsBetter ?? true);

              return (
                <div
                  key={item.id}
                  className={`px-3 py-2 text-center text-xs font-mono ${
                    item.id === pinnedItem?.id ? "bg-[#f0a020]/5" : ""
                  } ${diffClass(dir, field.higherIsBetter ?? true)}`}
                >
                  {format(value)}
                  {dir !== "equal" && dir !== "n/a" && item.id !== pinnedItem?.id && (
                    <span className="ml-1 text-[10px]">
                      {getDiffMark(dir, field.higherIsBetter ?? true)}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {visibleItems.length === 0 && (
        <div className="py-8 text-center text-gray-600 text-sm">
          Add items to compare
        </div>
      )}
    </div>
  );
}
