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

def get_devices_and_schools():
    """Fetch all devices and schools from the database."""
    devices = Device.query.all()
    schools = School.query.all()
    return devices, schools