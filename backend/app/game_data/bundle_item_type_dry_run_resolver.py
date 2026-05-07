"""Developer-only dry-run resolver for reviewed bundle item type mappings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.game_data.bundle_item_adapter_translations import get_adapter_translations
from app.game_data.bundle_item_mapping_review import load_mapping_review_fixture, validate_mapping_review_fixture


BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
DEFAULT_MAPPING_REVIEW_FIXTURE = (
    BACKEND_ROOT / "tests" / "fixtures" / "bundle_item_type_mapping_review.json"
)
DEFAULT_TRANSLATIONS_FIXTURE = (
    BACKEND_ROOT / "tests" / "fixtures" / "bundle_item_type_adapter_translations.json"
)

STATUS_RESOLVED = "resolved"
STATUS_NEEDS_CONTEXT = "needs_context"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_DEFERRED = "deferred"
STATUS_UNRESOLVED = "unresolved"

MATCH_ACCEPTED_DIRECT = "accepted_direct"
MATCH_ADAPTER_TRANSLATION = "adapter_translation"
MATCH_NONE = "none"


@dataclass
class DryRunResolution:
    forge_item_type: str
    base_type_id: int | None
    status: str
    bundle_item_type_id: str | None
    match_source: str
    production_safe: bool = False
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "forge_item_type": self.forge_item_type,
            "base_type_id": self.base_type_id,
            "status": self.status,
            "bundle_item_type_id": self.bundle_item_type_id,
            "match_source": self.match_source,
            "production_safe": self.production_safe,
            "warnings": self.warnings,
            "notes": self.notes,
        }


class BundleItemTypeDryRunResolver:
    """Read-only resolver backed by reviewed developer fixtures."""

    def __init__(
        self,
        mapping_review_fixture: str | Path = DEFAULT_MAPPING_REVIEW_FIXTURE,
        translations_fixture: str | Path = DEFAULT_TRANSLATIONS_FIXTURE,
    ) -> None:
        self.mapping_review_fixture = Path(mapping_review_fixture)
        self.translations_fixture = Path(translations_fixture)
        review_fixture = load_mapping_review_fixture(self.mapping_review_fixture)
        errors, _warnings = validate_mapping_review_fixture(review_fixture)
        if errors:
            raise ValueError("; ".join(errors))

        self.accepted = {
            (entry["forge_item_type"], entry["bundle_base_type_id"]): entry
            for entry in review_fixture["categories"]["accepted"]
        }
        self.accepted_types = {
            entry["forge_item_type"] for entry in review_fixture["categories"]["accepted"]
        }
        self.needs_review_types = {
            entry["forge_item_type"]
            for entry in review_fixture["categories"]["needs_review"]
            if entry.get("forge_item_type")
        }
        self.deferred_bundle_types = {
            entry["bundle_item_type_id"]
            for entry in review_fixture["categories"]["deferred"]
            if entry.get("bundle_item_type_id")
        }

        translations = get_adapter_translations(self.translations_fixture)
        self.translations = {
            (entry["forge_item_type"], entry["bundle_base_type_id"]): entry
            for entry in translations
        }
        self.translation_types = {entry["forge_item_type"] for entry in translations}
        self.collapsed_or_contextual_types = self.accepted_types | self.translation_types

    def resolve(
        self,
        forge_item_type: str,
        base_type_id: int | None = None,
        subtype_id: int | None = None,
    ) -> DryRunResolution:
        warnings: list[str] = []
        notes: list[str] = []
        if subtype_id is not None:
            warnings.append("subtype_id was provided but ignored; subtype_id alone is not a valid identity.")

        if not forge_item_type:
            return DryRunResolution(
                forge_item_type=forge_item_type,
                base_type_id=base_type_id,
                status=STATUS_UNRESOLVED,
                bundle_item_type_id=None,
                match_source=MATCH_NONE,
                warnings=warnings + ["Missing forge_item_type."],
            )

        if forge_item_type in self.needs_review_types:
            return DryRunResolution(
                forge_item_type=forge_item_type,
                base_type_id=base_type_id,
                status=STATUS_NEEDS_REVIEW,
                bundle_item_type_id=None,
                match_source=MATCH_NONE,
                warnings=warnings + ["Forge item type requires manual review before resolution."],
                notes=["No reviewed safe mapping exists."],
            )

        if base_type_id is None:
            if forge_item_type in self.collapsed_or_contextual_types:
                return DryRunResolution(
                    forge_item_type=forge_item_type,
                    base_type_id=None,
                    status=STATUS_NEEDS_CONTEXT,
                    bundle_item_type_id=None,
                    match_source=MATCH_NONE,
                    warnings=warnings + ["base_type_id is required; resolver will not guess from slug alone."],
                    notes=["Provide base_type_id to use accepted direct mappings or adapter translations."],
                )
            return DryRunResolution(
                forge_item_type=forge_item_type,
                base_type_id=None,
                status=STATUS_UNRESOLVED,
                bundle_item_type_id=None,
                match_source=MATCH_NONE,
                warnings=warnings + ["No reviewed mapping exists for this Forge item type."],
            )

        key = (forge_item_type, base_type_id)
        accepted = self.accepted.get(key)
        if accepted:
            return DryRunResolution(
                forge_item_type=forge_item_type,
                base_type_id=base_type_id,
                status=STATUS_RESOLVED,
                bundle_item_type_id=accepted["bundle_item_type_id"],
                match_source=MATCH_ACCEPTED_DIRECT,
                warnings=warnings,
                notes=["Resolved through reviewed accepted direct mapping."],
            )

        translation = self.translations.get(key)
        if translation:
            return DryRunResolution(
                forge_item_type=forge_item_type,
                base_type_id=base_type_id,
                status=STATUS_RESOLVED,
                bundle_item_type_id=translation["bundle_item_type_id"],
                match_source=MATCH_ADAPTER_TRANSLATION,
                warnings=warnings,
                notes=[f"Resolved through {translation['translation_type']} translation."],
            )

        if forge_item_type in self.collapsed_or_contextual_types:
            return DryRunResolution(
                forge_item_type=forge_item_type,
                base_type_id=base_type_id,
                status=STATUS_NEEDS_CONTEXT,
                bundle_item_type_id=None,
                match_source=MATCH_NONE,
                warnings=warnings + ["base_type_id does not match any reviewed mapping for this Forge item type."],
                notes=["Do not fall back to slug-only matching."],
            )

        return DryRunResolution(
            forge_item_type=forge_item_type,
            base_type_id=base_type_id,
            status=STATUS_UNRESOLVED,
            bundle_item_type_id=None,
            match_source=MATCH_NONE,
            warnings=warnings + ["No reviewed mapping exists for this Forge item type."],
        )


def summarize_resolutions(results: list[DryRunResolution]) -> dict[str, Any]:
    counts = {
        STATUS_RESOLVED: 0,
        STATUS_NEEDS_CONTEXT: 0,
        STATUS_NEEDS_REVIEW: 0,
        STATUS_DEFERRED: 0,
        STATUS_UNRESOLVED: 0,
    }
    subtype_warning_attempted = False
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
        if any("subtype_id" in warning for warning in result.warnings):
            subtype_warning_attempted = True
    return {
        "total_attempted": len(results),
        "counts": counts,
        "subtype_id_only_matching_attempted": False,
        "subtype_id_context_warnings_seen": subtype_warning_attempted,
        "results": [result.to_dict() for result in results],
    }
