/**
 * UI18 — Error Reporting Panel
 * Displays missing data warnings and validation errors.
 */

import { useState } from "react";
import { Panel, Button, Badge } from "@/components/ui";

export interface ValidationError {
  id: string;
  severity: "error" | "warning" | "info";
  source: string;
  message: string;
  field?: string;
  recordId?: string;
}

interface ErrorReportingPanelProps {
  errors?: ValidationError[];
  onDismiss?: (id: string) => void;
  onDismissAll?: () => void;
}

const SEVERITY_STYLES: Record<ValidationError["severity"], string> = {
  error:   "border-l-2 border-l-forge-red bg-forge-red/5",
  warning: "border-l-2 border-l-forge-amber bg-forge-amber/5",
  info:    "border-l-2 border-l-forge-cyan bg-forge-cyan/5",
};

const SEVERITY_BADGE: Record<ValidationError["severity"], string> = {
  error:   "bg-forge-red/20 text-forge-red",
  warning: "bg-forge-amber/20 text-forge-amber",
  info:    "bg-forge-cyan/20 text-forge-cyan",
};

const MOCK_ERRORS: ValidationError[] = [
  {
    id: "e1",
    severity: "warning",
    source: "Unique Items",
    message: "48 items missing level_req field",
    field: "level_req",
  },
  {
    id: "e2",
    severity: "warning",
    source: "Skills",
    message: "~25 Mage skills missing from skills_metadata.json",
    field: "class",
  },
  {
    id: "e3",
    severity: "info",
    source: "Passives",
    message: "All 534 nodes have descriptions populated",
  },
];

export function ErrorReportingPanel({
  errors: externalErrors,
  onDismiss,
  onDismissAll,
}: ErrorReportingPanelProps) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<"all" | "error" | "warning" | "info">("all");

  const allErrors = externalErrors ?? MOCK_ERRORS;
  const visible = allErrors.filter(
    (e) => !dismissed.has(e.id) && (filter === "all" || e.severity === filter)
  );

  function dismiss(id: string) {
    setDismissed((d) => new Set([...d, id]));
    onDismiss?.(id);
  }

  function dismissAll() {
    setDismissed(new Set(allErrors.map((e) => e.id)));
    onDismissAll?.();
  }

  const counts = allErrors.reduce(
    (acc, e) => {
      if (!dismissed.has(e.id)) acc[e.severity]++;
      return acc;
    },
    { error: 0, warning: 0, info: 0 }
  );

  return (
    <Panel
      title="Validation Report"
      action={
        <Button variant="ghost" size="sm" onClick={dismissAll}>
          Dismiss All
        </Button>
      }
    >
      {/* Filter tabs */}
      <div className="flex gap-2 mb-3">
        {(["all", "error", "warning", "info"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`font-mono text-xs uppercase tracking-wider px-2 py-1 rounded-sm border transition-colors ${
              filter === f
                ? "border-forge-cyan/40 bg-forge-cyan/10 text-forge-cyan"
                : "border-forge-border text-forge-muted hover:border-forge-border-hot hover:text-forge-text"
            }`}
          >
            {f === "all" ? "All" : f}
            {f !== "all" && counts[f] > 0 && (
              <span className="ml-1 opacity-70">({counts[f]})</span>
            )}
          </button>
        ))}
      </div>

      {/* Error list */}
      {visible.length === 0 ? (
        <div className="text-center py-8 text-forge-muted font-mono text-xs">
          {dismissed.size > 0 ? "All issues dismissed." : "No issues found. All data is valid."}
        </div>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {visible.map((err) => (
            <div
              key={err.id}
              className={`rounded p-3 flex items-start justify-between gap-3 ${SEVERITY_STYLES[err.severity]}`}
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`font-mono text-xs px-1.5 py-0.5 rounded ${SEVERITY_BADGE[err.severity]}`}>
                    {err.severity.toUpperCase()}
                  </span>
                  <span className="font-mono text-xs text-forge-muted">{err.source}</span>
                  {err.field && (
                    <span className="font-mono text-xs text-forge-dim">· {err.field}</span>
                  )}
                </div>
                <p className="font-mono text-xs text-forge-text">{err.message}</p>
                {err.recordId && (
                  <p className="font-mono text-xs text-forge-dim mt-0.5">ID: {err.recordId}</p>
                )}
              </div>
              <button
                onClick={() => dismiss(err.id)}
                className="shrink-0 text-forge-dim hover:text-forge-muted transition-colors font-mono text-xs"
                aria-label="Dismiss"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}
