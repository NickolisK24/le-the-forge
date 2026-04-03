/**
 * UI+8 — Bulk Comparison Selector
 * Multi-select interface for choosing items to compare simultaneously.
 */

import React, { useState, useCallback } from "react";

export interface SelectableItem {
  id: string;
  label: string;
  subtitle?: string;
  meta?: Record<string, unknown>;
  disabled?: boolean;
}

interface BulkSelectorProps {
  items: SelectableItem[];
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
  onCompare: (ids: string[]) => void;
  maxSelectable?: number;
  label?: string;
  className?: string;
  searchable?: boolean;
}

export function BulkSelector({
  items,
  selectedIds,
  onSelectionChange,
  onCompare,
  maxSelectable = 4,
  label = "Select to compare",
  className = "",
  searchable = true,
}: BulkSelectorProps): React.JSX.Element {
  const [query, setQuery] = useState("");

  const filtered = query.trim()
    ? items.filter(
        (i) =>
          i.label.toLowerCase().includes(query.toLowerCase()) ||
          i.subtitle?.toLowerCase().includes(query.toLowerCase())
      )
    : items;

  const toggle = useCallback(
    (id: string) => {
      if (selectedIds.includes(id)) {
        onSelectionChange(selectedIds.filter((s) => s !== id));
      } else if (selectedIds.length < maxSelectable) {
        onSelectionChange([...selectedIds, id]);
      }
    },
    [selectedIds, onSelectionChange, maxSelectable]
  );

  const selectAll = useCallback(() => {
    const available = filtered.filter((i) => !i.disabled).map((i) => i.id);
    onSelectionChange(available.slice(0, maxSelectable));
  }, [filtered, onSelectionChange, maxSelectable]);

  const clearAll = useCallback(() => {
    onSelectionChange([]);
  }, [onSelectionChange]);

  const canAddMore = selectedIds.length < maxSelectable;
  const hasSelection = selectedIds.length >= 2;

  return (
    <div
      className={`rounded-lg bg-[#0d1117] border border-[#2d3748] overflow-hidden ${className}`}
      role="region"
      aria-label="Bulk Selector"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#2d3748] bg-[#161b22]">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-[#f0a020] uppercase tracking-wider">
            {label}
          </span>
          <span className="text-xs text-gray-600">
            {selectedIds.length} / {maxSelectable} selected
          </span>
        </div>

        {searchable && (
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search..."
            className="w-full px-3 py-1.5 text-xs rounded bg-[#0d1117] border border-[#2d3748]
                       text-gray-300 placeholder-gray-600 focus:outline-none focus:border-[#f0a020]"
            aria-label="Search items"
          />
        )}
      </div>

      {/* Toolbar */}
      <div className="px-4 py-2 flex items-center gap-2 border-b border-[#2d3748]/50">
        <button
          onClick={selectAll}
          className="text-xs text-gray-500 hover:text-[#f0a020] transition-colors"
        >
          Select all
        </button>
        <span className="text-gray-700">·</span>
        <button
          onClick={clearAll}
          disabled={selectedIds.length === 0}
          className="text-xs text-gray-500 hover:text-red-400 disabled:opacity-30 transition-colors"
        >
          Clear
        </button>
      </div>

      {/* Item List */}
      <div className="max-h-64 overflow-y-auto divide-y divide-[#2d3748]/30">
        {filtered.map((item) => {
          const isSelected = selectedIds.includes(item.id);
          const isDisabled = item.disabled || (!isSelected && !canAddMore);

          return (
            <label
              key={item.id}
              className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors ${
                isSelected
                  ? "bg-[#f0a020]/5"
                  : isDisabled
                  ? "opacity-40 cursor-not-allowed"
                  : "hover:bg-white/[0.02]"
              }`}
            >
              <input
                type="checkbox"
                checked={isSelected}
                disabled={isDisabled}
                onChange={() => toggle(item.id)}
                className="accent-amber-500 w-3.5 h-3.5"
                aria-label={item.label}
              />
              <div className="min-w-0">
                <div
                  className={`text-xs font-medium truncate ${
                    isSelected ? "text-[#f0a020]" : "text-gray-300"
                  }`}
                >
                  {item.label}
                </div>
                {item.subtitle && (
                  <div className="text-[10px] text-gray-600 truncate">{item.subtitle}</div>
                )}
              </div>
            </label>
          );
        })}

        {filtered.length === 0 && (
          <div className="py-6 text-center text-xs text-gray-600">No items found</div>
        )}
      </div>

      {/* Compare Button */}
      <div className="px-4 py-3 border-t border-[#2d3748]">
        <button
          onClick={() => onCompare(selectedIds)}
          disabled={!hasSelection}
          className="w-full py-2 px-4 text-sm font-semibold rounded
                     bg-[#f0a020] text-black hover:bg-[#ffb83f]
                     disabled:opacity-30 disabled:cursor-not-allowed
                     transition-colors"
          aria-label={`Compare ${selectedIds.length} selected items`}
        >
          Compare {selectedIds.length > 0 ? `(${selectedIds.length})` : ""}
        </button>
        {!hasSelection && (
          <p className="text-xs text-gray-600 text-center mt-1">
            Select at least 2 items
          </p>
        )}
      </div>
    </div>
  );
}
