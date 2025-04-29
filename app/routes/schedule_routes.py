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

    # Thêm 'school_admin' vào danh sách các role được phép
    if user.role not in ['admin', 'school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403
        
    data = request.get_json()
    if not data:
        return jsonify(message="Dữ liệu không hợp lệ"), 400
    
    # Kiểm tra dữ liệu đầu vào
    if 'time_point' not in data or not valid_time_format(data['time_point']):
        return jsonify(message="Định dạng thời gian không hợp lệ. Định dạng mong đợi: HH:MM"), 400
    if 'bell_type' not in data or not isinstance(data['bell_type'], str):
        return jsonify(message="bell_type không hợp lệ. Phải là một chuỗi"), 400
    if 'day_of_week' not in data or not isinstance(data['day_of_week'], int) or not (0 <= data['day_of_week'] <= 6):
        return jsonify(message="day_of_week không hợp lệ. Phải là số nguyên từ 0 (Thứ Hai) đến 6 (Chủ Nhật)"), 400
    
    # Xác định school_id
    school_id = None
    if user.role == 'admin':
        school_id = data.get('school_id')
        if not school_id:
            return jsonify(message="Admin cần cung cấp school_id"), 400
    else:
        school_id = user.school_id
    
    # Chuyển đổi chuỗi thời gian thành đối tượng datetime.time
    time_point = datetime.strptime(data["time_point"], "%H:%M").time()
    
    # Tạo lịch mới
    new_schedule = Schedule(
        school_id=school_id,
        time_point=time_point,
        day_of_week=data["day_of_week"],
        bell_type=data["bell_type"],
        is_summer=data.get("is_summer", False),
    )
    db.session.add(new_schedule)
    db.session.commit()
    
    return jsonify(message="Lịch được tạo thành công", id=new_schedule.id), 201

# API: Lấy danh sách lịch chuông
@schedule_bp.route("/", methods=["GET"])
@jwt_required()
def get_schedules():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    if user.role == "admin":
        # Admin xem được tất cả lịch
        school_id = request.args.get("school_id")
        if school_id:
            schedules = Schedule.query.filter_by(school_id=school_id).paginate(
                page=page, per_page=per_page, error_out=False
            )
        else:
            schedules = Schedule.query.paginate(
                page=page, per_page=per_page, error_out=False
            )
    else:
        # Người dùng thường chỉ thấy lịch của trường mình
        schedules = Schedule.query.filter_by(school_id=user.school_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    result = []
    for schedule in schedules.items:
        result.append({
            "id": schedule.id,
            "day_of_week": schedule.day_of_week,
            "start_time": schedule.start_time.strftime("%H:%M") if hasattr(schedule, 'start_time') else None,
            "end_time": schedule.end_time.strftime("%H:%M") if hasattr(schedule, 'end_time') and schedule.end_time else None,
            "time_point": schedule.time_point.strftime("%H:%M") if hasattr(schedule, 'time_point') else None,
            "bell_type": schedule.bell_type,
            "is_summer": schedule.is_summer,
            "school_id": schedule.school_id
        })
    
    return jsonify({
        "schedules": result,
        "total": schedules.total,
        "pages": schedules.pages,
        "current_page": schedules.page
    }), 200

# API: Cập nhật lịch chuông
@schedule_bp.route("/<int:schedule_id>", methods=["PUT"])
@jwt_required()
def update_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify(message="User not found"), 404
        
    # Cho phép cả admin, school_user và school_admin cập nhật lịch chuông
    if user.role not in ['admin', 'school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403

    # Nếu là admin, có thể chỉnh sửa lịch chuông của bất kỳ trường nào
    # Nếu là school_user, chỉ có thể chỉnh sửa lịch chuông của trường mình
    if user.role == 'admin':
        schedule = Schedule.query.get(schedule_id)
    else:
        schedule = Schedule.query.filter_by(id=schedule_id, school_id=user.school_id).first()
    
    if not schedule:
        return jsonify(message="Schedule not found or access denied"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Kiểm tra và chuyển đổi các trường hợp lỗi hoặc thay đổi
    if 'start_time' in data and hasattr(schedule, 'start_time'):
        if not valid_time_format(data['start_time']):
            return jsonify(message="Invalid start time format. Expected format: HH:MM"), 400
        schedule.start_time = datetime.strptime(data['start_time'], "%H:%M").time()

    if 'end_time' in data and hasattr(schedule, 'end_time'):
        if not valid_time_format(data['end_time']):
            return jsonify(message="Invalid end time format. Expected format: HH:MM"), 400
        schedule.end_time = datetime.strptime(data['end_time'], "%H:%M").time()

    if 'time_point' in data and hasattr(schedule, 'time_point'):
        if not valid_time_format(data['time_point']):
            return jsonify(message="Invalid time_point format. Expected format: HH:MM"), 400
        schedule.time_point = datetime.strptime(data['time_point'], "%H:%M").time()

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
        
    # Cho phép admin chỉnh sửa school_id
    if user.role == 'admin' and 'school_id' in data:
        schedule.school_id = data['school_id']

    db.session.commit()

    return jsonify(message="Schedule updated")

# API: Xóa lịch chuông
@schedule_bp.route("/<int:schedule_id>", methods=["DELETE"])
@jwt_required()
def delete_schedule(schedule_id):
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

# API: Debug thông tin người dùng
@schedule_bp.route("/debug-user", methods=["GET"])
@jwt_required()
def debug_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify(message="User not found"), 404
    
    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "school_id": user.school_id
    }), 200
