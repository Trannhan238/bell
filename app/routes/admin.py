from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def system_stats():
    user_id = get_jwt_identity()
    # Admin chỉ có thể truy cập thống kê
    # Giả sử admin có role là "admin"
    return jsonify(message="System statistics..."), 200
