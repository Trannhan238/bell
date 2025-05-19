from flask import render_template, redirect, url_for, session
from .auth import auth_bp
from .user_routes import user_bp  # Đổi từ user thành user_routes
from .school import school_bp
from .device import device_bp
from .schedule_routes import schedule_bp  # Updated to match the correct file name
from .admin import admin_bp
from .holiday import holiday_bp  # Đảm bảo dòng này tồn tại và không bị lỗi
from .schedule_helper import schedule_helper_bp  # Đảm bảo dòng này tồn tại và không bị lỗi
from .season import season_bp
from .device_frontend import frontend_bp as device_frontend_bp  # Corrected import for frontend blueprint
from app.models.device import Device
from app.models.schedule import Schedule
from app.models.user import User
from app.models.holiday import Holiday
from app.models.school import School
from app.utils.decorators import login_required
import logging

def register_routes(app):
    app.register_blueprint(auth_bp)  # Đăng ký auth_bp KHÔNG có url_prefix để các route như /login, /logout hoạt động ở gốc
    app.register_blueprint(user_bp)  # Bỏ url_prefix để các route như /users hoạt động ở gốc domain
    app.register_blueprint(school_bp)  # Bỏ url_prefix để các route như /schools hoạt động ở gốc domain
    app.register_blueprint(device_bp, url_prefix="/api/device")  # Đăng ký các route liên quan đến thiết bị với prefix `/api/device`
    app.register_blueprint(schedule_bp)  # Ensure schedule routes are registered
    app.register_blueprint(admin_bp, url_prefix="/api/admin")  # Giữ url_prefix cho các blueprint API nếu cần
    app.register_blueprint(holiday_bp)  # Bỏ url_prefix để các route như /holidays hoạt động ở gốc domain
    app.register_blueprint(schedule_helper_bp, url_prefix="/api/schedule-helper")  # Giữ url_prefix cho các blueprint API nếu cần
    app.register_blueprint(season_bp)  # Bỏ url_prefix để các route như /seasons hoạt động ở gốc domain
    app.register_blueprint(device_frontend_bp)  # Đăng ký blueprint frontend KHÔNG có url_prefix để các route như /devices hoạt động ở gốc domain

    @app.route("/")
    def index():
        logging.info("Index route accessed")
        # Kiểm tra xem người dùng đã đăng nhập chưa (tự quản lý mà không dùng decorator)
        if 'user' not in session:
            logging.info("User not logged in, redirecting to login")
            return redirect(url_for('auth.login'))

        # Nếu đã đăng nhập, hiển thị trang dashboard với thông tin stats
        stats = {
            'devices': Device.query.count(),
            'schedules': Schedule.query.count(),
            'users': User.query.count(),
            # 'seasons': SeasonConfig.query.count(),  # Removed reference to season_config
            'holidays': Holiday.query.count(),
            'schools': School.query.count(),
        }

        # Phân biệt template dựa trên vai trò của người dùng
        if session['user']['role'] == 'admin':
            logging.info("Rendering dashboard_admin.html for admin user")
            return render_template("pages/dashboard_admin.html", stats=stats)
        else:
            logging.info("Rendering dashboard_school.html for non-admin user")
            return render_template("pages/dashboard_school.html", stats=stats)
