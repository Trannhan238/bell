import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysecretkey")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///school_bell.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 7200  # Để 2 giờ để dễ dàng test, có thể thay đổi sau

class DevConfig(Config):
    DEBUG = True    
