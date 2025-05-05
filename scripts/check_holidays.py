import sqlite3

def check_holidays_for_today():
    conn = sqlite3.connect('data/school_bell.db')
    cursor = conn.cursor()

    # Kiểm tra ngày nghỉ cho ngày 5/5/2025
    query = """
    SELECT * FROM holidays 
    WHERE start_date <= '2025-05-05' AND end_date >= '2025-05-05';
    """
    cursor.execute(query)
    holidays = cursor.fetchall()

    if holidays:
        print("Holidays for today:")
        for holiday in holidays:
            print(holiday)
    else:
        print("No holidays found for today.")

    conn.close()

if __name__ == "__main__":
    check_holidays_for_today()