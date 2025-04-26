from app import db
from flask import Flask
import os

# Tạo app instance tạm thời nếu cần
def create_app():
    app = Flask(__name__)
    
    # Cấu hình database trực tiếp
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_bell.db'
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
            from app.models.season_config import SeasonConfig
        except ImportError:
            pass
            
        print("Đang xóa tất cả các bảng...")
        db.drop_all()
        print("Đang tạo lại các bảng...")
        db.create_all()
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
            
            print("Khởi tạo dữ liệu mẫu thành công")
        except Exception as e:
            db.session.rollback()
            print(f"Không thể khởi tạo dữ liệu mẫu: {e}")
