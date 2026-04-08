/**
 * atlasConfig — Passive/skill icon sprite atlas metadata.
 *
 * The atlas contains all a-r-* node icons for passive and skill trees.
 * Sprite coordinates are in iconSpriteMap.json as { [iconId]: [x, y] }.
 *
 * Dimensions verified from WebP binary header (VP8X chunk).
 * Icon size verified from coordinate bounds:
 *   max x (2322) + ICON_SIZE (65) = ATLAS_WIDTH (2387) ✓
 *   max y (2338) + ICON_SIZE (65) = ATLAS_HEIGHT (2403) ✓
 */

export const ATLAS_PATH = "/assets/planner_skill_passive_icons_v142.webp";

/** Width of the full sprite atlas in pixels. */
export const ATLAS_WIDTH = 2387;

/** Height of the full sprite atlas in pixels. */
export const ATLAS_HEIGHT = 2403;

/** Width and height of each individual icon cell in the atlas. */
export const ICON_SIZE = 65;

/**
 * Compute CSS background properties to render a single sprite at a given
 * display size, scaling the atlas proportionally.
 *
 * @param x         Sprite x-origin in the atlas (from iconSpriteMap)
 * @param y         Sprite y-origin in the atlas (from iconSpriteMap)
 * @param displaySize  Target render size in pixels (width = height)
 */
export function spriteStyle(
  x: number,
  y: number,
  displaySize: number,
): React.CSSProperties {
  const scale = displaySize / ICON_SIZE;
  return {
    backgroundImage: `url('${ATLAS_PATH}')`,
    backgroundRepeat: "no-repeat",
    backgroundSize: `${ATLAS_WIDTH * scale}px ${ATLAS_HEIGHT * scale}px`,
    backgroundPosition: `${-x * scale}px ${-y * scale}px`,
    width: displaySize,
    height: displaySize,
  };
}
