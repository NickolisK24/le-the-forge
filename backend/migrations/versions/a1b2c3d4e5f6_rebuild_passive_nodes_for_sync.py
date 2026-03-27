"""Rebuild passive_nodes table for game-data sync

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-03-27 00:00:00.000000

Changes:
  - id: Integer → String(16)  (namespaced e.g. "ac_0")
  - Add raw_node_id Integer
  - Add mastery_index SmallInteger
  - Add mastery_requirement SmallInteger
  - Add stats JSON
  - Add ability_granted String(128)
  - Add icon String(32)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    # Drop and recreate the table — it's seeded data with no FK dependents,
    # so a full rebuild is simpler than a series of ALTER operations.
    op.drop_table('passive_nodes')
    op.create_table(
        'passive_nodes',
        sa.Column('id', sa.String(length=16), nullable=False),
        sa.Column('raw_node_id', sa.Integer(), nullable=False),
        sa.Column('character_class', sa.String(length=32), nullable=False),
        sa.Column('mastery', sa.String(length=32), nullable=True),
        sa.Column('mastery_index', sa.SmallInteger(), nullable=False),
        sa.Column('mastery_requirement', sa.SmallInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('node_type', sa.String(length=16), nullable=False),
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('max_points', sa.SmallInteger(), nullable=False),
        sa.Column('connections', sa.JSON(), nullable=False),
        sa.Column('stats', sa.JSON(), nullable=True),
        sa.Column('ability_granted', sa.String(length=128), nullable=True),
        sa.Column('icon', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('passive_nodes')
    op.create_table(
        'passive_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_class', sa.String(length=32), nullable=False),
        sa.Column('mastery', sa.String(length=32), nullable=True),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('node_type', sa.String(length=16), nullable=False),
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('max_points', sa.SmallInteger(), nullable=False),
        sa.Column('connections', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
