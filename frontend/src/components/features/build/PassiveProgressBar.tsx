import { useState, useRef, useEffect } from "react";
import { clsx } from "clsx";
import { PASSIVE_TREES } from "@/data/passiveTrees";
import type { PassiveNode } from "@/lib/gameData";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a flat id→node lookup across all regions for a class */
function buildNodeMap(characterClass: string): Map<number, PassiveNode> {
  const cls = characterClass.toLowerCase();
  const regionMap = PASSIVE_TREES[cls] ?? {};
  const map = new Map<number, PassiveNode>();
  for (const nodes of Object.values(regionMap)) {
    for (const n of nodes) map.set(n.id, n);
  }
  return map;
}

const TYPE_COLOR: Record<string, string> = {
  "mastery-gate": "border-orange-600/70 bg-orange-950/60 text-orange-300",
  keystone:       "border-emerald-600/70 bg-emerald-950/60 text-emerald-300",
  notable:        "border-sky-600/70 bg-sky-950/60 text-sky-300",
  core:           "border-forge-amber/40 bg-forge-bg/80 text-forge-amber",
};

const TYPE_DOT: Record<string, string> = {
  "mastery-gate": "bg-orange-500",
  keystone:       "bg-emerald-400",
  notable:        "bg-sky-400",
  core:           "bg-forge-amber",
};

// Level at which each passive point is awarded in Last Epoch (approx.)
// Points: 1 per level 2–90, then every 2 levels up to 100 → ~94 pts, + chapter rewards → ~113 total
function stepToLevel(step: number): number {
  // Rough approximation: first 90 levels give one point per level starting at level 2
  if (step <= 89) return step + 1;
  return 90 + (step - 89) * 2;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  /** Ordered array of node IDs — each entry = one point invested, in sequence */
  history: number[];
  characterClass: string;
  /** Called to undo all allocations after (and including) a given step index */
  onRewindTo?: (stepIndex: number) => void;
  readOnly?: boolean;
}

export default function PassiveProgressBar({
  history,
  characterClass,
  onRewindTo,
  readOnly = false,
}: Props) {
  const [collapsed, setCollapsed] = useState(false);
  const [hovered, setHovered] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const nodeMap = buildNodeMap(characterClass);

  // Auto-scroll to end when new steps added
  useEffect(() => {
    if (!collapsed && scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth;
    }
  }, [history.length, collapsed]);

  if (history.length === 0 && readOnly) return null;

  return (
    <div className="rounded border border-forge-border bg-forge-surface overflow-hidden min-w-0">
      {/* Header */}
      <button
        className="flex w-full items-center justify-between px-3 py-1.5 bg-forge-surface2 hover:bg-forge-surface transition-colors"
        onClick={() => setCollapsed(c => !c)}
      >
        <div className="flex items-center gap-2">
          <span className="font-display text-xs font-semibold text-forge-amber uppercase tracking-widest">
            Leveling Path
          </span>
          {history.length > 0 && (
            <span className="font-mono text-[10px] text-forge-dim">
              {history.length} step{history.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {history.length > 0 && (
            <span className="font-mono text-[10px] text-forge-dim/60">
              ~Lvl {stepToLevel(history.length)} to finish
            </span>
          )}
          <span className="text-forge-dim text-xs">{collapsed ? "▸" : "▾"}</span>
        </div>
      </button>

      {!collapsed && (
        <div className="p-2">
          {history.length === 0 ? (
            <p className="py-3 text-center font-mono text-[10px] text-forge-dim/50">
              Start allocating passives — each step will appear here in order.
            </p>
          ) : (
            <>
              {/* Scrollable step list */}
              <div
                ref={scrollRef}
                className="flex gap-1.5 overflow-x-auto pb-1 scroll-smooth min-w-0"
                style={{ scrollbarWidth: "thin" }}
              >
                {history.map((nodeId, i) => {
                  const node = nodeMap.get(nodeId);
                  const type = node?.type ?? "core";
                  const colorCls = TYPE_COLOR[type] ?? TYPE_COLOR.core;
                  const dotCls = TYPE_DOT[type] ?? TYPE_DOT.core;
                  const label = node?.name ?? `Node ${nodeId}`;
                  const short = label.length > 14 ? label.slice(0, 13) + "…" : label;
                  const isHov = hovered === i;

                  return (
                    <div
                      key={i}
                      className="relative shrink-0"
                      onMouseEnter={() => setHovered(i)}
                      onMouseLeave={() => setHovered(null)}
                    >
                      {/* Step chip */}
                      <div
                        className={clsx(
                          "flex items-center gap-1 rounded border px-2 py-0.5 cursor-default transition-opacity",
                          colorCls,
                          !readOnly && onRewindTo && "cursor-pointer hover:opacity-100",
                          i === history.length - 1 && "ring-1 ring-forge-amber/40"
                        )}
                        onClick={() => {
                          if (!readOnly && onRewindTo) onRewindTo(i);
                        }}
                      >
                        <span className="font-mono text-[9px] text-forge-dim/60 shrink-0">
                          {i + 1}
                        </span>
                        <span className={clsx("inline-block h-1.5 w-1.5 rounded-full shrink-0", dotCls)} />
                        <span className="font-mono text-[10px] whitespace-nowrap">
                          {short}
                        </span>
                        {/* Level badge every 10 steps */}
                        {(i + 1) % 10 === 0 && (
                          <span className="ml-0.5 font-mono text-[8px] text-forge-dim/50">
                            ~{stepToLevel(i + 1)}
                          </span>
                        )}
                      </div>

                      {/* Connector line (not after last) */}
                      {i < history.length - 1 && (
                        <div className="absolute top-1/2 -right-1 h-px w-1 bg-forge-border/60 -translate-y-px" />
                      )}

                      {/* Tooltip */}
                      {isHov && (
                        <div className="pointer-events-none absolute bottom-full left-0 mb-1.5 z-30 min-w-[160px] rounded border border-forge-border bg-forge-bg/95 px-2.5 py-2 shadow-xl">
                          <div className="font-display text-xs font-bold text-forge-amber">
                            {label}
                          </div>
                          <div className="mt-0.5 font-mono text-[10px] text-forge-dim uppercase tracking-widest">
                            Step {i + 1} · ~Lvl {stepToLevel(i + 1)}
                          </div>
                          <div className="mt-0.5 font-mono text-[10px] text-forge-dim capitalize">
                            {type.replace("-", " ")}
                          </div>
                          {node?.description && (
                            <div className="mt-1 font-body text-[10px] text-forge-muted leading-snug max-w-[200px]">
                              {node.description}
                            </div>
                          )}
                          {!readOnly && onRewindTo && (
                            <div className="mt-1.5 font-mono text-[9px] text-forge-dim/50">
                              Click to rewind to this step
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Level ruler */}
              <div className="mt-1.5 flex items-center gap-1 overflow-hidden">
                <div className="relative h-1 flex-1 rounded bg-forge-border/30">
                  <div
                    className="h-full rounded bg-gradient-to-r from-forge-amber/60 to-forge-amber/20 transition-all duration-300"
                    style={{ width: `${Math.min(100, (history.length / 113) * 100)}%` }}
                  />
                  {/* Milestone markers at 25/50/75% */}
                  {[28, 56, 85].map(pt => (
                    <div
                      key={pt}
                      className="absolute top-0 h-full w-px bg-forge-dim/30"
                      style={{ left: `${(pt / 113) * 100}%` }}
                    />
                  ))}
                </div>
                <span className="shrink-0 font-mono text-[9px] text-forge-dim/50">
                  {history.length}/113 pts
                </span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
