"""Known migration-chain debt, measured on PostgreSQL 16 (AUDIT-R2 P15, finding DB-5).

These registries are a ratchet: a new broken downgrade, new lossy step or new
schema drift fails the PostgreSQL suite, and an entry that stops being true
also fails (so the registry is updated when debt is paid). Migration files
are not modified by P15; fixing them is a later, explicit change.
"""

# revision -> why downgrading it fails
KNOWN_BROKEN_DOWNGRADES = {
    "3ffd55fa24ac": "downgrade calls op.drop_constraint(None, ...): SQLAlchemy cannot emit DROP CONSTRAINT "
                    "for an unnamed constraint (DB-5)",
}

# revision -> why its downgrade destroys data even though it succeeds on an empty database
KNOWN_LOSSY_DOWNGRADES = {
    "a1b2c3d4e5f6": "passive_nodes is dropped and rebuilt (int id -> String(16)); downgrade recreates the old "
                    "schema empty",
}

# (table, column, kind): model vs migrated-schema differences found by alembic autogenerate
KNOWN_SCHEMA_DRIFT = frozenset({
    ("import_failures", "missing_fields", "modify_default"),
    ("import_failures", "created_at", "modify_default"),
    ("import_failures", "updated_at", "modify_default"),
    ("passive_nodes", "requires", "modify_default"),
    ("users", "is_admin", "modify_default"),
})
