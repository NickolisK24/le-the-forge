from __future__ import annotations
from dataclasses import dataclass, field
import base64, importlib, json, urllib.parse

# integration.import is a reserved keyword path; use importlib to import it.
_schema_module = importlib.import_module("integration.import.schemas.import_schema")
ImportSchema = _schema_module.ImportSchema
ImportFormat = _schema_module.ImportFormat
SchemaValidator = _schema_module.SchemaValidator
ValidationResult = _schema_module.ValidationResult


@dataclass
class ParseResult:
    success: bool
    schema: ImportSchema | None
    validation: ValidationResult | None
    raw_data: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class BuildImportParser:
    def __init__(self):
        self._validator = SchemaValidator()

    def parse_json(self, json_str: str) -> ParseResult:
        """Parse raw JSON string, validate, and return a ParseResult."""
        try:
            raw = json.loads(json_str)
        except json.JSONDecodeError as e:
            return ParseResult(success=False, schema=None, validation=None, errors=[str(e)])
        schema = self._validator.from_json(raw)
        validation = self._validator.validate(schema)
        return ParseResult(
            success=validation.valid,
            schema=schema,
            validation=validation,
            raw_data=raw,
            errors=validation.errors,
        )

    def parse_build_string(self, build_string: str) -> ParseResult:
        """Decode a base64url-encoded JSON build string and parse it.

        Pads the string as needed before decoding.
        """
        try:
            # Restore stripped padding
            padding_needed = (4 - len(build_string) % 4) % 4
            padded = build_string + "=" * padding_needed
            decoded_bytes = base64.urlsafe_b64decode(padded)
            json_str = decoded_bytes.decode("utf-8")
        except Exception as e:
            return ParseResult(
                success=False,
                schema=None,
                validation=None,
                errors=[f"base64 decode error: {e}"],
            )
        return self.parse_json(json_str)

    def parse_url(self, url: str) -> ParseResult:
        """Extract the 'build' query parameter from a URL and parse it.

        Tries JSON first, then build_string (base64) decoding.
        """
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if "build" not in params:
            return ParseResult(
                success=False,
                schema=None,
                validation=None,
                errors=["no 'build' query parameter found in URL"],
            )
        build_value = params["build"][0]
        # Try JSON first
        try:
            json.loads(build_value)
            return self.parse_json(build_value)
        except json.JSONDecodeError:
            pass
        # Fall back to build_string (base64)
        return self.parse_build_string(build_value)

    def parse(self, data: str, format: ImportFormat | None = None) -> ParseResult:
        """Parse build data, auto-detecting format when format is None.

        Detection order:
          - starts with "http" → URL
          - valid base64 and not valid JSON → build_string
          - else → JSON
        """
        if format is not None:
            if format == ImportFormat.URL:
                return self.parse_url(data)
            if format == ImportFormat.BUILD_STRING:
                return self.parse_build_string(data)
            return self.parse_json(data)

        # Auto-detect
        if data.startswith("http"):
            return self.parse_url(data)

        # Check if it's valid JSON
        is_json = True
        try:
            json.loads(data)
        except json.JSONDecodeError:
            is_json = False

        if not is_json:
            # Attempt base64 decode to confirm it's a build_string
            try:
                padding_needed = (4 - len(data) % 4) % 4
                base64.urlsafe_b64decode(data + "=" * padding_needed)
                return self.parse_build_string(data)
            except Exception:
                pass

        return self.parse_json(data)
