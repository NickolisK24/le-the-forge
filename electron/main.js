/**
 * Electron main process — The Forge desktop app.
 *
 * Development mode:  loads http://localhost:5173 (Vite dev server).
 * Production mode:   serves the built frontend from ../frontend/dist,
 *                    and spawns the bundled Flask backend executable.
 *
 * Backend lifecycle:
 *   - In dev: assumes `npm run dev:backend` is already running on port 5050.
 *   - In production: spawns `backend/forge-backend` (PyInstaller bundle) or
 *     falls back to the system Python + wsgi.py.
 */

const { app, BrowserWindow, ipcMain, shell } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");

const isDev = !app.isPackaged;
const BACKEND_PORT = 5050;
const FRONTEND_PORT = 5173;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

let mainWindow = null;
let backendProcess = null;

// ---------------------------------------------------------------------------
// Backend management
// ---------------------------------------------------------------------------

function resolveBackendCommand() {
  const root = isDev
    ? path.join(__dirname, "..")
    : path.join(process.resourcesPath, "backend");

  // Prefer a PyInstaller bundle if it exists
  const bundlePath = path.join(root, "backend", "forge-backend");
  const bundlePathWin = path.join(root, "backend", "forge-backend.exe");
  const fs = require("fs");

  if (!isDev) {
    if (process.platform === "win32" && fs.existsSync(bundlePathWin)) {
      return { cmd: bundlePathWin, args: [], cwd: root };
    }
    if (fs.existsSync(bundlePath)) {
      return { cmd: bundlePath, args: [], cwd: root };
    }
  }

  // Fall back to Python in the virtual environment (dev) or system Python
  const venvPython = isDev
    ? path.join(root, ".venv", "bin", "python")
    : "python3";
  const wsgi = isDev
    ? path.join(root, "backend", "wsgi.py")
    : path.join(root, "backend", "wsgi.py");

  return {
    cmd: venvPython,
    args: ["-m", "flask", "run", "--port", String(BACKEND_PORT), "--no-debugger"],
    cwd: path.join(root, "backend"),
    env: {
      ...process.env,
      FLASK_APP: "wsgi.py",
      FLASK_ENV: isDev ? "development" : "production",
      PYTHONPATH: path.join(root, "backend"),
    },
  };
}

function startBackend() {
  if (isDev) {
    console.log("[Electron] Dev mode — assuming backend already running on :5050");
    return;
  }

  const { cmd, args, cwd, env } = resolveBackendCommand();
  console.log("[Electron] Starting backend:", cmd, args.join(" "));

  backendProcess = spawn(cmd, args, {
    cwd,
    env: env ?? process.env,
    stdio: "pipe",
    detached: false,
  });

  backendProcess.stdout.on("data", (d) => process.stdout.write(`[backend] ${d}`));
  backendProcess.stderr.on("data", (d) => process.stderr.write(`[backend] ${d}`));

  backendProcess.on("exit", (code) => {
    console.log(`[Electron] Backend exited with code ${code}`);
    backendProcess = null;
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log("[Electron] Stopping backend...");
    backendProcess.kill("SIGTERM");
    backendProcess = null;
  }
}

// ---------------------------------------------------------------------------
// Wait for backend to become ready
// ---------------------------------------------------------------------------

function waitForBackend(timeout = 30_000) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const check = () => {
      http
        .get(`${BACKEND_URL}/api/health`, (res) => {
          if (res.statusCode === 200) resolve();
          else retry();
        })
        .on("error", retry);
    };
    const retry = () => {
      if (Date.now() - start > timeout) {
        reject(new Error("Backend did not start in time"));
      } else {
        setTimeout(check, 500);
      }
    };
    check();
  });
}

// ---------------------------------------------------------------------------
// Window creation
// ---------------------------------------------------------------------------

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    title: "The Forge — Last Epoch Crafting Simulator",
    backgroundColor: "#0d0d0f",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
    // macOS: hide traffic lights until content loads
    show: false,
    titleBarStyle: process.platform === "darwin" ? "hiddenInset" : "default",
  });

  const url = isDev
    ? `http://localhost:${FRONTEND_PORT}`
    : `file://${path.join(__dirname, "..", "frontend", "dist", "index.html")}`;

  mainWindow.loadURL(url);

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    if (isDev) mainWindow.webContents.openDevTools({ mode: "detach" });
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  // Open external links in the system browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http")) shell.openExternal(url);
    return { action: "deny" };
  });
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.whenReady().then(async () => {
  startBackend();

  if (!isDev) {
    try {
      await waitForBackend();
    } catch (err) {
      console.error("[Electron] Backend failed to start:", err.message);
    }
  }

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  stopBackend();
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", stopBackend);

// ---------------------------------------------------------------------------
// IPC — renderer can request app version / quit
// ---------------------------------------------------------------------------

ipcMain.handle("app:version", () => app.getVersion());
ipcMain.handle("app:quit", () => app.quit());
