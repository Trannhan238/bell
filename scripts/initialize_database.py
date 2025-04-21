import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

def initialize_database():
    app = create_app()
    with app.app_context():
        # Tắt kiểm tra khóa ngoại (cho SQLite)
        db.session.execute("PRAGMA foreign_keys = OFF")
        db.drop_all()  # Drop all tables
        db.create_all()  # Recreate all tables
        # Bật lại chế độ kiểm tra khóa ngoại
        db.session.execute("PRAGMA foreign_keys = ON")
        db.session.commit()
        print("Database reset and initialized successfully.")

if __name__ == "__main__":
    initialize_database()
