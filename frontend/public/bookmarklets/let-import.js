/**
 * The Forge — Last Epoch Tools import bookmarklet
 *
 * Drop-in bookmarklet that runs on a Last Epoch Tools planner page
 * (lastepochtools.com/planner/...), reads window.buildInfo, and copies
 * the JSON payload to the clipboard. Paste the result into The Forge's
 * build import modal ({} JSON tab) to bring the build across.
 *
 * Necessary because LET moved to client-side rendering — the server
 * cannot fetch window.buildInfo any more, so it has to be captured in
 * the browser.
 *
 * To regenerate the minified bookmarklet string in let-import.bookmarklet.txt,
 * paste this file into any JS minifier, prefix with `javascript:`, and
 * single-line it.
 */
(async () => {
  try {
    const bi = window.buildInfo;
    if (!bi || typeof bi !== "object") {
      alert(
        "The Forge: window.buildInfo not found on this page. " +
        "Open a Last Epoch Tools planner and run the bookmarklet there."
      );
      return;
    }
    const json = JSON.stringify(bi);
    await navigator.clipboard.writeText(json);

    const toast = document.createElement("div");
    toast.textContent = "\u2713 Build JSON copied \u2014 paste into The Forge";
    Object.assign(toast.style, {
      position: "fixed",
      top: "16px",
      right: "16px",
      zIndex: "2147483647",
      background: "#1a1410",
      color: "#e8c87a",
      border: "1px solid #8b6a3a",
      padding: "10px 16px",
      fontFamily: "monospace",
      fontSize: "13px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
      borderRadius: "4px",
    });
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2800);
  } catch (e) {
    alert("The Forge bookmarklet failed: " + (e && e.message ? e.message : e));
  }
})();
