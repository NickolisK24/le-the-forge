from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import json, re


class ImportFormat(Enum):
    JSON = "json"
    BUILD_STRING = "build_string"    # base64-encoded compact format
    URL = "url"


@dataclass
class SkillEntry:
    skill_id: str
    level: int = 1
    quality: int = 0
    enabled: bool = True


@dataclass
class GearEntry:
    slot: str
    item_id: str
    affixes: list[str] = field(default_factory=list)


@dataclass
class PassiveEntry:
    node_id: str
    allocated: bool = True


@dataclass
class ImportSchema:
    format: ImportFormat
    version: str          # e.g. "1.0", "2.1"
    build_name: str
    character_class: str
    skills: list[SkillEntry] = field(default_factory=list)
    passives: list[PassiveEntry] = field(default_factory=list)
    gear: list[GearEntry] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SchemaValidator:
    VALID_SLOTS = {
        "helm", "chest", "gloves", "boots", "belt",
        "ring1", "ring2", "amulet", "weapon1", "weapon2", "offhand",
    }

    def validate(self, schema: ImportSchema) -> ValidationResult:
        errors = []
        warnings = []
        if not schema.build_name.strip():
            errors.append("build_name cannot be empty")
        if not schema.character_class.strip():
            errors.append("character_class cannot be empty")
        if not re.match(r'^\d+\.\d+$', schema.version):
            errors.append(f"invalid version format: {schema.version}")
        for s in schema.skills:
            if not s.skill_id:
                errors.append("skill_id cannot be empty")
            if not (1 <= s.level <= 20):
                errors.append(f"skill {s.skill_id}: level must be 1-20")
            if not (0 <= s.quality <= 20):
                warnings.append(f"skill {s.skill_id}: quality {s.quality} outside typical range")
        for g in schema.gear:
            if g.slot not in self.VALID_SLOTS:
                errors.append(f"invalid gear slot: {g.slot}")
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def from_json(self, data: str | dict) -> ImportSchema:
        """Parse JSON string or dict into ImportSchema.

        Handles missing optional keys with defaults.
        """
        if isinstance(data, str):
            data = json.loads(data)
        format_str = data.get("format", "json")
        fmt = (
            ImportFormat(format_str)
            if format_str in [e.value for e in ImportFormat]
            else ImportFormat.JSON
        )
        skills = [SkillEntry(**s) for s in data.get("skills", [])]
        passives = [PassiveEntry(**p) for p in data.get("passives", [])]
        gear = [GearEntry(**g) for g in data.get("gear", [])]
        return ImportSchema(
            format=fmt,
            version=str(data.get("version", "1.0")),
            build_name=str(data.get("build_name", "")),
            character_class=str(data.get("character_class", "")),
            skills=skills,
            passives=passives,
            gear=gear,
            metadata=data.get("metadata", {}),
        )
