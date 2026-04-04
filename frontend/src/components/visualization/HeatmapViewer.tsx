/**
 * N12 — Heatmap Viewer
 *
 * SVG-based grid where each cell is colored on an amber scale
 * (dark → mid-amber → bright amber) by its normalized [0,1] value.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface HeatmapCell {
  row: number;
  col: number;
  value: number;
  normalized: number;
}

export interface HeatmapViewerProps {
  cells: HeatmapCell[];
  rows: number;
  cols: number;
  title?: string;
  width?: number;
  height?: number;
}

// ---------------------------------------------------------------------------
// Color interpolation
// ---------------------------------------------------------------------------

/** Linearly interpolate between two hex colors. t ∈ [0, 1]. */
function lerpHex(a: string, b: string, t: number): string {
  const parse = (hex: string) => [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];
  const [ar, ag, ab] = parse(a);
  const [br, bg, bb] = parse(b);
  const r = Math.round(ar + (br - ar) * t);
  const g = Math.round(ag + (bg - ag) * t);
  const bv = Math.round(ab + (bb - ab) * t);
  return `rgb(${r},${g},${bv})`;
}

const DARK = "#10152a";
const MID  = "#92400e";
const BRIGHT = "#f5a623";

/** Map normalized [0,1] → amber color. Two-stop gradient. */
function amberColor(n: number): string {
  const t = Math.max(0, Math.min(1, n));
  if (t <= 0.5) {
    return lerpHex(DARK, MID, t / 0.5);
  }
  return lerpHex(MID, BRIGHT, (t - 0.5) / 0.5);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const LEGEND_HEIGHT = 20;
const LEGEND_MARGIN = 8;
const TITLE_HEIGHT  = 24;

export default function HeatmapViewer({
  cells,
  rows,
  cols,
  title,
  width = 400,
  height = 400,
}: HeatmapViewerProps) {
  const cellW = width / cols;
  const cellH = height / rows;
  const totalH = (title ? TITLE_HEIGHT : 0) + height + LEGEND_MARGIN + LEGEND_HEIGHT;
  const gradId = "heatmap-amber-grad";

  // Build a lookup for quick access
  const cellMap = new Map<string, HeatmapCell>();
  for (const c of cells) {
    cellMap.set(`${c.row},${c.col}`, c);
  }

  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4 inline-block">
      <svg width={width} height={totalH} style={{ display: "block" }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%"   stopColor={DARK} />
            <stop offset="50%"  stopColor={MID} />
            <stop offset="100%" stopColor={BRIGHT} />
          </linearGradient>
        </defs>

        {/* Title */}
        {title && (
          <text
            x={width / 2}
            y={16}
            textAnchor="middle"
            fill="#c8d0e0"
            fontSize={13}
            fontFamily="monospace"
          >
            {title}
          </text>
        )}

        {/* Grid cells */}
        <g transform={`translate(0, ${title ? TITLE_HEIGHT : 0})`}>
          {Array.from({ length: rows }, (_, r) =>
            Array.from({ length: cols }, (_, c) => {
              const cell = cellMap.get(`${r},${c}`);
              const n = cell?.normalized ?? 0;
              return (
                <rect
                  key={`${r}-${c}`}
                  x={c * cellW}
                  y={r * cellH}
                  width={cellW}
                  height={cellH}
                  fill={amberColor(n)}
                  stroke="#0d1124"
                  strokeWidth={0.5}
                >
                  <title>{`(${r},${c}) val=${cell?.value?.toFixed(2) ?? 0} n=${n.toFixed(2)}`}</title>
                </rect>
              );
            })
          )}
        </g>

        {/* Color scale legend */}
        <g transform={`translate(0, ${(title ? TITLE_HEIGHT : 0) + height + LEGEND_MARGIN})`}>
          <rect
            x={0}
            y={0}
            width={width}
            height={LEGEND_HEIGHT}
            fill={`url(#${gradId})`}
            rx={2}
          />
          <text x={2}         y={14} fill="#6b7280" fontSize={9} fontFamily="monospace">0</text>
          <text x={width / 2} y={14} fill="#6b7280" fontSize={9} fontFamily="monospace" textAnchor="middle">0.5</text>
          <text x={width - 2} y={14} fill="#6b7280" fontSize={9} fontFamily="monospace" textAnchor="end">1</text>
        </g>
      </svg>
    </div>
  );
}
