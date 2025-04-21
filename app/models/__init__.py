from .school import School
from .season import SeasonConfig  # Đảm bảo SeasonConfig được import sau School
from .user import User
from .device import Device
from .schedule import Schedule
from .profile import BellProfile
from .holiday import Holiday

# Chỉ import Holiday khi cần sử dụng
def get_holiday_model():
    from .holiday import Holiday
    return Holiday
