"""Shared generated artifact paths for read-only v2 repositories."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
GENERATED_DOCS_DIR = REPO_ROOT / "docs" / "generated"

V2_ARTIFACT_PATHS: dict[str, Path] = {
    "affix_bundle": GENERATED_DOCS_DIR / "v2_affix_bundle.json",
    "item_base_bundle": GENERATED_DOCS_DIR / "v2_item_base_bundle.json",
    "item_implicit_bundle": GENERATED_DOCS_DIR / "v2_item_implicit_bundle.json",
    "unique_bundle": GENERATED_DOCS_DIR / "v2_unique_bundle.json",
    "set_bundle": GENERATED_DOCS_DIR / "v2_set_bundle.json",
    "idol_bundle": GENERATED_DOCS_DIR / "v2_idol_bundle.json",
    "idol_affix_bundle": GENERATED_DOCS_DIR / "v2_idol_affix_bundle.json",
    "class_mastery_bundle": GENERATED_DOCS_DIR / "v2_class_mastery_bundle.json",
    "passive_tree_bundle": GENERATED_DOCS_DIR / "v2_passive_tree_bundle.json",
    "skill_bundle": GENERATED_DOCS_DIR / "v2_skill_bundle.json",
    "skill_tree_bundle": GENERATED_DOCS_DIR / "v2_skill_tree_bundle.json",
    "stat_registry": GENERATED_DOCS_DIR / "v2_stat_registry.json",
    "modifier_registry": GENERATED_DOCS_DIR / "v2_modifier_registry.json",
    "value_normalization_policy_report": GENERATED_DOCS_DIR / "v2_value_normalization_policy_report.json",
}


def artifact_path(artifact_key: str, *, root: str | Path | None = None) -> Path:
    """Return an artifact path, optionally rooted at a test workspace."""

    relative_path = V2_ARTIFACT_PATHS[artifact_key].relative_to(REPO_ROOT)
    if root is None:
        return V2_ARTIFACT_PATHS[artifact_key]
    return Path(root) / relative_path
