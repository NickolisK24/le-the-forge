"""
Enemy Registry — O(1) validated lookups over EnemyProfile domain objects.

Seeded from data/entities/enemy_profiles.json via the GameDataPipeline at
app startup. The registry receives pre-normalized domain objects; it does not
do normalization itself.

Usage:
    from flask import current_app
    registry = current_app.extensions["enemy_registry"]
    enemy = registry.get("black_widow")      # raises EnemyNotFoundError if missing
    all_  = registry.for_category("boss")    # O(1) list
"""

from __future__ import annotations
from app.domain.enemy import EnemyProfile
from app.utils.exceptions import ForgeError
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


class EnemyNotFoundError(ForgeError):
    status_code = 404

    def __init__(self, enemy_id: str) -> None:
        super().__init__(f"Unknown enemy: {enemy_id!r}")


class EnemyRegistry:
    """
    Two-way indexed map of all enemies loaded from enemy_profiles.json.

    Lookup by id or by category — both O(1).
    Receives a pre-normalized list[EnemyProfile] from the pipeline.
    Constructed once in create_app() and stored on app.extensions.
    """

    def __init__(self, enemies: list[EnemyProfile]) -> None:
        """
        Args:
            enemies: flat list of EnemyProfile domain objects, already
                     normalized by the pipeline. No further normalization here.
        Raises:
            ValueError: if enemies is empty or contains mixed data versions.
        """
        if not enemies:
            raise ValueError("EnemyRegistry requires at least one definition")

        version = enemies[0].data_version
        for e in enemies:
            if e.data_version != version:
                raise ValueError(
                    f"Mixed data versions in EnemyRegistry: "
                    f"expected {version!r}, got {e.data_version!r} on enemy {e.id!r}"
                )
        self.data_version = version

        self._by_id: dict[str, EnemyProfile] = {}
        self._by_category: dict[str, list[EnemyProfile]] = {}

        for enemy in enemies:
            self._by_id[enemy.id] = enemy
            if enemy.category not in self._by_category:
                self._by_category[enemy.category] = []
            self._by_category[enemy.category].append(enemy)

        log.info(
            "enemy_registry.initialized",
            data_version=self.data_version,
            count=len(self._by_id),
            categories=len(self._by_category),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, enemy_id: str) -> EnemyProfile:
        """Return an EnemyProfile by id, or raise EnemyNotFoundError."""
        enemy = self._by_id.get(enemy_id)
        if enemy is None:
            raise EnemyNotFoundError(enemy_id)
        return enemy

    def for_category(self, category: str) -> list[EnemyProfile]:
        """Return all enemies in the given category. O(1)."""
        return self._by_category.get(category, [])

    def all(self) -> list[EnemyProfile]:
        """Return all enemies as a flat list."""
        return list(self._by_id.values())

    def ids(self) -> list[str]:
        """Return all enemy ids, sorted."""
        return sorted(self._by_id.keys())

    def __contains__(self, enemy_id: str) -> bool:
        return enemy_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)
