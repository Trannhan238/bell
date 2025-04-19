from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.holiday import Holiday
from app.models.user import User
from datetime import datetime

holiday_bp = Blueprint("holiday", __name__, url_prefix="/api/holiday")

# API: Tạo kỳ nghỉ
@holiday_bp.route("/", methods=["POST"])
@jwt_required()
def create_holiday():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role != "admin":  # Kiểm tra vai trò người dùng
        return jsonify(message="Access denied"), 403

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Tạo kỳ nghỉ mới
    new_holiday = Holiday(
        name=data["name"],
        school_id=data.get("school_id"),
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
        end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
    )
    db.session.add(new_holiday)
    db.session.commit()

    return jsonify(message="Holiday created", id=new_holiday.id), 201

# API: Lấy danh sách kỳ nghỉ
@holiday_bp.route("/", methods=["GET"])
@jwt_required()
def get_holidays():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role == "admin":
        holidays = Holiday.query.all()
    else:
        holidays = Holiday.query.filter_by(school_id=user.school_id).all()

    result = []
    for h in holidays:
        result.append({
            "id": h.id,
            "name": h.name,
            "start_date": h.start_date.isoformat(),
            "end_date": h.end_date.isoformat(),
            "school_id": h.school_id,
        })
    return jsonify(holidays=result)

# API: Lấy thông tin chi tiết kỳ nghỉ
@holiday_bp.route("/<int:holiday_id>", methods=["GET"])
@jwt_required()
def get_holiday(holiday_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    holiday = Holiday.query.get(holiday_id)
    if not holiday:
        return jsonify(message="Holiday not found"), 404

    # Trả về thông tin chi tiết kỳ nghỉ
    return jsonify({
        "id": holiday.id,
        "name": holiday.name,
        "start_date": holiday.start_date.isoformat(),
        "end_date": holiday.end_date.isoformat(),
        "school_id": holiday.school_id,
    }), 200

# API: Xóa kỳ nghỉ
@holiday_bp.route("/<int:holiday_id>", methods=["DELETE"])
@jwt_required()
def delete_holiday(holiday_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role != "admin":  # Chỉ admin mới có quyền xóa
        return jsonify(message="Access denied"), 403

    holiday = Holiday.query.get(holiday_id)
    if not holiday:
        return jsonify(message="Holiday not found"), 404

    db.session.delete(holiday)
    db.session.commit()

    return jsonify(message="Holiday deleted successfully"), 200

# API: Cập nhật kỳ nghỉ
@holiday_bp.route("/<int:holiday_id>", methods=["PUT"])
@jwt_required()
def update_holiday(holiday_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role != "admin":  # Chỉ admin mới có quyền cập nhật
        return jsonify(message="Access denied"), 403

    holiday = Holiday.query.get(holiday_id)
    if not holiday:
        return jsonify(message="Holiday not found"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Cập nhật thông tin kỳ nghỉ
    holiday.name = data.get("name", holiday.name)
    holiday.school_id = data.get("school_id", holiday.school_id)
    holiday.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date() if "start_date" in data else holiday.start_date
    holiday.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date() if "end_date" in data else holiday.end_date

    db.session.commit()

    return jsonify(message="Holiday updated successfully"), 200
