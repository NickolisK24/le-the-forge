/**
 * N16 — Visualization Debug Page
 *
 * Route: /viz-debug
 *
 * Renders TimelinePanel, HeatmapViewer, and ReplayViewer with mock data.
 * Config panel lets you tweak duration, entity count, and tick size.
 */

import { useState, useMemo } from "react";

import TimelinePanel, { type TimelineEvent } from "@/components/visualization/TimelinePanel";
import HeatmapViewer, { type HeatmapCell } from "@/components/visualization/HeatmapViewer";
import ReplayViewer, { type ReplayFrame } from "@/components/visualization/ReplayViewer";

// ---------------------------------------------------------------------------
// Mock data generators
// ---------------------------------------------------------------------------

const EVENT_TYPES = ["damage", "buff", "movement"] as const;

function generateEvents(duration: number, count: number): TimelineEvent[] {
  return Array.from({ length: count }, (_, i) => ({
    time: Math.random() * duration,
    event_type: EVENT_TYPES[Math.floor(Math.random() * EVENT_TYPES.length)],
    source: `source_${(i % 5) + 1}`,
    value: Math.random() * 1000,
  }));
}

function generateHeatmapCells(rows: number, cols: number): HeatmapCell[] {
  const cells: HeatmapCell[] = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const value = Math.random() * 100;
      cells.push({ row: r, col: c, value, normalized: value / 100 });
    }
  }
  return cells;
}

function generateReplayFrames(
  frameCount: number,
  entityCount: number,
  tickSize: number
): ReplayFrame[] {
  // Initialise entity positions
  const positions = Array.from({ length: entityCount }, () => [
    Math.random() * 460 + 20,
    Math.random() * 460 + 20,
  ] as [number, number]);

  return Array.from({ length: frameCount }, (_, fi) => {
    // Drift positions slightly each frame
    const entities = positions.map((pos, ei) => {
      pos[0] = Math.max(10, Math.min(490, pos[0] + (Math.random() - 0.5) * 10));
      pos[1] = Math.max(10, Math.min(490, pos[1] + (Math.random() - 0.5) * 10));
      return {
        entity_id: `entity_${ei + 1}`,
        position: [pos[0], pos[1]] as [number, number],
        health: Math.max(0, 100 - fi * (100 / frameCount) * Math.random()),
        is_alive: fi < frameCount * 0.8 || Math.random() > 0.3,
      };
    });

    return {
      frame_index: fi,
      time: parseFloat((fi * tickSize).toFixed(3)),
      entities,
      projectiles:
        Math.random() > 0.6
          ? [
              {
                projectile_id: `proj_${fi}`,
                position: [Math.random() * 490, Math.random() * 490] as [number, number],
                direction: [Math.random() - 0.5, Math.random() - 0.5] as [number, number],
              },
            ]
          : [],
      events: [],
    };
  });
}

// ---------------------------------------------------------------------------
// Config types
// ---------------------------------------------------------------------------

interface Config {
  duration: number;
  entityCount: number;
  tickSize: number;
}

const DEFAULT_CONFIG: Config = {
  duration: 20,
  entityCount: 3,
  tickSize: 0.5,
};

const inputCls =
  "w-full rounded border border-[#2a3050] bg-[#0d1124] px-2 py-1 font-mono text-xs text-[#c8d0e0] " +
  "outline-none focus:border-[#f5a623]/60 accent-amber-400";

const labelCls = "block font-mono text-[10px] uppercase tracking-widest text-[#6b7280] mb-1";

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function VisualizationDebugPage() {
  const [config, setConfig] = useState<Config>(DEFAULT_CONFIG);

  function set<K extends keyof Config>(key: K, value: Config[K]) {
    setConfig((prev) => ({ ...prev, [key]: value }));
  }

  // Generate all mock data when config changes
  const { events, heatmapCells, replayFrames } = useMemo(() => {
    return {
      events:       generateEvents(config.duration, 200),
      heatmapCells: generateHeatmapCells(10, 10),
      replayFrames: generateReplayFrames(30, config.entityCount, config.tickSize),
    };
  }, [config.duration, config.entityCount, config.tickSize]);

  return (
    <div className="min-h-screen bg-[#0d1124] p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-display text-2xl text-[#c8d0e0]">Visualization Debug</h1>
        <p className="font-mono text-sm text-[#6b7280] mt-1">
          Interactive test bed for Phase N visualization components.
        </p>
      </div>

      {/* Config panel */}
      <div className="rounded border border-[#2a3050] bg-[#10152a] p-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className={labelCls}>
            Duration: <span className="text-[#f5a623]">{config.duration}s</span>
          </label>
          <input
            type="range"
            min={5}
            max={60}
            step={1}
            value={config.duration}
            onChange={(e) => set("duration", Number(e.target.value))}
            className={inputCls}
          />
          <div className="flex justify-between font-mono text-[10px] text-[#6b7280] mt-0.5">
            <span>5s</span><span>60s</span>
          </div>
        </div>

        <div>
          <label className={labelCls}>
            Entities: <span className="text-[#f5a623]">{config.entityCount}</span>
          </label>
          <input
            type="range"
            min={1}
            max={5}
            step={1}
            value={config.entityCount}
            onChange={(e) => set("entityCount", Number(e.target.value))}
            className={inputCls}
          />
          <div className="flex justify-between font-mono text-[10px] text-[#6b7280] mt-0.5">
            <span>1</span><span>5</span>
          </div>
        </div>

        <div>
          <label className={labelCls}>
            Tick Size: <span className="text-[#f5a623]">{config.tickSize}s</span>
          </label>
          <input
            type="range"
            min={0.1}
            max={1.0}
            step={0.1}
            value={config.tickSize}
            onChange={(e) => set("tickSize", Number(e.target.value))}
            className={inputCls}
          />
          <div className="flex justify-between font-mono text-[10px] text-[#6b7280] mt-0.5">
            <span>0.1</span><span>1.0</span>
          </div>
        </div>
      </div>

      {/* Timeline — full width */}
      <TimelinePanel
        events={events}
        duration={config.duration}
        tickSize={config.tickSize}
      />

      {/* Heatmap + Replay — side by side */}
      <div className="flex flex-wrap gap-6">
        <HeatmapViewer
          cells={heatmapCells}
          rows={10}
          cols={10}
          title="Position Heatmap (10×10)"
          width={400}
          height={400}
        />
        <ReplayViewer frames={replayFrames} tickSize={config.tickSize} />
      </div>
    </div>
  );
}
