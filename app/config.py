import os

# Tạo đường dẫn tuyệt đối đến thư mục data
base_dir = os.path.abspath(os.path.dirname(__file__))  # Thư mục chứa config.py
project_dir = os.path.dirname(base_dir)  # Thư mục gốc của dự án
data_dir = os.path.join(project_dir, 'data')  # Thư mục data trong dự án

# Đảm bảo thư mục data tồn tại
os.makedirs(data_dir, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysecretkey")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(data_dir, 'school_bell.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 7200  # Để 2 giờ để dễ dàng test, có thể thay đổi sau

class DevConfig(Config):
    DEBUG = True
