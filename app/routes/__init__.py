from .auth import auth_bp
from .user_routes import user_bp  # Đổi từ user thành user_routes
from .school import school_bp
from .device import device_bp
from .schedule_routes import schedule_bp  # Updated to match the correct file name
from .admin import admin_bp
from .holiday import holiday_bp  # Đảm bảo dòng này tồn tại và không bị lỗi
from .schedule_helper import schedule_helper_bp  # Đảm bảo dòng này tồn tại và không bị lỗi
from .season import season_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")  # Đảm bảo sử dụng user_bp từ user_routes
    app.register_blueprint(school_bp, url_prefix="/api/school")
    app.register_blueprint(device_bp, url_prefix="/api/device")
    app.register_blueprint(schedule_bp, url_prefix="/api/schedule")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(holiday_bp)
    app.register_blueprint(schedule_helper_bp, url_prefix="/api/schedule-helper")
    app.register_blueprint(season_bp, url_prefix="/api/season")

    @app.route("/")
    def index():
        return "Welcome to the School Bell API", 200
