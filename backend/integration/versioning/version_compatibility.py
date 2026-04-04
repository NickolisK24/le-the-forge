from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class MigrationStep:
    from_version: str
    to_version: str
    description: str
    migrate_fn: Callable[[dict], dict]  # takes build dict, returns migrated dict


@dataclass
class CompatibilityResult:
    original_version: str
    target_version: str
    migrated: bool
    steps_applied: int
    warnings: list[str]
    data: dict


class VersionCompatibilityEngine:
    def __init__(self):
        self._migrations: list[MigrationStep] = []
        self._deprecated: dict[str, str] = {}  # version -> deprecation message

    def register_migration(self, step: MigrationStep) -> None:
        self._migrations.append(step)
        self._migrations.sort(key=lambda m: (m.from_version, m.to_version))

    def register_deprecation(self, version: str, message: str) -> None:
        self._deprecated[version] = message

    def _version_tuple(self, v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split("."))

    def migrate(self, data: dict, target_version: str) -> CompatibilityResult:
        current = str(data.get("version", "1.0"))
        warnings = []
        if current in self._deprecated:
            warnings.append(
                f"version {current} is deprecated: {self._deprecated[current]}"
            )
        steps_applied = 0
        migrated_data = dict(data)
        current_v = self._version_tuple(current)
        target_v = self._version_tuple(target_version)
        # Apply migrations in order that advance from current toward target
        for step in self._migrations:
            sv = self._version_tuple(step.from_version)
            tv = self._version_tuple(step.to_version)
            if sv >= current_v and tv <= target_v:
                migrated_data = step.migrate_fn(migrated_data)
                migrated_data["version"] = step.to_version
                current_v = tv
                steps_applied += 1
        return CompatibilityResult(
            current,
            target_version,
            steps_applied > 0,
            steps_applied,
            warnings,
            migrated_data,
        )

    def is_compatible(self, version: str, min_version: str, max_version: str) -> bool:
        v = self._version_tuple(version)
        return self._version_tuple(min_version) <= v <= self._version_tuple(max_version)

    def latest_version(self) -> str | None:
        if not self._migrations:
            return None
        return max(
            (m.to_version for m in self._migrations), key=self._version_tuple
        )
