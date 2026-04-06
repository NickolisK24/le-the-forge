/**
 * TreeIcon — renders a game asset icon for passive/skill tree nodes.
 *
 * Uses local PNG files from /assets/passive-icons/ when available.
 * Falls back to a colored abbreviation placeholder when no local file exists.
 *
 * Icons are rendered inside SVG foreignObject with explicit centering
 * to handle varying PNG source sizes (54px–334px) consistently.
 */

import { useMemo } from "react";

import iconSpriteMap from "@/data/iconSpriteMap.json";

const LOCAL_ICONS: Set<string> = new Set(
  Object.keys(iconSpriteMap as Record<string, unknown>).filter((k) =>
    k.startsWith("a-r-"),
  ),
);

interface TreeIconProps {
  /** Icon asset ID, e.g. "a-r-292" */
  iconId: string | null | undefined;
  /** Display size in pixels */
  size: number;
  /** Node name for generating placeholder text */
  nodeName?: string;
}

/**
 * SVG foreignObject icon for use inside tree renderers.
 *
 * The foreignObject is positioned at (-size/2, -size/2) relative to the
 * parent <g> transform origin, centering it exactly on the node coordinate.
 * The inner container uses flexbox centering to handle any PNG aspect ratio.
 */
export default function TreeIcon({ iconId, size, nodeName }: TreeIconProps) {
  if (!iconId) return null;

  const hasLocal = LOCAL_ICONS.has(iconId);

  const abbr = useMemo(() => {
    if (!nodeName) return "?";
    const words = nodeName.split(/\s+/).filter(Boolean);
    if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
    return nodeName.slice(0, 2).toUpperCase();
  }, [nodeName]);

  if (hasLocal) {
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
            width: size,
            height: size,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            overflow: "hidden",
            borderRadius: "50%",
          }}
        >
          <img
            src={`/assets/passive-icons/${iconId}.png`}
            alt=""
            width={size}
            height={size}
            style={{
              objectFit: "contain",
              display: "block",
              imageRendering: "auto",
            }}
            loading="lazy"
          />
        </div>
      </foreignObject>
    );
  }

  // Fallback: colored circle with text abbreviation
  return (
    <g pointerEvents="none">
      <circle r={size / 2 - 1} fill="#1a2040" stroke="#3a4070" strokeWidth={0.5} />
      <text
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={size * 0.35}
        fill="#8890b8"
        fontFamily="monospace"
        fontWeight="bold"
      >
        {abbr}
      </text>
    </g>
  );
}

/**
 * Standalone HTML icon (not in SVG context) for use in tooltips/lists.
 */
export function TreeIconHtml({ iconId, size, nodeName }: TreeIconProps) {
  if (!iconId) return null;

  const hasLocal = LOCAL_ICONS.has(iconId);

  if (hasLocal) {
    return (
      <img
        src={`/assets/passive-icons/${iconId}.png`}
        alt={nodeName ?? ""}
        width={size}
        height={size}
        style={{ borderRadius: "50%", objectFit: "contain" }}
        loading="lazy"
      />
    );
  }

  const abbr = nodeName
    ? nodeName.split(/\s+/).filter(Boolean).map((w) => w[0]).join("").slice(0, 2).toUpperCase()
    : "?";

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
      }}
    >
      {abbr}
    </span>
  );
}
