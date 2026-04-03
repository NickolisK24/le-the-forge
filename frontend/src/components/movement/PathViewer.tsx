/**
 * L20 — Path Visualization Tool
 *
 * Renders an A* generated path as an SVG overlay with waypoints, the start
 * and goal markers, and optional grid-cell shading. Matches The Forge's
 * dark amber theme.
 */

import { useMemo } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Waypoint {
  x: number;
  y: number;
}

export interface GridCell {
  row: number;
  col: number;
  walkable: boolean;
}

export interface PathViewerProps {
  /** Width of the SVG viewport */
  width?: number;
  /** Height of the SVG viewport */
  height?: number;
  /** Number of grid columns */
  gridCols?: number;
  /** Number of grid rows */
  gridRows?: number;
  /** World-space bounds [minX, minY, maxX, maxY] */
  worldBounds?: [number, number, number, number];
  /** A* generated waypoints (world-space) */
  waypoints?: Waypoint[];
  /** Start position */
  start?: Waypoint | null;
  /** Goal position */
  goal?: Waypoint | null;
  /** Optional grid cell data for blocked-cell overlay */
  gridCells?: GridCell[];
  /** True if A* found a valid path */
  pathFound?: boolean;
  /** Metadata to display */
  meta?: { nodesExplored?: number; pathLength?: number };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function PathViewer({
  width = 500,
  height = 500,
  gridCols = 10,
  gridRows = 10,
  worldBounds = [0, 0, 10, 10],
  waypoints = [],
  start = null,
  goal = null,
  gridCells = [],
  pathFound = true,
  meta,
}: PathViewerProps) {
  const [wMinX, wMinY, wMaxX, wMaxY] = worldBounds;
  const wWidth  = wMaxX - wMinX || 1;
  const wHeight = wMaxY - wMinY || 1;

  const cellW = width / gridCols;
  const cellH = height / gridRows;

  const project = (wx: number, wy: number): [number, number] => [
    ((wx - wMinX) / wWidth) * width,
    height - ((wy - wMinY) / wHeight) * height,
  ];

  const pathD = useMemo(() => {
    if (waypoints.length === 0) return "";
    return waypoints
      .map(({ x, y }, i) => {
        const [sx, sy] = project(x, y);
        return `${i === 0 ? "M" : "L"} ${sx.toFixed(1)} ${sy.toFixed(1)}`;
      })
      .join(" ");
  }, [waypoints, worldBounds, width, height]);

  return (
    <div className="flex flex-col gap-3">
      <div className="relative rounded-lg overflow-hidden border border-forge-border bg-forge-surface">
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ display: "block" }}>
          {/* Background */}
          <rect width={width} height={height} fill="#06080f" />

          {/* Grid cells */}
          {Array.from({ length: gridRows }, (_, r) =>
            Array.from({ length: gridCols }, (_, c) => {
              const cell = gridCells.find((gc) => gc.row === r && gc.col === c);
              const blocked = cell ? !cell.walkable : false;
              const x = c * cellW;
              const y = r * cellH;
              return (
                <rect
                  key={`${r}-${c}`}
                  x={x} y={y}
                  width={cellW} height={cellH}
                  fill={blocked ? "rgba(255,80,80,0.18)" : "transparent"}
                  stroke="rgba(80,100,210,0.1)"
                  strokeWidth="0.5"
                />
              );
            })
          )}

          {/* Path */}
          {pathD && (
            <path
              d={pathD}
              fill="none"
              stroke={pathFound ? "#f0a020" : "#ff5050"}
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={pathFound ? "none" : "6,4"}
            />
          )}

          {/* Waypoint dots */}
          {waypoints.map(({ x, y }, i) => {
            const [sx, sy] = project(x, y);
            const isFirst = i === 0;
            const isLast  = i === waypoints.length - 1;
            return (
              <circle
                key={i}
                cx={sx} cy={sy} r={isFirst || isLast ? 0 : 3}
                fill="#f0a020"
                fillOpacity="0.6"
              />
            );
          })}

          {/* Start */}
          {start && (() => {
            const [sx, sy] = project(start.x, start.y);
            return (
              <g>
                <circle cx={sx} cy={sy} r={7} fill="#3dca74" fillOpacity="0.25" stroke="#3dca74" strokeWidth="2" />
                <text x={sx} y={sy + 4} textAnchor="middle" fontSize="9" fill="#3dca74" fontFamily="JetBrains Mono, monospace">S</text>
              </g>
            );
          })()}

          {/* Goal */}
          {goal && (() => {
            const [gx, gy] = project(goal.x, goal.y);
            return (
              <g>
                <circle cx={gx} cy={gy} r={7} fill="#f0a020" fillOpacity="0.25" stroke="#f0a020" strokeWidth="2" />
                <text x={gx} y={gy + 4} textAnchor="middle" fontSize="9" fill="#f0a020" fontFamily="JetBrains Mono, monospace">G</text>
              </g>
            );
          })()}
        </svg>
      </div>

      {/* Metadata bar */}
      {meta && (
        <div className="flex gap-4 text-xs font-mono text-forge-muted px-1">
          {meta.nodesExplored !== undefined && (
            <span>
              Nodes explored: <span className="text-forge-amber">{meta.nodesExplored}</span>
            </span>
          )}
          {meta.pathLength !== undefined && (
            <span>
              Path length: <span className="text-forge-amber">{meta.pathLength.toFixed(2)} u</span>
            </span>
          )}
          <span>
            Status:{" "}
            <span className={pathFound ? "text-forge-green" : "text-forge-red"}>
              {pathFound ? "Path found" : "No path"}
            </span>
          </span>
        </div>
      )}
    </div>
  );
}
