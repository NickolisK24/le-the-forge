"""Add build_views table and last_viewed_at column

Revision ID: d1e2f3a4b5c6
Revises: f8953bcaab80
Create Date: 2026-04-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = 'f8953bcaab80'
branch_labels = None
depends_on = None


def upgrade():
    # Add last_viewed_at to builds
    op.add_column('builds', sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True))

    # Create build_views table
    op.create_table(
        'build_views',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('build_id', sa.String(36), sa.ForeignKey('builds.id'), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('viewer_ip_hash', sa.String(64), nullable=False),
    )
    op.create_index('ix_build_views_build_id', 'build_views', ['build_id'])


def downgrade():
    op.drop_index('ix_build_views_build_id', table_name='build_views')
    op.drop_table('build_views')
    op.drop_column('builds', 'last_viewed_at')
