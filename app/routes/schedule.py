from flask import Blueprint, request, jsonify
from app import db
from app.models.schedule import Schedule
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

schedule_bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")

# API tạo lịch chuông
@schedule_bp.route("/create", methods=["POST"])
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

# API: Cập nhật lịch chuông
@schedule_bp.route("/<int:schedule_id>", methods=["PUT"])
def update_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    schedule = Schedule.query.filter_by(id=schedule_id, school_id=user.school.id).first()
    if not schedule:
        return jsonify(message="Schedule not found or not belonging to your school"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Cập nhật các trường nếu có trong dữ liệu đầu vào
    if "start_time" in data:
        try:
            schedule.start_time = datetime.strptime(data["start_time"], "%H:%M").time()
        except ValueError:
            return jsonify(message="Invalid start time format. Expected HH:MM"), 400

    if "end_time" in data:
        try:
            schedule.end_time = datetime.strptime(data["end_time"], "%H:%M").time()
        except ValueError:
            return jsonify(message="Invalid end time format. Expected HH:MM"), 400

    if "bell_type" in data:
        schedule.bell_type = data["bell_type"]

    if "day_of_week" in data:
        if not isinstance(data["day_of_week"], int) or not (0 <= data["day_of_week"] <= 6):
            return jsonify(message="Invalid day_of_week. Should be an integer between 0 and 6"), 400
        schedule.day_of_week = data["day_of_week"]

    db.session.commit()
    return jsonify(message="Schedule updated successfully"), 200

# API: Xóa lịch chuông
@schedule_bp.route("/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.school:
        return jsonify(message="User or School not found"), 404

    schedule = Schedule.query.filter_by(id=schedule_id, school_id=user.school.id).first()
    if not schedule:
        return jsonify(message="Schedule not found or not belonging to your school"), 404

    db.session.delete(schedule)
    db.session.commit()
    return jsonify(message="Schedule deleted successfully"), 200

@schedule_bp.route("/list", methods=["GET"])
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

@schedule_bp.route('/api/schedule/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def api_delete_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify(message="User not found"), 404
    
    # Cho phép cả admin, school_user và school_admin xóa lịch chuông
    if user.role not in ['admin', 'school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403

    # Nếu là admin, có thể xóa lịch chuông của bất kỳ trường nào
    # Nếu là school_user hoặc school_admin, chỉ có thể xóa lịch chuông của trường mình
    if user.role == 'admin':
        schedule = Schedule.query.get(schedule_id)
    else:
        schedule = Schedule.query.filter_by(id=schedule_id, school_id=user.school_id).first()
    
    if not schedule:
        return jsonify(message="Schedule not found or access denied"), 404

    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify(message="Schedule deleted")
