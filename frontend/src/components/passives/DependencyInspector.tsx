/**
 * DependencyInspector — debug panel that explains node dependency state.
 *
 * Shows on shift-hover: why a node is locked, available, or can't be removed.
 * Rendered as a floating panel near the cursor.
 */

import type { DependencyReport } from "@/logic/analyzeNodeDependencies";

interface Props {
  report: DependencyReport | null;
  screenX: number;
  screenY: number;
  containerRect: DOMRect | null;
}

export default function DependencyInspector({ report, screenX, screenY, containerRect }: Props) {
  if (!report || !containerRect) return null;

  const tx = screenX - containerRect.left + 16;
  const ty = screenY - containerRect.top - 12;

  return (
    <div
      className="pointer-events-none absolute z-30 w-72 rounded border border-forge-amber/30 bg-forge-bg/98 p-3 shadow-2xl"
      style={{ left: Math.min(tx, containerRect.width - 288), top: Math.max(4, ty) }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="font-display text-sm font-bold text-forge-amber">{report.nodeName}</span>
        <span className="font-mono text-[10px] text-forge-dim">{report.nodeId}</span>
      </div>

      {/* Status */}
      <div className={`rounded px-2 py-1 mb-2 font-mono text-xs ${
        report.isAllocated
          ? report.canRemove ? "bg-green-500/15 text-green-400" : "bg-red-500/15 text-red-400"
          : report.tierRequirementMet && (report.isTierRoot || report.allocatedParents.length > 0)
            ? "bg-green-500/15 text-green-400"
            : "bg-yellow-500/15 text-yellow-400"
      }`}>
        {report.reason}
      </div>

      {/* Details grid */}
      <div className="space-y-1.5 font-mono text-[10px]">
        <Row label="Allocated" value={report.isAllocated ? "Yes" : "No"} />
        <Row label="Reachable" value={report.reachableFromStart ? "Yes" : "No"} warn={!report.reachableFromStart} />
        <Row label="Tier Root" value={report.isTierRoot ? "Yes" : "No"} />
        <Row
          label="Tier Req"
          value={`${report.tierPoints.current} / ${report.tierPoints.required}`}
          warn={!report.tierRequirementMet}
        />

        {report.parentIds.length > 0 && (
          <Row
            label="Parents"
            value={`${report.allocatedParents.length}/${report.parentIds.length} allocated`}
            detail={report.parentIds.join(", ")}
          />
        )}

        {report.missingParents.length > 0 && (
          <Row
            label="Missing"
            value={report.missingParents.join(", ")}
            warn
          />
        )}

        {report.childIds.length > 0 && (
          <Row
            label="Children"
            value={`${report.childIds.length} total, ${report.blockingChildren.length} blocking`}
          />
        )}

        {report.blockingChildren.length > 0 && (
          <Row
            label="Blocking"
            value={report.blockingChildren.join(", ")}
            warn
          />
        )}

        {report.isAllocated && (
          <Row
            label="Can Remove"
            value={report.canRemove ? "Yes" : "No — would orphan nodes"}
            warn={!report.canRemove}
          />
        )}
      </div>
    </div>
  );
}

function Row({ label, value, detail, warn }: {
  label: string;
  value: string;
  detail?: string;
  warn?: boolean;
}) {
  return (
    <div className="flex justify-between gap-2">
      <span className="text-forge-dim">{label}</span>
      <span className={warn ? "text-red-400" : "text-forge-muted"} title={detail}>
        {value}
      </span>
    </div>
  );
}
