from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    jwt.init_app(app)
    
    # Đăng ký Blueprint
    from app.routes import auth, user, school, device, schedule, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(school.bp)
    app.register_blueprint(device.bp)
    app.register_blueprint(schedule.bp)
    app.register_blueprint(admin.bp)
    
    return app
