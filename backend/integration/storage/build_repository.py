from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import OrderedDict


@dataclass
class StoredBuild:
    build_id: str
    build_name: str
    character_class: str
    version: str
    data: dict           # raw build dict
    owner_id: str | None
    is_public: bool
    created_at: float
    updated_at: float
    tags: list[str] = field(default_factory=list)
    view_count: int = 0


@dataclass
class QueryResult:
    builds: list[StoredBuild]
    total: int
    offset: int
    limit: int


class BuildRepository:
    def __init__(self, max_builds: int = 10_000):
        self._builds: OrderedDict[str, StoredBuild] = OrderedDict()
        self.max_builds = max_builds

    def save(self, build: StoredBuild) -> StoredBuild:
        # Upsert by build_id; update updated_at if exists
        # Evict oldest if at capacity
        if build.build_id in self._builds:
            build.updated_at = time.time()
        elif len(self._builds) >= self.max_builds:
            self._builds.popitem(last=False)  # evict oldest
        self._builds[build.build_id] = build
        return build

    def get(self, build_id: str) -> StoredBuild | None:
        return self._builds.get(build_id)

    def get_and_increment_views(self, build_id: str) -> StoredBuild | None:
        build = self.get(build_id)
        if build:
            build.view_count += 1
        return build

    def delete(self, build_id: str) -> bool:
        if build_id in self._builds:
            del self._builds[build_id]
            return True
        return False

    def list_public(
        self,
        offset: int = 0,
        limit: int = 20,
        character_class: str | None = None,
        tag: str | None = None,
        search: str | None = None,
    ) -> QueryResult:
        # Filter public builds; search on build_name (case-insensitive contains)
        builds = [b for b in self._builds.values() if b.is_public]
        if character_class:
            builds = [b for b in builds if b.character_class.lower() == character_class.lower()]
        if tag:
            builds = [b for b in builds if tag in b.tags]
        if search:
            builds = [b for b in builds if search.lower() in b.build_name.lower()]
        total = len(builds)
        return QueryResult(builds[offset:offset + limit], total, offset, limit)

    def list_by_owner(self, owner_id: str, offset: int = 0, limit: int = 20) -> QueryResult:
        builds = [b for b in self._builds.values() if b.owner_id == owner_id]
        total = len(builds)
        return QueryResult(builds[offset:offset + limit], total, offset, limit)

    def version_build(
        self, build_id: str, new_data: dict, new_version: str
    ) -> StoredBuild | None:
        # Update build data and version; return updated build or None if not found
        build = self.get(build_id)
        if build:
            build.data = new_data
            build.version = new_version
            build.updated_at = time.time()
        return build

    def __len__(self) -> int:
        return len(self._builds)
