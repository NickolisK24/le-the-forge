"""Read-only v2 passive tree repository."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


class V2PassiveBundleError(ValueError):
    """Raised when the v2 passive tree bundle is missing or invalid."""


class V2PassiveRepository:
    """Read-only repository over the generated v2 passive tree bundle."""

    def __init__(self, bundle_path: str | Path) -> None:
        self.bundle_path = Path(bundle_path)
        self._payload: dict[str, Any] | None = None
        self._trees: tuple[dict[str, Any], ...] = ()
        self._nodes: tuple[dict[str, Any], ...] = ()
        self._trees_by_id: dict[str, dict[str, Any]] = {}
        self._nodes_by_id: dict[str, dict[str, Any]] = {}
        self._nodes_by_tree_id: dict[str, tuple[dict[str, Any], ...]] = {}

    def load(self) -> "V2PassiveRepository":
        return self.load_payload(_read_json(self.bundle_path, "v2 passive tree bundle"))

    def load_payload(self, payload: dict[str, Any]) -> "V2PassiveRepository":
        trees = _records(payload, "passive_trees")
        nodes = _records(payload, "passive_nodes")
        self._validate(trees, nodes)
        self._payload = deepcopy(payload)
        self._trees = tuple(deepcopy(record) for record in trees)
        self._nodes = tuple(deepcopy(record) for record in nodes)
        self._trees_by_id = {record["canonical_id"]: record for record in self._trees}
        self._nodes_by_id = {record["canonical_id"]: record for record in self._nodes}
        nodes_by_tree: dict[str, list[dict[str, Any]]] = {}
        for node in self._nodes:
            nodes_by_tree.setdefault(node["tree_id"], []).append(node)
        self._nodes_by_tree_id = {tree_id: tuple(records) for tree_id, records in nodes_by_tree.items()}
        return self

    def list_trees(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._trees, limit=limit, offset=offset)

    def get_tree(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._trees_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def filter_trees(
        self,
        *,
        query: str = "",
        class_id: str = "",
        mastery_id: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._trees)
        if query:
            needle = query.strip().lower()
            records = [record for record in records if needle in record["canonical_id"].lower() or needle in str(record.get("display_name", "")).lower()]
        if class_id:
            expected = class_id.strip().lower()
            records = [record for record in records if str(record.get("owner_class_id", "")).lower() == expected]
        if mastery_id:
            expected = mastery_id.strip().lower()
            records = [record for record in records if str(record.get("owner_mastery_id", "")).lower() == expected]
        return _page(tuple(records), limit=limit, offset=offset)

    def get_nodes_by_tree(self, tree_id: str, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._nodes_by_tree_id.get(tree_id, ()), limit=limit, offset=offset)

    def get_node(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._nodes_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def count_trees(self) -> int:
        return len(self._trees)

    def count_nodes(self) -> int:
        return len(self._nodes)

    def debug_summary(self) -> dict[str, Any]:
        return {
            "bundle_path": str(self.bundle_path),
            "passive_tree_count": self.count_trees(),
            "passive_node_count": self.count_nodes(),
            "summary": deepcopy(self._payload.get("summary", {}) if self._payload else {}),
            "cross_reference": deepcopy(self._payload.get("cross_reference", {}) if self._payload else {}),
            "production_consumer": False,
            "production_safe": False,
        }

    @staticmethod
    def _validate(trees: list[Any], nodes: list[Any]) -> None:
        tree_ids = _validate_common(trees, "Passive tree")
        node_ids = _validate_common(nodes, "Passive node")
        for tree in trees:
            canonical_id = tree["canonical_id"]
            if not isinstance(tree.get("node_ids"), list):
                raise V2PassiveBundleError(f"Passive tree {canonical_id} has invalid node_ids.")
            for node_id in tree.get("node_ids") or []:
                if node_id not in node_ids:
                    raise V2PassiveBundleError(f"Passive tree {canonical_id} links missing node {node_id}.")
        for node in nodes:
            canonical_id = node["canonical_id"]
            if node.get("tree_id") not in tree_ids:
                raise V2PassiveBundleError(f"Passive node {canonical_id} links missing tree {node.get('tree_id')}.")
            position = node.get("position")
            if position and (not isinstance(position, dict) or not all(isinstance(position.get(axis), (int, float)) for axis in ("x", "y"))):
                raise V2PassiveBundleError(f"Passive node {canonical_id} has invalid position.")
            if not isinstance(node.get("max_points"), int) or node.get("max_points") < 0:
                raise V2PassiveBundleError(f"Passive node {canonical_id} has invalid max_points.")
            if not isinstance(node.get("required_points"), int) or node.get("required_points") < 0:
                raise V2PassiveBundleError(f"Passive node {canonical_id} has invalid required_points.")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise V2PassiveBundleError(f"Invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise V2PassiveBundleError(f"{label} must be a JSON object.")
    return payload


def _records(payload: dict[str, Any], key: str) -> list[Any]:
    records = payload.get("records")
    if not isinstance(records, dict) or not isinstance(records.get(key), list):
        raise V2PassiveBundleError(f"v2 passive tree bundle records.{key} must be a list.")
    return records[key]


def _validate_common(records: list[Any], label: str) -> set[str]:
    seen: set[str] = set()
    ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise V2PassiveBundleError(f"{label} record {index} must be an object.")
        canonical_id = record.get("canonical_id")
        try:
            validate_canonical_id(canonical_id)
        except ValueError as exc:
            raise V2PassiveBundleError(f"{label} record {index} has invalid canonical_id: {exc}") from exc
        if canonical_id in seen:
            raise V2PassiveBundleError(f"Duplicate canonical_id in v2 passive tree bundle: {canonical_id}")
        seen.add(canonical_id)
        ids.add(canonical_id)
        provenance = record.get("provenance")
        if not isinstance(provenance, dict) or not provenance.get("source_path") or not provenance.get("source_id"):
            raise V2PassiveBundleError(f"{label} {canonical_id} is missing provenance.")
        try:
            status = SupportStatus(str(record.get("support_status")))
        except ValueError as exc:
            raise V2PassiveBundleError(f"{label} {canonical_id} has invalid support_status.") from exc
        try:
            TrustLevel(str(record.get("trust_level")))
        except ValueError as exc:
            raise V2PassiveBundleError(f"{label} {canonical_id} has invalid trust_level.") from exc
        if record.get("stable_calculable") is True or status == SupportStatus.TRUSTED:
            raise V2PassiveBundleError(f"{label} {canonical_id} is not approved for stable calculation in Phase 8.")
        for modifier in record.get("modifier_rows") or []:
            if not isinstance(modifier, dict) or not modifier.get("provenance"):
                raise V2PassiveBundleError(f"{label} {canonical_id} has modifier row without provenance.")
            if not modifier.get("support_status"):
                raise V2PassiveBundleError(f"{label} {canonical_id} has modifier row without support_status.")
    return ids


def _page(records: tuple[dict[str, Any], ...], *, limit: int | None, offset: int) -> list[dict[str, Any]]:
    start = max(0, offset)
    end = None if limit is None else start + max(0, limit)
    return [deepcopy(record) for record in records[start:end]]
