"""Typed, fail-closed errors for the canonical data boundary (AUDIT-R2).

Every error has a stable ``code`` (the R2 contract's loader rejection codes)
so that callers, tests and health reporting never match on message text.
None of these errors is ever caught and converted into a default value inside
this package.
"""
from __future__ import annotations


class CanonicalDataError(Exception):
    code = "CANONICAL_DATA_ERROR"

    def __init__(self, message: str, **context):
        super().__init__(message)
        self.context = context

    def to_dict(self) -> dict:
        return {"error": self.code, "message": str(self), **{k: v for k, v in self.context.items()}}


# --- manifest / bundle (contract L1-L4) -------------------------------------------
class ManifestMissing(CanonicalDataError):
    code = "MANIFEST_MISSING"


class ManifestInvalid(CanonicalDataError):
    code = "MANIFEST_INVALID"


class UnsupportedCanonicalSchema(CanonicalDataError):
    code = "SCHEMA_VERSION_UNSUPPORTED"


class ProvenanceMissing(CanonicalDataError):
    code = "PROVENANCE_MISSING"


# --- content / snapshot / patch (L5, L7) -------------------------------------------
class HashMismatch(CanonicalDataError):
    code = "CONTENT_HASH_MISMATCH"


class MixedSnapshot(CanonicalDataError):
    code = "MIXED_SNAPSHOT"


class MixedPatch(CanonicalDataError):
    code = "MIXED_PATCH"


# --- families (L8, L9, L11) -----------------------------------------------------------
class FamilyMissing(CanonicalDataError):
    code = "FAMILY_MISSING"


class FamilyDeclarationInvalid(CanonicalDataError):
    code = "FAMILY_DECLARATION_INVALID"


class UntrustedFamily(CanonicalDataError):
    code = "TRUST_REJECTED"


class CoverageInsufficient(CanonicalDataError):
    code = "COVERAGE_INSUFFICIENT"


class SchemaReviewRequired(CanonicalDataError):
    """A supported schema carries fields the adapter does not know (schema evolution)."""

    code = "SCHEMA_REVIEW_REQUIRED"


class ForeignSource(CanonicalDataError):
    code = "FOREIGN_SOURCE"


# --- identity / records / relationships (L10) -----------------------------------------
class InvalidIdentity(CanonicalDataError, ValueError):
    code = "INVALID_IDENTITY"


class DuplicateCanonicalId(CanonicalDataError):
    code = "DUPLICATE_CANONICAL_ID"


class CanonicalRecordMissing(CanonicalDataError, KeyError):
    code = "REFERENCE_NOT_FOUND"

    def __str__(self) -> str:  # KeyError would repr() the message
        return self.args[0] if self.args else self.code


class RelationshipIntegrityFailure(CanonicalDataError):
    code = "RELATIONSHIP_UNRESOLVED"


class StoreImmutable(CanonicalDataError, AttributeError):
    code = "STORE_IMMUTABLE"
