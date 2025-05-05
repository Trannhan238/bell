"""
Drop season_config table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'drop_season_config'
down_revision = '54c61cbe8675'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table('season_config')

def downgrade():
    op.create_table(
        'season_config',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('school_id', sa.Integer, sa.ForeignKey('schools.id'), nullable=False),
        sa.Column('summer_start', sa.Date, nullable=False),
        sa.Column('summer_end', sa.Date, nullable=False),
        sa.Column('winter_start', sa.Date, nullable=True),
        sa.Column('winter_end', sa.Date, nullable=True)
    )