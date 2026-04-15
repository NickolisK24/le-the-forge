"""add blessings to builds

Revision ID: 654f2ebcd332
Revises: e2f3a4b5c6d1
Create Date: 2026-04-15 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "654f2ebcd332"
down_revision = "e2f3a4b5c6d1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("builds", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "blessings",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            )
        )

    with op.batch_alter_table("builds", schema=None) as batch_op:
        batch_op.alter_column("blessings", server_default=None)


def downgrade():
    with op.batch_alter_table("builds", schema=None) as batch_op:
        batch_op.drop_column("blessings")
