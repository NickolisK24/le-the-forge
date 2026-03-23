# Screenshots

This directory holds screenshots and demo assets for The Forge.

## Capturing Screenshots

Use the capture script from the project root (macOS only):

```bash
# Start the app first
npm run dev:desktop

# In another terminal, run the capture script
./scripts/screenshot.sh
```

Screenshots are saved with a timestamp prefix: `YYYYMMDD_HHMMSS_<page>.png`

## Manual Capture

If the script doesn't work, manually navigate to each page and press:

- **macOS:** `Shift + Cmd + 4` → click the Electron window
- Or `Shift + Cmd + 3` for full screen

## Pages to Capture

| File | URL | Description |
|---|---|---|
| `home.png` | `/` | Landing page with CTA |
| `builds.png` | `/builds` | Community builds browser |
| `build_planner.png` | `/build` | New build planner |
| `build_view.png` | `/build/<slug>` | Saved build detail |
| `craft.png` | `/craft` | Craft simulator |
| `compare.png` | `/compare?a=<slug>&b=<slug>` | Build comparison |
| `profile.png` | `/profile` | User profile |

## Demo GIF

To create an animated demo GIF from screenshots:

```bash
# Install ffmpeg if needed: brew install ffmpeg
ffmpeg -framerate 0.5 -pattern_type glob -i 'docs/screenshots/*.png' \
  -vf "scale=1280:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 docs/demo.gif
```
