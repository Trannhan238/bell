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

    if not user or user.role != "admin":
        return jsonify(message="Access denied"), 403

    data = request.get_json()
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
