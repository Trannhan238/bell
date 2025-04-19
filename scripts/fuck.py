import sqlite3

conn = sqlite3.connect("app/school_bell.db")  # sửa đường dẫn nếu cần
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO season_configs (school_id, summer_start, summer_end)
    VALUES (1, '2025-04-01', '2025-09-30');
""")

conn.commit()
conn.close()

print("✅ Đã chèn mùa hè cho school_id = 1")
