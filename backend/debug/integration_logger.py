from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
import time


@dataclass
class IntegrationLogEntry:
    event_type: str     # "import_success", "import_failure", "export", "share", "version_mismatch", "auth_failure"
    build_id: str | None
    user_id: str | None
    format: str | None  # "json", "build_string", "url_param"
    duration_ms: float
    metadata: dict
    timestamp: float = field(default_factory=time.time)


class IntegrationLogger:
    def __init__(self, capacity: int = 1000):
        self._entries: deque[IntegrationLogEntry] = deque(maxlen=capacity)

    def log_import_success(
        self,
        build_id: str,
        user_id: str | None,
        fmt: str,
        duration_ms: float,
    ) -> None:
        self._entries.append(
            IntegrationLogEntry(
                event_type="import_success",
                build_id=build_id,
                user_id=user_id,
                format=fmt,
                duration_ms=duration_ms,
                metadata={},
            )
        )

    def log_import_failure(
        self,
        user_id: str | None,
        fmt: str,
        errors: list[str],
        duration_ms: float,
    ) -> None:
        self._entries.append(
            IntegrationLogEntry(
                event_type="import_failure",
                build_id=None,
                user_id=user_id,
                format=fmt,
                duration_ms=duration_ms,
                metadata={"errors": errors},
            )
        )

    def log_export(
        self,
        build_id: str,
        user_id: str | None,
        fmt: str,
        size_bytes: int,
        duration_ms: float,
    ) -> None:
        self._entries.append(
            IntegrationLogEntry(
                event_type="export",
                build_id=build_id,
                user_id=user_id,
                format=fmt,
                duration_ms=duration_ms,
                metadata={"size_bytes": size_bytes},
            )
        )

    def log_share(
        self,
        build_id: str,
        user_id: str | None,
        share_url: str,
        duration_ms: float,
    ) -> None:
        self._entries.append(
            IntegrationLogEntry(
                event_type="share",
                build_id=build_id,
                user_id=user_id,
                format=None,
                duration_ms=duration_ms,
                metadata={"share_url": share_url},
            )
        )

    def log_version_mismatch(
        self,
        build_id: str | None,
        from_v: str,
        to_v: str,
        steps: int,
    ) -> None:
        self._entries.append(
            IntegrationLogEntry(
                event_type="version_mismatch",
                build_id=build_id,
                user_id=None,
                format=None,
                duration_ms=0.0,
                metadata={"from": from_v, "to": to_v, "steps": steps},
            )
        )

    def log_auth_failure(
        self,
        user_id: str | None,
        action: str,
        reason: str,
    ) -> None:
        self._entries.append(
            IntegrationLogEntry(
                event_type="auth_failure",
                build_id=None,
                user_id=user_id,
                format=None,
                duration_ms=0.0,
                metadata={"action": action, "reason": reason},
            )
        )

    def get_entries(self, event_type: str | None = None) -> list[IntegrationLogEntry]:
        if event_type is None:
            return list(self._entries)
        return [e for e in self._entries if e.event_type == event_type]

    def summary(self) -> dict:
        # {"total": int, "by_type": {}, "success_rate": float}
        # success_rate = import_success / (import_success + import_failure) or 1.0 if no imports
        by_type: dict[str, int] = {}
        for entry in self._entries:
            by_type[entry.event_type] = by_type.get(entry.event_type, 0) + 1

        successes = by_type.get("import_success", 0)
        failures = by_type.get("import_failure", 0)
        total_imports = successes + failures
        success_rate = (successes / total_imports) if total_imports > 0 else 1.0

        return {
            "total": len(self._entries),
            "by_type": by_type,
            "success_rate": success_rate,
        }

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)
