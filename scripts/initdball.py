import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.school import School
from app.models.schedule import Schedule
from datetime import time

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()  # Khởi tạo các bảng nếu chưa tồn tại
        
        # Tạo admin hệ thống
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", role="admin", full_name="ADMIN")
            admin.set_password("123")
            db.session.add(admin)
        
        # Tạo 3 trường và tài khoản người dùng (admin trường)
        school_usernames = ["ad1", "ad2", "ad3"]
        for username in school_usernames:
            # Tạo trường nếu chưa tồn tại
            school = School.query.filter_by(name=username).first()
            if not school:
                school = School(name=username, address=f"Địa chỉ {username}", phone="000-000")
                db.session.add(school)
                db.session.commit()  # Để lấy id của trường mới tạo
            
            # Tạo tài khoản người dùng trường nếu chưa có
            if not User.query.filter_by(username=username).first():
                user = User(username=username, role="school_user", full_name=username.upper(), school_id=school.id)
                user.set_password("123")
                db.session.add(user)
        db.session.commit()
        
        # Tạo lịch chuông mẫu cho mỗi trường (cho thứ Hai, day_of_week=0)
        morning_types = ["Vào học", "điểm tiết", "điểm tiết", "Ra chơi", "Vào học"]
        afternoon_types = ["điểm tiết", "Ra về", "Vào học", "điểm tiết", "Ra về"]
        morning_times = [
            (time(7, 0), time(7, 15)),
            (time(7, 20), time(7, 35)),
            (time(7, 40), time(7, 55)),
            (time(8, 0), time(8, 15)),
            (time(8, 20), time(8, 35))
        ]
        afternoon_times = [
            (time(13, 0), time(13, 15)),
            (time(13, 20), time(13, 35)),
            (time(13, 40), time(13, 55)),
            (time(14, 0), time(14, 15)),
            (time(14, 20), time(14, 35))
        ]
        
        schools = School.query.all()
        for school in schools:
            # Xoá lịch chuông của thứ Hai nếu có (cho demo)
            Schedule.query.filter_by(school_id=school.id, day_of_week=0).delete()
            # Thêm lịch buổi sáng
            for bell_type, (start, end) in zip(morning_types, morning_times):
                sch = Schedule(
                    school_id=school.id,
                    start_time=start,
                    end_time=end,
                    day_of_week=0,
                    bell_type=bell_type,
                    is_summer=False
                )
                db.session.add(sch)
            # Thêm lịch buổi chiều
            for bell_type, (start, end) in zip(afternoon_types, afternoon_times):
                sch = Schedule(
                    school_id=school.id,
                    start_time=start,
                    end_time=end,
                    day_of_week=0,
                    bell_type=bell_type,
                    is_summer=False
                )
                db.session.add(sch)
        db.session.commit()
        print("Database initialized with sample data.")

if __name__ == "__main__":
    init_db()
