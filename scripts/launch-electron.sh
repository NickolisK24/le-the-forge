#!/bin/bash
# Launch Electron via macOS LaunchServices (open command).
# Clears ELECTRON_RUN_AS_NODE which VS Code sets to prevent child electron
# processes from hijacking its own process context.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ELECTRON_APP="$PROJECT_ROOT/node_modules/electron/dist/Electron.app"

if [ ! -d "$ELECTRON_APP" ]; then
  echo "[launch-electron] Electron.app not found at $ELECTRON_APP" >&2
  exit 1
fi

export ELECTRON_RUN_AS_NODE=
echo "[launch-electron] Launching $ELECTRON_APP with args: $PROJECT_ROOT"
"$ELECTRON_APP/Contents/MacOS/Electron" "$PROJECT_ROOT"
