/**
 * L19 — Movement Visualization Canvas
 *
 * SVG canvas that renders moving targets, the player, path traces, and
 * per-entity movement arrows. Designed to match The Forge's dark amber/cyan
 * color scheme.
 */

import { useMemo } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface EntityPosition {
  id: string;
  x: number;
  y: number;
  behaviorType?: string;
  isAlive?: boolean;
}

export interface MovementTrace {
  entityId: string;
  points: [number, number][];
  color?: string;
}

export interface MovementCanvasProps {
  /** Width of the SVG viewport in pixels */
  width?: number;
  /** Height of the SVG viewport in pixels */
  height?: number;
  /** World-space bounds displayed — [minX, minY, maxX, maxY] */
  worldBounds?: [number, number, number, number];
  /** Current positions of all entities */
  entities?: EntityPosition[];
  /** Player position */
  playerPosition?: { x: number; y: number } | null;
  /** Historical movement traces */
  traces?: MovementTrace[];
  /** Show velocity arrows */
  showArrows?: boolean;
  /** Velocity vectors per entity {entityId: [vx, vy]} */
  velocities?: Record<string, [number, number]>;
}

// Behavior color mapping
const BEHAVIOR_COLORS: Record<string, string> = {
  aggressive: "#ff5050",
  defensive:  "#3dca74",
  orbiting:   "#00d4f5",
  random:     "#b87fff",
  linear:     "#f0a020",
  idle:       "#4a5480",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function MovementCanvas({
  width = 600,
  height = 500,
  worldBounds = [-5, -5, 55, 45],
  entities = [],
  playerPosition = null,
  traces = [],
  showArrows = true,
  velocities = {},
}: MovementCanvasProps) {
  const [wMinX, wMinY, wMaxX, wMaxY] = worldBounds;
  const wWidth  = wMaxX - wMinX || 1;
  const wHeight = wMaxY - wMinY || 1;

  // Project world coords → SVG coords
  const project = (wx: number, wy: number): [number, number] => [
    ((wx - wMinX) / wWidth) * width,
    height - ((wy - wMinY) / wHeight) * height,
  ];

  // Build path strings for traces
  const tracePaths = useMemo(() => {
    return traces.map((trace) => {
      if (trace.points.length < 2) return null;
      const d = trace.points
        .map(([x, y], i) => {
          const [sx, sy] = project(x, y);
          return `${i === 0 ? "M" : "L"} ${sx.toFixed(1)} ${sy.toFixed(1)}`;
        })
        .join(" ");
      return { id: trace.entityId, d, color: trace.color ?? "#4a5480" };
    });
  }, [traces, worldBounds, width, height]);

  const gridLines = useMemo(() => {
    const lines: JSX.Element[] = [];
    const step = 10;
    for (let wx = Math.ceil(wMinX / step) * step; wx <= wMaxX; wx += step) {
      const [sx] = project(wx, 0);
      lines.push(
        <line
          key={`v${wx}`}
          x1={sx} y1={0} x2={sx} y2={height}
          stroke="rgba(80,100,210,0.12)" strokeWidth="1"
        />
      );
    }
    for (let wy = Math.ceil(wMinY / step) * step; wy <= wMaxY; wy += step) {
      const [, sy] = project(0, wy);
      lines.push(
        <line
          key={`h${wy}`}
          x1={0} y1={sy} x2={width} y2={sy}
          stroke="rgba(80,100,210,0.12)" strokeWidth="1"
        />
      );
    }
    return lines;
  }, [worldBounds, width, height]);

  return (
    <div className="relative rounded-lg overflow-hidden border border-forge-border bg-forge-surface">
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        style={{ display: "block" }}
      >
        {/* Background */}
        <rect width={width} height={height} fill="#06080f" />

        {/* Grid */}
        {gridLines}

        {/* Movement traces */}
        {tracePaths.map(
          (tp) =>
            tp && (
              <path
                key={`trace-${tp.id}`}
                d={tp.d}
                fill="none"
                stroke={tp.color}
                strokeWidth="1.5"
                strokeOpacity="0.35"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )
        )}

        {/* Entity dots */}
        {entities.map((e) => {
          const [sx, sy] = project(e.x, e.y);
          const color = BEHAVIOR_COLORS[e.behaviorType ?? "idle"] ?? "#4a5480";
          const alive = e.isAlive !== false;
          const vel = velocities[e.id];

          return (
            <g key={e.id}>
              {/* Velocity arrow */}
              {showArrows && vel && vel[0] !== 0 || (vel && vel[1] !== 0) ? (
                <line
                  x1={sx}
                  y1={sy}
                  x2={sx + vel![0] * 4}
                  y2={sy - vel![1] * 4}
                  stroke={color}
                  strokeWidth="1.5"
                  strokeOpacity="0.7"
                  markerEnd="url(#arrowhead)"
                />
              ) : null}

              {/* Entity circle */}
              <circle
                cx={sx}
                cy={sy}
                r={alive ? 5 : 3}
                fill={alive ? color : "#2a2f4a"}
                stroke={alive ? color : "#4a5480"}
                strokeWidth="1.5"
                strokeOpacity={alive ? 0.9 : 0.4}
                fillOpacity={alive ? 0.8 : 0.3}
              />

              {/* ID label */}
              <text
                x={sx + 7}
                y={sy + 4}
                fontSize="9"
                fill="#8890b8"
                fontFamily="JetBrains Mono, monospace"
              >
                {e.id}
              </text>
            </g>
          );
        })}

        {/* Player */}
        {playerPosition && (() => {
          const [sx, sy] = project(playerPosition.x, playerPosition.y);
          return (
            <g>
              {/* Glow ring */}
              <circle cx={sx} cy={sy} r={10} fill="none" stroke="#f0a020" strokeWidth="1.5" strokeOpacity="0.3" />
              {/* Player diamond */}
              <polygon
                points={`${sx},${sy - 8} ${sx + 7},${sy} ${sx},${sy + 8} ${sx - 7},${sy}`}
                fill="#f0a020"
                stroke="#ffb83f"
                strokeWidth="1.5"
                fillOpacity="0.9"
              />
              <text x={sx + 10} y={sy + 4} fontSize="9" fill="#f0a020" fontFamily="JetBrains Mono, monospace">
                player
              </text>
            </g>
          );
        })()}

        {/* Arrow marker definition */}
        <defs>
          <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0,0 L0,6 L6,3 z" fill="#8890b8" />
          </marker>
        </defs>
      </svg>

      {/* Legend */}
      <div className="absolute bottom-2 right-2 flex flex-col gap-1 text-[10px] font-mono text-forge-muted">
        {Object.entries(BEHAVIOR_COLORS).map(([name, color]) => (
          <div key={name} className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
            <span>{name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
