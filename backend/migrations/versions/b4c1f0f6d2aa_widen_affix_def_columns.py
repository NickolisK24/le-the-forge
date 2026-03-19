"""widen affix def columns

Revision ID: b4c1f0f6d2aa
Revises: 8d9b7a5c2e11
Create Date: 2026-03-19 01:52:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b4c1f0f6d2aa"
down_revision = "8d9b7a5c2e11"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("affix_defs", schema=None) as batch_op:
        batch_op.alter_column(
            "name",
            existing_type=sa.String(length=64),
            type_=sa.String(length=80),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "affix_type",
            existing_type=sa.String(length=8),
            type_=sa.String(length=16),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("affix_defs", schema=None) as batch_op:
        batch_op.alter_column(
            "affix_type",
            existing_type=sa.String(length=16),
            type_=sa.String(length=8),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "name",
            existing_type=sa.String(length=80),
            type_=sa.String(length=64),
            existing_nullable=False,
        )