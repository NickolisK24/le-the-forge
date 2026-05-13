"""Conservative v2 planner adapter boundary."""

from .adapter import V2PlannerSafeAdapter
from .affix_metadata import V2AffixDisplayProvenanceMetadata, build_affix_metadata_view
from .contracts import PlannerAdapterDomainSummary, PlannerAdapterRecordEligibility
from .diagnostics import build_planner_adapter_diagnostics
from .eligibility import evaluate_modifier_record
from .errors import V2PlannerAdapterError
from .item_metadata import V2ItemBaseDisplayMetadata, build_item_base_metadata_view
from .metadata import V2PlannerMetadataRemap, build_metadata_view
from .passive_skill_identity import V2PassiveSkillIdentityMetadata

__all__ = [
    "PlannerAdapterDomainSummary",
    "PlannerAdapterRecordEligibility",
    "V2AffixDisplayProvenanceMetadata",
    "V2PlannerAdapterError",
    "V2ItemBaseDisplayMetadata",
    "V2PassiveSkillIdentityMetadata",
    "V2PlannerSafeAdapter",
    "V2PlannerMetadataRemap",
    "build_affix_metadata_view",
    "build_item_base_metadata_view",
    "build_planner_adapter_diagnostics",
    "build_metadata_view",
    "evaluate_modifier_record",
]
