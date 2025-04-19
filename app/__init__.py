from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate  # Import Flask-Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()  # Initialize Flask-Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Bind Flask-Migrate to the app and db
    
    # Đăng ký Blueprint
    from app.routes import register_routes
    register_routes(app)
    
    return app
