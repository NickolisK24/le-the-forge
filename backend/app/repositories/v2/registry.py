"""Central read-only registry for generated v2 backend repositories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from app.normalization.v2 import V2ModifierRegistry, V2StatRegistry
from app.repositories.v2.affix_repository import V2AffixRepository
from app.repositories.v2.class_mastery_repository import V2ClassMasteryRepository
from app.repositories.v2.idol_repository import V2IdolRepository
from app.repositories.v2.item_repository import V2ItemRepository
from app.repositories.v2.passive_repository import V2PassiveRepository
from app.repositories.v2.paths import artifact_path
from app.repositories.v2.skill_repository import V2SkillRepository
from app.repositories.v2.unique_set_repository import V2UniqueSetRepository

RepositoryFactory = Callable[[str | Path | None], Any]


@dataclass(frozen=True)
class V2RepositoryDescriptor:
    domain: str
    label: str
    artifact_keys: tuple[str, ...]
    required_methods: tuple[str, ...]
    experimental_routes: tuple[str, ...]
    factory: RepositoryFactory

    def artifact_paths(self, *, root: str | Path | None = None) -> tuple[Path, ...]:
        return tuple(artifact_path(key, root=root) for key in self.artifact_keys)


def default_repository_descriptors() -> tuple[V2RepositoryDescriptor, ...]:
    """Return the v2 domains currently exposed through read-only loaders."""

    return (
        V2RepositoryDescriptor(
            domain="affixes",
            label="Affixes",
            artifact_keys=("affix_bundle",),
            required_methods=("load", "list_affixes", "get_affix", "filter_affixes", "debug_summary"),
            experimental_routes=("/experimental/v2/affixes", "/experimental/v2/affixes/<affix_id>", "/experimental/v2/affixes/debug"),
            factory=lambda root=None: V2AffixRepository(artifact_path("affix_bundle", root=root)),
        ),
        V2RepositoryDescriptor(
            domain="items",
            label="Item bases and implicits",
            artifact_keys=("item_base_bundle", "item_implicit_bundle"),
            required_methods=("load", "list_bases", "get_base", "filter_bases", "list_implicits", "get_implicit", "debug_summary"),
            experimental_routes=("/experimental/v2/items/bases", "/experimental/v2/items/bases/<item_base_id>", "/experimental/v2/items/implicits", "/experimental/v2/items/debug"),
            factory=lambda root=None: V2ItemRepository(
                artifact_path("item_base_bundle", root=root),
                artifact_path("item_implicit_bundle", root=root),
            ),
        ),
        V2RepositoryDescriptor(
            domain="unique_sets",
            label="Uniques and sets",
            artifact_keys=("unique_bundle", "set_bundle"),
            required_methods=("load", "list_uniques", "get_unique", "filter_uniques", "list_sets", "get_set", "debug_summary"),
            experimental_routes=("/experimental/v2/uniques", "/experimental/v2/uniques/<unique_id>", "/experimental/v2/sets", "/experimental/v2/sets/<set_id>", "/experimental/v2/uniques/debug", "/experimental/v2/sets/debug"),
            factory=lambda root=None: V2UniqueSetRepository(
                artifact_path("unique_bundle", root=root),
                artifact_path("set_bundle", root=root),
            ),
        ),
        V2RepositoryDescriptor(
            domain="idols",
            label="Idols and idol affixes",
            artifact_keys=("idol_bundle", "idol_affix_bundle"),
            required_methods=("load", "list_idols", "get_idol", "filter_idols", "list_affixes", "get_affix", "debug_summary"),
            experimental_routes=("/experimental/v2/idols", "/experimental/v2/idols/<idol_id>", "/experimental/v2/idols/affixes", "/experimental/v2/idols/affixes/<affix_id>", "/experimental/v2/idols/debug"),
            factory=lambda root=None: V2IdolRepository(
                artifact_path("idol_bundle", root=root),
                artifact_path("idol_affix_bundle", root=root),
            ),
        ),
        V2RepositoryDescriptor(
            domain="classes_masteries",
            label="Classes and masteries",
            artifact_keys=("class_mastery_bundle",),
            required_methods=("load", "list_classes", "get_class", "filter_classes", "list_masteries", "get_mastery", "debug_summary"),
            experimental_routes=("/experimental/v2/classes", "/experimental/v2/classes/<class_id>", "/experimental/v2/masteries", "/experimental/v2/masteries/<mastery_id>", "/experimental/v2/classes/debug"),
            factory=lambda root=None: V2ClassMasteryRepository(artifact_path("class_mastery_bundle", root=root)),
        ),
        V2RepositoryDescriptor(
            domain="passives",
            label="Passive trees",
            artifact_keys=("passive_tree_bundle",),
            required_methods=("load", "list_trees", "get_tree", "filter_trees", "get_nodes_by_tree", "get_node", "debug_summary"),
            experimental_routes=("/experimental/v2/passives", "/experimental/v2/passives/<tree_id>", "/experimental/v2/passives/<tree_id>/nodes/<node_id>", "/experimental/v2/passives/debug"),
            factory=lambda root=None: V2PassiveRepository(artifact_path("passive_tree_bundle", root=root)),
        ),
        V2RepositoryDescriptor(
            domain="skills",
            label="Skills and skill trees",
            artifact_keys=("skill_bundle", "skill_tree_bundle"),
            required_methods=("load", "list_skills", "filter_skills", "get_skill", "get_tree", "get_tree_by_skill", "get_nodes_by_tree", "get_node", "debug_summary"),
            experimental_routes=("/experimental/v2/skills", "/experimental/v2/skills/<skill_id>", "/experimental/v2/skills/<skill_id>/tree", "/experimental/v2/skills/trees/<tree_id>", "/experimental/v2/skills/trees/<tree_id>/nodes/<node_id>", "/experimental/v2/skills/debug"),
            factory=lambda root=None: V2SkillRepository(
                artifact_path("skill_bundle", root=root),
                artifact_path("skill_tree_bundle", root=root),
            ),
        ),
        V2RepositoryDescriptor(
            domain="stats",
            label="Stat registry",
            artifact_keys=("stat_registry",),
            required_methods=("load", "list_stats", "get_stat", "debug_summary"),
            experimental_routes=("/experimental/v2/stats", "/experimental/v2/stats/<stat_id>"),
            factory=lambda root=None: V2StatRegistry(artifact_path("stat_registry", root=root)),
        ),
        V2RepositoryDescriptor(
            domain="modifiers",
            label="Modifier registry",
            artifact_keys=("modifier_registry",),
            required_methods=("load", "list_modifiers", "get_modifier", "debug_summary"),
            experimental_routes=("/experimental/v2/modifiers", "/experimental/v2/modifiers/<modifier_id>", "/experimental/v2/modifiers/debug"),
            factory=lambda root=None: V2ModifierRegistry(artifact_path("modifier_registry", root=root)),
        ),
        V2RepositoryDescriptor(
            domain="value_policy",
            label="Value normalization policy",
            artifact_keys=("value_normalization_policy_report",),
            required_methods=(),
            experimental_routes=(),
            factory=lambda root=None: None,
        ),
    )


class V2RepositoryRegistry:
    """Read-only facade for generated v2 repository domains."""

    def __init__(
        self,
        *,
        root: str | Path | None = None,
        descriptors: tuple[V2RepositoryDescriptor, ...] | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else None
        self._descriptors = {descriptor.domain: descriptor for descriptor in (descriptors or default_repository_descriptors())}

    def list_domains(self) -> list[str]:
        return sorted(self._descriptors)

    def descriptor(self, domain: str) -> V2RepositoryDescriptor:
        return self._descriptors[domain]

    def load(self, domain: str) -> Any:
        descriptor = self.descriptor(domain)
        repository = descriptor.factory(self.root)
        if repository is None:
            return None
        return repository.load()

    def method_coverage(self, domain: str) -> dict[str, bool]:
        descriptor = self.descriptor(domain)
        repository = descriptor.factory(self.root)
        return {method: hasattr(repository, method) for method in descriptor.required_methods}

    def validate_domain(self, domain: str) -> dict[str, Any]:
        descriptor = self.descriptor(domain)
        artifacts = [
            {
                "artifact_key": key,
                "path": str(path),
                "exists": path.exists(),
            }
            for key, path in zip(descriptor.artifact_keys, descriptor.artifact_paths(root=self.root), strict=True)
        ]
        missing_artifacts = [artifact for artifact in artifacts if not artifact["exists"]]
        method_coverage = self.method_coverage(domain)
        missing_methods = [method for method, present in method_coverage.items() if not present]
        if missing_artifacts:
            return {
                "domain": domain,
                "label": descriptor.label,
                "status": "missing_artifacts",
                "artifacts": artifacts,
                "missing_artifact_count": len(missing_artifacts),
                "method_coverage": method_coverage,
                "missing_methods": missing_methods,
                "experimental_routes": list(descriptor.experimental_routes),
                "production_consumed": False,
                "error": f"Missing v2 generated artifacts for {domain}.",
            }
        try:
            repository = self.load(domain)
            debug_summary = repository.debug_summary() if repository is not None and hasattr(repository, "debug_summary") else {}
        except Exception as exc:
            return {
                "domain": domain,
                "label": descriptor.label,
                "status": "invalid",
                "artifacts": artifacts,
                "missing_artifact_count": 0,
                "method_coverage": method_coverage,
                "missing_methods": missing_methods,
                "experimental_routes": list(descriptor.experimental_routes),
                "production_consumed": False,
                "error": str(exc),
            }
        return {
            "domain": domain,
            "label": descriptor.label,
            "status": "ok",
            "artifacts": artifacts,
            "missing_artifact_count": 0,
            "method_coverage": method_coverage,
            "missing_methods": missing_methods,
            "experimental_routes": list(descriptor.experimental_routes),
            "debug_summary": debug_summary,
            "production_consumed": False,
        }

    def validation_status(self) -> dict[str, Any]:
        domains = [self.validate_domain(domain) for domain in self.list_domains()]
        missing_count = sum(domain["missing_artifact_count"] for domain in domains)
        invalid_count = sum(1 for domain in domains if domain["status"] == "invalid")
        return {
            "summary": {
                "repository_domain_count": len(domains),
                "loaded_repository_count": sum(1 for domain in domains if domain["status"] == "ok"),
                "missing_artifact_count": missing_count,
                "invalid_repository_count": invalid_count,
                "production_consumed": False,
            },
            "repositories": domains,
        }
