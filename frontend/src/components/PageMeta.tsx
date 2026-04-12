/**
 * PageMeta — Lightweight per-page <title> and <meta> tag manager.
 *
 * Drop this into any page component to set the document title and description.
 * On unmount it restores the default title. No extra dependencies needed.
 *
 * Usage:
 *   <PageMeta title="Build Planner" description="Plan your Last Epoch build..." />
 */

import { useEffect } from "react";

const DEFAULT_TITLE = "The Forge — Last Epoch Community Hub";
const DEFAULT_DESCRIPTION =
  "Plan builds, simulate DPS and survivability, optimize gear, and explore the meta for Last Epoch.";
const SITE_URL = "https://epochforge.gg";

interface PageMetaProps {
  /** Page-specific title. Will be rendered as "title | The Forge" */
  title?: string;
  /** Page-specific description for search engines and social previews. */
  description?: string;
  /** Canonical path (e.g. "/builds"). Defaults to current location. */
  path?: string;
  /** Optional Open Graph image URL for social sharing. */
  ogImage?: string;
}

function setMetaTag(name: string, content: string, attribute = "name") {
  let el = document.querySelector(`meta[${attribute}="${name}"]`);
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attribute, name);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

export default function PageMeta({
  title,
  description,
  path,
  ogImage,
}: PageMetaProps) {
  useEffect(() => {
    // Document title
    const fullTitle = title ? `${title} | The Forge` : DEFAULT_TITLE;
    document.title = fullTitle;

    // Meta description
    const desc = description || DEFAULT_DESCRIPTION;
    setMetaTag("description", desc);

    // Open Graph
    setMetaTag("og:title", fullTitle, "property");
    setMetaTag("og:description", desc, "property");
    setMetaTag("og:type", "website", "property");
    setMetaTag("og:site_name", "The Forge", "property");

    const canonicalUrl = `${SITE_URL}${path || window.location.pathname}`;
    setMetaTag("og:url", canonicalUrl, "property");

    if (ogImage) {
      setMetaTag("og:image", ogImage, "property");
    }

    // Twitter Card
    setMetaTag("twitter:card", "summary_large_image");
    setMetaTag("twitter:title", fullTitle);
    setMetaTag("twitter:description", desc);
    if (ogImage) {
      setMetaTag("twitter:image", ogImage);
    }

    // Cleanup: restore defaults on unmount
    return () => {
      document.title = DEFAULT_TITLE;
      setMetaTag("description", DEFAULT_DESCRIPTION);
      setMetaTag("og:title", DEFAULT_TITLE, "property");
      setMetaTag("og:description", DEFAULT_DESCRIPTION, "property");
    };
  }, [title, description, path, ogImage]);

  return null;
}
