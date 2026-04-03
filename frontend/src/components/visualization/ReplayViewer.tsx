/**
 * N13 — Replay Viewer
 *
 * SVG-based frame-by-frame replay player. Entities render as circles
 * (green = alive, red = dead), projectiles as small amber diamonds.
 * Includes play/pause, prev/next, speed control, and a scrubber.
 */

import { useState, useEffect, useRef } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ReplayEntity {
  entity_id: string;
  position: [number, number];
  health: number;
  is_alive: boolean;
}

export interface ReplayProjectile {
  projectile_id: string;
  position: [number, number];
  direction: [number, number];
}

export interface ReplayFrame {
  frame_index: number;
  time: number;
  entities: ReplayEntity[];
  projectiles: ReplayProjectile[];
  events: unknown[];
}

export interface ReplayViewerProps {
  frames: ReplayFrame[];
  tickSize?: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CANVAS = 500;
const SPEEDS = [0.5, 1, 2] as const;
type Speed = (typeof SPEEDS)[number];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Maps a diamond shape centred at (cx, cy) with half-size s. */
function diamondPoints(cx: number, cy: number, s: number): string {
  return `${cx},${cy - s} ${cx + s},${cy} ${cx},${cy + s} ${cx - s},${cy}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ReplayViewer({ frames, tickSize = 0.5 }: ReplayViewerProps) {
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [isPlaying, setIsPlaying]                 = useState(false);
  const [playSpeed, setPlaySpeed]                 = useState<Speed>(1);
  const intervalRef                               = useRef<ReturnType<typeof setInterval> | null>(null);

  // Playback interval
  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (!isPlaying || frames.length === 0) return;

    const ms = (tickSize / playSpeed) * 1000;
    intervalRef.current = setInterval(() => {
      setCurrentFrameIndex((prev) => {
        const next = prev + 1;
        if (next >= frames.length) {
          setIsPlaying(false);
          return prev;
        }
        return next;
      });
    }, ms);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying, playSpeed, tickSize, frames.length]);

  if (frames.length === 0) {
    return (
      <div
        className="rounded border border-[#2a3050] bg-[#10152a] flex items-center justify-center"
        style={{ width: CANVAS, height: CANVAS + 80 }}
      >
        <span className="font-mono text-sm text-[#6b7280]">No replay data</span>
      </div>
    );
  }

  const frame = frames[currentFrameIndex];

  function handlePrev() {
    setCurrentFrameIndex((p) => Math.max(0, p - 1));
  }
  function handleNext() {
    setCurrentFrameIndex((p) => Math.min(frames.length - 1, p + 1));
  }
  function handlePlayPause() {
    if (currentFrameIndex >= frames.length - 1) {
      setCurrentFrameIndex(0);
    }
    setIsPlaying((p) => !p);
  }

  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4 inline-block">
      <p className="font-mono text-[11px] uppercase tracking-widest text-[#6b7280] mb-3">
        Replay Viewer
      </p>

      {/* SVG canvas */}
      <svg
        width={CANVAS}
        height={CANVAS}
        style={{ background: "#0d1124", display: "block", borderRadius: 4 }}
      >
        {/* Entities */}
        {frame.entities.map((e) => (
          <circle
            key={e.entity_id}
            cx={e.position[0]}
            cy={e.position[1]}
            r={10}
            fill={e.is_alive ? "#22c55e" : "#ef4444"}
            stroke={e.is_alive ? "#16a34a" : "#b91c1c"}
            strokeWidth={1.5}
            opacity={0.9}
          >
            <title>{`${e.entity_id} hp=${e.health}`}</title>
          </circle>
        ))}

        {/* Projectiles */}
        {frame.projectiles.map((p) => (
          <polygon
            key={p.projectile_id}
            points={diamondPoints(p.position[0], p.position[1], 5)}
            fill="#f5a623"
            stroke="#92400e"
            strokeWidth={1}
            opacity={0.85}
          />
        ))}
      </svg>

      {/* Controls */}
      <div className="mt-3 space-y-2">
        {/* Scrubber */}
        <input
          type="range"
          min={0}
          max={frames.length - 1}
          value={currentFrameIndex}
          onChange={(e) => {
            setIsPlaying(false);
            setCurrentFrameIndex(Number(e.target.value));
          }}
          className="w-full accent-amber-400"
          style={{ width: CANVAS }}
        />

        {/* Button row */}
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={handlePrev}
            disabled={currentFrameIndex === 0}
            className="px-3 py-1 rounded border border-[#2a3050] bg-[#0d1124] font-mono text-xs text-[#c8d0e0] disabled:opacity-40 hover:border-[#f5a623]/60"
          >
            ‹ Prev
          </button>

          <button
            onClick={handlePlayPause}
            className="px-4 py-1 rounded border border-[#f5a623]/60 bg-[#0d1124] font-mono text-xs text-[#f5a623] hover:bg-[#f5a623]/10"
          >
            {isPlaying ? "Pause" : "Play"}
          </button>

          <button
            onClick={handleNext}
            disabled={currentFrameIndex >= frames.length - 1}
            className="px-3 py-1 rounded border border-[#2a3050] bg-[#0d1124] font-mono text-xs text-[#c8d0e0] disabled:opacity-40 hover:border-[#f5a623]/60"
          >
            Next ›
          </button>

          {/* Speed selector */}
          <div className="flex items-center gap-1 ml-auto">
            <span className="font-mono text-[11px] text-[#6b7280]">Speed:</span>
            {SPEEDS.map((s) => (
              <button
                key={s}
                onClick={() => setPlaySpeed(s)}
                className={`px-2 py-0.5 rounded font-mono text-[11px] border ${
                  playSpeed === s
                    ? "border-[#f5a623] text-[#f5a623] bg-[#f5a623]/10"
                    : "border-[#2a3050] text-[#6b7280]"
                }`}
              >
                {s}x
              </button>
            ))}
          </div>

          {/* Time display */}
          <span className="font-mono text-xs text-[#c8d0e0]">
            t = {frame.time.toFixed(1)}s
          </span>
        </div>
      </div>
    </div>
  );
}
