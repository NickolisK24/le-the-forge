/**
 * TreeIcon — renders a game asset icon for passive/skill tree nodes.
 *
 * Renders icons from the planner sprite atlas (planner_skill_passive_icons_v142.webp)
 * using CSS background-position for all a-r-* icon IDs. Returns null when
 * the icon ID is unknown, allowing the underlying node shape to show through.
 *
 * Icon coordinates are sourced from iconSpriteMap.json.
 * Atlas metadata (dimensions, icon cell size) lives in atlasConfig.ts.
 */

import type React from "react";
import iconSpriteMap from "@/data/iconSpriteMap.json";
import { spriteStyle } from "@/data/atlasConfig";

const spriteMapTyped = iconSpriteMap as unknown as Record<string, [number, number]>;

interface TreeIconProps {
  /** Icon asset ID, e.g. "a-r-292" */
  iconId: string | null | undefined;
  /** Display size in pixels */
  size: number;
  /** Node name for generating placeholder text */
  nodeName?: string;
}

function getAbbr(nodeName?: string): string {
  if (!nodeName) return "?";
  const words = nodeName.split(/\s+/).filter(Boolean);
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
  return nodeName.slice(0, 2).toUpperCase();
}

/**
 * SVG foreignObject icon for use inside tree renderers.
 */
export default function TreeIcon({ iconId, size }: TreeIconProps) {
  if (!iconId) return null;

  const coords = spriteMapTyped[iconId];

  if (coords) {
    const style = spriteStyle(coords[0], coords[1], size);
    return (
      <foreignObject
        x={-size / 2}
        y={-size / 2}
        width={size}
        height={size}
        pointerEvents="none"
      >
        <div
          style={{
            ...style,
            borderRadius: "50%",
            overflow: "hidden",
          }}
        />
      </foreignObject>
    );
  }

  // Icon not in sprite map — return null so the underlying node shape shows through.
  // The geometric shapes (hexagons/diamonds with radial gradients) already provide
  // clean type-differentiated visuals.
  return null;
}

/**
 * Standalone HTML icon (not in SVG context) for use in tooltips/lists.
 */
export function TreeIconHtml({ iconId, size, nodeName }: TreeIconProps) {
  if (!iconId) return null;

  const coords = spriteMapTyped[iconId];

  if (coords) {
    const style = spriteStyle(coords[0], coords[1], size);
    return (
      <div
        style={{
          ...style,
          borderRadius: "50%",
          overflow: "hidden",
          flexShrink: 0,
        }}
        aria-label={nodeName}
      />
    );
  }

  const abbr = getAbbr(nodeName);

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: size,
        height: size,
        borderRadius: "50%",
        background: "#1a2040",
        border: "1px solid #3a4070",
        fontSize: size * 0.35,
        fontFamily: "monospace",
        fontWeight: "bold",
        color: "#8890b8",
        flexShrink: 0,
      }}
    >
      {abbr}
    </span>
  );
}
