/**
 * UI4 — Build Workspace
 *
 * Route: /build-workspace
 *
 * Unified build workspace with 3-column layout:
 *   Left  (280px) — Skill configuration + passive tree summary
 *   Center (flex) — Equipment slots (gear grid)
 *   Right (280px) — Build summary stats
 */

import { Link } from "react-router-dom";
import { Panel, Button, EmptyState } from "@/components/ui";

// ---------------------------------------------------------------------------
// Gear slot data
// ---------------------------------------------------------------------------

const GEAR_SLOTS = [
  { id: "helm",    label: "Helm",    icon: "helm" },
  { id: "chest",   label: "Chest",   icon: "chest" },
  { id: "gloves",  label: "Gloves",  icon: "gloves" },
  { id: "boots",   label: "Boots",   icon: "boots" },
  { id: "belt",    label: "Belt",    icon: "belt" },
  { id: "ring1",   label: "Ring 1",  icon: "ring" },
  { id: "ring2",   label: "Ring 2",  icon: "ring" },
  { id: "amulet",  label: "Amulet",  icon: "amulet" },
  { id: "weapon",  label: "Weapon",  icon: "weapon" },
];

// ---------------------------------------------------------------------------
// Slot icons (inline SVG)
// ---------------------------------------------------------------------------

function SlotIcon({ type }: { type: string }) {
  switch (type) {
    case "helm":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 3C7 3 4 7 4 12v2h16v-2c0-5-3-9-8-9z" />
          <path d="M4 14h16" />
        </svg>
      );
    case "chest":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="6" width="16" height="14" rx="1" />
          <path d="M9 6V4h6v2" />
          <path d="M12 10v6M9 13h6" />
        </svg>
      );
    case "gloves":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M8 20V10l-2-3V5a1 1 0 012 0v3h1V4a1 1 0 012 0v4h1V5a1 1 0 012 0v3h1V6a1 1 0 012 0v8l-3 3v3" />
        </svg>
      );
    case "boots":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 18h12v2H6zM8 18V8l-2-2V4h8v10l4 4" />
        </svg>
      );
    case "belt":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="10" width="18" height="4" rx="1" />
          <rect x="10" y="9" width="4" height="6" rx="0.5" />
        </svg>
      );
    case "ring":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="12" r="5" />
          <circle cx="12" cy="12" r="2" />
        </svg>
      );
    case "amulet":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 3v4M9 7h6" />
          <polygon points="12,10 15,16 9,16" />
        </svg>
      );
    case "weapon":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 20L14 10M14 10l4-8-8 4z" />
          <path d="M7 17l-3 3" />
        </svg>
      );
    default:
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="4" y="4" width="16" height="16" rx="2" />
        </svg>
      );
  }
}

// ---------------------------------------------------------------------------
// Skill slot row
// ---------------------------------------------------------------------------

function SkillSlot({ index }: { index: number }) {
  return (
    <div className="flex items-center gap-3 rounded border border-forge-border bg-forge-surface2 px-3 py-2">
      <div className="w-6 h-6 rounded-full border border-forge-border bg-forge-bg flex items-center justify-center flex-shrink-0">
        <span className="font-mono text-[10px] text-forge-dim">{index + 1}</span>
      </div>
      <span className="font-body text-sm text-forge-dim italic">Empty Slot</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Gear slot card
// ---------------------------------------------------------------------------

function GearSlotCard({ slot }: { slot: typeof GEAR_SLOTS[number] }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded border border-forge-border bg-forge-surface2 p-3 h-24 hover:border-forge-amber/40 transition-colors cursor-pointer">
      <div className="text-forge-dim">
        <SlotIcon type={slot.icon} />
      </div>
      <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
        {slot.label}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function BuildWorkspace() {
  return (
    <div className="flex flex-col h-full min-h-0 p-4 gap-4">
      {/* Back link */}
      <div>
        <Link
          to="/builds"
          className="font-mono text-xs text-forge-cyan hover:text-forge-cyan/80 transition-colors uppercase tracking-widest"
        >
          ← Back to Builds
        </Link>
      </div>

      {/* 3-column workspace */}
      <div className="flex-1 grid gap-4 min-h-0" style={{ gridTemplateColumns: "280px 1fr 280px" }}>

        {/* Left: Skill Config */}
        <Panel title="Skill Config">
          <div className="flex flex-col gap-2">
            {Array.from({ length: 5 }, (_, i) => (
              <SkillSlot key={i} index={i} />
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-forge-border">
            <div className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan/70 mb-2">
              Passive Tree
            </div>
            <div className="rounded border border-forge-border bg-forge-surface2 px-3 py-3">
              <div className="font-body text-sm text-forge-dim">0 points allocated</div>
              <div className="mt-1 h-1.5 rounded-full bg-forge-border overflow-hidden">
                <div className="h-full w-0 rounded-full bg-forge-amber" />
              </div>
            </div>
          </div>
        </Panel>

        {/* Center: Equipment */}
        <Panel title="Equipment">
          <div className="grid grid-cols-3 gap-3">
            {GEAR_SLOTS.map((slot) => (
              <GearSlotCard key={slot.id} slot={slot} />
            ))}
          </div>
        </Panel>

        {/* Right: Build Summary */}
        <Panel title="Build Summary">
          <div className="flex flex-col gap-3">
            {[
              { label: "DPS", value: "--" },
              { label: "Survivability", value: "--" },
              { label: "Efficiency", value: "--" },
            ].map((stat) => (
              <div
                key={stat.label}
                className="flex items-center justify-between rounded border border-forge-border bg-forge-surface2 px-3 py-2.5"
              >
                <span className="font-mono text-xs uppercase tracking-widest text-forge-muted">
                  {stat.label}
                </span>
                <span className="font-mono text-sm text-forge-dim">{stat.value}</span>
              </div>
            ))}

            <div className="mt-4 pt-4 border-t border-forge-border">
              <EmptyState
                title="No build loaded"
                description="Configure skills and gear to see summary stats."
              />
            </div>
          </div>
        </Panel>
      </div>

      {/* Bottom bar */}
      <div className="flex items-center gap-3 pt-2 border-t border-forge-border shrink-0">
        <Button variant="primary">Simulate Build</Button>
        <Button variant="ghost">Export</Button>
      </div>
    </div>
  );
}
