"""Remove instability and fracture columns for modern Last Epoch

Revision ID: f1a2b3c4d5e6
Revises: 21bc975a3016
Create Date: 2026-03-22 04:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '21bc975a3016'
branch_labels = None
depends_on = None


def upgrade():
    # Remove instability and fracture columns from craft_sessions
    with op.batch_alter_table('craft_sessions', schema=None) as batch_op:
        batch_op.drop_column('instability')
        batch_op.drop_column('is_fractured')

    # Remove instability and fracture columns from craft_steps
    with op.batch_alter_table('craft_steps', schema=None) as batch_op:
        batch_op.drop_column('instability_before')
        batch_op.drop_column('instability_after')
        batch_op.drop_column('fracture_risk_pct')


def downgrade():
    # Add back the columns (for rollback purposes)
    with op.batch_alter_table('craft_steps', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fracture_risk_pct', sa.Float(), nullable=False, default=0.0))
        batch_op.add_column(sa.Column('instability_after', sa.SmallInteger(), nullable=False, default=0))
        batch_op.add_column(sa.Column('instability_before', sa.SmallInteger(), nullable=False, default=0))

    with op.batch_alter_table('craft_sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_fractured', sa.Boolean(), nullable=False, default=False))
        batch_op.add_column(sa.Column('instability', sa.SmallInteger(), nullable=False, default=0))