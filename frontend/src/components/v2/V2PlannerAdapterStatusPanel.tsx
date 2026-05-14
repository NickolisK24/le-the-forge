import { V2LimitationNotice } from "./V2LimitationNotice";
import { V2StatusBadgeGroup } from "./V2StatusBadgeGroup";

export interface V2PlannerAdapterStatus {
  adapterModeEnabled?: boolean;
  productionConsumed?: boolean;
  adapterVisibleCount?: number;
  blockedCount?: number;
  plannerCalculableCount?: number;
  stableCalculableCount?: number;
  topBlockedReasons?: Record<string, unknown>;
  safeNowBaselineFixtureCount?: number;
  blockedBaselineFixtureCount?: number;
  valueNormalizationStatus?: string;
  skillIdentityBridgeStatus?: string;
}

interface V2PlannerAdapterStatusPanelProps {
  status: V2PlannerAdapterStatus;
}

export function V2PlannerAdapterStatusPanel({ status }: V2PlannerAdapterStatusPanelProps) {
  const adapterModeEnabled = status.adapterModeEnabled === true;
  const productionConsumed = status.productionConsumed === true;
  const plannerCalculableCount = numberValue(status.plannerCalculableCount);
  const stableCalculableCount = numberValue(status.stableCalculableCount);
  const valueNormalizationStatus = status.valueNormalizationStatus ?? "audit_only";
  const skillIdentityBridgeStatus = status.skillIdentityBridgeStatus ?? "unbridged";

  return (
    <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
            Planner-safe adapter
          </p>
          <h2 className="mt-1 text-lg font-semibold text-gray-100">v2 adapter status</h2>
          <p className="mt-2 max-w-3xl text-sm text-gray-300">
            The v2 adapter is available for read-only diagnostics. It is not production planner math, and it does not change DPS, EHP, crafting, or build output.
          </p>
        </div>
        <V2StatusBadgeGroup
          statuses={[
            {
              key: adapterModeEnabled ? "experimental-enabled" : "experimental-disabled",
              label: adapterModeEnabled ? "Experimental Enabled" : "Experimental Disabled",
              title: adapterModeEnabled
                ? "The explicit experimental adapter mode is enabled for diagnostics only."
                : "The explicit experimental adapter mode is disabled by default.",
              tone: adapterModeEnabled ? "purple" : "gray",
            },
            {
              key: "not-production",
              label: productionConsumed ? "Production Consuming v2" : "Production Unchanged",
              title: productionConsumed
                ? "Production consumption is active for this status."
                : "Production planner calculations are not consuming v2 data.",
              tone: productionConsumed ? "red" : "blue",
            },
            {
              key: "not-planner-calculable",
              label: "Not Planner-Calculable",
              title: "Current adapter-visible records remain blocked from planner calculations.",
              tone: "slate",
            },
          ]}
        />
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatusMetric label="Adapter mode" value={adapterModeEnabled ? "enabled" : "disabled"} />
        <StatusMetric label="Production consumed" value={String(productionConsumed)} />
        <StatusMetric label="Adapter-visible" value={numberValue(status.adapterVisibleCount)} />
        <StatusMetric label="Blocked records" value={numberValue(status.blockedCount)} />
        <StatusMetric label="Planner-calculable" value={plannerCalculableCount} />
        <StatusMetric label="Stable-calculable" value={stableCalculableCount} />
        <StatusMetric label="Value normalization" value={valueNormalizationStatus} />
        <StatusMetric label="Skill identity bridge" value={skillIdentityBridgeStatus} />
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <div className="rounded border border-[#2a3050] bg-[#0f172a] p-3">
          <h3 className="text-sm font-semibold text-gray-100">Top blocked reasons</h3>
          <p className="mt-2 break-words font-mono text-xs text-gray-300">
            {summarizeReasons(status.topBlockedReasons)}
          </p>
        </div>
        <div className="rounded border border-[#2a3050] bg-[#0f172a] p-3">
          <h3 className="text-sm font-semibold text-gray-100">Baseline readiness</h3>
          <p className="mt-2 text-xs text-gray-300">
            Safe non-mechanical fixtures:{" "}
            <span className="font-mono text-gray-100">{numberValue(status.safeNowBaselineFixtureCount)}</span>
          </p>
          <p className="mt-1 text-xs text-gray-300">
            Blocked mechanical fixtures:{" "}
            <span className="font-mono text-gray-100">{numberValue(status.blockedBaselineFixtureCount)}</span>
          </p>
        </div>
      </div>

      <div className="mt-4">
        <V2LimitationNotice
          codes={[
            "audit_only_value_normalization",
            "not_planner_calculable",
            "stable_calculable_unavailable",
            "production_not_consuming_v2",
            "unresolved_skill_identity",
          ]}
          mode="full"
        />
      </div>

      <p className="mt-3 text-xs text-gray-500">
        v3 mechanical intelligence is required before adapter-visible records can become production calculation inputs.
      </p>
    </section>
  );
}

function StatusMetric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded border border-[#2a3050] bg-[#0f172a] p-3">
      <div className="text-xs uppercase text-gray-500">{label}</div>
      <div className="mt-2 break-words font-mono text-base text-gray-100">{value}</div>
    </div>
  );
}

function summarizeReasons(reasons: Record<string, unknown> | undefined): string {
  if (!reasons || !Object.keys(reasons).length) return "No blocked reason summary available.";
  return Object.entries(reasons)
    .slice(0, 5)
    .map(([reason, count]) => `${reason}: ${String(count)}`)
    .join(", ");
}

function numberValue(value: unknown): number {
  return typeof value === "number" ? value : 0;
}
