"""Add requires column to passive_nodes

Revision ID: dd1840cac963
Revises: 654f2ebcd332
Create Date: 2026-04-18 00:00:00.000000

Stores directed parent requirements as JSON:
    [{"parent_id": str, "points": int}, ...]

A node unlocks once ANY listed parent has >= points allocated
(LE "OR-of-parents" rule). Empty list == tier root.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dd1840cac963"
down_revision = "654f2ebcd332"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("passive_nodes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("requires", sa.JSON(), nullable=False, server_default="[]")
        )


def downgrade():
    with op.batch_alter_table("passive_nodes", schema=None) as batch_op:
        batch_op.drop_column("requires")
