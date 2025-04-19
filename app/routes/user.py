from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint("user", __name__)

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify(username=user.username, full_name=user.full_name, email=user.email), 200
    return jsonify(message="User not found"), 404

@user_bp.route("/update", methods=["POST"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    user.full_name = data.get("full_name", user.full_name)
    user.email = data.get("email", user.email)
    
    db.session.commit()
    return jsonify(message="Profile updated successfully"), 200
