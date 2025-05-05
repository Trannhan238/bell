import sqlite3

def check_device(mac_address):
    conn = sqlite3.connect('data/school_bell.db')
    cursor = conn.cursor()

    # Kiểm tra thông tin thiết bị với địa chỉ MAC
    query = """
    SELECT * FROM devices WHERE mac_address = ?;
    """
    cursor.execute(query, (mac_address,))
    device = cursor.fetchone()

    if device:
        print("Device information:")
        print(device)
    else:
        print("No device found with the given MAC address.")

    conn.close()

if __name__ == "__main__":
    mac_address = input("Enter the MAC address of the device: ")
    check_device(mac_address)