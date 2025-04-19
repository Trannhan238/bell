# scripts/create_default_admins.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.school import School

def create_default_users():
    app = create_app()
    with app.app_context():
        # Tạo cơ sở dữ liệu nếu chưa tồn tại
        db.create_all()

        users = [
            {"username": "admin", "role": "admin"},
            {"username": "ad1", "role": "school_user"},
            {"username": "ad2", "role": "school_user"},
            {"username": "ad3", "role": "school_user"},
        ]
        
        for u in users:
            if not User.query.filter_by(username=u["username"]).first():
                user = User(
                    username=u["username"],
                    role=u["role"],
                    full_name=u["username"].upper()
                )
                user.set_password("123")
                db.session.add(user)
                print(f"Created user {u['username']} with role {u['role']}")
            else:
                existing_user = User.query.filter_by(username=u["username"]).first()
                print(f"User {existing_user.username} already exists with role {existing_user.role}.")

        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    create_default_users()
