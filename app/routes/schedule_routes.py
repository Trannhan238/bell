from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.schedule import Schedule
from app.models.user import User
from app.models.school import School
from app import db
from datetime import datetime
from app.utils.decorators import login_required, admin_required, school_admin_required, school_user_required, school_specific_access
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Bỏ url_prefix để đường dẫn /schedules hoạt động đúng
schedule_bp = Blueprint("schedule", __name__)

# Hàm kiểm tra định dạng thời gian hợp lệ
def valid_time_format(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

# API: Tạo lịch chuông mới
@schedule_bp.route("/api/schedule/", methods=["POST"])
@jwt_required()
def create_schedule():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role not in ['admin', 'school_admin']:
        return jsonify(message="Access denied"), 403

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    school_id = data.get('school_id') if user.role == 'admin' else user.school_id
    if not school_id:
        return jsonify(message="School ID is required"), 400

    new_schedule = Schedule(
        school_id=school_id,
        time_point=datetime.strptime(data['time_point'], "%H:%M").time(),
        day_of_week=data['day_of_week'],
        bell_type=data['bell_type'],
        is_summer=data.get('is_summer', False)
    )
    db.session.add(new_schedule)
    db.session.commit()
    return jsonify(message="Schedule created successfully", id=new_schedule.id), 201

# API: Lấy danh sách lịch chuông
@schedule_bp.route("/api/schedule/", methods=["GET"])
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
@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["PUT"])
@jwt_required()
def update_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role not in ['admin', 'school_admin']:
        return jsonify(message="Access denied"), 403

    schedule = Schedule.query.get(schedule_id) if user.role == 'admin' else \
        Schedule.query.filter_by(id=schedule_id, school_id=user.school_id).first()

    if not schedule:
        return jsonify(message="Schedule not found or access denied"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="Invalid data"), 400

    # Update fields
    if 'time_point' in data and valid_time_format(data['time_point']):
        schedule.time_point = datetime.strptime(data['time_point'], "%H:%M").time()
    if 'day_of_week' in data:
        schedule.day_of_week = data['day_of_week']
    if 'bell_type' in data:
        schedule.bell_type = data['bell_type']

    db.session.commit()
    return jsonify(message="Schedule updated successfully"), 200

# API: Xóa lịch chuông
@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["DELETE"])
@jwt_required()
def delete_schedule(schedule_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(message="User not found"), 404

    if user.role not in ['admin', 'school_admin']:
        return jsonify(message="Access denied"), 403

    schedule = Schedule.query.get(schedule_id) if user.role == 'admin' else \
        Schedule.query.filter_by(id=schedule_id, school_id=user.school_id).first()

    if not schedule:
        return jsonify(message="Schedule not found or access denied"), 404

    db.session.delete(schedule)
    db.session.commit()
    return jsonify(message="Schedule deleted successfully"), 200

# API: Debug thông tin người dùng
@schedule_bp.route("/api/schedule/debug-user", methods=["GET"])
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

# API: Giao diện quản lý lịch chuông
@schedule_bp.route('/schedules', methods=['GET'])
@login_required
@school_specific_access
def schedules_page():
    user = session.get('user')
    logging.debug(f"User session data: {user}")

    if not user:
        flash('Không tìm thấy thông tin người dùng!', 'danger')
        return redirect(url_for('auth.login'))

    # Nếu là admin hệ thống, sử dụng template riêng
    if user.get('role') == 'admin':
        school_id = request.args.get('school_id')
        logging.debug(f"Admin accessing schedules with school_id: {school_id}")
        schools = School.query.all()
        schedules = []

        if school_id:
            schedules = Schedule.query.filter_by(school_id=school_id).all()
            schedules = sorted(schedules, key=lambda schedule: schedule.time_point)

        return render_template('pages/schedules_admin.html', schedules=schedules, schools=schools, selected_school_id=int(school_id) if school_id else None)

    # Nếu là school_admin hoặc school_user, sử dụng template mặc định
    elif user.get('role') in ['school_admin', 'school_user']:
        school_id = user.get('school_id')
        logging.debug(f"School user/admin accessing schedules for school_id: {school_id}")
        if not school_id:
            flash('Không tìm thấy trường học của bạn!', 'danger')
            return redirect(url_for('index'))
        schedules = Schedule.query.filter_by(school_id=school_id).all()
        schedules = sorted(schedules, key=lambda schedule: schedule.time_point)
        schools = School.query.filter_by(id=school_id).all()
        return render_template('pages/schedules.html', schedules=schedules, schools=schools)

    else:
        logging.warning(f"Unauthorized access attempt by user: {user}")
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))

# API: Thêm lịch chuông từ modal
@schedule_bp.route('/schedules/add', methods=['POST'])
@login_required
@school_specific_access
def add_schedule():
    user = session['user']
    school_id = request.form.get('school_id')

    # Nếu không phải admin, chỉ cho phép thêm lịch cho trường của mình
    if user.get('role') != 'admin' and int(school_id) != int(user.get('school_id', 0)):
        flash('Bạn không có quyền thêm lịch cho trường khác!', 'danger')
        return redirect(url_for('schedule.schedules_page'))

    time_point = request.form.get('time_point')
    repeat_days = request.form.getlist('repeat_days')
    bell_type = request.form.get('bell_type')
    is_summer = True if request.form.get('is_summer') else False

    # Validate
    if not (school_id and time_point and repeat_days and bell_type):
        flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
        return redirect(url_for('schedule.schedules_page'))

    try:
        # Chuyển đổi time_point sang đối tượng datetime.time
        time_point = datetime.strptime(time_point, '%H:%M').time()
    except ValueError:
        flash('Định dạng thời gian không hợp lệ!', 'danger')
        return redirect(url_for('schedule.schedules_page'))

    # Tạo mới cho từng ngày được chọn
    for day in repeat_days:
        schedule = Schedule(
            school_id=school_id,
            time_point=time_point,
            day_of_week=int(day),
            bell_type=bell_type,
            is_summer=is_summer
        )
        db.session.add(schedule)

    db.session.commit()
    flash('Thêm lịch chuông thành công!', 'success')
    return redirect(url_for('schedule.schedules_page'))

@schedule_bp.route('/schedules/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@school_specific_access
def web_edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)

    # Kiểm tra quyền - school_admin chỉ được sửa lịch của trường mình
    user = session['user']
    if user.get('role') != 'admin' and int(schedule.school_id) != int(user.get('school_id', 0)):
        flash('Bạn không có quyền chỉnh sửa lịch chuông của trường khác!', 'danger')
        return redirect(url_for('schedule.schedules_page'))

    # Admin được phép thấy tất cả trường, school_admin chỉ thấy trường của mình
    if user.get('role') == 'admin':
        schools = School.query.all()
    else:
        schools = School.query.filter_by(id=user.get('school_id')).all()

    if request.method == 'POST':
        school_id = request.form.get('school_id')
        time_point = request.form.get('time_point')
        bell_type = request.form.get('bell_type')
        repeat_days = request.form.getlist('repeat_days')

        # Kiểm tra quyền khi cập nhật
        if user.get('role') != 'admin' and int(school_id) != int(user.get('school_id', 0)):
            flash('Bạn không có quyền cập nhật lịch cho trường khác!', 'danger')
            return redirect(url_for('schedule.schedules_page'))

        # Xóa các bản ghi cũ có cùng time_point và bell_type
        Schedule.query.filter_by(
            school_id=schedule.school_id,
            time_point=schedule.time_point,
            bell_type=schedule.bell_type
        ).delete()

        # Tạo mới các bản ghi với repeat_days
        for day in repeat_days:
            new_schedule = Schedule(
                school_id=school_id,
                time_point=datetime.strptime(time_point, '%H:%M').time(),
                day_of_week=int(day),
                bell_type=bell_type
            )
            db.session.add(new_schedule)

        db.session.commit()
        flash('Cập nhật lịch chuông thành công!', 'success')

        # Redirect về trường vừa sửa
        if user.get('role') == 'admin':
            return redirect(url_for('schedule.schedules_admin_page', school_id=school_id))
        else:
            return redirect(url_for('schedule.schedules_page'))

    return render_template('pages/edit_schedule.html', schedule=schedule, schools=schools)

@schedule_bp.route('/schedules/delete/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@school_specific_access
def web_delete_schedule(schedule_id):
    schedule_to_delete = Schedule.query.get_or_404(schedule_id)
    school_id = request.args.get('school_id')  # Get school_id from query parameters

    # Kiểm tra quyền - chỉ xóa lịch của trường mình
    user = session['user']
    if user.get('role') != 'admin' and int(schedule_to_delete.school_id) != int(user.get('school_id', 0)):
        flash('Bạn không có quyền xóa lịch chuông của trường khác!', 'danger')
        return redirect(url_for('schedule.schedules_page'))

    # Xóa tất cả các lịch chuông có cùng time_point và bell_type
    schedules_to_delete = Schedule.query.filter_by(
        school_id=schedule_to_delete.school_id,
        time_point=schedule_to_delete.time_point,
        bell_type=schedule_to_delete.bell_type
    ).all()

    for schedule in schedules_to_delete:
        db.session.delete(schedule)

    db.session.commit()
    flash('Xóa tất cả các ngày lặp lại thành công!', 'success')
    
    # Preserve school_id in redirect for admin users
    if user.get('role') == 'admin' and school_id:
        return redirect(url_for('schedule.schedules_page', school_id=school_id))
    return redirect(url_for('schedule.schedules_page'))

@schedule_bp.route('/schedules/delete', methods=['POST'])
@login_required
@school_specific_access
def delete_schedules():
    data = request.get_json()
    ids_to_delete = data.get('ids', [])

    if not ids_to_delete:
        return jsonify({'message': 'Không có lịch chuông nào được chọn để xóa.'}), 400

    schedules_to_delete = Schedule.query.filter(Schedule.id.in_(ids_to_delete)).all()

    if not schedules_to_delete:
        return jsonify({'message': 'Không tìm thấy lịch chuông nào để xóa.'}), 404

    for schedule in schedules_to_delete:
        db.session.delete(schedule)

    db.session.commit()
    return jsonify({'message': 'Xóa thành công!'}), 200

@schedule_bp.route('/schedules/admin', methods=['GET'])
@login_required
@admin_required
def schedules_admin_page():
    user = session.get('user')

    if not user or user.get('role') != 'admin':
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))

    school_id = request.args.get('school_id')
    schools = School.query.all()
    schedules = []

    if school_id:
        schedules = Schedule.query.filter_by(school_id=school_id).all()
        schedules = sorted(schedules, key=lambda schedule: schedule.time_point)

    return render_template('pages/schedules_admin.html', schedules=schedules, schools=schools, selected_school_id=int(school_id) if school_id else None)

@schedule_bp.route('/schedules/admin/add', methods=['POST'])
@login_required
@admin_required
def add_schedule_admin():
    user = session.get('user')

    if not user or user.get('role') != 'admin':
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))

    school_id = request.form.get('school_id')
    time_point = request.form.get('time_point')
    repeat_days = request.form.getlist('repeat_days')
    bell_type = request.form.get('bell_type')

    # Validate
    if not (school_id and time_point and repeat_days and bell_type):
        flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
        return redirect(url_for('schedule.schedules_admin_page'))

    try:
        # Chuyển đổi time_point sang đối tượng datetime.time
        time_point = datetime.strptime(time_point, '%H:%M').time()
    except ValueError:
        flash('Định dạng thời gian không hợp lệ!', 'danger')
        return redirect(url_for('schedule.schedules_admin_page'))

    # Tạo mới cho từng ngày được chọn
    for day in repeat_days:
        schedule = Schedule(
            school_id=school_id,
            time_point=time_point,
            day_of_week=int(day),
            bell_type=bell_type
        )
        db.session.add(schedule)

    db.session.commit()
    flash('Thêm lịch chuông thành công!', 'success')
    return redirect(url_for('schedule.schedules_admin_page', school_id=school_id))
