from __future__ import annotations
from dataclasses import dataclass
import hashlib, time


@dataclass
class ShareLink:
    build_id: str       # short hash
    url: str
    build_name: str
    version: str
    created_at: float
    expires_at: float | None  # None = never


class ShareLinkGenerator:
    BASE_URL = "https://le-the-forge.app/share"   # placeholder

    def generate_build_id(self, build_name: str, version: str, salt: str = "") -> str:
        """Return the first 12 hex characters of SHA-256 over name:version:salt:timestamp."""
        raw = f"{build_name}:{version}:{salt}:{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def generate(
        self,
        build_name: str,
        version: str,
        ttl_seconds: float | None = None,
    ) -> ShareLink:
        """Create a new ShareLink, optionally with an expiry time."""
        build_id = self.generate_build_id(build_name, version)
        url = f"{self.BASE_URL}/{build_id}"
        now = time.time()
        expires = now + ttl_seconds if ttl_seconds is not None else None
        return ShareLink(build_id, url, build_name, version, now, expires)

    def is_expired(self, link: ShareLink) -> bool:
        """Return True if the link has a finite expiry that has already passed."""
        if link.expires_at is None:
            return False
        return time.time() > link.expires_at

    def generate_hash(self, content: str) -> str:
        """Return the deterministic SHA-256 hex digest of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def tag_version(self, url: str, version: str) -> str:
        """Append ?v=<version> or &v=<version> to url depending on existing query string."""
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}v={version}"
