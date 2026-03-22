/**
 * Electron preload script — safe context bridge between renderer and main.
 *
 * Only explicitly listed APIs are exposed. No full Node.js access in renderer.
 */

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  /** Returns the app version string from package.json. */
  getVersion: () => ipcRenderer.invoke("app:version"),

  /** Gracefully quits the application. */
  quit: () => ipcRenderer.invoke("app:quit"),

  /** True when running inside Electron (vs browser). */
  isElectron: true,
});
