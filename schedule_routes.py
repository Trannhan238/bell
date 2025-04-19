from flask import Blueprint, request, jsonify
from app import db
from app.models.schedule import Schedule
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

schedule_bp = Blueprint("schedule", __name__, url_prefix="/api/schedules")

# GET Lịch chuông của trường
@schedule_bp.route("/", methods=["GET"])
@jwt_required()
def get_schedules():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    schedules = Schedule.query.filter_by(school_id=user.school.id).all()
    
    return jsonify([{
        "id": schedule.id,
        "bell_type": schedule.bell_type,
        "start_time": schedule.start_time,
        "end_time": schedule.end_time,
        "repeat_days": schedule.repeat_days,
        "is_summer": schedule.is_summer
    } for schedule in schedules]), 200


# POST Tạo lịch chuông mới
@schedule_bp.route("/", methods=["POST"])
@jwt_required()
def create_schedule():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Tạo lịch chuông mới
    new_schedule = Schedule(
        school_id=user.school.id,
        bell_type=data["bell_type"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        repeat_days=data.get("repeat_days", ""),
        is_summer=data.get("is_summer", False)
    )

    db.session.add(new_schedule)
    db.session.commit()

    return jsonify(message="Schedule created successfully", id=new_schedule.id), 201


# PUT Cập nhật lịch chuông
@schedule_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_schedule(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    schedule = Schedule.query.get(id)
    if not schedule or schedule.school_id != user.school.id:
        return jsonify(message="Schedule not found or not belonging to your school"), 404

    data = request.get_json()
    if "bell_type" in data:
        schedule.bell_type = data["bell_type"]
    if "start_time" in data:
        schedule.start_time = data["start_time"]
    if "end_time" in data:
        schedule.end_time = data["end_time"]
    if "repeat_days" in data:
        schedule.repeat_days = data.get("repeat_days", schedule.repeat_days)
    if "is_summer" in data:
        schedule.is_summer = data["is_summer"]

    db.session.commit()
    return jsonify(message="Schedule updated successfully"), 200


# DELETE Xóa lịch chuông
@schedule_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_schedule(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    schedule = Schedule.query.get(id)
    if not schedule or schedule.school_id != user.school.id:
        return jsonify(message="Schedule not found or not belonging to your school"), 404

    db.session.delete(schedule)
    db.session.commit()
    return jsonify(message="Schedule deleted successfully"), 200
