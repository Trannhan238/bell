def validate_mac_address(mac_address):
    """Validate the format of a MAC address."""
    import re
    if not mac_address:
        return False
    # Regular expression for MAC address validation
    mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return re.match(mac_regex, mac_address) is not None

from app.models.device import Device
from app.models.school import School
from datetime import time, timedelta, datetime

def apply_winter_shift(base_time: time, date: datetime.date, shift_minutes: int) -> time:
    """
    Adjusts the base time by adding shift_minutes if the date is in winter months.

    :param base_time: The original time to adjust.
    :param date: The current date to check for winter months.
    :param shift_minutes: The number of minutes to shift the time.
    :return: Adjusted time if in winter months, else the original base time.
    """
    winter_months = {10, 11, 12, 1, 2, 3}  # October to March
    if date.month in winter_months:
        # Add shift_minutes to base_time
        full_datetime = datetime.combine(date, base_time) + timedelta(minutes=shift_minutes)
        return full_datetime.time()
    return base_time

def get_devices_and_schools():
    """Fetch all devices and schools from the database."""
    devices = Device.query.all()
    schools = School.query.all()
    return devices, schools