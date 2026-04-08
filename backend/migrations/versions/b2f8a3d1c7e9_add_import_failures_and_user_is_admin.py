"""add import_failures table and user is_admin

Revision ID: b2f8a3d1c7e9
Revises: a1b2c3d4e5f6
Create Date: 2026-04-08 19:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f8a3d1c7e9'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_admin to users
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))

    # Create import_failures table
    op.create_table(
        'import_failures',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source', sa.String(32), nullable=False),
        sa.Column('raw_url', sa.String(2048), nullable=False),
        sa.Column('missing_fields', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('partial_data', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('error_message', sa.String(1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('import_failures')
    op.drop_column('users', 'is_admin')
