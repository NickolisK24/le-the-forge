/**
 * UI15 — Simulation Timeline
 *
 * Combat events timeline display with:
 *   - Horizontal timeline bar with event markers
 *   - Scrollable event list below
 *   - Click handler for individual events
 */

import { EmptyState } from "@/components/ui";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CombatEvent {
  time: number; // seconds
  type: "damage" | "ability" | "death" | "buff" | "debuff";
  label: string;
  value?: number;
  targetId?: string;
}

export interface SimulationTimelineProps {
  events?: CombatEvent[];
  duration?: number;
  onEventSelect?: (event: CombatEvent) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function eventColor(type: CombatEvent["type"]): string {
  switch (type) {
    case "damage":  return "#ef4444"; // forge-red
    case "ability": return "#f5a623"; // forge-amber
    case "death":   return "#dc2626"; // dark red
    case "buff":    return "#4ade80"; // forge-green
    case "debuff":  return "#8b5cf6"; // purple
    default:        return "#8090b0";
  }
}

function eventBadgeClass(type: CombatEvent["type"]): string {
  switch (type) {
    case "damage":  return "text-forge-red border-forge-red/40 bg-forge-red/8";
    case "ability": return "text-forge-amber border-forge-amber/40 bg-forge-amber/8";
    case "death":   return "text-red-300 border-red-400/40 bg-red-400/10";
    case "buff":    return "text-forge-green border-forge-green/40 bg-forge-green/12";
    case "debuff":  return "text-purple-400 border-purple-400/40 bg-purple-400/10";
    default:        return "text-forge-muted border-forge-border";
  }
}

function formatTime(t: number): string {
  const m = Math.floor(t / 60);
  const s = (t % 60).toFixed(1);
  return m > 0 ? `${m}:${s.padStart(4, "0")}` : `${s}s`;
}

// ---------------------------------------------------------------------------
// Timeline bar with markers
// ---------------------------------------------------------------------------

function TimelineBar({
  events,
  duration,
  onEventSelect,
}: {
  events: CombatEvent[];
  duration: number;
  onEventSelect?: (e: CombatEvent) => void;
}) {
  return (
    <div className="relative h-8 rounded bg-forge-surface2 border border-forge-border overflow-hidden">
      {/* Track */}
      <div className="absolute inset-0 flex items-center px-2">
        <div className="w-full h-1 rounded-full bg-forge-border" />
      </div>

      {/* Event markers */}
      {events.map((event, idx) => {
        const pct = duration > 0 ? (event.time / duration) * 100 : 0;
        const isDeath = event.type === "death";
        return (
          <button
            key={idx}
            type="button"
            onClick={() => onEventSelect?.(event)}
            title={`${event.label} @ ${formatTime(event.time)}`}
            className="absolute top-1/2 -translate-x-1/2 -translate-y-1/2 transition-transform hover:scale-125 cursor-pointer"
            style={{ left: `${pct}%` }}
          >
            <div
              className="rounded-full border border-white/20"
              style={{
                width: isDeath ? 10 : 6,
                height: isDeath ? 10 : 6,
                background: eventColor(event.type),
              }}
            />
          </button>
        );
      })}

      {/* Duration labels */}
      <div className="absolute bottom-0.5 left-2 font-mono text-[9px] text-forge-dim">0s</div>
      <div className="absolute bottom-0.5 right-2 font-mono text-[9px] text-forge-dim">
        {formatTime(duration)}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Event list row
// ---------------------------------------------------------------------------

function EventRow({
  event,
  onSelect,
}: {
  event: CombatEvent;
  onSelect?: (e: CombatEvent) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(event)}
      className="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-forge-surface2 transition-colors text-left"
    >
      {/* Time */}
      <span className="font-mono text-[11px] text-forge-dim w-12 flex-shrink-0 text-right">
        {formatTime(event.time)}
      </span>

      {/* Type badge */}
      <span
        className={[
          "inline-block font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-sm border flex-shrink-0",
          eventBadgeClass(event.type),
        ].join(" ")}
      >
        {event.type}
      </span>

      {/* Label */}
      <span className="font-body text-sm text-forge-text flex-1 truncate">{event.label}</span>

      {/* Value */}
      {event.value !== undefined && (
        <span className="font-mono text-xs text-forge-amber flex-shrink-0">
          {event.value.toLocaleString()}
        </span>
      )}

      {/* Target */}
      {event.targetId && (
        <span className="font-mono text-[10px] text-forge-dim flex-shrink-0">
          → {event.targetId}
        </span>
      )}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SimulationTimeline({
  events = [],
  duration = 60,
  onEventSelect,
}: SimulationTimelineProps) {
  if (events.length === 0) {
    return (
      <EmptyState
        title="No events"
        description="Run a simulation to populate the combat timeline."
      />
    );
  }

  // Sort events by time
  const sorted = [...events].sort((a, b) => a.time - b.time);

  return (
    <div className="flex flex-col gap-4">
      {/* Horizontal timeline bar */}
      <div>
        <div className="font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-2">
          Timeline · {events.length} events · {formatTime(duration)} total
        </div>
        <TimelineBar events={sorted} duration={duration} onEventSelect={onEventSelect} />
      </div>

      {/* Scrollable event list */}
      <div className="rounded border border-forge-border bg-forge-surface overflow-hidden">
        <div className="flex items-center justify-between px-3 py-2 border-b border-forge-border bg-forge-surface2">
          <span className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan">
            Events
          </span>
          <span className="font-mono text-[11px] text-forge-dim">{events.length} total</span>
        </div>
        <div className="overflow-y-auto max-h-64 py-1">
          {sorted.map((event, idx) => (
            <EventRow key={idx} event={event} onSelect={onEventSelect} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default SimulationTimeline;
