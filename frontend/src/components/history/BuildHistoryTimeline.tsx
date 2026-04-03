/**
 * UI+6 — Build History Timeline
 * Visual undo/redo timeline using the useUndoRedo hook.
 */

import React from "react";

export interface HistoryEntry<T> {
  state: T;
  label: string;
  timestamp: number;
}

interface BuildHistoryTimelineProps<T> {
  past: T[];
  present: T;
  future: T[];
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  getLabel?: (state: T, index: number) => string;
  className?: string;
  maxVisible?: number;
}

function formatTime(timestamp: number): string {
  const d = new Date(timestamp);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function BuildHistoryTimeline<T>({
  past,
  present,
  future,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  getLabel,
  className = "",
  maxVisible = 10,
}: BuildHistoryTimelineProps<T>): React.JSX.Element {
  const allEntries: Array<{ state: T; label: string; isCurrent: boolean; isFuture: boolean; index: number }> = [
    ...past.slice(-maxVisible).map((state, i) => ({
      state,
      label: getLabel ? getLabel(state, i) : `Change ${i + 1}`,
      isCurrent: false,
      isFuture: false,
      index: i,
    })),
    {
      state: present,
      label: getLabel ? getLabel(present, past.length) : "Current",
      isCurrent: true,
      isFuture: false,
      index: past.length,
    },
    ...future.slice(0, maxVisible).map((state, i) => ({
      state,
      label: getLabel ? getLabel(state, past.length + 1 + i) : `Future ${i + 1}`,
      isCurrent: false,
      isFuture: true,
      index: past.length + 1 + i,
    })),
  ];

  return (
    <div
      className={`rounded-lg bg-[#0d1117] border border-[#2d3748] p-4 ${className}`}
      role="region"
      aria-label="Build History"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-[#f0a020] uppercase tracking-wider">
          History
        </h3>
        <div className="flex gap-1">
          <button
            onClick={onUndo}
            disabled={!canUndo}
            className="px-2 py-1 text-xs rounded border border-[#2d3748] text-gray-300
                       hover:border-[#f0a020] hover:text-[#f0a020] disabled:opacity-30
                       disabled:cursor-not-allowed transition-colors"
            aria-label="Undo"
            title="Undo (Ctrl+Z)"
          >
            ↩ Undo
          </button>
          <button
            onClick={onRedo}
            disabled={!canRedo}
            className="px-2 py-1 text-xs rounded border border-[#2d3748] text-gray-300
                       hover:border-[#00d4f5] hover:text-[#00d4f5] disabled:opacity-30
                       disabled:cursor-not-allowed transition-colors"
            aria-label="Redo"
            title="Redo (Ctrl+Shift+Z)"
          >
            ↪ Redo
          </button>
        </div>
      </div>

      {/* Timeline */}
      <div className="space-y-1 max-h-64 overflow-y-auto" role="list">
        {allEntries.map((entry, idx) => (
          <div
            key={idx}
            role="listitem"
            className={`flex items-center gap-2 px-2 py-1 rounded text-xs transition-colors ${
              entry.isCurrent
                ? "bg-[#f0a020]/10 border border-[#f0a020]/40"
                : entry.isFuture
                ? "opacity-40"
                : "hover:bg-white/5"
            }`}
          >
            {/* Indicator dot */}
            <div
              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                entry.isCurrent
                  ? "bg-[#f0a020]"
                  : entry.isFuture
                  ? "bg-gray-600"
                  : "bg-gray-500"
              }`}
              aria-hidden
            />

            {/* Label */}
            <span
              className={
                entry.isCurrent
                  ? "text-[#f0a020] font-semibold"
                  : entry.isFuture
                  ? "text-gray-600"
                  : "text-gray-400"
              }
            >
              {entry.label}
            </span>

            {entry.isCurrent && (
              <span className="ml-auto text-[#f0a020] text-[10px] font-medium">NOW</span>
            )}
          </div>
        ))}

        {allEntries.length === 0 && (
          <p className="text-xs text-gray-600 text-center py-2">No history yet</p>
        )}
      </div>

      {/* Summary */}
      <div className="mt-3 pt-3 border-t border-[#2d3748] flex justify-between text-xs text-gray-600">
        <span>{past.length} undo step{past.length !== 1 ? "s" : ""}</span>
        <span>{future.length} redo step{future.length !== 1 ? "s" : ""}</span>
      </div>
    </div>
  );
}
