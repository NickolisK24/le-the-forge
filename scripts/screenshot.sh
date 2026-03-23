#!/bin/bash
# Screenshot helper for The Forge.
# Captures screenshots of the running Electron / browser app using macOS screencapture.
# Usage: ./scripts/screenshot.sh [output_dir]
#
# Prerequisites:
#   - The Forge must be running (`npm run dev:desktop` or just frontend at :5173)
#   - Run from project root
#   - macOS only (uses screencapture + osascript)

set -e

OUTPUT_DIR="${1:-docs/screenshots}"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "📸 The Forge Screenshot Capture"
echo "   Output: $OUTPUT_DIR"
echo ""

# Check if the app is reachable
if ! curl -sf http://localhost:5173 > /dev/null 2>&1; then
  echo "⚠️  Frontend not detected at http://localhost:5173"
  echo "   Start the app first: npm run dev:desktop"
  exit 1
fi

echo "✅ App detected at http://localhost:5173"
echo ""

# Use osascript to find and focus the Electron or browser window
echo "🔍 Looking for Forge window..."

# Try to find Electron window
WINDOW_FOUND=false

if osascript -e 'tell application "Electron" to activate' 2>/dev/null; then
  WINDOW_FOUND=true
  APP_NAME="Electron"
elif osascript -e 'tell application "Google Chrome" to activate' 2>/dev/null; then
  WINDOW_FOUND=true
  APP_NAME="Chrome"
elif osascript -e 'tell application "Safari" to activate' 2>/dev/null; then
  WINDOW_FOUND=true
  APP_NAME="Safari"
fi

if [ "$WINDOW_FOUND" = false ]; then
  echo "⚠️  Could not find a running window. Taking full screen capture instead."
fi

sleep 1

capture_page() {
  local name="$1"
  local url="$2"
  local file="$OUTPUT_DIR/${TIMESTAMP}_${name}.png"

  echo "  📷 Capturing: $name → $file"

  if [ "$WINDOW_FOUND" = true ] && [ -n "$url" ]; then
    # Open the URL in the app if possible
    open "$url" 2>/dev/null || true
    sleep 2
  fi

  # Capture the focused window
  screencapture -x -o -w "$file" 2>/dev/null || screencapture -x "$file"
  echo "     ✅ Saved: $file"
}

echo ""
echo "📸 Capturing pages..."
echo "   (You may need to interact with the app between captures)"
echo ""

# Capture each main page
capture_page "01_home"       "http://localhost:5173/"
capture_page "02_builds"     "http://localhost:5173/builds"
capture_page "03_build_new"  "http://localhost:5173/build"
capture_page "04_craft"      "http://localhost:5173/craft"
capture_page "05_compare"    "http://localhost:5173/compare"

echo ""
echo "✅ Done! Screenshots saved to: $OUTPUT_DIR"
echo ""
echo "📝 Next steps:"
echo "   1. Review screenshots in $OUTPUT_DIR"
echo "   2. Optimize with: sips -Z 1920 $OUTPUT_DIR/*.png"
echo "   3. Convert to WebP: for f in $OUTPUT_DIR/*.png; do ffmpeg -i \"\$f\" \"\${f%.png}.webp\"; done"
echo "   4. Add to README.md with relative links"
