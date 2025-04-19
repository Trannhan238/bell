# scripts/create_schools_and_assign_users.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.school import School
from app.models.user import User

def create_schools_and_assign_users():
    app = create_app()
    with app.app_context():
        schools_data = [
            {"name": "Trường Tiểu học Hoa Sen", "address": "Số 1, Đường A"},
            {"name": "Trường THCS Lý Tự Trọng", "address": "Số 2, Đường B"},
            {"name": "Trường THPT Nguyễn Huệ", "address": "Số 3, Đường C"},
        ]

        usernames = ["ad1", "ad2", "ad3"]

        for i in range(3):
            school_info = schools_data[i]
            existing_school = School.query.filter_by(name=school_info["name"]).first()

            if not existing_school:
                school = School(name=school_info["name"], address=school_info["address"])
                db.session.add(school)
                db.session.commit()
                print(f"Created school: {school.name}")
            else:
                school = existing_school
                print(f"School already exists: {school.name}")

            # Gán user vào trường
            user = User.query.filter_by(username=usernames[i]).first()
            if user:
                user.school_id = school.id
                db.session.commit()
                print(f"Assigned {user.username} to {school.name}")
            else:
                print(f"User {usernames[i]} not found!")

        print("Done.")

if __name__ == "__main__":
    create_schools_and_assign_users()
