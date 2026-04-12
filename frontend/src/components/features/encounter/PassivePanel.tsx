/**
 * E10 — Passive Panel
 *
 * For serious builds, plan passives in the Build Planner and import them.
 * The raw node-ID textarea is kept as a collapsible advanced input so power
 * users can still paste IDs directly.
 */

import { useState } from "react";
import { Link } from "react-router-dom";

interface Props {
  passiveIds: number[];
  onChange: (ids: number[]) => void;
  disabled?: boolean;
}

export default function PassivePanel({ passiveIds, onChange, disabled }: Props) {
  const [showAdvanced, setShowAdvanced] = useState(passiveIds.length > 0);
  const raw = passiveIds.join(", ");

  function handleChange(value: string) {
    const ids = value
      .split(/[,\s]+/)
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n) && n > 0);
    onChange(ids);
  }

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Passive Nodes
      </h3>

      <div className="rounded border border-forge-border bg-forge-surface2/40 px-4 py-3">
        <p className="text-sm text-forge-muted leading-relaxed">
          Passive trees are complex. Plan yours in the{" "}
          <strong className="text-forge-text">Build Planner</strong>, then
          import it here for simulation.
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Link to="/build">
            <button
              type="button"
              className="rounded bg-forge-amber/20 border border-forge-amber/50 text-forge-amber hover:bg-forge-amber/30 px-3 py-1.5 text-xs font-mono uppercase tracking-widest transition-colors"
              disabled={disabled}
            >
              Go to Build Planner →
            </button>
          </Link>
          {passiveIds.length > 0 && (
            <span className="text-xs text-forge-muted font-mono">
              {passiveIds.length} node{passiveIds.length !== 1 ? "s" : ""} loaded
            </span>
          )}
        </div>
      </div>

      <button
        type="button"
        onClick={() => setShowAdvanced((v) => !v)}
        disabled={disabled}
        className="mt-2 text-[11px] font-mono uppercase tracking-widest text-forge-dim hover:text-forge-muted bg-transparent border-none cursor-pointer transition-colors"
      >
        {showAdvanced ? "▾" : "▸"} Advanced: paste node IDs
      </button>

      {showAdvanced && (
        <div className="mt-2">
          <p className="mb-1 text-xs text-forge-dim">
            For testing: paste allocated passive node IDs (comma- or
            space-separated).
          </p>
          <textarea
            value={raw}
            disabled={disabled}
            onChange={(e) => handleChange(e.target.value)}
            rows={2}
            placeholder="e.g. 101, 205, 340"
            className="
              w-full rounded border border-forge-border bg-forge-input
              px-3 py-2 text-xs text-forge-text font-mono
              focus:border-forge-accent focus:outline-none
              disabled:opacity-50 resize-none
            "
          />
        </div>
      )}
    </section>
  );
}
