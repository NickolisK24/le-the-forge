"""v2 experimental repositories."""

from .affix_repository import V2AffixBundleError, V2AffixRepository
from .class_mastery_repository import V2ClassMasteryBundleError, V2ClassMasteryRepository
from .idol_repository import V2IdolBundleError, V2IdolRepository
from .item_repository import V2ItemBundleError, V2ItemRepository
from .passive_repository import V2PassiveBundleError, V2PassiveRepository
from .registry import V2RepositoryDescriptor, V2RepositoryRegistry, default_repository_descriptors
from .skill_repository import V2SkillBundleError, V2SkillRepository
from .unique_set_repository import V2UniqueSetBundleError, V2UniqueSetRepository

__all__ = [
    "V2AffixBundleError",
    "V2AffixRepository",
    "V2ClassMasteryBundleError",
    "V2ClassMasteryRepository",
    "V2IdolBundleError",
    "V2IdolRepository",
    "V2ItemBundleError",
    "V2ItemRepository",
    "V2PassiveBundleError",
    "V2PassiveRepository",
    "V2RepositoryDescriptor",
    "V2RepositoryRegistry",
    "V2SkillBundleError",
    "V2SkillRepository",
    "V2UniqueSetBundleError",
    "V2UniqueSetRepository",
    "default_repository_descriptors",
]
