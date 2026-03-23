/**
 * SimulationDashboard — renders the full results of /api/builds/<slug>/simulate.
 *
 * Sections:
 *   1. Summary strip (DPS, EHP, survivability score, sustain score)
 *   2. DPS breakdown bar chart (hit, ailment, total)
 *   3. Monte Carlo distribution (p25/mean/p75 with std dev range)
 *   4. EHP layers stacked bar (health, ward buffer, avoidance bonus)
 *   5. Resistance heptagon bar chart (7 resist types)
 *   6. Stat upgrade recommendations bar chart (top 5 by DPS gain)
 *   7. Strengths & weaknesses
 */

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine, ErrorBar,
} from "recharts";
import type { BuildSimulationResult, DefenseResult, StatUpgrade } from "@/lib/api";
import { Panel } from "@/components/ui";

// ---------------------------------------------------------------------------
// Colour tokens (match Tailwind forge palette)
// ---------------------------------------------------------------------------
const C = {
  amber:   "#f0a020",
  amberHot:"#ffb83f",
  cyan:    "#22d3ee",
  green:   "#4ade80",
  red:     "#f87171",
  muted:   "#6b7280",
  surface: "#1a1a2e",
  border:  "rgba(255,255,255,0.08)",
  text:    "#e5e7eb",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return String(Math.round(n));
}

function ScoreRing({ label, value, color }: { label: string; value: number; color: string }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const filled = (value / 100) * circ;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="72" height="72" viewBox="0 0 72 72">
        <circle cx="36" cy="36" r={r} fill="none" stroke={C.border} strokeWidth="6" />
        <circle
          cx="36" cy="36" r={r}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeDasharray={`${filled} ${circ - filled}`}
          strokeLinecap="round"
          transform="rotate(-90 36 36)"
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
        <text x="36" y="40" textAnchor="middle" fill={color} fontSize="14" fontWeight="bold" fontFamily="monospace">
          {value}
        </text>
      </svg>
      <span className="font-mono text-[10px] uppercase tracking-widest text-forge-muted">{label}</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// DPS Breakdown
// ---------------------------------------------------------------------------

function DpsBreakdown({ dps }: { dps: BuildSimulationResult["dps"] }) {
  const data = [
    { name: "Hit DPS",     value: dps.dps,        fill: C.amber },
    { name: "Ailment DPS", value: dps.ailment_dps, fill: C.cyan  },
    { name: "Total DPS",   value: dps.total_dps,  fill: C.green  },
  ].filter(d => d.value > 0);

  return (
    <Panel title="DPS Breakdown">
      <div className="space-y-3">
        {data.map(d => (
          <div key={d.name}>
            <div className="flex justify-between font-mono text-xs mb-1">
              <span style={{ color: d.fill }}>{d.name}</span>
              <span className="text-forge-text">{fmt(d.value)}</span>
            </div>
            <div className="h-1.5 rounded-full bg-forge-surface3 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${Math.min(100, (d.value / dps.total_dps) * 100)}%`,
                  backgroundColor: d.fill,
                }}
              />
            </div>
          </div>
        ))}
        <div className="pt-2 border-t border-forge-border/30 grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="font-mono text-[10px] text-forge-muted">Atk Speed</div>
            <div className="font-display text-sm font-bold text-forge-text">
              {dps.effective_attack_speed.toFixed(2)}/s
            </div>
          </div>
          <div>
            <div className="font-mono text-[10px] text-forge-muted">Avg Hit</div>
            <div className="font-display text-sm font-bold text-forge-text">{fmt(dps.average_hit)}</div>
          </div>
          <div>
            <div className="font-mono text-[10px] text-forge-muted">Crit Contrib</div>
            <div className="font-display text-sm font-bold text-forge-amber">{dps.crit_contribution_pct}%</div>
          </div>
        </div>
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Monte Carlo Distribution
// ---------------------------------------------------------------------------

function MonteCarloPanel({ mc }: { mc: BuildSimulationResult["monte_carlo"] }) {
  const data = [
    { label: "Min",  value: mc.min_dps,       fill: C.red    },
    { label: "P25",  value: mc.percentile_25,  fill: C.muted  },
    { label: "Mean", value: mc.mean_dps,       fill: C.amber  },
    { label: "P75",  value: mc.percentile_75,  fill: C.cyan   },
    { label: "Max",  value: mc.max_dps,        fill: C.green  },
  ];

  const maxVal = mc.max_dps || 1;

  return (
    <Panel title="DPS Distribution" action={
      <span className="font-mono text-[10px] text-forge-dim">{mc.n_simulations.toLocaleString()} sims</span>
    }>
      <div className="space-y-2">
        {data.map(d => (
          <div key={d.label} className="flex items-center gap-2">
            <span className="font-mono text-[10px] w-8 text-right" style={{ color: d.fill }}>{d.label}</span>
            <div className="flex-1 h-2 rounded-full bg-forge-surface3 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${(d.value / maxVal) * 100}%`, backgroundColor: d.fill }}
              />
            </div>
            <span className="font-mono text-[10px] w-14 text-right text-forge-muted">{fmt(d.value)}</span>
          </div>
        ))}
        <div className="flex justify-between pt-2 border-t border-forge-border/30 font-mono text-[10px] text-forge-dim">
          <span>Std Dev: {fmt(mc.std_dev)}</span>
          <span>Variance: {mc.std_dev > 0 ? `±${((mc.std_dev / mc.mean_dps) * 100).toFixed(0)}%` : "0%"}</span>
        </div>
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// EHP Breakdown
// ---------------------------------------------------------------------------

function EhpBreakdown({ def }: { def: DefenseResult }) {
  const total = def.total_ehp || 1;
  const layers = [
    { name: "Base Health", value: def.max_health,       color: C.amber  },
    { name: "EHP Bonus",   value: Math.max(0, def.effective_hp - def.max_health), color: C.cyan },
    { name: "Ward Buffer", value: def.ward_buffer,       color: C.green  },
  ].filter(l => l.value > 0);

  return (
    <Panel title="Effective HP Layers">
      <div className="space-y-2">
        <div className="flex h-5 rounded overflow-hidden gap-px">
          {layers.map(l => (
            <div
              key={l.name}
              title={`${l.name}: ${fmt(l.value)}`}
              className="transition-all duration-700"
              style={{ flex: l.value / total, backgroundColor: l.color }}
            />
          ))}
        </div>
        <div className="flex justify-center gap-4">
          {layers.map(l => (
            <div key={l.name} className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: l.color }} />
              <span className="font-mono text-[10px] text-forge-dim">{l.name}</span>
              <span className="font-mono text-[10px] text-forge-text">{fmt(l.value)}</span>
            </div>
          ))}
        </div>
        <div className="text-center font-display text-lg font-bold text-forge-text">
          {fmt(def.total_ehp)} <span className="text-forge-dim font-mono text-xs">total EHP</span>
        </div>
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Resistance Chart
// ---------------------------------------------------------------------------

function ResistanceChart({ def }: { def: DefenseResult }) {
  const resistances = [
    { name: "Fire",      value: def.fire_res,        fill: "#ef4444" },
    { name: "Cold",      value: def.cold_res,        fill: "#60a5fa" },
    { name: "Lightning", value: def.lightning_res,   fill: "#fbbf24" },
    { name: "Void",      value: def.void_res,        fill: "#8b5cf6" },
    { name: "Necrotic",  value: def.necrotic_res,    fill: "#a3e635" },
    { name: "Physical",  value: def.physical_res,    fill: "#94a3b8" },
    { name: "Poison",    value: def.poison_res,      fill: "#4ade80" },
  ];

  return (
    <Panel title="Resistances">
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={resistances} margin={{ top: 4, right: 8, bottom: 4, left: -16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
          <XAxis dataKey="name" tick={{ fill: C.muted, fontSize: 10, fontFamily: "monospace" }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 75]} tick={{ fill: C.muted, fontSize: 10 }} axisLine={false} tickLine={false} />
          <ReferenceLine y={75} stroke={C.amber} strokeDasharray="4 2" label={{ value: "cap", fill: C.amber, fontSize: 9 }} />
          <Tooltip
            contentStyle={{ background: "#1a1a2e", border: `1px solid ${C.border}`, borderRadius: 4, fontSize: 11 }}
            labelStyle={{ color: C.text }}
            formatter={(v: number) => [`${v}%`, ""]}
          />
          <Bar dataKey="value" radius={[2, 2, 0, 0]}>
            {resistances.map((r) => <Cell key={r.name} fill={r.fill} opacity={r.value >= 70 ? 1 : r.value >= 50 ? 0.75 : 0.5} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Stat Upgrade Recommendations
// ---------------------------------------------------------------------------

function UpgradeChart({ upgrades }: { upgrades: StatUpgrade[] }) {
  const top = [...upgrades]
    .sort((a, b) => b.dps_gain_pct - a.dps_gain_pct)
    .slice(0, 6);

  return (
    <Panel title="Stat Upgrade Priorities">
      <div className="space-y-2">
        {top.map((u, i) => (
          <div key={u.stat} className="grid gap-2 items-center" style={{ gridTemplateColumns: "18px 1fr 50px 50px" }}>
            <span className="font-display text-xs font-bold text-forge-amber">{i + 1}</span>
            <div className="min-w-0">
              <div className="font-body text-xs text-forge-text truncate">{u.label}</div>
              <div className="mt-0.5 h-1 rounded-full bg-forge-surface3 overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${Math.min(100, (u.dps_gain_pct / top[0].dps_gain_pct) * 100)}%`,
                    background: `linear-gradient(90deg, ${C.amber}, ${C.amberHot})`,
                  }}
                />
              </div>
            </div>
            <div className="text-right">
              <div className="font-mono text-[10px] text-forge-dim">DPS</div>
              <div className="font-mono text-xs text-forge-amber">+{u.dps_gain_pct.toFixed(1)}%</div>
            </div>
            <div className="text-right">
              <div className="font-mono text-[10px] text-forge-dim">EHP</div>
              <div className="font-mono text-xs text-forge-cyan">+{u.ehp_gain_pct.toFixed(1)}%</div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Avoidance Layers
// ---------------------------------------------------------------------------

function AvoidancePanel({ def }: { def: DefenseResult }) {
  const layers = [
    { label: "Dodge",         value: def.dodge_chance_pct,      color: C.cyan  },
    { label: "Block",         value: def.block_chance_pct,      color: C.amber },
    { label: "Crit Avoid",    value: def.crit_avoidance_pct,   color: C.green },
    { label: "Glancing Blow", value: def.glancing_blow_pct,    color: C.muted },
    { label: "Endurance",     value: def.endurance_pct,        color: "#a78bfa"},
    { label: "Stun Avoid",    value: def.stun_avoidance_pct,   color: "#f472b6"},
  ].filter(l => l.value > 0);

  const sustainRows = [
    { label: "Leech",           value: def.leech_pct > 0 ? `${def.leech_pct}%` : "—"       },
    { label: "Health Regen",    value: def.health_regen > 0 ? `${def.health_regen}/s` : "—" },
    { label: "Ward Net",        value: def.net_ward_per_second !== 0 ? `${def.net_ward_per_second > 0 ? "+" : ""}${def.net_ward_per_second}/s` : "—" },
    { label: "On Kill (HP)",    value: def.health_on_kill > 0 ? fmt(def.health_on_kill) : "—"   },
  ];

  return (
    <Panel title="Avoidance & Sustain">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-2">Avoidance</div>
          {layers.length > 0 ? layers.map(l => (
            <div key={l.label} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: l.color }} />
              <span className="font-mono text-[10px] text-forge-dim flex-1">{l.label}</span>
              <span className="font-mono text-xs" style={{ color: l.color }}>{l.value.toFixed(1)}%</span>
            </div>
          )) : (
            <p className="font-mono text-[10px] text-forge-dim italic">No avoidance layers</p>
          )}
        </div>
        <div className="space-y-2">
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-2">Sustain</div>
          {sustainRows.map(r => (
            <div key={r.label} className="flex items-center justify-between gap-2">
              <span className="font-mono text-[10px] text-forge-dim">{r.label}</span>
              <span className={`font-mono text-xs ${r.value === "—" ? "text-forge-dim" : "text-forge-green"}`}>
                {r.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Strengths / Weaknesses
// ---------------------------------------------------------------------------

function InsightsPanel({ def }: { def: DefenseResult }) {
  return (
    <Panel title="Build Insights">
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-green mb-2">✓ Strengths</div>
          {def.strengths.length > 0 ? (
            <ul className="space-y-1">
              {def.strengths.map((s, i) => (
                <li key={i} className="font-body text-xs text-forge-muted flex gap-1.5">
                  <span className="text-forge-green shrink-0">·</span>{s}
                </li>
              ))}
            </ul>
          ) : (
            <p className="font-mono text-[10px] text-forge-dim italic">None detected</p>
          )}
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-red mb-2">✗ Weaknesses</div>
          {def.weaknesses.length > 0 ? (
            <ul className="space-y-1">
              {def.weaknesses.map((w, i) => (
                <li key={i} className="font-body text-xs text-forge-muted flex gap-1.5">
                  <span className="text-forge-red shrink-0">·</span>{w}
                </li>
              ))}
            </ul>
          ) : (
            <p className="font-mono text-[10px] text-forge-dim italic">No critical weaknesses</p>
          )}
        </div>
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Root export
// ---------------------------------------------------------------------------

export default function SimulationDashboard({ result }: { result: BuildSimulationResult }) {
  const { dps, monte_carlo: mc, defense: def, stat_upgrades: upgrades } = result;

  return (
    <div className="space-y-4">
      {/* Summary strip */}
      <div className="flex items-center justify-between rounded border border-forge-border bg-forge-surface2 px-6 py-3">
        <div className="text-center">
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted">Total DPS</div>
          <div className="font-display text-2xl font-bold text-forge-amber">{fmt(dps.total_dps)}</div>
        </div>
        <div className="text-center">
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted">Mean DPS (sim)</div>
          <div className="font-display text-2xl font-bold text-forge-text">{fmt(mc.mean_dps)}</div>
        </div>
        <div className="text-center">
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted">Total EHP</div>
          <div className="font-display text-2xl font-bold text-forge-cyan">{fmt(def.total_ehp)}</div>
        </div>
        <div className="flex gap-6">
          <ScoreRing label="Survivability" value={def.survivability_score} color={C.amber} />
          <ScoreRing label="Sustain" value={def.sustain_score} color={C.cyan} />
        </div>
        <div className="text-center">
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted">Skill</div>
          <div className="font-body text-sm text-forge-text">{result.primary_skill}</div>
          <div className="font-mono text-[10px] text-forge-dim">Lv {result.skill_level}</div>
        </div>
      </div>

      {/* Grid: DPS + Monte Carlo */}
      <div className="grid grid-cols-2 gap-4">
        <DpsBreakdown dps={dps} />
        <MonteCarloPanel mc={mc} />
      </div>

      {/* Grid: EHP + Resistances */}
      <div className="grid grid-cols-2 gap-4">
        <EhpBreakdown def={def} />
        <ResistanceChart def={def} />
      </div>

      {/* Grid: Avoidance + Upgrades */}
      <div className="grid grid-cols-2 gap-4">
        <AvoidancePanel def={def} />
        <UpgradeChart upgrades={upgrades} />
      </div>

      {/* Full width insights */}
      <InsightsPanel def={def} />
    </div>
  );
}
