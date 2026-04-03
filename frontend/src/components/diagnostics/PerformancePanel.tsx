/**
 * UI+14 — Performance Diagnostics Panel
 * Display execution time, search depth, and memory usage.
 */

import React, { useState, useEffect, useRef } from "react";

export interface PerformanceMetric {
  label: string;
  value: number;
  unit: "ms" | "MB" | "ops" | "depth" | "%";
  good?: number;    // threshold below which is good
  warn?: number;    // threshold above which is warning
  description?: string;
}

export interface PerformanceSnapshot {
  metrics: PerformanceMetric[];
  capturedAt: number;
}

interface PerformancePanelProps {
  metrics?: PerformanceMetric[];
  /** Auto-refresh interval in ms. 0 = no auto-refresh. */
  refreshInterval?: number;
  className?: string;
  collapsed?: boolean;
}

function getStatusColor(metric: PerformanceMetric): string {
  if (metric.good !== undefined && metric.value <= metric.good) return "text-green-400";
  if (metric.warn !== undefined && metric.value >= metric.warn) return "text-red-400";
  if (metric.good !== undefined || metric.warn !== undefined) return "text-amber-400";
  return "text-gray-300";
}

function getBarColor(metric: PerformanceMetric): string {
  if (metric.good !== undefined && metric.value <= metric.good) return "bg-green-500";
  if (metric.warn !== undefined && metric.value >= metric.warn) return "bg-red-500";
  return "bg-amber-500";
}

function formatValue(metric: PerformanceMetric): string {
  const v = metric.value;
  switch (metric.unit) {
    case "ms":    return `${v < 1 ? v.toFixed(2) : v < 10 ? v.toFixed(1) : Math.round(v)}ms`;
    case "MB":    return `${v.toFixed(1)}MB`;
    case "%":     return `${Math.round(v)}%`;
    case "depth": return String(Math.round(v));
    case "ops":   return v >= 1000 ? `${(v / 1000).toFixed(1)}k ops` : `${Math.round(v)} ops`;
    default:      return String(v);
  }
}

function getBarWidth(metric: PerformanceMetric): number {
  const max = metric.warn ?? (metric.good ? metric.good * 2 : 100);
  return Math.min(100, (metric.value / max) * 100);
}

function collectBrowserMetrics(): PerformanceMetric[] {
  const metrics: PerformanceMetric[] = [];

  // Memory (Chrome only)
  const perf = performance as Performance & { memory?: { usedJSHeapSize: number; jsHeapSizeLimit: number } };
  if (perf.memory) {
    const usedMB = perf.memory.usedJSHeapSize / 1024 / 1024;
    const limitMB = perf.memory.jsHeapSizeLimit / 1024 / 1024;
    metrics.push({
      label: "JS Heap",
      value: Math.round(usedMB * 10) / 10,
      unit: "MB",
      good: limitMB * 0.4,
      warn: limitMB * 0.8,
      description: `${usedMB.toFixed(1)}MB of ${limitMB.toFixed(0)}MB limit`,
    });
  }

  // Navigation timing
  const nav = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
  if (nav) {
    metrics.push({
      label: "Page Load",
      value: Math.round(nav.loadEventEnd - nav.startTime),
      unit: "ms",
      good: 1000,
      warn: 3000,
    });
  }

  return metrics;
}

export function PerformancePanel({
  metrics: externalMetrics = [],
  refreshInterval = 0,
  className = "",
  collapsed: initialCollapsed = false,
}: PerformancePanelProps): React.JSX.Element {
  const [collapsed, setCollapsed] = useState(initialCollapsed);
  const [browserMetrics, setBrowserMetrics] = useState<PerformanceMetric[]>([]);
  const [lastRefresh, setLastRefresh] = useState(Date.now());
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = () => {
    setBrowserMetrics(collectBrowserMetrics());
    setLastRefresh(Date.now());
  };

  useEffect(() => {
    refresh();
    if (refreshInterval > 0) {
      intervalRef.current = setInterval(refresh, refreshInterval);
      return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    }
    return undefined;
  }, [refreshInterval]);

  const allMetrics = [...externalMetrics, ...browserMetrics];
  const worstMetric = allMetrics.find(
    (m) => m.warn !== undefined && m.value >= m.warn
  );

  return (
    <div
      className={`rounded-lg bg-[#0d1117] border ${
        worstMetric ? "border-red-500/50" : "border-[#2d3748]"
      } overflow-hidden ${className}`}
      role="region"
      aria-label="Performance Diagnostics"
    >
      {/* Header */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="w-full flex items-center justify-between px-4 py-3
                   bg-[#161b22] hover:bg-[#1c2230] transition-colors text-left"
        aria-expanded={!collapsed}
      >
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-[#f0a020] uppercase tracking-wider">
            Performance
          </span>
          {worstMetric && (
            <span className="text-[10px] text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded">
              ⚠ {worstMetric.label}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); refresh(); }}
            className="text-xs text-gray-500 hover:text-[#f0a020] transition-colors"
            aria-label="Refresh metrics"
          >
            ↻
          </button>
          <span className="text-gray-600">{collapsed ? "▾" : "▴"}</span>
        </div>
      </button>

      {/* Metrics Grid */}
      {!collapsed && (
        <div className="p-4 space-y-3">
          {allMetrics.length === 0 ? (
            <p className="text-xs text-gray-600 text-center py-2">No metrics available</p>
          ) : (
            allMetrics.map((metric, i) => (
              <div key={i} title={metric.description}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-500">{metric.label}</span>
                  <span className={`text-xs font-mono font-semibold ${getStatusColor(metric)}`}>
                    {formatValue(metric)}
                  </span>
                </div>
                <div className="h-1 bg-[#2d3748] rounded overflow-hidden">
                  <div
                    className={`h-full rounded transition-all duration-300 ${getBarColor(metric)}`}
                    style={{ width: `${getBarWidth(metric)}%` }}
                  />
                </div>
              </div>
            ))
          )}

          <div className="text-[10px] text-gray-700 text-right mt-2">
            Updated {new Date(lastRefresh).toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  );
}
