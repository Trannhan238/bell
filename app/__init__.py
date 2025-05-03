from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_login import LoginManager  # Import Flask-Login

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()  # Initialize Flask-Migrate
login_manager = LoginManager()  # Initialize Flask-Login

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Bind Flask-Migrate to the app and db
    login_manager.init_app(app)  # Initialize Flask-Login
    login_manager.login_view = 'auth.login'  # Set the login view
    
    # Add current_user to Jinja2 context
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(current_user=current_user)
    
    # Áp dụng monkey patch cho JWT trước khi đăng ký blueprint
    from app.utils.jwt_patch import apply_jwt_patch
    apply_jwt_patch()
    
    # Đăng ký Blueprint
    from app.routes import register_routes
    register_routes(app)
    
    # Đăng ký filter vào Jinja2
    def get_day_name(index):
        days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật']
        return days[index]

    app.jinja_env.filters['get_day_name'] = get_day_name

    return app

from app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
