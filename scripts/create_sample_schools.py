# scripts/create_sample_schools.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.school import School

def create_sample_schools():
    app = create_app()
    with app.app_context():
        schools_data = [
            {"name": "Trường Tiểu học Hoa Sen", "address": "Số 1, Đường A"},
            {"name": "Trường THCS Lý Tự Trọng", "address": "Số 2, Đường B"},
            {"name": "Trường THPT Nguyễn Huệ", "address": "Số 3, Đường C"},
        ]

        for school_info in schools_data:
            existing_school = School.query.filter_by(name=school_info["name"]).first()
            if not existing_school:
                school = School(name=school_info["name"], address=school_info["address"])
                db.session.add(school)
                db.session.commit()
                print(f"Created school: {school.name}")
            else:
                print(f"School already exists: {existing_school.name}")

if __name__ == "__main__":
    create_sample_schools()
