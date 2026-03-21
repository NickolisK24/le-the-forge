import { useState, useEffect, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { clsx } from "clsx";

import { Panel, Button, RiskBar, SectionLabel, Spinner } from "@/components/ui";
import {
  fractureRiskPct, successPct, riskLevel, optimalPath, simulateSequence,
  compareStrategies, instabilityColor, MAX_INSTABILITY, fpCost, RISK_COLORS,
} from "@/lib/crafting";
import { useCraftStore } from "@/store";
import { useCreateCraftSession, useCraftSession, useCraftAction, useCraftSummary, useAffixes } from "@/hooks";
import { useAuthStore } from "@/store";
import type {
  CraftAffix, CraftAction, CraftOutcome, AffixDef,
  OptimalPathStep, SimulationResult, StrategyComparison,
} from "@/types";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ITEM_TYPES = [
  "Wand","Staff","Sword","Axe","Dagger","Sceptre","Mace","Bow",
  "Shield","Helm","Chest","Gloves","Boots","Belt","Ring","Amulet",
];
const RARITIES = ["Normal","Magic","Rare","Exalted","Unique"];
const TIERS = [1,2,3,4,5];
const COMMON_AFFIXES = [
  "Cast Speed","Necrotic Damage","Spell Damage","Minion Damage",
  "Health","Armour","Dodge Rating","Ward Retention",
  "Fire Resistance","Cold Resistance","Lightning Resistance",
  "Critical Strike Chance","Mana","Intelligence","Strength","Dexterity",
];

const ACTION_LABELS: Record<CraftAction, string> = {
  add_affix:     "Add Affix",
  upgrade_affix: "Upgrade Affix",
  seal_affix:    "Seal Affix",
  unseal_affix:  "Unseal Affix",
  remove_affix:  "Remove Affix",
};

const ACTION_FP: Record<CraftAction, number> = {
  add_affix: 4, upgrade_affix: 5, seal_affix: 8,
  unseal_affix: 2, remove_affix: 3,
};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface LogEntry {
  ts: string;
  message: string;
  outcome: CraftOutcome | "info";
  roll?: number;
  riskPct?: number;
  instabilityAfter?: number;
}

// ---------------------------------------------------------------------------
// Local simulation engine
// Mirrors the backend craft_service logic exactly so local sim is accurate
// ---------------------------------------------------------------------------

function localSimulate(
  action: CraftAction,
  affixName: string | undefined,
  targetTier: number | undefined,
  instability: number,
  fp: number,
  affixes: CraftAffix[],
  isFractured: boolean,
): {
  outcome: CraftOutcome | "error";
  message: string;
  newInstability: number;
  newFp: number;
  newAffixes: CraftAffix[];
  roll: number;
  riskPct: number;
} {
  if (isFractured) return {
    outcome: "error", message: "Item is fractured.", roll: 0, riskPct: 0,
    newInstability: instability, newFp: fp, newAffixes: affixes,
  };

  const cost = ACTION_FP[action];
  if (fp < cost) return {
    outcome: "error",
    message: `Not enough Forge Potential. Need ${cost} FP, have ${fp}.`,
    roll: 0, riskPct: 0,
    newInstability: instability, newFp: fp, newAffixes: affixes,
  };

  const sealedCount = affixes.filter((a) => a.sealed).length;
  const riskPct = fractureRiskPct(instability, sealedCount);
  const roll = Math.random() * 100;
  const fractured = roll < riskPct;

  let instGain = 0;
  let outcome: CraftOutcome;

  if (fractured) {
    outcome = "fracture";
    instGain = 0;
  } else if (roll > 95) {
    outcome = "perfect";
    instGain = Math.floor(Math.random() * 3) + 1;
  } else {
    outcome = "success";
    const gainRanges: Record<CraftAction, [number, number]> = {
      add_affix: [3, 7], upgrade_affix: [4, 10], seal_affix: [0, 0],
      unseal_affix: [1, 3], remove_affix: [2, 5],
    };
    const [lo, hi] = gainRanges[action];
    instGain = lo === hi ? lo : Math.floor(Math.random() * (hi - lo + 1)) + lo;
  }

  const newInstability = Math.min(MAX_INSTABILITY, instability + instGain);
  const newFp = fp - cost;

  let newAffixes = [...affixes];
  if (!fractured) {
    if (action === "add_affix" && affixName && newAffixes.filter((a) => !a.sealed).length < 4) {
      newAffixes.push({ name: affixName, tier: targetTier ?? 1, sealed: false });
    } else if (action === "upgrade_affix" && affixName) {
      newAffixes = newAffixes.map((a) =>
        a.name === affixName && !a.sealed
          ? { ...a, tier: Math.min(5, a.tier + 1) }
          : a
      );
    } else if (action === "seal_affix" && affixName) {
      newAffixes = newAffixes.map((a) =>
        a.name === affixName ? { ...a, sealed: true } : a
      );
    } else if (action === "unseal_affix" && affixName) {
      newAffixes = newAffixes.map((a) =>
        a.name === affixName ? { ...a, sealed: false } : a
      );
    } else if (action === "remove_affix" && affixName) {
      newAffixes = newAffixes.filter((a) => a.name !== affixName);
    }
  }

  const messages: Record<CraftOutcome, string> = {
    success: `${ACTION_LABELS[action]} succeeded. +${instGain} instability.`,
    perfect: `Perfect craft! ${ACTION_LABELS[action]} with minimal instability gain (+${instGain}).`,
    fracture: `Item fractured! Roll: ${roll.toFixed(1)} vs ${riskPct.toFixed(1)}% threshold.`,
  };

  return {
    outcome, message: messages[outcome], roll: parseFloat(roll.toFixed(2)),
    riskPct, newInstability, newFp, newAffixes,
  };
}

// ---------------------------------------------------------------------------
// Survival curve SVG
// ---------------------------------------------------------------------------

function SurvivalCurve({
  curve,
  steps,
}: {
  curve: number[];
  steps: OptimalPathStep[];
}) {
  if (curve.length === 0) {
    return (
      <div className="h-24 flex items-center justify-center">
        <p className="font-mono text-[11px] text-forge-dim uppercase tracking-wider">
          No crafting steps predicted
        </p>
      </div>
    );
  }

  const W = 320;
  const H = 96;
  const PAD_L = 28;
  const PAD_R = 8;
  const PAD_T = 8;
  const PAD_B = 20;
  const plotW = W - PAD_L - PAD_R;
  const plotH = H - PAD_T - PAD_B;

  // Points: (stepIndex, survivalPct)
  // Include a leading point at (0, 100%)
  const allPoints = [1.0, ...curve];
  const n = allPoints.length;

  function xOf(i: number) {
    return PAD_L + (i / (n - 1)) * plotW;
  }
  function yOf(v: number) {
    return PAD_T + (1 - v) * plotH;
  }

  const pathD = allPoints
    .map((v, i) => `${i === 0 ? "M" : "L"} ${xOf(i).toFixed(1)} ${yOf(v).toFixed(1)}`)
    .join(" ");

  // Fill area under curve (down to plot bottom)
  const areaD =
    pathD +
    ` L ${xOf(n - 1).toFixed(1)} ${(PAD_T + plotH).toFixed(1)}` +
    ` L ${xOf(0).toFixed(1)} ${(PAD_T + plotH).toFixed(1)} Z`;

  // Color the line based on final survival %
  const finalSurvival = curve[curve.length - 1] ?? 1;
  const lineColor =
    finalSurvival >= 0.70 ? "#3dca74" :
    finalSurvival >= 0.40 ? "#f0a020" :
    "#ff5050";

  // Y-axis labels
  const yLabels = [1.0, 0.75, 0.5, 0.25, 0.0];

  // Step labels on x-axis (only show every other if too many)
  const stepLabels = allPoints.map((_, i) => i);
  const showEvery = n > 8 ? 2 : 1;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: H }}>
      {/* Y-axis gridlines */}
      {yLabels.map((v) => (
        <g key={v}>
          <line
            x1={PAD_L} y1={yOf(v)}
            x2={W - PAD_R} y2={yOf(v)}
            stroke="#1c2240" strokeWidth="1"
          />
          <text
            x={PAD_L - 4} y={yOf(v) + 3.5}
            textAnchor="end"
            fontSize="7"
            fill="#4a5480"
            fontFamily="monospace"
          >
            {Math.round(v * 100)}%
          </text>
        </g>
      ))}

      {/* Area fill */}
      <path d={areaD} fill={lineColor} fillOpacity="0.08" />

      {/* Survival line */}
      <path
        d={pathD}
        fill="none"
        stroke={lineColor}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />

      {/* Data points */}
      {allPoints.map((v, i) => (
        <circle
          key={i}
          cx={xOf(i)} cy={yOf(v)}
          r="2.5"
          fill={lineColor}
          opacity={i === 0 ? 0 : 1}
        />
      ))}

      {/* X-axis step labels */}
      {stepLabels.map((i) =>
        i === 0 || (i % showEvery === 0) ? (
          <text
            key={i}
            x={xOf(i)} y={H - 4}
            textAnchor="middle"
            fontSize="7"
            fill="#4a5480"
            fontFamily="monospace"
          >
            {i === 0 ? "Start" : `S${i}`}
          </text>
        ) : null
      )}
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Outcome Predictor Panel (survival curve + brick/perfect chance)
// ---------------------------------------------------------------------------

function OutcomePredictorPanel({
  optPath,
  simResult,
}: {
  optPath: OptimalPathStep[];
  simResult: SimulationResult;
}) {
  const brickPct = Math.round(simResult.brick_chance * 1000) / 10;
  const perfectPct = Math.round(simResult.perfect_item_chance * 1000) / 10;

  return (
    <Panel title="Outcome Predictor">
      <div className="flex flex-col gap-3">
        {/* Survival curve */}
        <div>
          <SectionLabel>Survival Curve</SectionLabel>
          <SurvivalCurve curve={simResult.step_survival_curve} steps={optPath} />
        </div>

        {/* Summary stats */}
        <div className="grid grid-cols-2 gap-px bg-forge-border border border-forge-border rounded-sm overflow-hidden">
          <div className="bg-forge-surface text-center py-3 px-2">
            <span
              className="font-display text-xl font-bold block mb-0.5"
              style={{ color: brickPct < 20 ? "#3dca74" : brickPct < 40 ? "#f0a020" : "#ff5050" }}
            >
              {brickPct.toFixed(1)}%
            </span>
            <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-forge-dim">
              Brick Chance
            </span>
          </div>
          <div className="bg-forge-surface text-center py-3 px-2">
            <span
              className="font-display text-xl font-bold block mb-0.5"
              style={{ color: perfectPct >= 75 ? "#3dca74" : perfectPct >= 50 ? "#f0a020" : "#ff5050" }}
            >
              {perfectPct.toFixed(1)}%
            </span>
            <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-forge-dim">
              Perfect Item Chance
            </span>
          </div>
        </div>

        {simResult.n_simulations > 0 && (
          <p className="font-mono text-[11px] text-forge-dim text-center">
            {simResult.n_simulations.toLocaleString()} simulations · median instability: {simResult.median_instability}
          </p>
        )}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Optimal Path Panel (enhanced with cumulative survival %)
// ---------------------------------------------------------------------------

function OptimalPathPanel({ steps }: { steps: OptimalPathStep[] }) {
  if (steps.length === 0) {
    return (
      <Panel title="Optimal Craft Path">
        <p className="font-body text-sm italic text-forge-dim py-1 text-center">
          No upgrades needed — all affixes at T4 or sealed.
        </p>
      </Panel>
    );
  }

  return (
    <Panel title="Optimal Craft Path">
      <div className="flex flex-col">
        {steps.map((step, i) => {
          const rl = riskLevel(step.risk_pct);
          const isSeal = step.action === "seal_affix";
          return (
            <div
              key={i}
              className="grid gap-2 py-2 border-b border-forge-border/40 last:border-b-0"
              style={{ gridTemplateColumns: "20px 1fr 52px 60px" }}
            >
              {/* Step number */}
              <span className="font-display text-xs font-bold text-forge-amber self-start pt-0.5">
                {i + 1}
              </span>

              {/* Action + note */}
              <div className="min-w-0">
                <div className={clsx(
                  "font-body text-xs truncate",
                  isSeal ? "text-forge-amber" : "text-forge-text",
                )}>
                  {step.affix}
                </div>
                <div className="font-mono text-[11px] text-forge-dim leading-snug mt-0.5">
                  {step.note}
                </div>
              </div>

              {/* Risk at step */}
              <div className="text-right self-start pt-0.5">
                <span className={clsx(
                  "font-mono text-[11px] px-1 py-0.5 border rounded-sm",
                  isSeal ? "text-forge-green border-forge-green/40" :
                  rl === "safe" ? "text-forge-green border-forge-green/40" :
                  rl === "moderate" ? "text-forge-amber border-forge-amber/40" :
                  "text-forge-red border-forge-red/40"
                )}>
                  {isSeal ? "0%" : `~${step.risk_pct.toFixed(0)}%`}
                </span>
              </div>

              {/* Cumulative survival */}
              <div className="text-right self-start pt-0.5">
                <span
                  className="font-mono text-[11px]"
                  style={{
                    color: step.cumulative_survival_pct >= 70 ? "#3dca74" :
                           step.cumulative_survival_pct >= 40 ? "#f0a020" : "#ff5050",
                  }}
                >
                  {step.cumulative_survival_pct.toFixed(1)}%
                </span>
                <div className="font-mono text-[7px] text-forge-dim">survival</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Final summary row */}
      {steps.length > 0 && (
        <div className="flex justify-between pt-2 mt-1 border-t border-forge-border/40">
          <span className="font-mono text-[11px] text-forge-dim uppercase tracking-wider">
            {steps.length} steps · {steps.reduce((s, step) => s + fpCost(step.action), 0)} FP total
          </span>
          <span
            className="font-mono text-[11px]"
            style={{
              color: (steps[steps.length - 1]?.cumulative_survival_pct ?? 100) >= 70
                ? "#3dca74"
                : "#f0a020",
            }}
          >
            {(steps[steps.length - 1]?.cumulative_survival_pct ?? 100).toFixed(1)}% overall survival
          </span>
        </div>
      )}
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Strategy Comparison Panel
// ---------------------------------------------------------------------------

function StrategyComparisonPanel({
  strategies,
}: {
  strategies: StrategyComparison[];
}) {
  const recommended = strategies.reduce((best, s) =>
    s.perfect_item_chance > best.perfect_item_chance ? s : best,
    strategies[0],
  );

  return (
    <Panel title="Strategy Comparison">
      <div className="grid grid-cols-3 gap-2">
        {strategies.map((s) => {
          const isRec = s.name === recommended?.name;
          const brickPct = Math.round(s.brick_chance * 1000) / 10;
          const perfectPct = Math.round(s.perfect_item_chance * 1000) / 10;

          return (
            <div
              key={s.name}
              className={clsx(
                "border rounded-sm px-3 py-2.5 flex flex-col gap-1.5 transition-colors",
                isRec
                  ? "border-forge-amber/50 bg-forge-amber/5"
                  : "border-forge-border bg-forge-surface",
              )}
            >
              <div className="flex items-center justify-between gap-1">
                <span className={clsx(
                  "font-mono text-[11px] uppercase tracking-wider font-bold",
                  isRec ? "text-forge-amber" : "text-forge-muted",
                )}>
                  {s.name}
                </span>
                {isRec && (
                  <span className="font-mono text-[7px] uppercase tracking-wider text-forge-amber border border-forge-amber/40 px-1 py-0.5 rounded-sm">
                    Best
                  </span>
                )}
              </div>

              <p className="font-body text-xs text-forge-dim leading-snug">
                {s.description}
              </p>

              <div className="grid grid-cols-2 gap-1 mt-1">
                <div>
                  <div
                    className="font-display text-sm font-bold"
                    style={{ color: perfectPct >= 75 ? "#3dca74" : perfectPct >= 50 ? "#f0a020" : "#ff5050" }}
                  >
                    {perfectPct.toFixed(0)}%
                  </div>
                  <div className="font-mono text-[7px] text-forge-dim uppercase tracking-wider">
                    Perfect
                  </div>
                </div>
                <div>
                  <div
                    className="font-display text-sm font-bold"
                    style={{ color: brickPct < 15 ? "#3dca74" : brickPct < 35 ? "#f0a020" : "#ff5050" }}
                  >
                    {brickPct.toFixed(0)}%
                  </div>
                  <div className="font-mono text-[7px] text-forge-dim uppercase tracking-wider">
                    Brick
                  </div>
                </div>
              </div>

              {s.expected_steps > 0 && (
                <div className="font-mono text-[11px] text-forge-dim border-t border-forge-border/40 pt-1.5">
                  {s.expected_steps} steps · {s.expected_fp_cost} FP
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Action Panel
// ---------------------------------------------------------------------------

interface ActionPanelProps {
  affixes: CraftAffix[];
  fp: number;
  isFractured: boolean;
  isLive: boolean;
  isPending: boolean;
  itemType: string;
  onAction: (action: CraftAction, affixName?: string, targetTier?: number, affixType?: "prefix" | "suffix") => void;
}

function ActionPanel({ affixes, fp, isFractured, isLive, isPending, itemType, onAction }: ActionPanelProps) {
  const [action, setAction] = useState<CraftAction>("upgrade_affix");
  const [targetAffix, setTargetAffix] = useState(affixes[0]?.name ?? "");
  const [targetTier, setTargetTier] = useState(1);
  const [affixFilter, setAffixFilter] = useState<"prefix" | "suffix" | "experimental" | "personal" | "">("");

  // Fetch real affixes from the backend, filtered by item slot
  const { data: affixRes } = useAffixes({ slot: itemType.toLowerCase() });
  const availableAffixes: AffixDef[] = affixRes?.data ?? [];

  // Slot counts — sealed affixes don't count toward prefix/suffix limits
  const prefixCount = affixes.filter((a) => a.type === "prefix" && !a.sealed).length;
  const suffixCount = affixes.filter((a) => a.type === "suffix" && !a.sealed).length;
  const sealedCount = affixes.filter((a) => a.sealed).length;

  // The affix name selected for add_affix — defaults to first available
  const [newAffixName, setNewAffixName] = useState("");
  useEffect(() => {
    if (!newAffixName && availableAffixes.length > 0) {
      setNewAffixName(availableAffixes[0].name);
    }
  }, [availableAffixes]);

  useEffect(() => {
    if (affixes.length > 0 && !affixes.find((a) => a.name === targetAffix)) {
      setTargetAffix(affixes[0].name);
    }
  }, [affixes]);

  const cost = ACTION_FP[action];
  const canAct = !isFractured && fp >= cost && !isPending;

  const needsExistingAffix = action !== "add_affix";
  const affixOptions = action === "seal_affix"
    ? affixes.filter((a) => !a.sealed)
    : action === "unseal_affix"
    ? affixes.filter((a) => a.sealed)
    : affixes;

  function handleSubmit() {
    if (action === "add_affix") {
      const def = availableAffixes.find((a) => a.name === newAffixName);
      onAction(action, newAffixName, targetTier, def?.type);
    } else {
      onAction(action, targetAffix);
    }
  }

  return (
    <Panel title="Forge Action">
      <div className="flex flex-col gap-3">
        <div>
          <SectionLabel>Action</SectionLabel>
          <div className="grid grid-cols-2 gap-1.5">
            {(Object.keys(ACTION_LABELS) as CraftAction[]).map((a) => (
              <button
                key={a}
                onClick={() => setAction(a)}
                className={clsx(
                  "font-mono text-[11px] uppercase tracking-wider px-2 py-2 border rounded-sm cursor-pointer transition-all text-left",
                  action === a
                    ? "border-forge-amber text-forge-amber bg-forge-amber/8"
                    : "border-forge-border text-forge-dim hover:border-forge-border-hot hover:text-forge-muted bg-transparent"
                )}
              >
                <span className="block">{ACTION_LABELS[a]}</span>
                <span className="text-forge-dim font-mono text-[11px]">{ACTION_FP[a]} FP</span>
              </button>
            ))}
          </div>
        </div>

        {action === "add_affix" ? (
          <div className="flex flex-col gap-3">
            {/* Slot capacity indicator */}
            <div className="grid grid-cols-2 gap-2 rounded-sm border border-forge-border bg-forge-bg px-3 py-2">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">Prefix</div>
                <div className={`font-display text-lg ${prefixCount >= 2 ? "text-red-400" : "text-forge-text"}`}>
                  {prefixCount} <span className="text-forge-dim text-sm">/ 2</span>
                </div>
              </div>
              <div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">Suffix</div>
                <div className={`font-display text-lg ${suffixCount >= 2 ? "text-red-400" : "text-forge-text"}`}>
                  {suffixCount} <span className="text-forge-dim text-sm">/ 2</span>
                </div>
              </div>
            </div>

            {/* Filter bar */}
            <div className="flex flex-col gap-1">
              <SectionLabel>Add Affix</SectionLabel>
              <div className="flex flex-wrap gap-1">
                {([
                  { key: "", label: "All" },
                  { key: "prefix", label: "Prefix" },
                  { key: "suffix", label: "Suffix" },
                  { key: "experimental", label: "Experimental" },
                  { key: "personal", label: "Personal" },
                ] as const).map(({ key, label }) => {
                  const full = key === "prefix" ? prefixCount >= 2 : key === "suffix" ? suffixCount >= 2 : false;
                  return (
                    <button
                      key={key || "all"}
                      type="button"
                      onClick={() => setAffixFilter(key)}
                      disabled={full}
                      className={`px-2 py-0.5 rounded-sm font-mono text-[10px] uppercase border transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
                        affixFilter === key
                          ? "border-forge-amber bg-forge-amber/15 text-forge-amber"
                          : "border-forge-border text-forge-dim hover:border-forge-amber/50"
                      }`}
                    >
                      {label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Clickable affix grid */}
            <div className="max-h-40 overflow-y-auto rounded-sm border border-forge-border bg-forge-bg p-1">
              {availableAffixes.length === 0 ? (
                <p className="p-2 font-mono text-xs text-forge-dim italic">Loading affixes…</p>
              ) : (
                <div className="flex flex-col gap-0.5">
                  {availableAffixes
                    .filter((a) => {
                      if (!affixFilter) return true;
                      if (affixFilter === "experimental" || affixFilter === "personal") {
                        return (a.tags ?? []).includes(affixFilter);
                      }
                      return a.type === affixFilter && !(a.tags ?? []).includes("experimental") && !(a.tags ?? []).includes("personal");
                    })
                    .filter((a) => !affixes.find((ex) => ex.name === a.name))
                    .map((a) => {
                      const slotFull = (a.type === "prefix" && prefixCount >= 2) || (a.type === "suffix" && suffixCount >= 2);
                      // Label: show experimental/personal tag if present, else type
                      const specialTag = (a.tags ?? []).find((t) => t === "experimental" || t === "personal");
                      const label = specialTag ?? a.type;
                      const labelColor = specialTag === "experimental"
                        ? "text-yellow-400"
                        : specialTag === "personal"
                        ? "text-emerald-400"
                        : a.type === "prefix"
                        ? "text-blue-400"
                        : "text-purple-400";
                      return (
                        <button
                          key={a.id}
                          type="button"
                          disabled={slotFull}
                          onClick={() => !slotFull && setNewAffixName(a.name)}
                          className={`flex items-center justify-between w-full px-2 py-1 rounded-sm text-left transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
                            newAffixName === a.name
                              ? "bg-forge-amber/20 border border-forge-amber/40 text-forge-amber"
                              : slotFull
                              ? "border border-transparent text-forge-dim"
                              : "hover:bg-forge-surface2 text-forge-text border border-transparent"
                          }`}
                        >
                          <span className="font-body text-xs">{a.name}</span>
                          <span className={`font-mono text-[9px] uppercase ${labelColor}`}>
                            {slotFull ? "full" : label}
                          </span>
                        </button>
                      );
                    })}
                </div>
              )}
            </div>

            {/* Tier picker */}
            <div>
              <SectionLabel>Starting Tier</SectionLabel>
              <div className="mt-1 flex gap-1">
                {TIERS.map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTargetTier(t)}
                    className={`flex-1 py-1 rounded-sm font-mono text-xs border transition-colors ${
                      targetTier === t
                        ? "border-forge-amber bg-forge-amber/15 text-forge-amber"
                        : "border-forge-border text-forge-dim hover:border-forge-amber/50"
                    }`}
                  >
                    T{t}
                  </button>
                ))}
              </div>
            </div>

            {/* Selected affixes on this item */}
            {affixes.length > 0 && (
              <div>
                <SectionLabel>Selected Affixes</SectionLabel>
                <div className="mt-1 flex flex-col gap-0.5">
                  {affixes.map((a) => (
                    <div
                      key={a.name}
                      className="flex items-center justify-between rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1"
                    >
                      <span className="font-body text-xs text-forge-text">{a.name}</span>
                      <span className="font-mono text-[10px] text-forge-dim">
                        T{a.tier}{a.sealed ? " · 🔒" : ""}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <SectionLabel>Target Affix</SectionLabel>
            {affixOptions.length === 0 ? (
              <p className="font-mono text-xs text-forge-dim italic">
                No valid affixes for this action
              </p>
            ) : (
              <select
                className="w-full bg-forge-surface2 border border-forge-border text-forge-text font-body text-sm px-2 py-1.5 rounded-sm outline-none focus:border-forge-amber"
                value={targetAffix}
                onChange={(e) => setTargetAffix(e.target.value)}
              >
                {affixOptions.map((a) => (
                  <option key={a.name} value={a.name}>
                    {a.name} (T{a.tier}{a.sealed ? " · Sealed" : ""})
                  </option>
                ))}
              </select>
            )}
          </div>
        )}

        <div className="flex justify-between font-mono text-[11px] uppercase tracking-wider">
          <span className="text-forge-dim">FP Required</span>
          <span className={fp >= cost ? "text-forge-green" : "text-forge-red"}>
            {cost} / {fp} available
          </span>
        </div>

        <Button
          variant={isFractured ? "danger" : "primary"}
          className="w-full"
          disabled={!canAct || (needsExistingAffix && affixOptions.length === 0)}
          onClick={handleSubmit}
        >
          {isPending ? "Forging..." : isFractured ? "Item Fractured" : `${ACTION_LABELS[action]}`}
        </Button>

        {!isLive && (
          <p className="font-mono text-[11px] text-forge-dim text-center">
            Local simulation — save session to persist
          </p>
        )}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Affix list
// ---------------------------------------------------------------------------

function AffixList({
  affixes, onAdd, onRemove, onUpdate, disabled,
}: {
  affixes: CraftAffix[];
  onAdd: () => void;
  onRemove: (name: string) => void;
  onUpdate: (name: string, updates: Partial<CraftAffix>) => void;
  disabled: boolean;
}) {
  return (
    <Panel title="Current Affixes" action={
      !disabled ? (
        <button
          onClick={onAdd}
          disabled={affixes.length >= 4}
          className="font-mono text-[11px] uppercase tracking-[0.14em] text-forge-dim hover:text-forge-amber disabled:opacity-30 bg-transparent border-none cursor-pointer transition-colors"
        >
          + Add
        </button>
      ) : undefined
    }>
      {affixes.length === 0 ? (
        <p className="font-body text-sm italic text-forge-dim text-center py-2">
          No affixes — use the Action panel to add one
        </p>
      ) : (
        <div className="flex flex-col gap-1.5">
          {affixes.map((affix) => (
            <div
              key={affix.name}
              className={clsx(
                "flex items-center gap-2 border rounded-sm px-2.5 py-2 transition-colors",
                affix.sealed
                  ? "bg-forge-amber/5 border-forge-amber/30"
                  : "bg-forge-surface border-forge-border"
              )}
            >
              <div
                className={clsx(
                  "w-2.5 h-2.5 rounded-full flex-shrink-0 border",
                  affix.sealed
                    ? "bg-forge-amber border-forge-amber"
                    : "bg-transparent border-forge-dim"
                )}
                title={affix.sealed ? "Sealed" : "Unsealed"}
              />

              <span className="flex-1 font-body text-sm text-forge-text truncate">
                {affix.name}
              </span>

              <span className={clsx(
                "font-mono text-[11px] px-1.5 py-0.5 border rounded-sm",
                affix.tier === 5 ? "text-forge-gold border-yellow-500/40 bg-yellow-500/7" :
                affix.tier === 4 ? "text-forge-amber border-amber-600/40 bg-amber-600/7" :
                affix.tier === 3 ? "text-forge-blue border-blue-500/40" :
                "text-forge-muted border-forge-border"
              )}>
                T{affix.tier}
              </span>

              {!disabled && (
                <button
                  onClick={() => onRemove(affix.name)}
                  className="text-forge-dim hover:text-forge-red font-mono text-sm bg-transparent border-none cursor-pointer transition-colors"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function CraftSimulatorPage() {
  const { slug } = useParams<{ slug?: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const store = useCraftStore();
  const createSession = useCreateCraftSession();
  const craftAction = useCraftAction();

  const { data: sessionRes, isLoading: sessionLoading } = useCraftSession(slug ?? "");
  const { data: summaryRes } = useCraftSummary(slug ?? "");

  const [log, setLog] = useState<LogEntry[]>([]);
  const [copied, setCopied] = useState(false);

  const isLive = Boolean(slug);
  const session = sessionRes?.data;
  const summary = summaryRes?.data;

  const instability = isLive ? (session?.instability ?? 0) : store.instability;
  const fp = isLive ? (session?.forge_potential ?? 0) : store.forgePotential;
  const affixes: CraftAffix[] = isLive ? (session?.affixes ?? []) : store.affixes;
  const isFractured = isLive ? (session?.is_fractured ?? false) : store.isFractured;

  const sealedCount = affixes.filter((a) => a.sealed).length;
  const riskPct = fractureRiskPct(instability, sealedCount);
  const successP = successPct(instability, sealedCount);
  const rl = riskLevel(riskPct);

  // ---------------------------------------------------------------------------
  // Prediction data — from backend (live) or computed locally (local mode)
  // ---------------------------------------------------------------------------

  const localOptPath = useMemo(
    () => optimalPath(instability, affixes, fp),
    [instability, fp, affixes],
  );

  const localSimResult = useMemo(() => {
    const simSteps = localOptPath.map((s) => ({
      action: s.action,
      sealed_count_at_step: s.sealed_count_at_step,
    }));
    if (simSteps.length === 0) {
      return {
        brick_chance: 0,
        perfect_item_chance: 1,
        step_survival_curve: [],
        step_fracture_rates: [],
        median_instability: instability,
        n_simulations: 0,
      };
    }
    return simulateSequence(instability, fp, simSteps, 3_000);
  }, [localOptPath, instability, fp]);

  const localStrategies = useMemo(
    () => compareStrategies(instability, affixes, fp),
    [instability, fp, affixes],
  );

  const optPath: OptimalPathStep[] = isLive
    ? (summary?.optimal_path ?? localOptPath)
    : localOptPath;

  const simResult: SimulationResult = isLive
    ? (summary?.simulation_result ?? localSimResult)
    : localSimResult;

  const strategies: StrategyComparison[] = isLive
    ? (summary?.strategy_comparison ?? localStrategies)
    : localStrategies;

  // ---------------------------------------------------------------------------
  // Event handlers
  // ---------------------------------------------------------------------------

  function addLog(entry: Omit<LogEntry, "ts">) {
    const ts = new Date().toLocaleTimeString("en-US", {
      hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
    setLog((prev) => [{ ts, ...entry }, ...prev.slice(0, 14)]);
  }

  async function handleAction(action: CraftAction, affixName?: string, targetTier?: number, affixType?: "prefix" | "suffix") {
    if (isLive && session) {
      const res = await craftAction.mutateAsync({ slug: slug!, action, affixName, targetTier });
      if (res.data) {
        addLog({
          message: res.data.message,
          outcome: res.data.outcome,
          roll: res.data.roll,
          riskPct: res.data.fracture_risk_pct,
          instabilityAfter: res.data.instability,
        });
        if (res.data.is_fractured) store.setFractured(true);
      } else if (res.errors) {
        addLog({ message: res.errors[0].message, outcome: "info" });
      }
    } else {
      // Enforce affix slot limits locally before simulating
      if (action === "add_affix" && affixName) {
        const prefixCount = store.affixes.filter((a) => a.type === "prefix" && !a.sealed).length;
        const suffixCount = store.affixes.filter((a) => a.type === "suffix" && !a.sealed).length;
        if (affixType === "prefix" && prefixCount >= 2) {
          addLog({ message: "Prefix slots full (max 2 active prefixes).", outcome: "info" }); return;
        }
        if (affixType === "suffix" && suffixCount >= 2) {
          addLog({ message: "Suffix slots full (max 2 active suffixes).", outcome: "info" }); return;
        }
      }
      if (action === "seal_affix") {
        const sealedCount = store.affixes.filter((a) => a.sealed).length;
        if (sealedCount >= 1) {
          addLog({ message: "Only 1 affix can be sealed at a time.", outcome: "info" }); return;
        }
      }

      const result = localSimulate(
        action, affixName, targetTier,
        store.instability, store.forgePotential, store.affixes, store.isFractured,
      );

      if (result.outcome === "error") {
        addLog({ message: result.message, outcome: "info" });
        return;
      }

      // Attach type to newly added affix
      const newAffixes = result.newAffixes.map((a) =>
        a.name === affixName && !a.type ? { ...a, type: affixType } : a
      );

      store.setInstability(result.newInstability);
      store.setForgePotential(result.newFp);
      store.setAffixes(newAffixes);
      if (result.outcome === "fracture") store.setFractured(true);

      addLog({
        message: result.message,
        outcome: result.outcome as CraftOutcome,
        roll: result.roll,
        riskPct: result.riskPct,
        instabilityAfter: result.newInstability,
      });
    }
  }

  async function handleSaveSession() {
    const res = await createSession.mutateAsync({
      item_type: store.itemType,
      item_name: store.itemName || undefined,
      item_level: store.itemLevel,
      rarity: store.rarity,
      instability: store.instability,
      forge_potential: store.forgePotential,
      affixes: store.affixes,
    });
    if (res.data) {
      navigate(`/craft/${res.data.slug}`);
      addLog({ message: "Session saved and synced to server.", outcome: "info" });
    } else if (res.errors) {
      addLog({ message: res.errors?.[0]?.message ?? "Failed to save.", outcome: "info" });
    }
  }

  function handleReset() {
    store.resetSession();
    setLog([]);
    if (slug) navigate("/craft");
  }

  function copyShareLink() {
    const url = `${window.location.origin}/craft/${slug}`;
    navigator.clipboard?.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  if (isLive && sessionLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spinner size={28} />
      </div>
    );
  }

  const sessionTitle = isLive && session
    ? session.item_name ?? session.item_type
    : store.itemName || store.itemType;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="font-display text-2xl font-bold text-forge-amber tracking-wider">
              Craft Simulator
            </h1>
            {isLive && (
              <span className="font-mono text-[11px] uppercase tracking-wider text-forge-green border border-forge-green/40 bg-forge-green/7 px-2 py-0.5 rounded-sm">
                Live Session
              </span>
            )}
            {!isLive && (
              <span className="font-mono text-[11px] uppercase tracking-wider text-forge-dim border border-forge-border px-2 py-0.5 rounded-sm">
                Local
              </span>
            )}
          </div>
          <p className="font-body text-sm italic text-forge-muted">
            {isLive ? `Session: ${sessionTitle}` : "Simulating locally — save to persist and share"}
          </p>
        </div>

        <div className="flex gap-2">
          {isLive && (
            <Button variant="outline" size="sm" onClick={copyShareLink}>
              {copied ? "Copied!" : "Share Link"}
            </Button>
          )}
          {!isLive && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSaveSession}
              disabled={createSession.isPending}
            >
              {createSession.isPending ? "Saving..." : user ? "Save Session" : "Sign In to Save"}
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={handleReset}>
            New Session
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
        {/* ── LEFT COLUMN ── */}
        <div className="flex flex-col gap-3">

          {/* Item config */}
          <Panel title="Item Configuration">
            <div className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <SectionLabel>Type</SectionLabel>
                  <select
                    disabled={isLive}
                    className="w-full bg-forge-surface2 border border-forge-border text-forge-text font-body text-sm px-2 py-1.5 rounded-sm outline-none focus:border-forge-amber disabled:opacity-50"
                    value={isLive ? (session?.item_type ?? store.itemType) : store.itemType}
                    onChange={(e) => store.setItemType(e.target.value)}
                  >
                    {ITEM_TYPES.map((t) => <option key={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <SectionLabel>Rarity</SectionLabel>
                  <select
                    disabled={isLive}
                    className="w-full bg-forge-surface2 border border-forge-border text-forge-text font-body text-sm px-2 py-1.5 rounded-sm outline-none focus:border-forge-amber disabled:opacity-50"
                    value={isLive ? (session?.rarity ?? store.rarity) : store.rarity}
                    onChange={(e) => store.setRarity(e.target.value)}
                  >
                    {RARITIES.map((r) => <option key={r}>{r}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <SectionLabel>Item Name</SectionLabel>
                <input
                  disabled={isLive}
                  className="w-full bg-forge-surface2 border border-forge-border text-forge-text font-body text-sm px-2 py-1.5 rounded-sm outline-none focus:border-forge-amber disabled:opacity-50 placeholder-forge-dim"
                  placeholder="e.g. Siphon of Anguish"
                  value={isLive ? (session?.item_name ?? "") : store.itemName}
                  onChange={(e) => store.setItemName(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <SectionLabel>Item Level</SectionLabel>
                  <input
                    type="number" min={1} max={100}
                    disabled={isLive}
                    className="w-full bg-forge-surface2 border border-forge-border text-forge-text font-body text-sm px-2 py-1.5 rounded-sm outline-none focus:border-forge-amber disabled:opacity-50"
                    value={isLive ? (session?.item_level ?? store.itemLevel) : store.itemLevel}
                    onChange={(e) => store.setItemLevel(Number(e.target.value))}
                  />
                </div>
                <div>
                  <SectionLabel>Item Level Cap</SectionLabel>
                  <div className="w-full bg-forge-surface2 border border-forge-border text-forge-muted font-mono text-sm px-2 py-1.5 rounded-sm">
                    {isLive ? session?.item_level ?? "—" : store.itemLevel}
                  </div>
                </div>
              </div>
            </div>
          </Panel>

          {/* Instability panel */}
          <Panel title="Forge Potential">
            <div className="mb-3">
              <div className="flex justify-between items-baseline mb-1.5">
                <span className="font-display text-xl font-bold" style={{ color: instabilityColor(instability) }}>
                  {instability}
                </span>
                <span className="font-body text-sm text-forge-dim">/ {MAX_INSTABILITY} instability</span>
              </div>
              <RiskBar pct={(instability / MAX_INSTABILITY) * 100} level={rl} />
              {!isLive && (
                <input
                  type="range" min={0} max={80} step={1}
                  value={instability}
                  onChange={(e) => store.setInstability(Number(e.target.value))}
                  className="w-full mt-2 accent-forge-amber"
                />
              )}
            </div>

            <div className="flex justify-between items-center py-2 border-t border-forge-border">
              <span className="font-mono text-xs uppercase tracking-wider text-forge-dim">
                Forge Potential
              </span>
              <span className={clsx(
                "font-display text-base font-bold",
                fp > 15 ? "text-forge-text" : fp > 8 ? "text-forge-amber" : "text-forge-red"
              )}>
                {fp} FP
              </span>
            </div>

            <div className="flex justify-between items-center py-2 border-t border-forge-border">
              <span className="font-mono text-xs uppercase tracking-wider text-forge-dim">
                Sealed Affixes
              </span>
              <span className="font-display text-base font-bold text-forge-text">
                {sealedCount} / {affixes.length}
              </span>
            </div>

            {isFractured && (
              <div className="mt-2 border border-forge-red/40 bg-forge-red/8 rounded-sm px-3 py-2 text-forge-red font-mono text-xs tracking-wider uppercase text-center">
                ⚠ Item Fractured
              </div>
            )}
          </Panel>

          {/* Affix list */}
          <AffixList
            affixes={affixes}
            disabled={isLive}
            onAdd={() => store.addAffix({ name: "Health", tier: 1, sealed: false })}
            onRemove={(name) => store.removeAffix(name)}
            onUpdate={(name, updates) => store.updateAffix(name, updates)}
          />
        </div>

        {/* ── RIGHT COLUMN ── */}
        <div className="flex flex-col gap-3">

          {/* Risk stat cards */}
          <div className="grid grid-cols-4 gap-px bg-forge-border border border-forge-border rounded-sm overflow-hidden">
            {[
              { label: "Fracture Risk", value: `${riskPct.toFixed(1)}%`, color: RISK_COLORS[rl] },
              { label: "Success Rate", value: `${successP.toFixed(1)}%`, color: "#3dca74" },
              { label: "With 1 Seal", value: `${fractureRiskPct(instability, sealedCount + 1).toFixed(1)}%`, color: "#3dca74" },
              { label: "FP Remaining", value: `${fp}`, color: fp > 15 ? "#3dca74" : fp > 8 ? "#f0a020" : "#ff5050" },
            ].map((card) => (
              <div key={card.label} className="bg-forge-surface text-center py-4 px-2">
                <span className="font-display text-2xl font-bold block mb-1" style={{ color: card.color }}>
                  {card.value}
                </span>
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-forge-dim">
                  {card.label}
                </span>
              </div>
            ))}
          </div>

          {/* Action + Outcome Predictor */}
          <div className="grid grid-cols-2 gap-3">
            <ActionPanel
              affixes={affixes}
              fp={fp}
              isFractured={isFractured}
              isLive={isLive}
              isPending={craftAction.isPending || createSession.isPending}
              itemType={isLive ? (session?.item_type ?? store.itemType) : store.itemType}
              onAction={handleAction}
            />
            <OutcomePredictorPanel optPath={optPath} simResult={simResult} />
          </div>

          {/* Optimal path table */}
          <OptimalPathPanel steps={optPath} />

          {/* Strategy comparison */}
          {strategies.length > 0 && (
            <StrategyComparisonPanel strategies={strategies} />
          )}

          {/* Craft log */}
          <Panel title={`Craft Log ${log.length > 0 ? `(${log.length})` : ""}`}>
            {log.length === 0 ? (
              <p className="font-body text-sm italic text-forge-dim py-1">
                No actions yet — select an action and strike the forge.
              </p>
            ) : (
              <div className="flex flex-col max-h-52 overflow-y-auto">
                {log.map((entry, i) => (
                  <div key={i} className="flex gap-2 items-start border-b border-forge-border/40 last:border-b-0 py-2">
                    <span className="font-mono text-[11px] text-forge-dim flex-shrink-0 pt-0.5">{entry.ts}</span>
                    <div className="flex-1">
                      <span className={clsx(
                        "font-mono text-xs",
                        entry.outcome === "success" || entry.outcome === "perfect" ? "text-forge-green" :
                        entry.outcome === "fracture" ? "text-forge-red" :
                        "text-forge-muted"
                      )}>
                        {entry.message}
                      </span>
                      {entry.roll !== undefined && (
                        <div className="font-mono text-[11px] text-forge-dim mt-0.5">
                          Roll: {entry.roll.toFixed(1)} · Risk: {entry.riskPct?.toFixed(1)}% · Inst: {entry.instabilityAfter}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Panel>

          {/* Session summary (live only) */}
          {isLive && summary && (
            <Panel title="Session Summary">
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Total Actions", value: summary.total_actions },
                  { label: "Successes", value: summary.successes },
                  { label: "Perfects", value: summary.perfects },
                  { label: "Fractures", value: summary.fractures, danger: summary.fractures > 0 },
                  { label: "FP Spent", value: summary.fp_spent },
                  { label: "Current Risk", value: `${summary.current_risk_pct.toFixed(1)}%` },
                ].map((s) => (
                  <div key={s.label} className="text-center py-2 border border-forge-border rounded-sm">
                    <span className={clsx(
                      "font-display text-lg font-bold block",
                      s.danger ? "text-forge-red" : "text-forge-amber"
                    )}>
                      {s.value}
                    </span>
                    <span className="font-mono text-[11px] uppercase tracking-wider text-forge-dim">
                      {s.label}
                    </span>
                  </div>
                ))}
              </div>
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}
