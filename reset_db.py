from app import db
from flask import Flask
import os
from datetime import time

# Tạo app instance tạm thời nếu cần
def create_app():
    app = Flask(__name__)
    
    # Cấu hình database với đường dẫn cụ thể
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'school_bell.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Tạo thư mục data nếu chưa tồn tại
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Khởi tạo extensions
    db.init_app(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()  # Drop all tables
        db.create_all()  # Recreate all tables
        print("Database reset and initialized successfully.")
