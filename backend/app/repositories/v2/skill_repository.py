"""Read-only v2 skill and skill tree repository."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


class V2SkillBundleError(ValueError):
    """Raised when the v2 skill bundles are missing or invalid."""


class V2SkillRepository:
    """Read-only repository over the generated v2 skill and skill tree bundles."""

    def __init__(self, skill_bundle_path: str | Path, skill_tree_bundle_path: str | Path) -> None:
        self.skill_bundle_path = Path(skill_bundle_path)
        self.skill_tree_bundle_path = Path(skill_tree_bundle_path)
        self._skill_payload: dict[str, Any] | None = None
        self._tree_payload: dict[str, Any] | None = None
        self._skills: tuple[dict[str, Any], ...] = ()
        self._trees: tuple[dict[str, Any], ...] = ()
        self._nodes: tuple[dict[str, Any], ...] = ()
        self._skills_by_id: dict[str, dict[str, Any]] = {}
        self._trees_by_id: dict[str, dict[str, Any]] = {}
        self._trees_by_skill_id: dict[str, dict[str, Any]] = {}
        self._nodes_by_id: dict[str, dict[str, Any]] = {}
        self._nodes_by_tree_id: dict[str, tuple[dict[str, Any], ...]] = {}

    def load(self) -> "V2SkillRepository":
        return self.load_payloads(
            _read_json(self.skill_bundle_path, "v2 skill bundle"),
            _read_json(self.skill_tree_bundle_path, "v2 skill tree bundle"),
        )

    def load_payloads(self, skill_payload: dict[str, Any], tree_payload: dict[str, Any]) -> "V2SkillRepository":
        skills = _records(skill_payload, "skills")
        trees = _records(tree_payload, "skill_trees")
        nodes = _records(tree_payload, "skill_nodes")
        self._validate(skills, trees, nodes)
        self._skill_payload = deepcopy(skill_payload)
        self._tree_payload = deepcopy(tree_payload)
        self._skills = tuple(deepcopy(record) for record in skills)
        self._trees = tuple(deepcopy(record) for record in trees)
        self._nodes = tuple(deepcopy(record) for record in nodes)
        self._skills_by_id = {record["canonical_id"]: record for record in self._skills}
        self._trees_by_id = {record["canonical_id"]: record for record in self._trees}
        self._trees_by_skill_id = {record["skill_id"]: record for record in self._trees}
        self._nodes_by_id = {record["canonical_id"]: record for record in self._nodes}
        nodes_by_tree: dict[str, list[dict[str, Any]]] = {}
        for node in self._nodes:
            nodes_by_tree.setdefault(node["skill_tree_id"], []).append(node)
        self._nodes_by_tree_id = {tree_id: tuple(records) for tree_id, records in nodes_by_tree.items()}
        return self

    def list_skills(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._skills, limit=limit, offset=offset)

    def filter_skills(
        self,
        *,
        query: str = "",
        class_id: str = "",
        mastery_id: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._skills)
        if query:
            needle = query.strip().lower()
            records = [record for record in records if needle in record["canonical_id"].lower() or needle in str(record.get("display_name", "")).lower()]
        if class_id:
            expected = class_id.strip().lower()
            records = [record for record in records if expected in [str(value).lower() for value in record.get("owner_class_ids", [])]]
        if mastery_id:
            expected = mastery_id.strip().lower()
            records = [record for record in records if expected in [str(value).lower() for value in record.get("owner_mastery_ids", [])]]
        return _page(tuple(records), limit=limit, offset=offset)

    def get_skill(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._skills_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def list_trees(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._trees, limit=limit, offset=offset)

    def get_tree(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._trees_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def get_tree_by_skill(self, skill_id: str) -> dict[str, Any] | None:
        record = self._trees_by_skill_id.get(skill_id)
        return deepcopy(record) if record else None

    def get_nodes_by_tree(self, tree_id: str, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._nodes_by_tree_id.get(tree_id, ()), limit=limit, offset=offset)

    def get_node(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._nodes_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def count_skills(self) -> int:
        return len(self._skills)

    def count_trees(self) -> int:
        return len(self._trees)

    def count_nodes(self) -> int:
        return len(self._nodes)

    def debug_summary(self) -> dict[str, Any]:
        return {
            "skill_bundle_path": str(self.skill_bundle_path),
            "skill_tree_bundle_path": str(self.skill_tree_bundle_path),
            "skill_count": self.count_skills(),
            "skill_tree_count": self.count_trees(),
            "skill_node_count": self.count_nodes(),
            "skill_summary": deepcopy(self._skill_payload.get("summary", {}) if self._skill_payload else {}),
            "skill_tree_summary": deepcopy(self._tree_payload.get("summary", {}) if self._tree_payload else {}),
            "cross_reference": deepcopy(self._skill_payload.get("cross_reference", {}) if self._skill_payload else {}),
            "production_consumer": False,
            "production_safe": False,
        }

    @staticmethod
    def _validate(skills: list[Any], trees: list[Any], nodes: list[Any]) -> None:
        skill_ids = _validate_common(skills, "Skill")
        tree_ids = _validate_common(trees, "Skill tree")
        node_ids = _validate_common(nodes, "Skill node")
        for skill in skills:
            tree_id = skill.get("skill_tree_id")
            if tree_id and tree_id not in tree_ids:
                raise V2SkillBundleError(f"Skill {skill['canonical_id']} links missing tree {tree_id}.")
        for tree in trees:
            canonical_id = tree["canonical_id"]
            if tree.get("skill_id") not in skill_ids:
                raise V2SkillBundleError(f"Skill tree {canonical_id} links missing skill {tree.get('skill_id')}.")
            if not isinstance(tree.get("node_ids"), list):
                raise V2SkillBundleError(f"Skill tree {canonical_id} has invalid node_ids.")
            for node_id in tree.get("node_ids") or []:
                if node_id not in node_ids:
                    raise V2SkillBundleError(f"Skill tree {canonical_id} links missing node {node_id}.")
        for node in nodes:
            canonical_id = node["canonical_id"]
            if node.get("skill_tree_id") not in tree_ids:
                raise V2SkillBundleError(f"Skill node {canonical_id} links missing tree {node.get('skill_tree_id')}.")
            if node.get("skill_id") not in skill_ids:
                raise V2SkillBundleError(f"Skill node {canonical_id} links missing skill {node.get('skill_id')}.")
            position = node.get("position")
            if position and (not isinstance(position, dict) or not all(isinstance(position.get(axis), (int, float)) for axis in ("x", "y"))):
                raise V2SkillBundleError(f"Skill node {canonical_id} has invalid position.")
            if not isinstance(node.get("max_points"), int) or node.get("max_points") < 0:
                raise V2SkillBundleError(f"Skill node {canonical_id} has invalid max_points.")
            if not isinstance(node.get("required_points"), int) or node.get("required_points") < 0:
                raise V2SkillBundleError(f"Skill node {canonical_id} has invalid required_points.")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise V2SkillBundleError(f"Invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise V2SkillBundleError(f"{label} must be a JSON object.")
    return payload


def _records(payload: dict[str, Any], key: str) -> list[Any]:
    records = payload.get("records")
    if not isinstance(records, dict) or not isinstance(records.get(key), list):
        raise V2SkillBundleError(f"v2 skill bundle records.{key} must be a list.")
    return records[key]


def _validate_common(records: list[Any], label: str) -> set[str]:
    seen: set[str] = set()
    ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise V2SkillBundleError(f"{label} record {index} must be an object.")
        canonical_id = record.get("canonical_id")
        try:
            validate_canonical_id(canonical_id)
        except ValueError as exc:
            raise V2SkillBundleError(f"{label} record {index} has invalid canonical_id: {exc}") from exc
        if canonical_id in seen:
            raise V2SkillBundleError(f"Duplicate canonical_id in v2 skill bundle: {canonical_id}")
        seen.add(canonical_id)
        ids.add(canonical_id)
        provenance = record.get("provenance")
        if not isinstance(provenance, dict) or not provenance.get("source_path") or not provenance.get("source_id"):
            raise V2SkillBundleError(f"{label} {canonical_id} is missing provenance.")
        try:
            status = SupportStatus(str(record.get("support_status")))
        except ValueError as exc:
            raise V2SkillBundleError(f"{label} {canonical_id} has invalid support_status.") from exc
        try:
            TrustLevel(str(record.get("trust_level")))
        except ValueError as exc:
            raise V2SkillBundleError(f"{label} {canonical_id} has invalid trust_level.") from exc
        if record.get("stable_calculable") is True or status == SupportStatus.TRUSTED:
            raise V2SkillBundleError(f"{label} {canonical_id} is not approved for stable calculation in Phase 9.")
        for modifier in record.get("modifier_rows") or []:
            if not isinstance(modifier, dict) or not modifier.get("provenance"):
                raise V2SkillBundleError(f"{label} {canonical_id} has modifier row without provenance.")
            if not modifier.get("support_status"):
                raise V2SkillBundleError(f"{label} {canonical_id} has modifier row without support_status.")
    return ids


def _page(records: tuple[dict[str, Any], ...], *, limit: int | None, offset: int) -> list[dict[str, Any]]:
    start = max(0, offset)
    end = None if limit is None else start + max(0, limit)
    return [deepcopy(record) for record in records[start:end]]
