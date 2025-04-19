from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.schedule import Schedule
from app.models.user import User
from app import db
from datetime import datetime

schedule_bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")

# Hàm kiểm tra định dạng thời gian hợp lệ
def valid_time_format(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

# API: Tạo lịch chuông mới
@schedule_bp.route("/", methods=["POST"])
@jwt_required()
def create_schedule():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role != 'school_user':  # Kiểm tra vai trò người dùng
        return jsonify(message="Access denied"), 403

    if not user.school_id:  # Kiểm tra người dùng có liên kết với trường học không
        return jsonify(message="User is not assigned to any school"), 403

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Kiểm tra dữ liệu đầu vào
    if 'start_time' not in data or not valid_time_format(data['start_time']):
        return jsonify(message="Invalid start time format. Expected format: HH:MM"), 400
    if 'end_time' not in data or not valid_time_format(data['end_time']):
        return jsonify(message="Invalid end time format. Expected format: HH:MM"), 400
    if 'day_of_week' not in data or not isinstance(data['day_of_week'], int) or not (0 <= data['day_of_week'] <= 6):
        return jsonify(message="Invalid day_of_week. Should be an integer between 0 (Sunday) and 6 (Saturday)"), 400
    if 'bell_type' not in data or not isinstance(data['bell_type'], str):
        return jsonify(message="Invalid bell_type. Should be a string"), 400
    
    # Chuyển đổi chuỗi thời gian thành đối tượng datetime.time
    start_time = datetime.strptime(data["start_time"], "%H:%M").time()
    end_time = datetime.strptime(data["end_time"], "%H:%M").time()
    
    # Tạo mới lịch chuông
    new_schedule = Schedule(
        school_id=user.school_id,
        start_time=start_time,
        end_time=end_time,
        day_of_week=data["day_of_week"],
        bell_type=data["bell_type"],
        is_summer=data.get("is_summer", False),
    )
    db.session.add(new_schedule)
    db.session.commit()
    
    return jsonify(message="Schedule created successfully", id=new_schedule.id), 201

# API: Lấy danh sách lịch chuông
@schedule_bp.route("/", methods=["GET"])
@jwt_required()
def get_schedules():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role not in ['school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403

    # Phân trang
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    schedules = Schedule.query.filter_by(school_id=user.school_id).paginate(page, per_page, False)

    schedules_data = []
    for schedule in schedules.items:
        schedules_data.append({
            "id": schedule.id,
            "start_time": schedule.start_time.strftime('%H:%M'),
            "end_time": schedule.end_time.strftime('%H:%M'),
            "day_of_week": schedule.day_of_week,
            "bell_type": schedule.bell_type,
            "is_summer": schedule.is_summer
        })

    return jsonify(schedules=schedules_data, total=schedules.total, pages=schedules.pages)

# API: Cập nhật lịch chuông
@schedule_bp.route("/<int:schedule_id>", methods=["PUT"])
@jwt_required()
def update_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'school_user':
        return jsonify(message="Access denied"), 403

    schedule = Schedule.query.filter_by(id=schedule_id, school_id=user.school_id).first()
    if not schedule:
        return jsonify(message="Schedule not found or access denied"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Kiểm tra và chuyển đổi các trường hợp lỗi hoặc thay đổi
    if 'start_time' in data:
        if not valid_time_format(data['start_time']):
            return jsonify(message="Invalid start time format. Expected format: HH:MM"), 400
        schedule.start_time = datetime.strptime(data['start_time'], "%H:%M").time()

    if 'end_time' in data:
        if not valid_time_format(data['end_time']):
            return jsonify(message="Invalid end time format. Expected format: HH:MM"), 400
        schedule.end_time = datetime.strptime(data['end_time'], "%H:%M").time()

    if 'day_of_week' in data:
        if not isinstance(data['day_of_week'], int) or not (0 <= data['day_of_week'] <= 6):
            return jsonify(message="Invalid day_of_week. Should be an integer between 0 (Sunday) and 6 (Saturday)"), 400
        schedule.day_of_week = data['day_of_week']

    if 'bell_type' in data:
        if not isinstance(data['bell_type'], str):
            return jsonify(message="Invalid bell_type. Should be a string"), 400
        schedule.bell_type = data['bell_type']

    if 'is_summer' in data:
        schedule.is_summer = data['is_summer']

    db.session.commit()

    return jsonify(message="Schedule updated")

# API: Xóa lịch chuông
@schedule_bp.route("/<int:schedule_id>", methods=["DELETE"])
@jwt_required()
def delete_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'school_user':
        return jsonify(message="Access denied"), 403

    schedule = Schedule.query.filter_by(id=schedule_id, school_id=user.school_id).first()
    if not schedule:
        return jsonify(message="Schedule not found or access denied"), 404

    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify(message="Schedule deleted")
