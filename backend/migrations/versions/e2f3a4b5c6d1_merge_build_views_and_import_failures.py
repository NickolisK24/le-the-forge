"""Merge build_views and import_failures heads

Revision ID: e2f3a4b5c6d1
Revises: b2f8a3d1c7e9, d1e2f3a4b5c6
Create Date: 2026-04-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2f3a4b5c6d1'
down_revision = ('b2f8a3d1c7e9', 'd1e2f3a4b5c6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
