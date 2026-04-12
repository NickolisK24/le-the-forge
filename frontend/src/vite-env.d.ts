/// <reference types="vite/client" />

// Injected at build time by vite.config.ts `define` from the project-root
// VERSION file. Available synchronously in the client bundle.
declare const __APP_VERSION__: string;
