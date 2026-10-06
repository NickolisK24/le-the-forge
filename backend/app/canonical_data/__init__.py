"""AUDIT-R2 canonical data foundation (P01, P02, P03, P09, P17).

This package is the boundary between R1 canonical output and the Forge. It is
deliberately disconnected from production: the app factory does not import
it, no route or calculation reads it, and it never reads the legacy ``data/``
tree. It becomes an authority only at the R2 cutover (R2-P20).

Modules:
    errors          typed, fail-closed errors (stable ``code`` per error)
    ids             typed source identities (P03)
    trust           trust states and the consumption policy
    hashing         content hashing identical to R1 (r1_snapshot)
    manifest        CanonicalDataManifest and family declarations
    importer        R1 output -> immutable Forge bundle (P01)
    store           read-only, one-snapshot canonical store (P02)
    relationships   relationship and graph primitives (P09)
    schemas         per-schema identity adapters and known-field sets
    contracts       count-independent contract checks runnable on any bundle (P17)
"""
