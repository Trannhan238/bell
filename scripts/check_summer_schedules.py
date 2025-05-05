import sqlite3

def check_summer_schedules():
    conn = sqlite3.connect('data/school_bell.db')
    cursor = conn.cursor()

    # Kiểm tra lịch chuông với is_summer=True
    query = """
    SELECT * FROM schedule WHERE is_summer = 1;
    """
    cursor.execute(query)
    schedules = cursor.fetchall()

    if schedules:
        print("Summer schedules:")
        for schedule in schedules:
            print(schedule)
    else:
        print("No summer schedules found.")

    conn.close()

if __name__ == "__main__":
    check_summer_schedules()