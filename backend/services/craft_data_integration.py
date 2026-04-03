from __future__ import annotations
from dataclasses import dataclass, field

from crafting.models.craft_state import CraftState, AffixState
from crafting.models.bis_target import BisTarget


@dataclass
class AffixDefinition:
    affix_id: str
    affix_name: str
    category: str       # "prefix" or "suffix"
    max_tier: int = 7
    valid_item_classes: list[str] = field(default_factory=list)  # empty = all


@dataclass
class ValidationReport:
    valid: bool
    errors: list[str]
    warnings: list[str]


class CraftDataIntegration:
    def __init__(self):
        self._affix_registry: dict[str, AffixDefinition] = {}

    def register_affix(self, defn: AffixDefinition) -> None:
        self._affix_registry[defn.affix_id] = defn

    def register_bulk(self, defns: list[AffixDefinition]) -> None:
        for d in defns:
            self.register_affix(d)

    def validate_state(self, state: CraftState) -> ValidationReport:
        errors, warnings = [], []
        for a in state.affixes:
            defn = self._affix_registry.get(a.affix_id)
            if defn is None:
                warnings.append(f"unknown affix: {a.affix_id}")
                continue
            if a.current_tier > defn.max_tier:
                errors.append(f"{a.affix_id}: tier {a.current_tier} exceeds max {defn.max_tier}")
            if defn.valid_item_classes and state.item_class not in defn.valid_item_classes:
                errors.append(f"{a.affix_id}: not valid for {state.item_class}")
        return ValidationReport(not errors, errors, warnings)

    def validate_bis_target(self, target: BisTarget) -> ValidationReport:
        errors, warnings = [], []
        for req in target.requirements:
            defn = self._affix_registry.get(req.affix_id)
            if defn is None:
                warnings.append(f"unknown affix in BIS target: {req.affix_id}")
            elif req.target_tier > defn.max_tier:
                errors.append(f"{req.affix_id}: target tier {req.target_tier} exceeds max {defn.max_tier}")
        return ValidationReport(not errors, errors, warnings)

    def get_available_affixes(self, item_class: str) -> list[str]:
        return [aid for aid, defn in self._affix_registry.items()
                if not defn.valid_item_classes or item_class in defn.valid_item_classes]

    def enrich_state(self, state: CraftState) -> CraftState:
        # Set max_tier from registry for each affix if known
        for a in state.affixes:
            defn = self._affix_registry.get(a.affix_id)
            if defn:
                a.max_tier = defn.max_tier
        return state
