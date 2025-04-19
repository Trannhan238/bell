from .auth import auth_bp
from .user import user_bp
from .school import school_bp
from .device import device_bp
from .schedule import schedule_bp
from .admin import admin_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(school_bp, url_prefix="/api/school")
    app.register_blueprint(device_bp, url_prefix="/api/device")
    app.register_blueprint(schedule_bp, url_prefix="/api/schedule")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
