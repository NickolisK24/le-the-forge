"""add affix metadata columns

Revision ID: 8d9b7a5c2e11
Revises: 3ffd55fa24ac
Create Date: 2026-03-19 01:48:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d9b7a5c2e11"
down_revision = "3ffd55fa24ac"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("affix_defs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("class_requirement", sa.String(length=32), nullable=True))
        batch_op.add_column(
            sa.Column(
                "tags",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            )
        )

    with op.batch_alter_table("affix_defs", schema=None) as batch_op:
        batch_op.alter_column("tags", server_default=None)


def downgrade():
    with op.batch_alter_table("affix_defs", schema=None) as batch_op:
        batch_op.drop_column("tags")
        batch_op.drop_column("class_requirement")