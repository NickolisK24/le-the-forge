from __future__ import annotations
from dataclasses import dataclass, asdict
import base64, importlib, json

# integration.import is a reserved keyword path; use importlib to import it.
_schema_module = importlib.import_module("integration.import.schemas.import_schema")
ImportSchema = _schema_module.ImportSchema


@dataclass
class ExportResult:
    format: str            # "json", "build_string", "url_param"
    content: str           # the exported string
    size_bytes: int
    build_name: str
    version: str


class BuildExporter:
    BASE_URL = "https://le-the-forge.app/build"   # placeholder, not called

    def to_json(self, schema: ImportSchema, indent: int = 2) -> ExportResult:
        """Serialize an ImportSchema to a pretty-printed JSON string."""
        d = asdict(schema)
        d["format"] = schema.format.value
        content = json.dumps(d, indent=indent)
        return ExportResult("json", content, len(content.encode()), schema.build_name, schema.version)

    def to_build_string(self, schema: ImportSchema) -> ExportResult:
        """Serialize an ImportSchema to a compact base64url-encoded build string."""
        d = asdict(schema)
        d["format"] = schema.format.value
        compact = json.dumps(d, separators=(",", ":"))
        encoded = base64.urlsafe_b64encode(compact.encode()).decode().rstrip("=")
        return ExportResult("build_string", encoded, len(encoded), schema.build_name, schema.version)

    def to_url_param(self, schema: ImportSchema) -> ExportResult:
        """Produce a shareable URL with the build encoded as a query parameter."""
        result = self.to_build_string(schema)
        url = f"{self.BASE_URL}?build={result.content}"
        return ExportResult("url_param", url, len(url), schema.build_name, schema.version)

    def roundtrip_check(self, schema: ImportSchema) -> bool:
        """Export to build_string, re-import, and verify build_name survives the round-trip."""
        _parser_module = importlib.import_module("integration.import.build_import_parser")
        BuildImportParser = _parser_module.BuildImportParser
        result = self.to_build_string(schema)
        parsed = BuildImportParser().parse_build_string(result.content)
        return (
            parsed.success
            and parsed.schema is not None
            and parsed.schema.build_name == schema.build_name
        )
