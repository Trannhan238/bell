from flask import Blueprint, request, jsonify
from app import db
from app.models.schedule import Schedule
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

schedule_bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")

@schedule_bp.route("/create", methods=["POST"])
@jwt_required()
def create_schedule():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    bell_type = data.get("bell_type")
    day_of_week = data.get("day_of_week")

    # Kiểm tra định dạng thời gian
    try:
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
    except (ValueError, TypeError):
        return jsonify(message="Invalid time format. Expected HH:MM"), 400

    # Kiểm tra các trường bắt buộc
    if not bell_type or day_of_week is None:
        return jsonify(message="Missing bell_type or day_of_week"), 400

    # Tạo lịch chuông mới
    new_schedule = Schedule(
        school_id=user.school.id,
        start_time=start_time,
        end_time=end_time,
        bell_type=bell_type,
        day_of_week=day_of_week
    )
    db.session.add(new_schedule)
    db.session.commit()

    return jsonify(message="Schedule created successfully", id=new_schedule.id), 201

@schedule_bp.route("/list", methods=["GET"])
@jwt_required()
def list_schedules():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    schedules = Schedule.query.filter_by(school_id=user.school.id).all()
    schedule_list = [
        {
            "id": schedule.id,
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
            "bell_type": schedule.bell_type,
            "day_of_week": schedule.day_of_week,
        }
        for schedule in schedules
    ]
    return jsonify(schedule_list), 200
