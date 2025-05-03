from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from app.models.user import User

def jwt_role_required(required_role):
    """
    Decorator chỉ dùng cho các API yêu cầu role cụ thể với JWT
    KHÔNG dùng cho các route giao diện web
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify(message="User not found"), 404
            if user.role != required_role:
                return jsonify(message="Access denied"), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Định nghĩa các decorator JWT dùng cho API
jwt_admin_required = jwt_role_required("admin") 
jwt_school_user_required = jwt_role_required("school_user")
jwt_school_admin_required = jwt_role_required("school_admin")