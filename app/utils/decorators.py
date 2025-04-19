from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models.user import User

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify(message="User not found"), 404
            if user.role != required_role:
                return jsonify(message="Access denied"), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Ví dụ decorator sẵn để dùng
admin_required = role_required("admin")
school_user_required = role_required("school_user")
