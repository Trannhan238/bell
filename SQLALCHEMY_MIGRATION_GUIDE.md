# Hướng dẫn nâng cấp lên SQLAlchemy 2.0

## Các thay đổi cần thực hiện

1. **Cập nhật cú pháp thực thi câu lệnh SQL**:
   - Trước đây: `db.session.execute("SQL STATEMENT")`
   - Mới: `db.session.execute(db.text("SQL STATEMENT"))`

2. **Sử dụng context manager cho các kết nối**:
   ```python
   # Thay vì:
   conn = db.engine.connect()
   conn.execute(...)
   conn.commit()
   
   # Sử dụng:
   with db.engine.begin() as conn:
       conn.execute(db.text(...))
       # Tự động commit khi kết thúc block
   ```

3. **Thay đổi trong truy vấn ORM**:
   - Sử dụng `select()` thay vì truy vấn trực tiếp qua model
   ```python
   # Thay vì:
   users = User.query.filter_by(username="admin").all()
   
   # Sử dụng:
   from sqlalchemy import select
   stmt = select(User).where(User.username == "admin")
   users = db.session.execute(stmt).scalars().all()
   ```

4. **Sử dụng transaction rõ ràng**:
   ```python
   # Cách mới để bắt đầu một transaction:
   with db.session.begin():
       db.session.add(user)
       # Không cần gọi db.session.commit() - tự động khi kết thúc block
   ```

5. **Kiểm tra và cập nhật các mối quan hệ back references**:
   - Đảm bảo tất cả các mối quan hệ đều sử dụng `back_populates` thay vì `backref`

## Quy trình nâng cấp

1. Cài đặt các thư viện mới:
   ```bash
   pip install -r requirements-sqlalchemy2.txt
   ```
   
2. Chạy các test để phát hiện các lỗi tương thích
3. Cập nhật mã theo hướng dẫn trên
4. Kiểm tra ứng dụng hoạt động đúng sau khi cập nhật

## Tài liệu tham khảo

- [Hướng dẫn di chuyển SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [SQLAlchemy 2.0 API](https://docs.sqlalchemy.org/en/20/)
