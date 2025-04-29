# Tạo file migration mới sử dụng Alembic/Flask-Migrate
"""Thay đổi lịch từ khoảng thời gian sang điểm thời gian

Revision ID: [tự động tạo]
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Đổi tên start_time thành time_point
    op.alter_column('schedule', 'start_time', new_column_name='time_point')
    # Xóa cột end_time
    op.drop_column('schedule', 'end_time')
    # Đặt bell_type thành không nullable
    op.alter_column('schedule', 'bell_type', nullable=False)

def downgrade():
    # Thêm lại cột end_time
    op.add_column('schedule', sa.Column('end_time', sa.Time(), nullable=True))
    # Đổi tên time_point lại thành start_time
    op.alter_column('schedule', 'time_point', new_column_name='start_time')
    # Đặt bell_type thành nullable lại
    op.alter_column('schedule', 'bell_type', nullable=True)