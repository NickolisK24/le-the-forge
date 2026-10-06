"""Cascade build_views rows when their build is deleted

Deleting a build that had view records failed: the ORM tried to null
build_views.build_id, which is NOT NULL. View rows belong to their build,
so the foreign key now cascades on delete.

Revision ID: a7c3e91f4d20
Revises: dd1840cac963
Create Date: 2026-10-06 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a7c3e91f4d20'
down_revision = 'dd1840cac963'
branch_labels = None
depends_on = None

FK_NAME = 'build_views_build_id_fkey'


def upgrade():
    with op.batch_alter_table('build_views') as batch_op:
        batch_op.drop_constraint(FK_NAME, type_='foreignkey')
        batch_op.create_foreign_key(
            FK_NAME, 'builds', ['build_id'], ['id'], ondelete='CASCADE',
        )


def downgrade():
    with op.batch_alter_table('build_views') as batch_op:
        batch_op.drop_constraint(FK_NAME, type_='foreignkey')
        batch_op.create_foreign_key(FK_NAME, 'builds', ['build_id'], ['id'])
