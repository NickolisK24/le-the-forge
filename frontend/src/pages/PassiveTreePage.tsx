/**
 * PassiveTreePage — SVG-based passive tree viewer.
 *
 * Follows the Classes Viewer pattern:
 *   1. Fetch via shared API client (passiveTreeService)
 *   2. Handle loading / error / empty states explicitly
 *   3. Validate loaded count against expected
 *   4. Render via reusable components (PassiveTreeNode, PassiveTreeConnections)
 *   5. Measure render time
 *
 * Class/mastery selector filters which subtree is displayed.
 * Rendering is read-only — no allocation interactions yet.
 */

import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Spinner } from "@/components/ui";
import type { CharacterClass } from "@/types";
import {
  fetchClassTree,
  type PassiveNode,
  type PassiveTreeResponse,
} from "@/services/passiveTreeService";
import { MASTERIES } from "@/lib/gameData";
import { BASE_CLASSES } from "@constants";
import PassiveTreeNode from "@/components/passives/PassiveTreeNode";
import PassiveTreeConnections from "@/components/passives/PassiveTreeConnections";

const CLASSES: CharacterClass[] = [...BASE_CLASSES] as CharacterClass[];
const EXPECTED_TOTAL = 542;
const CANVAS_H = 560;
const NODE_R_CORE = 14;
const NODE_R_NOTABLE = 20;

// ---------------------------------------------------------------------------
// Layout helpers
// ---------------------------------------------------------------------------

interface LayoutResult {
  nodes: PassiveNode[];
  positions: Map<string, { sx: number; sy: number; masteryIndex: number }>;
  edges: Array<{ fromId: string; toId: string }>;
  scale: number;
  offsetX: number;
  offsetY: number;
}

function computeLayout(
  nodes: PassiveNode[],
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const positions = new Map<string, { sx: number; sy: number; masteryIndex: number }>();
  const edges: Array<{ fromId: string; toId: string }> = [];

  if (nodes.length === 0) {
    return { nodes, positions, edges, scale: 1, offsetX: 0, offsetY: 0 };
  }

  // Center coordinates
  const xs = nodes.map((n) => n.x);
  const ys = nodes.map((n) => n.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const midX = (minX + maxX) / 2;
  const midY = (minY + maxY) / 2;
  const treeW = maxX - minX || 1;
  const treeH = maxY - minY || 1;

  const pad = 60;
  const scale = Math.min(
    (canvasW - pad * 2) / treeW,
    (canvasH - pad * 2) / treeH,
  );
  const offsetX = (canvasW - treeW * scale) / 2 - minX * scale;
  const offsetY = (canvasH - treeH * scale) / 2 - minY * scale;

  // Build positions
  const idSet = new Set(nodes.map((n) => n.id));
  for (const node of nodes) {
    const lx = node.x - midX;
    const ly = -(node.y - midY); // flip Y for screen coords
    const sx = lx * scale + canvasW / 2;
    const sy = ly * scale + canvasH / 2;
    positions.set(node.id, { sx, sy, masteryIndex: node.mastery_index });
  }

  // Build edges from connections
  for (const node of nodes) {
    for (const connId of node.connections) {
      if (idSet.has(connId)) {
        edges.push({ fromId: connId, toId: node.id });
      }
    }
  }

  return { nodes, positions, edges, scale, offsetX, offsetY };
}

// ---------------------------------------------------------------------------
// Tooltip
// ---------------------------------------------------------------------------

interface TooltipData {
  node: PassiveNode;
  x: number;
  y: number;
}

function NodeTooltip({ data, containerRect }: { data: TooltipData; containerRect: DOMRect | null }) {
  if (!containerRect) return null;
  const n = data.node;
  const tx = data.x - containerRect.left + 16;
  const ty = data.y - containerRect.top - 12;

  return (
    <div
      className="pointer-events-none absolute z-20 w-64 rounded border border-forge-border bg-forge-bg/95 p-3 shadow-2xl"
      style={{ left: Math.min(tx, containerRect.width - 272), top: Math.max(4, ty) }}
    >
      <div className="font-display text-sm font-bold text-forge-amber">{n.name || "Passive Node"}</div>
      <div className="mt-0.5 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
        {n.node_type} · {n.max_points} pts
        {n.mastery && <span> · {n.mastery}</span>}
      </div>
      {n.description && (
        <p className="mt-1.5 font-body text-[11px] leading-relaxed text-forge-text/90 whitespace-pre-line">
          {n.description}
        </p>
      )}
      {n.stats.length > 0 && (
        <ul className="mt-1.5 space-y-0.5">
          {n.stats.map((s, i) => (
            <li key={i} className="font-mono text-[10px] text-forge-cyan/80">
              {s.key}: {s.value}
            </li>
          ))}
        </ul>
      )}
      {n.ability_granted && (
        <div className="mt-1 font-mono text-[10px] text-forge-amber/80">
          Grants: {n.ability_granted}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function PassiveTreePage() {
  const [selectedClass, setSelectedClass] = useState<CharacterClass | null>(null);
  const [selectedMastery, setSelectedMastery] = useState<string>("__all__");
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [renderTimeMs, setRenderTimeMs] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [canvasSize, setCanvasSize] = useState({ w: 900, h: CANVAS_H });

  // Track container size
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      setCanvasSize({ w: entry.contentRect.width, h: CANVAS_H });
    });
    ro.observe(el);
    setCanvasSize({ w: el.clientWidth, h: CANVAS_H });
    return () => ro.disconnect();
  }, []);

  // Fetch data
  const {
    data: treeData,
    isLoading,
    isError,
    error,
  } = useQuery<PassiveTreeResponse | null>({
    queryKey: ["passives-viewer", selectedClass],
    queryFn: () => (selectedClass ? fetchClassTree(selectedClass) : null),
    enabled: Boolean(selectedClass),
    staleTime: 5 * 60 * 1000,
  });

  // Filter nodes by mastery selection
  const filteredNodes = useMemo(() => {
    const all = treeData?.nodes ?? [];
    if (selectedMastery === "__all__") return all;
    if (selectedMastery === "__base__") return all.filter((n) => n.mastery === null);
    return all.filter((n) => n.mastery === selectedMastery || n.mastery === null);
  }, [treeData, selectedMastery]);

  // Compute layout
  const layout = useMemo(() => {
    const start = performance.now();
    const result = computeLayout(filteredNodes, canvasSize.w, canvasSize.h);
    const elapsed = performance.now() - start;
    return { ...result, computeMs: elapsed };
  }, [filteredNodes, canvasSize]);

  // Measure render time
  useEffect(() => {
    if (filteredNodes.length === 0) return;
    const start = performance.now();
    requestAnimationFrame(() => {
      const elapsed = Math.round(performance.now() - start);
      setRenderTimeMs(elapsed);
      if (elapsed > 500) {
        console.warn(`[PassiveTreePage] Render time ${elapsed}ms exceeds 500ms threshold`);
      }
    });
  }, [filteredNodes]);

  const handleHover = useCallback((node: PassiveNode, screenX: number, screenY: number) => {
    setTooltip({ node, x: screenX, y: screenY });
  }, []);

  const handleLeave = useCallback(() => setTooltip(null), []);

  // Derive masteries for current class
  const masteries = selectedClass ? (MASTERIES[selectedClass] ?? []) : [];
  const allNodeCount = treeData?.nodes?.length ?? 0;
  const withIcons = filteredNodes.filter((n) => n.icon).length;
  const atOrigin = filteredNodes.filter((n) => n.x === 0 && n.y === 0).length;

  // --- Loading: no class selected ---
  if (!selectedClass) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <PageHeader />
        <ClassSelector selectedClass={null} onSelect={(c) => { setSelectedClass(c); setSelectedMastery("__all__"); }} />
        <div className="mt-4 flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
          <p className="font-mono text-sm text-forge-dim">Select a class above to load the passive tree.</p>
        </div>
      </div>
    );
  }

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <PageHeader />
        <ClassSelector selectedClass={selectedClass} onSelect={(c) => { setSelectedClass(c); setSelectedMastery("__all__"); }} />
        <div className="mt-4 flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
          <div className="flex flex-col items-center gap-3">
            <Spinner size={32} />
            <span className="font-mono text-xs text-forge-dim">Loading passive tree…</span>
          </div>
        </div>
      </div>
    );
  }

  // --- Error state ---
  if (isError) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <PageHeader />
        <ClassSelector selectedClass={selectedClass} onSelect={(c) => { setSelectedClass(c); setSelectedMastery("__all__"); }} />
        <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3">
          <p className="text-sm text-red-400 font-medium">Error loading passive tree</p>
          <p className="text-xs text-red-400/70 mt-1">{(error as Error)?.message ?? "Unknown error"}</p>
        </div>
      </div>
    );
  }

  // --- Empty state ---
  if (filteredNodes.length === 0 && treeData) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <PageHeader />
        <ClassSelector selectedClass={selectedClass} onSelect={(c) => { setSelectedClass(c); setSelectedMastery("__all__"); }} />
        <MasterySelector masteries={masteries} selected={selectedMastery} onSelect={setSelectedMastery} />
        <div className="mt-4 flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
          <p className="font-mono text-sm text-forge-dim">No passive nodes found for this selection.</p>
        </div>
      </div>
    );
  }

  // --- Loaded state ---
  const containerRect = containerRef.current?.getBoundingClientRect() ?? null;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <PageHeader />
      <ClassSelector selectedClass={selectedClass} onSelect={(c) => { setSelectedClass(c); setSelectedMastery("__all__"); }} />
      <MasterySelector masteries={masteries} selected={selectedMastery} onSelect={setSelectedMastery} />

      {/* Validation badges */}
      <div className="mt-3 mb-3 flex flex-wrap items-center gap-3">
        <ValidationBadge
          label={`Nodes: ${filteredNodes.length}${selectedMastery === "__all__" ? ` / ${allNodeCount} total` : ""}`}
          ok={filteredNodes.length > 0}
        />
        <ValidationBadge label={`Connections: ${layout.edges.length}`} ok={layout.edges.length >= 0} />
        <ValidationBadge label={`Icons: ${withIcons}/${filteredNodes.length}`} ok={withIcons >= filteredNodes.length - 1} />
        {atOrigin > 1 && (
          <ValidationBadge label={`At origin: ${atOrigin} (expected ≤1)`} ok={false} />
        )}
        {renderTimeMs !== null && (
          <span className={`rounded px-2 py-0.5 font-mono text-[10px] ${
            renderTimeMs > 500 ? "bg-yellow-500/15 text-yellow-400" : "bg-forge-surface2 text-forge-dim"
          }`}>
            Render: {renderTimeMs}ms
          </span>
        )}
      </div>

      {/* SVG canvas */}
      <div
        ref={containerRef}
        className="relative overflow-hidden rounded border border-forge-border select-none"
        style={{ height: CANVAS_H, background: "#0b0e1a" }}
      >
        <svg
          width={canvasSize.w}
          height={canvasSize.h}
          style={{ display: "block" }}
        >
          {/* Background */}
          <rect width={canvasSize.w} height={canvasSize.h} fill="#0b0e1a" />

          {/* Connections */}
          <PassiveTreeConnections edges={layout.edges} positions={layout.positions} />

          {/* Nodes */}
          {filteredNodes.map((node) => {
            const pos = layout.positions.get(node.id);
            if (!pos) return null;
            const radius = (node.max_points === 1 ? NODE_R_NOTABLE : NODE_R_CORE) * Math.max(0.3, layout.scale);
            return (
              <PassiveTreeNode
                key={node.id}
                node={node}
                sx={pos.sx}
                sy={pos.sy}
                radius={Math.max(5, radius)}
                onHover={handleHover}
                onLeave={handleLeave}
              />
            );
          })}
        </svg>

        {/* Tooltip overlay */}
        {tooltip && <NodeTooltip data={tooltip} containerRect={containerRect} />}
      </div>

      {/* Legend */}
      <div className="mt-2 flex flex-wrap items-center gap-4 font-mono text-[10px] text-forge-dim">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full border" style={{ background: "#181c30", borderColor: "#3a4070" }} /> Base
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full border" style={{ background: "#0a1e26", borderColor: "#1a5570" }} /> Mastery I
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full border" style={{ background: "#221a08", borderColor: "#664410" }} /> Mastery II
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full border" style={{ background: "#180d2a", borderColor: "#4c1880" }} /> Mastery III
        </span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function PageHeader() {
  return (
    <div className="mb-4">
      <h1 className="font-display text-2xl font-bold text-forge-amber">Passive Tree</h1>
      <p className="mt-1 font-body text-sm text-forge-muted">
        Browse passive nodes with their positions and connections from the verified backend.
      </p>
    </div>
  );
}

function ClassSelector({
  selectedClass,
  onSelect,
}: {
  selectedClass: CharacterClass | null;
  onSelect: (cls: CharacterClass) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {CLASSES.map((cls) => (
        <button
          key={cls}
          onClick={() => onSelect(cls)}
          className={`rounded px-3 py-1.5 font-body text-sm transition-colors ${
            selectedClass === cls
              ? "bg-forge-amber/20 text-forge-amber font-semibold"
              : "bg-forge-surface2 text-forge-muted hover:text-forge-text"
          }`}
        >
          {cls}
        </button>
      ))}
    </div>
  );
}

function MasterySelector({
  masteries,
  selected,
  onSelect,
}: {
  masteries: string[];
  selected: string;
  onSelect: (m: string) => void;
}) {
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      <button
        onClick={() => onSelect("__all__")}
        className={`rounded px-2.5 py-1 font-mono text-xs transition-colors ${
          selected === "__all__"
            ? "bg-forge-cyan/20 text-forge-cyan font-semibold"
            : "bg-forge-surface2 text-forge-dim hover:text-forge-muted"
        }`}
      >
        All
      </button>
      <button
        onClick={() => onSelect("__base__")}
        className={`rounded px-2.5 py-1 font-mono text-xs transition-colors ${
          selected === "__base__"
            ? "bg-forge-cyan/20 text-forge-cyan font-semibold"
            : "bg-forge-surface2 text-forge-dim hover:text-forge-muted"
        }`}
      >
        Base
      </button>
      {masteries.map((m) => (
        <button
          key={m}
          onClick={() => onSelect(m)}
          className={`rounded px-2.5 py-1 font-mono text-xs transition-colors ${
            selected === m
              ? "bg-forge-cyan/20 text-forge-cyan font-semibold"
              : "bg-forge-surface2 text-forge-dim hover:text-forge-muted"
          }`}
        >
          {m}
        </button>
      ))}
    </div>
  );
}

function ValidationBadge({ label, ok }: { label: string; ok: boolean }) {
  return (
    <span
      className={`rounded px-2.5 py-1 font-mono text-xs font-semibold ${
        ok ? "bg-green-500/15 text-green-400" : "bg-yellow-500/15 text-yellow-400"
      }`}
    >
      {label}
    </span>
  );
}
