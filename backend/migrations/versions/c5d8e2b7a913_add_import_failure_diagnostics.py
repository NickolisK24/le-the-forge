"""Add diagnostics JSON to import_failures

Stores the structured failure record (stage, HTTP status, safe upstream
headers, missing-field evaluation state, app/data versions) so an import
failure can be diagnosed without guessing.

Revision ID: c5d8e2b7a913
Revises: a7c3e91f4d20
Create Date: 2026-10-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d8e2b7a913'
down_revision = 'a7c3e91f4d20'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('import_failures', sa.Column('diagnostics', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('import_failures', 'diagnostics')
