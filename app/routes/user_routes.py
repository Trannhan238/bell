from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    return jsonify({
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "school": {
            "id": user.school.id if user.school else None,
            "name": user.school.name if user.school else None,
            "address": user.school.address if user.school else None
        }
    })
