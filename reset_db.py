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
        # Import tất cả các models trước khi tạo bảng
        # để đảm bảo SQLAlchemy biết tất cả các quan hệ
        from app.models.user import User
        from app.models.school import School
        from app.models.device import Device
        try:
            from app.models.holiday import Holiday, DisabledPeriod
        except ImportError:
            pass  # Bỏ qua nếu không có model này
        try:
            from app.models.schedule import Schedule
        except ImportError:
            pass
        try:
            from app.models.profile import BellProfile
        except ImportError:
            pass
        try:
            from app.models.season_config import SeasonConfig
        except ImportError:
            pass
            
        print("Đang xóa tất cả các bảng...")
        # Vô hiệu hóa kiểm tra khóa ngoại trước khi xóa (cho SQLite)
        # Sử dụng cú pháp tương thích SQLAlchemy 2.0
        with db.engine.begin() as conn:
            conn.execute(db.text("PRAGMA foreign_keys = OFF"))
            # Không cần gọi conn.commit() vì .begin() tự động commit khi kết thúc block

        db.drop_all()
        print("Đang tạo lại các bảng...")
        db.create_all()
        
        # Bật lại kiểm tra khóa ngoại sau khi tạo xong
        with db.engine.begin() as conn:
            conn.execute(db.text("PRAGMA foreign_keys = ON"))
            # Không cần gọi conn.commit() vì .begin() tự động commit khi kết thúc block
            
        print("Hoàn tất! Database đã được khởi tạo lại.")
        
        # Tạo dữ liệu mẫu thủ công
        try:
            # Tạo admin hệ thống
            if not User.query.filter_by(username="admin").first():
                admin = User(username="admin", role="admin", full_name="ADMIN")
                admin.set_password("123")
                db.session.add(admin)
                db.session.commit()  # Commit trước để đảm bảo dữ liệu được lưu
                print("Đã tạo admin hệ thống")
            
            # Tạo 3 trường và tài khoản trường
            for i in range(1, 4):
                username = f"ad{i}"
                # Tạo trường nếu chưa có
                school = School.query.filter_by(name=username).first()
                if not school:
                    school = School(name=username, address=f"Địa chỉ {username}")
                    db.session.add(school)
                    db.session.commit()  # Commit ngay để lấy ID
                    print(f"Đã tạo trường {username}")
                
                # Tạo tài khoản cho trường
                if not User.query.filter_by(username=username).first():
                    user = User(
                        username=username, 
                        role="school_admin", 
                        full_name=username.upper(),
                        school_id=school.id
                    )
                    user.set_password("123")
                    db.session.add(user)
                    db.session.commit()  # Commit sau mỗi lần tạo user
                    print(f"Đã tạo tài khoản {username}")
                
                # Tạo một bell profile mẫu cho mỗi trường
                from datetime import date
                profile = BellProfile(
                    name=f"Profile chuẩn - {username}",
                    active_from=date(2023, 9, 1),
                    active_to=date(2024, 5, 31)
                )
                db.session.add(profile)
                db.session.commit()
                print(f"Đã tạo profile chuông cho {username}")
                
                # Tạo lịch chuông mẫu cho thứ Hai (day_of_week=0)
                # Sử dụng mô hình điểm thời gian thay vì khoảng thời gian
                bell_points = [
                    (time(7, 0), "vào học"),
                    (time(7, 45), "điểm tiết"),
                    (time(8, 30), "điểm tiết"),
                    (time(9, 0), "ra chơi"),
                    (time(9, 15), "vào học"),
                    (time(10, 0), "điểm tiết"),
                    (time(10, 45), "điểm tiết"),
                    (time(11, 30), "ra về")
                ]
                
                # Thêm lịch với liên kết đến profile
                for time_point, bell_type in bell_points:
                    sch = Schedule(
                        school_id=school.id,
                        profile_id=profile.id,
                        time_point=time_point,
                        day_of_week=0,
                        bell_type=bell_type,
                        is_summer=False
                    )
                    db.session.add(sch)
                db.session.commit()
                print(f"Đã tạo lịch chuông mới cho {username}")
            
            print("Khởi tạo dữ liệu mẫu thành công")
        except Exception as e:
            db.session.rollback()
            print(f"Không thể khởi tạo dữ liệu mẫu: {e}")
