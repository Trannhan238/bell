"""Add profile_id to Schedule

Revision ID: 71d148317f24
Revises: 21f52afd05d3
Create Date: 2025-04-19 19:31:58.597539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71d148317f24'
down_revision = '21f52afd05d3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('schedule', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_schedule_profile',  # Add a name for the foreign key constraint
            'bell_profiles',  # Referenced table
            ['profile_id'],  # Local column
            ['id']  # Referenced column
        )


def downgrade():
    with op.batch_alter_table('schedule', schema=None) as batch_op:
        batch_op.drop_constraint('fk_schedule_profile', type_='foreignkey')  # Use the same name as above
        batch_op.drop_column('profile_id')
