import sqlite3

def check_schedule_for_today():
    conn = sqlite3.connect('data/school_bell.db')
    cursor = conn.cursor()

    # Lấy lịch chuông cho thứ Hai (day_of_week = 1)
    cursor.execute("SELECT * FROM schedule WHERE day_of_week = 1;")
    schedules = cursor.fetchall()

    if schedules:
        print("Schedules for today:")
        for schedule in schedules:
            print(schedule)
    else:
        print("No schedules found for today.")

    conn.close()

if __name__ == "__main__":
    check_schedule_for_today()