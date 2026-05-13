"""Audit v2 class/mastery skill references against v2 skill identities.

This is a read-only Phase 9.5 diagnostic. It reports whether class/mastery
`skill_path:*` references can be deterministically aligned to generated v2 skill
records without changing runtime behavior or introducing inferred bridges.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_CLASS_MASTERY_BUNDLE = Path("docs/generated/v2_class_mastery_bundle.json")
DEFAULT_SKILL_BUNDLE = Path("docs/generated/v2_skill_bundle.json")
DEFAULT_SKILL_TREE_BUNDLE = Path("docs/generated/v2_skill_tree_bundle.json")
DEFAULT_SOURCE_CLASSES = Path("D:/Forge/last-epoch-data/exports_json/classes.json")
DEFAULT_SOURCE_SKILLS = Path("D:/Forge/last-epoch-data/exports_json/skills_with_trees.json")
DEFAULT_OUTPUT = Path("docs/generated/v2_skill_identity_alignment_report.json")
DEFAULT_MARKDOWN_OUTPUT = Path("docs/migration/V2_SKILL_IDENTITY_ALIGNMENT.md")

PATH_ID_RE = re.compile(r"(?:pathId|PathID|Ability)\D*(\d+)")
TOP_LEVEL_PATH_FIELDS = {
    "abilityPathId",
    "pathId",
    "sourcePathId",
    "source_path_id",
    "skillPathId",
    "skill_path_id",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, report: dict[str, Any], command: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    fields = report["field_inventory"]
    lines = [
        "# v2 Skill Identity Alignment",
        "",
        "## Purpose",
        "",
        "This Phase 9.5 audit diagnoses the class/mastery to skill identity mismatch reported during Phase 9. It does not create a runtime bridge, change generators, or alter planner behavior.",
        "",
        "## Generation Command",
        "",
        "```powershell",
        command,
        "```",
        "",
        "## Summary",
        "",
        f"- Total class/mastery skill references: {summary['total_class_mastery_skill_references']}",
        f"- Total skill records: {summary['total_skill_records']}",
        f"- Exact ID matches: {summary['exact_id_match_count']}",
        f"- Exact raw path matches: {summary['exact_path_match_count']}",
        f"- Top-level path matches: {summary['top_level_path_match_count']}",
        f"- Nested path-only matches: {summary['nested_path_only_match_count']}",
        f"- Normalized name matches: {summary['normalized_name_match_count']}",
        f"- Ambiguous matches: {summary['ambiguous_match_count']}",
        f"- Unresolved references: {summary['unresolved_reference_count']}",
        f"- Bridge safe: {str(summary['bridge_safe']).lower()}",
        f"- Recommended mapping strategy: `{summary['recommended_mapping_strategy']}`",
        "",
        "## Field Inventory",
        "",
        "Class/mastery records use these fields for skill references:",
        "",
        *[f"- `{field}`" for field in fields["class_mastery_skill_reference_fields"]],
        "",
        "Skill records expose these source identity fields:",
        "",
        *[f"- `{field}`" for field in fields["skill_identity_fields"]],
        "",
        "Raw skill records expose these observed path-like fields:",
        "",
        *[f"- `{field}`" for field in fields["raw_skill_path_like_fields"][:50]],
        "",
        "## What Matched",
        "",
        "Exact ID matching did not resolve the class/mastery `skill_path:*` references because generated v2 skills use source skill IDs such as `skill:ab0lh`, not numeric path IDs.",
        "",
        "Raw path matching now includes upstream `sourceIdentity.skillPath` when present. Those top-level matches are accepted as safe identity evidence. Nested path evidence is still not accepted as a bridge.",
        "",
        "Normalized name matching cannot resolve these references because the class/mastery `skill_path:*` values do not include display names.",
        "",
        "## Examples",
        "",
        "### Resolved By Safe Identity",
        "",
        *(_reference_lines(report["examples"]["resolved_records"]) or ["- None"]),
        "",
        "### Nested Path Matches Not Accepted As A Bridge",
        "",
        *(_reference_lines(report["examples"]["nested_path_only_records"]) or ["- None"]),
        "",
        "### Ambiguous",
        "",
        *(_reference_lines(report["examples"]["ambiguous_records"]) or ["- None"]),
        "",
        "### Unresolved",
        "",
        *_reference_lines(report["examples"]["unresolved_records"]),
        "",
        "## Conclusion",
        "",
        "A complete deterministic bridge is still not safe from the current evidence. The enriched upstream export resolves the references that have top-level `sourceIdentity.skillPath` evidence, but remaining unresolved or ambiguous references must stay blocked.",
        "",
        "## Recommended Next Action",
        "",
        "Before modifier/stat normalization consumes class/mastery skill ownership, either resolve the remaining source gaps upstream or carry them as an explicit identity gap. Do not infer the remaining bridge from nested summoned actor evidence or tooltip text.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _reference_lines(records: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for record in records:
        status = record.get("status")
        reference = record.get("class_mastery_skill_reference")
        owners = ", ".join(record.get("owners", [])[:3])
        matches = record.get("candidate_skill_ids") or []
        suffix = f" -> {', '.join(matches[:3])}" if matches else ""
        lines.append(f"- `{reference}` ({status}; owners: {owners or 'none'}){suffix}")
    return lines


def _normalize_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _class_mastery_skill_references(bundle: dict[str, Any]) -> tuple[dict[str, set[str]], set[str]]:
    references: dict[str, set[str]] = defaultdict(set)
    fields: set[str] = set()
    records = bundle.get("records", {})
    for kind in ("classes", "masteries"):
        for record in records.get(kind, []):
            owner = str(record.get("canonical_id") or record.get("display_name") or kind)
            for field in ("linked_skill_source_ids", "skill_ids"):
                values = record.get(field) or []
                if values:
                    fields.add(field)
                for value in values:
                    if isinstance(value, str) and (value.startswith("skill_path:") or value.startswith("skill:")):
                        references[value].add(owner)
    return references, fields


def _skill_records(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    records = bundle.get("records", {})
    return list(records.get("skills", []))


def _raw_skills(source_skills: dict[str, Any]) -> list[dict[str, Any]]:
    skills = source_skills.get("skills", [])
    return skills if isinstance(skills, list) else []


def _walk_path_ids(value: Any, path: list[str], hits: list[dict[str, Any]], path_fields: set[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if "path" in key.lower() or "ability" in key.lower():
                path_fields.add(".".join(path + [str(key)]))
            _walk_path_ids(child, path + [str(key)], hits, path_fields)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _walk_path_ids(child, path + [str(index)], hits, path_fields)
        return

    found: set[str] = set()
    if isinstance(value, int):
        found.add(str(value))
    elif isinstance(value, str):
        if value.isdigit():
            found.add(value)
        found.update(match.group(1) for match in PATH_ID_RE.finditer(value))
    for path_id in found:
        field_path = ".".join(path)
        hits.append(
            {
                "path_id": path_id,
                "field_path": field_path,
                "top_level_identity": len(path) == 1 and path[0] in TOP_LEVEL_PATH_FIELDS,
                "value": value,
            }
        )


def _build_skill_identity_index(skill_records: list[dict[str, Any]], raw_skills: list[dict[str, Any]]) -> dict[str, Any]:
    by_canonical_id = {skill.get("canonical_id"): skill for skill in skill_records if skill.get("canonical_id")}
    by_source_id = {
        f"skill:{skill.get('source_skill_id')}": skill.get("canonical_id")
        for skill in skill_records
        if skill.get("source_skill_id")
    }
    by_normalized_name: dict[str, set[str]] = defaultdict(set)
    raw_by_source_id = {raw.get("id"): raw for raw in raw_skills if raw.get("id")}
    path_matches: dict[str, list[dict[str, Any]]] = defaultdict(list)
    path_like_fields: set[str] = set()

    for skill in skill_records:
        canonical_id = skill.get("canonical_id")
        if not canonical_id:
            continue
        for value in (skill.get("display_name"), skill.get("source_skill_id")):
            normalized = _normalize_name(value)
            if normalized:
                by_normalized_name[normalized].add(canonical_id)
        raw = raw_by_source_id.get(skill.get("source_skill_id"))
        if raw:
            raw_identity = raw.get("sourceIdentity") if isinstance(raw.get("sourceIdentity"), dict) else {}
            raw_skill_path = raw_identity.get("skillPath")
            if isinstance(raw_skill_path, str) and raw_skill_path.startswith("skill_path:"):
                raw_path_id = raw_skill_path.split(":", 1)[1]
                path_matches[raw_path_id].append(
                    {
                        "skill_id": canonical_id,
                        "source_skill_id": skill.get("source_skill_id"),
                        "display_name": skill.get("display_name"),
                        "field_path": "sourceIdentity.skillPath",
                        "top_level_identity": True,
                        "identity_source": raw_identity.get("identitySource"),
                        "identity_confidence": raw_identity.get("identityConfidence"),
                    }
                )
                path_like_fields.add("sourceIdentity.skillPath")
            raw_tree = raw.get("skillTree") if isinstance(raw.get("skillTree"), dict) else {}
            for value in (raw.get("name"), raw.get("_mName"), raw_tree.get("ability")):
                normalized = _normalize_name(value)
                if normalized:
                    by_normalized_name[normalized].add(canonical_id)
            raw_for_nested_scan = {
                key: value
                for key, value in raw.items()
                if key not in {"sourceIdentity", "source_ability_path_id", "source_tree_path_id"}
            }
            hits: list[dict[str, Any]] = []
            _walk_path_ids(raw_for_nested_scan, [], hits, path_like_fields)
            for hit in hits:
                path_matches[hit["path_id"]].append(
                    {
                        "skill_id": canonical_id,
                        "source_skill_id": skill.get("source_skill_id"),
                        "display_name": skill.get("display_name"),
                        "field_path": hit["field_path"],
                        "top_level_identity": hit["top_level_identity"],
                    }
                )

    return {
        "by_canonical_id": by_canonical_id,
        "by_source_id": by_source_id,
        "by_normalized_name": by_normalized_name,
        "path_matches": path_matches,
        "raw_skill_path_like_fields": sorted(path_like_fields),
    }


def _numeric_skill_path(reference: str) -> str | None:
    if not reference.startswith("skill_path:"):
        return None
    value = reference.split(":", 1)[1]
    return value if value.isdigit() else None


def build_report(
    class_mastery_bundle: dict[str, Any],
    skill_bundle: dict[str, Any],
    skill_tree_bundle: dict[str, Any],
    source_classes: dict[str, Any],
    source_skills: dict[str, Any],
) -> dict[str, Any]:
    references, reference_fields = _class_mastery_skill_references(class_mastery_bundle)
    skills = _skill_records(skill_bundle)
    raw_skill_records = _raw_skills(source_skills)
    index = _build_skill_identity_index(skills, raw_skill_records)

    results: list[dict[str, Any]] = []
    exact_id_count = 0
    exact_path_count = 0
    top_level_path_count = 0
    normalized_name_count = 0
    nested_path_only_count = 0
    ambiguous_count = 0
    unresolved_count = 0
    path_context_counter: Counter[str] = Counter()

    for reference in sorted(references):
        numeric = _numeric_skill_path(reference)
        exact_id = index["by_source_id"].get(reference)
        path_hits = index["path_matches"].get(numeric or "", [])
        path_skill_ids = sorted({hit["skill_id"] for hit in path_hits})
        top_level_hits = [hit for hit in path_hits if hit.get("top_level_identity")]
        top_level_skill_ids = sorted({hit["skill_id"] for hit in top_level_hits})
        normalized_name_hits = sorted(index["by_normalized_name"].get(_normalize_name(reference), set()))

        for hit in path_hits:
            path_context_counter[hit["field_path"]] += 1

        candidate_ids: set[str] = set()
        match_methods: list[str] = []
        safe_candidate_ids: set[str] = set()
        if exact_id:
            candidate_ids.add(exact_id)
            safe_candidate_ids.add(exact_id)
            exact_id_count += 1
            match_methods.append("exact_id")
        if path_skill_ids:
            exact_path_count += 1
            match_methods.append("exact_path")
        if top_level_skill_ids:
            candidate_ids.update(top_level_skill_ids)
            safe_candidate_ids.update(top_level_skill_ids)
            top_level_path_count += 1
            match_methods.append("top_level_path")
        if normalized_name_hits and not safe_candidate_ids:
            candidate_ids.update(normalized_name_hits)
            normalized_name_count += 1
            match_methods.append("normalized_name")
        if path_skill_ids and not safe_candidate_ids:
            candidate_ids.update(path_skill_ids)

        has_safe_identity_match = bool(safe_candidate_ids)
        if len(candidate_ids) > 1:
            status = "ambiguous"
            ambiguous_count += 1
        elif len(candidate_ids) == 1:
            if has_safe_identity_match:
                status = "resolved"
            else:
                status = "nested_path_match_not_bridge_safe"
                nested_path_only_count += 1
        else:
            status = "unresolved"
            unresolved_count += 1

        results.append(
            {
                "class_mastery_skill_reference": reference,
                "owners": sorted(references[reference]),
                "status": status,
                "match_methods": match_methods,
                "candidate_skill_ids": sorted(candidate_ids),
                "exact_id_match": exact_id,
                "exact_path_matches": path_hits[:10],
                "normalized_name_matches": normalized_name_hits,
            }
        )

    total = len(results)
    bridge_safe = total > 0 and unresolved_count == 0 and ambiguous_count == 0 and (
        exact_id_count == total or top_level_path_count == total
    )
    if bridge_safe:
        strategy = "safe_deterministic_bridge_possible"
    elif top_level_path_count:
        strategy = "top_level_source_identity_partial_unresolved"
    elif exact_path_count:
        strategy = "do_not_bridge_from_nested_path_evidence"
    else:
        strategy = "source_identity_gap_requires_upstream_alignment"

    source_data_missing = unresolved_count > 0 or top_level_path_count == 0

    return {
        "summary": {
            "total_class_mastery_skill_references": total,
            "total_skill_records": len(skills),
            "exact_id_match_count": exact_id_count,
            "exact_path_match_count": exact_path_count,
            "top_level_path_match_count": top_level_path_count,
            "nested_path_only_match_count": nested_path_only_count,
            "normalized_name_match_count": normalized_name_count,
            "ambiguous_match_count": ambiguous_count,
            "unresolved_reference_count": unresolved_count,
            "bridge_safe": bridge_safe,
            "source_data_missing": source_data_missing,
            "recommended_mapping_strategy": strategy,
            "production_consumed": False,
        },
        "field_inventory": {
            "class_mastery_skill_reference_fields": sorted(reference_fields),
            "skill_identity_fields": [
                "canonical_id",
                "display_name",
                "source_skill_id",
                "raw_reference.source_skill_id",
                "skill_tree_id",
            ],
            "raw_class_skill_reference_fields": [
                "classes[].abilities.defaultPathIds",
                "classes[].abilities.knownPathIds",
                "classes[].abilities.unlockable[].abilityPathId",
                "classes[].masteries[].masteryAbilityPathId",
            ],
            "raw_skill_path_like_fields": index["raw_skill_path_like_fields"],
            "top_path_match_contexts": [
                {"field_path": path, "match_count": count} for path, count in path_context_counter.most_common(20)
            ],
        },
        "references": results,
        "examples": {
            "resolved_records": [record for record in results if record["status"] == "resolved"][:10],
            "nested_path_only_records": [
                record for record in results if record["status"] == "nested_path_match_not_bridge_safe"
            ][:10],
            "unresolved_records": [record for record in results if record["status"] == "unresolved"][:10],
            "ambiguous_records": [record for record in results if record["status"] == "ambiguous"][:10],
        },
        "metadata": {
            "source": "v2_class_mastery_bundle + v2_skill_bundle + source exports",
            "read_only": True,
            "experimental": True,
            "production_safe": False,
            "generated_on": datetime.now(UTC).date().isoformat(),
            "source_class_count": len(source_classes.get("classes", [])) if isinstance(source_classes, dict) else None,
            "source_skill_count": len(raw_skill_records),
        },
    }


def _command_for_docs(args: argparse.Namespace) -> str:
    return (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_skill_identity_alignment.py "
        f"--class-mastery-bundle {args.class_mastery_bundle} "
        f"--skill-bundle {args.skill_bundle} "
        f"--skill-tree-bundle {args.skill_tree_bundle} "
        f"--source-classes {args.source_classes} "
        f"--source-skills {args.source_skills} "
        f"--output {args.output} "
        f"--markdown-output {args.markdown_output}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--class-mastery-bundle", type=Path, default=DEFAULT_CLASS_MASTERY_BUNDLE)
    parser.add_argument("--skill-bundle", type=Path, default=DEFAULT_SKILL_BUNDLE)
    parser.add_argument("--skill-tree-bundle", type=Path, default=DEFAULT_SKILL_TREE_BUNDLE)
    parser.add_argument("--source-classes", type=Path, default=DEFAULT_SOURCE_CLASSES)
    parser.add_argument("--source-skills", type=Path, default=DEFAULT_SOURCE_SKILLS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        _read_json(args.class_mastery_bundle),
        _read_json(args.skill_bundle),
        _read_json(args.skill_tree_bundle),
        _read_json(args.source_classes),
        _read_json(args.source_skills),
    )
    _write_json(args.output, report)
    _write_markdown(args.markdown_output, report, _command_for_docs(args))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
