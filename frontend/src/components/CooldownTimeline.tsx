/**
 * G14 — Cooldown Timeline Visualization
 *
 * Renders a horizontal swimlane chart showing when each skill was cast
 * and any cooldown gaps between casts.
 */

import type { CastDetail } from "@/services/rotationApi";

interface Props {
  castResults: CastDetail[];
  duration:    number;
}

const COLORS: Record<string, string> = {};
const PALETTE = [
  "#f5a623", "#4a9eff", "#5edd7e", "#e06060",
  "#a78bfa", "#fb923c", "#38bdf8", "#34d399",
];
function colorFor(skill_id: string): string {
  if (!COLORS[skill_id]) {
    const idx = Object.keys(COLORS).length % PALETTE.length;
    COLORS[skill_id] = PALETTE[idx];
  }
  return COLORS[skill_id];
}

export default function CooldownTimeline({ castResults, duration }: Props) {
  if (!castResults.length) return null;

  // Group by skill
  const bySkill: Record<string, CastDetail[]> = {};
  for (const c of castResults) {
    (bySkill[c.skill_id] ??= []).push(c);
  }

  const skills = Object.keys(bySkill);
  const rowH = 28;
  const labelW = 100;
  const chartW = 600;
  const totalH = skills.length * rowH + 24; // +24 for time axis

  return (
    <div className="overflow-x-auto">
      <svg
        width={labelW + chartW + 8}
        height={totalH}
        className="text-xs font-mono"
      >
        {/* Time axis ticks */}
        {Array.from({ length: 7 }, (_, i) => {
          const t = (i / 6) * duration;
          const x = labelW + (t / duration) * chartW;
          return (
            <g key={i}>
              <line x1={x} y1={0} x2={x} y2={totalH - 18} stroke="#2a3050" strokeWidth={1} />
              <text x={x} y={totalH - 4} textAnchor="middle" fill="#6b7280" fontSize={10}>
                {t.toFixed(1)}s
              </text>
            </g>
          );
        })}

        {skills.map((sid, row) => {
          const y = row * rowH + 4;
          const color = colorFor(sid);
          return (
            <g key={sid}>
              {/* Label */}
              <text
                x={labelW - 6}
                y={y + rowH / 2}
                textAnchor="end"
                dominantBaseline="middle"
                fill="#c8d0e0"
                fontSize={11}
              >
                {sid}
              </text>

              {/* Background track */}
              <rect
                x={labelW}
                y={y + 4}
                width={chartW}
                height={rowH - 10}
                fill="#1a2040"
                rx={2}
              />

              {/* Cast bars */}
              {bySkill[sid].map((cast, i) => {
                const x1 = labelW + (cast.cast_at / duration) * chartW;
                const x2 = labelW + (cast.resolves_at / duration) * chartW;
                const barW = Math.max(x2 - x1, 3);
                return (
                  <rect
                    key={i}
                    x={x1}
                    y={y + 6}
                    width={barW}
                    height={rowH - 14}
                    fill={color}
                    rx={2}
                    opacity={0.85}
                  >
                    <title>{`${sid} @ ${cast.cast_at.toFixed(2)}s — ${cast.damage.toFixed(0)} dmg`}</title>
                  </rect>
                );
              })}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
