import { useEffect, useMemo, useState } from "react";

import { V2EnvelopePanels } from "@/components/v2/V2EnvelopePanels";
import { V2LimitationNotice } from "@/components/v2/V2LimitationNotice";
import { V2PlannerAdapterStatusPanel } from "@/components/v2/V2PlannerAdapterStatusPanel";
import { getV2ErrorMessage, summarizeObject, type V2ApiEnvelope } from "@/lib/v2ApiEnvelope";

interface RegistryDebugSummary extends Record<string, unknown> {
  source_path?: string;
  stat_count?: number;
  modifier_count?: number;
  summary?: Record<string, unknown>;
  production_consumer?: boolean;
  production_safe?: boolean;
}

interface V2StatsModifiersDebugSummary extends Record<string, unknown> {
  stats?: RegistryDebugSummary;
  modifiers?: RegistryDebugSummary;
}

interface V2StatsModifiersDebugResponse extends V2ApiEnvelope {
  success?: boolean;
  experimental?: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  data_source?: string;
  debug_summary?: V2StatsModifiersDebugSummary;
  message?: string;
}

async function fetchStatsModifiersDebug(): Promise<V2StatsModifiersDebugResponse> {
  const response = await fetch("/api/experimental/v2/modifiers/debug");
  const json = await response.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return {
      success: false,
      error: "invalid_response",
      message: `Backend returned an unreadable response (${response.status}).`,
    };
  }
  return json as V2StatsModifiersDebugResponse;
}

export default function V2StatsModifiersDebugPage() {
  const [data, setData] = useState<V2StatsModifiersDebugResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchStatsModifiersDebug();
      setData(result);
      if (!result.success) setError(getV2ErrorMessage(result));
    } catch (err) {
      setData(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const summary = getStatsModifierSummary(data);
  const envelope = useMemo(() => buildEnvelopeForPanels(data, summary), [data, summary]);

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <header className="border-b border-[#2a3050] pb-4">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          Debug / Experimental / Read-only
        </p>
        <h1 className="mt-2 font-display text-2xl text-[#f5a623]">
          v2 stats and modifiers inspection
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-400">
          This page explains v2 stat and modifier registry status for inspection only. Modifier values are not used for planner calculations.
        </p>
      </header>

      {loading && (
        <div className="rounded border border-[#2a3050] bg-[#0f172a] p-4 text-sm text-gray-300">
          Loading stat and modifier debug endpoint...
        </div>
      )}

      {!loading && error && (
        <section className="rounded border border-red-900 bg-red-950/30 p-4">
          <h2 className="text-sm font-semibold text-red-300">Debug endpoint unavailable</h2>
          <p className="mt-2 text-sm text-red-100">{error}</p>
        </section>
      )}

      {!loading && data?.success && (
        <>
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Stat registry entries" value={summary.statCount} />
            <MetricCard label="Modifier rows" value={summary.modifierCount} />
            <MetricCard label="Planner-calculable" value={summary.plannerCalculableCount} />
            <MetricCard label="Stable-calculable" value={summary.stableCalculableCount} />
            <MetricCard label="Value normalization" value={summary.valueNormalizationStatus} />
            <MetricCard label="Source units" value={summary.sourceUnitsCount} />
            <MetricCard label="Unknown value scale" value={summary.unknownValueScaleCount} />
            <MetricCard label="Production consumer" value={String(data.production_consumer ?? false)} />
          </section>

          <V2EnvelopePanels response={envelope} />

          <V2PlannerAdapterStatusPanel
            status={{
              adapterModeEnabled: false,
              productionConsumed: false,
              adapterVisibleCount: summary.modifierCount,
              blockedCount: summary.modifierCount,
              plannerCalculableCount: summary.plannerCalculableCount,
              stableCalculableCount: summary.stableCalculableCount,
              topBlockedReasons: summary.blockedReasonCounts,
              safeNowBaselineFixtureCount: 7,
              blockedBaselineFixtureCount: 6,
              valueNormalizationStatus: summary.valueNormalizationStatus,
              skillIdentityBridgeStatus: "unbridged",
            }}
          />

          <section className="rounded border border-amber-400/20 bg-amber-500/5 p-4">
            <h2 className="text-sm font-semibold text-amber-100">Planner safety limitations</h2>
            <div className="mt-3">
              <V2LimitationNotice
                codes={[
                  "audit_only_value_normalization",
                  "not_planner_calculable",
                  "stable_calculable_unavailable",
                  "production_not_consuming_v2",
                ]}
                mode="full"
              />
            </div>
          </section>

          <section className="grid gap-3 lg:grid-cols-3">
            <DistributionCard title="Top blocked reasons" values={summary.blockedReasonCounts} />
            <DistributionCard title="Operation distribution" values={summary.operationCounts} />
            <DistributionCard title="Value scale distribution" values={summary.valueScaleStatusCounts} />
          </section>

          <section className="grid gap-3 lg:grid-cols-2">
            <SourceCard title="Stat registry source" value={summary.statSourcePath} />
            <SourceCard title="Modifier registry source" value={summary.modifierSourcePath} />
          </section>

          <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
            <h2 className="text-sm font-semibold text-gray-100">Calculation boundary</h2>
            <p className="mt-2 text-sm text-gray-300">
              v2 stat and modifier data is visible for audit and debugging. Unknown operations, source-unit values, unknown value scales, and blocked identities keep modifier rows out of planner math.
            </p>
            <p className="mt-2 text-sm text-gray-300">
              v3 mechanical intelligence is required before these values can be considered for stat aggregation or planner output.
            </p>
          </section>
        </>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
      <div className="text-xs uppercase text-gray-500">{label}</div>
      <div className="mt-2 break-words font-mono text-lg text-gray-100">{value}</div>
    </div>
  );
}

function DistributionCard({ title, values }: { title: string; values: Record<string, unknown> | undefined }) {
  return (
    <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
      <h2 className="text-sm font-semibold text-gray-100">{title}</h2>
      <p className="mt-2 break-words font-mono text-xs text-gray-300">{summarizeObject(values)}</p>
    </section>
  );
}

function SourceCard({ title, value }: { title: string; value: string }) {
  return (
    <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
      <h2 className="text-sm font-semibold text-gray-100">{title}</h2>
      <p className="mt-2 break-all font-mono text-xs text-gray-400">{value}</p>
    </section>
  );
}

function getStatsModifierSummary(response: V2StatsModifiersDebugResponse | null) {
  const debugSummary = response?.debug_summary ?? response?.data?.debug_summary as V2StatsModifiersDebugSummary | undefined;
  const modifierSummary = debugSummary?.modifiers?.summary ?? {};
  const statSummary = debugSummary?.stats?.summary ?? {};
  const valueScaleStatusCounts = recordValue(modifierSummary.value_scale_status_counts);

  return {
    statCount: numberValue(debugSummary?.stats?.stat_count, statSummary.stat_count),
    modifierCount: numberValue(debugSummary?.modifiers?.modifier_count, modifierSummary.modifier_count),
    plannerCalculableCount: 0,
    stableCalculableCount: numberValue(modifierSummary.stable_calculable_count),
    valueNormalizationStatus: "audit_only",
    sourceUnitsCount: numberValue(valueScaleStatusCounts?.source_units),
    unknownValueScaleCount: numberValue(valueScaleStatusCounts?.unknown),
    blockedReasonCounts: recordValue(modifierSummary.blocked_reason_counts),
    operationCounts: recordValue(modifierSummary.operation_counts),
    valueScaleStatusCounts,
    statSourcePath: String(debugSummary?.stats?.source_path ?? "n/a"),
    modifierSourcePath: String(debugSummary?.modifiers?.source_path ?? "n/a"),
    unresolvedSkillReferenceCount: numberValue(modifierSummary.unresolved_skill_reference_count),
    ambiguousSkillReferenceCount: numberValue(modifierSummary.ambiguous_skill_reference_count),
  };
}

function buildEnvelopeForPanels(
  response: V2StatsModifiersDebugResponse | null,
  summary: ReturnType<typeof getStatsModifierSummary>,
): V2ApiEnvelope {
  return {
    ...response,
    success: response?.success,
    experimental: true,
    read_only: true,
    production_consumer: false,
    data_source: "v2_modifier_registries",
    source_path: summary.modifierSourcePath,
    summary: {
      modifier_count: summary.modifierCount,
      stat_count: summary.statCount,
      stable_calculable_count: summary.stableCalculableCount,
      value_normalization_status: summary.valueNormalizationStatus,
      blocked_reason_counts: summary.blockedReasonCounts,
      operation_counts: summary.operationCounts,
      value_scale_status_counts: summary.valueScaleStatusCounts,
      unresolved_skill_reference_count: summary.unresolvedSkillReferenceCount,
      ambiguous_skill_reference_count: summary.ambiguousSkillReferenceCount,
      production_consumed: false,
    },
    support_summary: {
      partial: summary.modifierCount,
      stable_calculable: summary.stableCalculableCount,
      audit_only: summary.modifierCount,
    },
    meta: {
      domain: "stats_modifiers",
      experimental: true,
      read_only: true,
      production_consumed: false,
      value_normalization_status: summary.valueNormalizationStatus,
    },
    provenance: {
      data_source: "v2_modifier_registries",
      source_path: summary.modifierSourcePath,
      stat_registry_source_path: summary.statSourcePath,
      production_consumed: false,
    },
    debug: {
      ...(response?.debug ?? {}),
      planner_calculable_count: summary.plannerCalculableCount,
      blocked_reason_counts: summary.blockedReasonCounts,
      value_normalization_status: summary.valueNormalizationStatus,
      production_consumed: false,
      read_only: true,
    },
  };
}

function numberValue(...values: unknown[]): number {
  for (const value of values) {
    if (typeof value === "number") return value;
  }
  return 0;
}

function recordValue(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : undefined;
}
