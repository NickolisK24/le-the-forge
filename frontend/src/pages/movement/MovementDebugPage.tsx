/**
 * L21 — Movement Debug Dashboard
 *
 * Visual inspection page for movement simulation events. Lets users configure
 * a small movement scenario, run it, and explore the results via:
 *   - MovementCanvas: live entity positions
 *   - PathViewer: A* generated path
 *   - DistanceTimeline: distance history chart
 *   - Event log table
 */

import { useState, useCallback, useRef } from "react";
import MovementCanvas, { EntityPosition, MovementTrace } from "@/components/movement/MovementCanvas";
import PathViewer, { Waypoint } from "@/components/movement/PathViewer";
import DistanceTimeline, { DistanceSample } from "@/components/movement/DistanceTimeline";

// ---------------------------------------------------------------------------
// Types mirroring backend payload
// ---------------------------------------------------------------------------

interface SimConfig {
  numEnemies: number;
  duration: number;
  tickSize: number;
  enemySpeed: number;
  behaviorType: "aggressive" | "defensive" | "orbiting" | "random";
  kiteMinRange: number;
  kiteMaxRange: number;
  kiteSpeed: number;
}

interface KiteEntry {
  time: number;
  action: string;
  closest: number;
}

interface FinalState {
  entity_id: string;
  position: [number, number];
  behavior_type: string;
  distance_moved: number;
  is_moving: boolean;
}

interface LogEntry {
  event_type: string;
  time: number;
  payload: Record<string, unknown>;
}

interface SimResult {
  final_states: FinalState[];
  kite_results: KiteEntry[];
  metrics_summary: Record<string, unknown>;
  log_entries: LogEntry[];
  ticks_executed: number;
}

// ---------------------------------------------------------------------------
// Mock simulation (runs entirely client-side for demo)
// In production this would POST to /api/movement/simulate
// ---------------------------------------------------------------------------

function runMockSimulation(cfg: SimConfig): SimResult {
  const states: FinalState[] = [];
  const kite_results: KiteEntry[] = [];
  const log_entries: LogEntry[] = [];

  let playerX = 0;
  let playerY = 0;
  const enemies = Array.from({ length: cfg.numEnemies }, (_, i) => ({
    id: `enemy_${i}`,
    x: (i + 1) * 8 + 5,
    y: (i % 3) * 4,
    dist_moved: 0,
  }));

  const dt = cfg.tickSize;
  const n_ticks = Math.ceil(cfg.duration / dt);

  for (let t = 0; t < n_ticks; t++) {
    const now = (t + 1) * dt;

    // Move enemies toward player (aggressive)
    for (const e of enemies) {
      const dx = playerX - e.x;
      const dy = playerY - e.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > 1.0) {
        const step = Math.min(cfg.enemySpeed * dt, dist);
        e.x += (dx / dist) * step;
        e.y += (dy / dist) * step;
        e.dist_moved += step;
      }
    }

    // Kite: find closest enemy and react
    let closestDist = Infinity;
    let closestX = 0, closestY = 0;
    for (const e of enemies) {
      const d = Math.sqrt((playerX - e.x) ** 2 + (playerY - e.y) ** 2);
      if (d < closestDist) { closestDist = d; closestX = e.x; closestY = e.y; }
    }

    let action = "hold";
    if (closestDist < cfg.kiteMinRange) {
      const awayX = playerX - closestX;
      const awayY = playerY - closestY;
      const mag = Math.sqrt(awayX ** 2 + awayY ** 2) || 1;
      playerX += (awayX / mag) * cfg.kiteSpeed * dt;
      playerY += (awayY / mag) * cfg.kiteSpeed * dt;
      action = "retreat";
      if (t % 5 === 0) {
        log_entries.push({ event_type: "kite", time: now, payload: { closest_enemy_dist: closestDist } });
      }
    } else if (closestDist > cfg.kiteMaxRange) {
      action = "advance";
    }

    kite_results.push({ time: parseFloat(now.toFixed(3)), action, closest: parseFloat(closestDist.toFixed(3)) });
  }

  for (const e of enemies) {
    states.push({
      entity_id: e.id,
      position: [parseFloat(e.x.toFixed(3)), parseFloat(e.y.toFixed(3))],
      behavior_type: cfg.behaviorType,
      distance_moved: parseFloat(e.dist_moved.toFixed(3)),
      is_moving: true,
    });
  }

  const kite_count = kite_results.filter((k) => k.action === "retreat").length;
  return {
    final_states: states,
    kite_results,
    log_entries,
    metrics_summary: {
      total_distance_all: states.reduce((s, st) => s + st.distance_moved, 0).toFixed(2),
      kite_events: kite_count,
      total_repositions: 0,
    },
    ticks_executed: Math.ceil(cfg.duration / cfg.tickSize),
  };
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

const DEFAULT_CONFIG: SimConfig = {
  numEnemies: 4,
  duration: 5.0,
  tickSize: 0.1,
  enemySpeed: 4.0,
  behaviorType: "aggressive",
  kiteMinRange: 5.0,
  kiteMaxRange: 15.0,
  kiteSpeed: 6.0,
};

export default function MovementDebugPage() {
  const [config, setConfig] = useState<SimConfig>(DEFAULT_CONFIG);
  const [result, setResult]  = useState<SimResult | null>(null);
  const [running, setRunning] = useState(false);

  const handleRun = useCallback(() => {
    setRunning(true);
    // Defer to avoid blocking UI
    setTimeout(() => {
      try {
        const r = runMockSimulation(config);
        setResult(r);
      } finally {
        setRunning(false);
      }
    }, 50);
  }, [config]);

  // Build entities for canvas
  const entities: EntityPosition[] = result?.final_states.map((s) => ({
    id: s.entity_id,
    x: s.position[0],
    y: s.position[1],
    behaviorType: s.behavior_type,
    isAlive: true,
  })) ?? [];

  // Build traces from kite log (player movement)
  const playerTrace: MovementTrace = {
    entityId: "player",
    points: result?.kite_results
      ? (() => {
          let px = 0, py = 0;
          const pts: [number, number][] = [[0, 0]];
          for (const k of result.kite_results) {
            if (k.action === "retreat") {
              // Simple approximation for trace
              pts.push([px - 0.3, py]);
              px -= 0.3;
            }
          }
          return pts;
        })()
      : [],
    color: "#f0a020",
  };

  // Player final position (approx from kite trace)
  const playerPos = (() => {
    if (!result) return null;
    const retreats = result.kite_results.filter((k) => k.action === "retreat").length;
    return { x: -retreats * 0.3, y: 0 };
  })();

  // Distance samples for chart
  const distanceSamples: DistanceSample[] = result?.kite_results
    .filter((_, i) => i % 5 === 0)
    .map((k) => ({ time: k.time, "player:enemy_0": k.closest })) ?? [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-display text-2xl text-forge-amber tracking-wide">Movement Debug</h1>
        <p className="text-forge-muted text-sm mt-1">
          Phase L — Inspect movement behaviors, pathfinding, and kiting dynamics
        </p>
      </div>

      {/* Config panel */}
      <div className="rounded-xl border border-forge-border bg-forge-surface p-5 grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Enemies", key: "numEnemies", type: "number", min: 1, max: 20, step: 1 },
          { label: "Duration (s)", key: "duration", type: "number", min: 1, max: 30, step: 0.5 },
          { label: "Tick Size", key: "tickSize", type: "number", min: 0.01, max: 0.5, step: 0.01 },
          { label: "Enemy Speed", key: "enemySpeed", type: "number", min: 0.5, max: 20, step: 0.5 },
          { label: "Min Kite Range", key: "kiteMinRange", type: "number", min: 1, max: 20, step: 0.5 },
          { label: "Max Kite Range", key: "kiteMaxRange", type: "number", min: 2, max: 50, step: 0.5 },
          { label: "Kite Speed", key: "kiteSpeed", type: "number", min: 1, max: 20, step: 0.5 },
        ].map(({ label, key, ...rest }) => (
          <label key={key} className="flex flex-col gap-1">
            <span className="text-xs text-forge-muted font-mono">{label}</span>
            <input
              type="number"
              value={config[key as keyof SimConfig] as number}
              onChange={(e) =>
                setConfig((c) => ({ ...c, [key]: parseFloat(e.target.value) || 0 }))
              }
              className="w-full bg-forge-surface2 border border-forge-border rounded px-2 py-1 text-forge-text text-sm font-mono focus:outline-none focus:border-forge-amber/60"
              {...rest}
            />
          </label>
        ))}

        <label className="flex flex-col gap-1">
          <span className="text-xs text-forge-muted font-mono">Behavior</span>
          <select
            value={config.behaviorType}
            onChange={(e) => setConfig((c) => ({ ...c, behaviorType: e.target.value as SimConfig["behaviorType"] }))}
            className="bg-forge-surface2 border border-forge-border rounded px-2 py-1 text-forge-text text-sm font-mono focus:outline-none focus:border-forge-amber/60"
          >
            <option value="aggressive">aggressive</option>
            <option value="defensive">defensive</option>
            <option value="orbiting">orbiting</option>
            <option value="random">random</option>
          </select>
        </label>
      </div>

      {/* Run button */}
      <div className="flex gap-3 items-center">
        <button
          onClick={handleRun}
          disabled={running}
          className="px-6 py-2 rounded-lg bg-forge-amber text-forge-bg font-display font-semibold text-sm tracking-wide hover:bg-forge-amber-hot transition-colors disabled:opacity-50"
        >
          {running ? "Running…" : "Run Simulation"}
        </button>
        {result && (
          <span className="text-xs font-mono text-forge-muted">
            {result.ticks_executed} ticks · {result.final_states.length} entities
          </span>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Canvas */}
          <div className="flex flex-col gap-2">
            <h2 className="text-sm font-display text-forge-amber/80">Entity Positions</h2>
            <MovementCanvas
              width={550}
              height={420}
              worldBounds={[-10, -5, 60, 35]}
              entities={entities}
              playerPosition={playerPos}
              traces={[playerTrace]}
              showArrows={false}
            />
          </div>

          {/* Path viewer (static demo — shows a simple path) */}
          <div className="flex flex-col gap-2">
            <h2 className="text-sm font-display text-forge-amber/80">A* Path Preview</h2>
            <PathViewer
              width={550}
              height={420}
              gridCols={10}
              gridRows={10}
              worldBounds={[0, 0, 10, 10]}
              start={{ x: 0.5, y: 0.5 }}
              goal={{ x: 9.5, y: 9.5 }}
              waypoints={[
                { x: 0.5, y: 0.5 },
                { x: 2.5, y: 2.5 },
                { x: 5.5, y: 3.5 },
                { x: 7.5, y: 6.5 },
                { x: 9.5, y: 9.5 },
              ]}
              pathFound
              meta={{ nodesExplored: 47, pathLength: 12.73 }}
            />
          </div>

          {/* Distance timeline */}
          <div className="xl:col-span-2">
            <DistanceTimeline
              data={distanceSamples}
              pairs={["player:enemy_0"]}
              dangerThreshold={config.kiteMinRange}
              safeThreshold={config.kiteMaxRange}
              title="Player–Enemy Distance Over Time"
              height={240}
            />
          </div>

          {/* Metrics */}
          <div className="rounded-xl border border-forge-border bg-forge-surface p-4">
            <h2 className="text-sm font-display text-forge-amber/80 mb-3">Metrics</h2>
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              {Object.entries(result.metrics_summary).map(([k, v]) => (
                <div key={k} className="flex justify-between border-b border-forge-border/30 pb-1">
                  <span className="text-forge-muted">{k.replace(/_/g, " ")}</span>
                  <span className="text-forge-amber">{String(v)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Event log */}
          <div className="rounded-xl border border-forge-border bg-forge-surface p-4">
            <h2 className="text-sm font-display text-forge-amber/80 mb-3">
              Event Log <span className="text-forge-muted">({result.log_entries.length})</span>
            </h2>
            <div className="overflow-y-auto max-h-52 space-y-1">
              {result.log_entries.slice(0, 50).map((entry, i) => (
                <div
                  key={i}
                  className="flex gap-3 text-xs font-mono border-b border-forge-border/20 pb-0.5"
                >
                  <span className="text-forge-dim w-14 shrink-0">
                    {entry.time.toFixed(2)}s
                  </span>
                  <span className="text-forge-cyan shrink-0">{entry.event_type}</span>
                  <span className="text-forge-muted truncate">
                    {JSON.stringify(entry.payload)}
                  </span>
                </div>
              ))}
              {result.log_entries.length === 0 && (
                <p className="text-forge-dim text-xs">No events recorded</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
