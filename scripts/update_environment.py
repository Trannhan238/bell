import subprocess
import sys

def update_pip():
    print("Đang cập nhật pip lên phiên bản mới nhất...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    print("Đã cập nhật pip thành công!")

def update_dependencies():
    print("Đang cập nhật các thư viện phụ thuộc...")
    # Cập nhật SQLAlchemy lên bản mới nhất với cú pháp 2.0
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'sqlalchemy>=2.0.0'])
    # Cập nhật Flask-SQLAlchemy
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'flask-sqlalchemy>=3.0.0'])
    # Các thư viện khác nếu cần
    print("Đã cập nhật các thư viện phụ thuộc thành công!")

def main():
    update_pip()
    update_dependencies()
    print("\nMôi trường đã được cập nhật thành công!")
    print("Khuyến nghị: Kiểm tra lại ứng dụng để đảm bảo tương thích với phiên bản mới.")

if __name__ == "__main__":
    main()
