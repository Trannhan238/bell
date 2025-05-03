import sqlite3

def inspect_foreign_keys(database_path, table_name):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        # Query to fetch foreign key details for the specified table
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()
        print(f"Foreign keys in table '{table_name}':")
        for fk in foreign_keys:
            print(fk)
        conn.close()
    except sqlite3.Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    database_path = "data/school_bell.db"
    table_name = "season_config"
    inspect_foreign_keys(database_path, table_name)