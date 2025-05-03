from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'add_foreign_key_school_id'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Use batch mode to recreate the table with the foreign key constraint
    with op.batch_alter_table('season_config', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_season_config_school',
            'schools',
            ['school_id'],
            ['id']
        )

def downgrade():
    # Use batch mode to drop the foreign key constraint
    with op.batch_alter_table('season_config', schema=None) as batch_op:
        batch_op.drop_constraint('fk_season_config_school', type_='foreignkey')