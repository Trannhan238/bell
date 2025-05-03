from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError, validates_schema
from datetime import datetime, date
from app.models.holiday import Holiday  # Ensure Holiday is imported
from app.models.user import User  # Ensure User is imported
from app.models.school import School  # Ensure School is imported
from app import db  # Import db for database operations
import logging  # Add logging for debugging
from app.utils.decorators import login_required, admin_required, school_admin_required

# Bỏ url_prefix để các route web hoạt động đúng
holiday_bp = Blueprint("holiday", __name__)

# Schema for validating holiday data
class HolidaySchema(Schema):
    name = fields.String(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    school_id = fields.Integer(required=False)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if "start_date" in data and "end_date" in data:
            if data["start_date"] > data["end_date"]:
                raise ValidationError("start_date must be before end_date.")

holiday_schema = HolidaySchema()
pagination_schema = Schema.from_dict({
    "page": fields.Integer(load_default=1),  # Fixed
    "per_page": fields.Integer(load_default=10),  # Fixed
    "search": fields.String(load_default=None)  # Fixed
})()

# API routes - thêm đường dẫn /api/holiday/
@holiday_bp.route("/api/holiday/", methods=["POST"])
@jwt_required()
def create_holiday():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Access denied"}), 403

    try:
        data = holiday_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # Check for overlapping holidays
    overlapping_holiday = Holiday.query.filter(
        Holiday.school_id == data.get("school_id"),
        Holiday.start_date <= data["end_date"],
        Holiday.end_date >= data["start_date"]
    ).first()

    if overlapping_holiday:
        return jsonify({"error": "Holiday dates overlap with an existing holiday"}), 400

    try:
        # Logic to create a holiday
        new_holiday = Holiday(
            name=data["name"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            school_id=data.get("school_id")
        )
        db.session.add(new_holiday)
        db.session.commit()
        return jsonify({"message": "Holiday created successfully", "data": data}), 201
    except Exception as e:
        logging.error(f"Error creating holiday: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@holiday_bp.route("/api/holiday/", methods=["GET"])
@jwt_required()
def get_holidays():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role not in ["admin", "school_admin"]:
        return jsonify({"error": "Access denied"}), 403

    # Lấy các giá trị phân trang và tìm kiếm từ request: page, per_page, search
    args = request.args.to_dict()
    page = int(args.get("page", 1))
    per_page = int(args.get("per_page", 10))
    search = args.get("search", "")

    query = Holiday.query
    if search:
        query = query.filter(Holiday.name.ilike(f"%{search}%"))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    holidays = [
        {
            "id": h.id,
            "name": h.name,
            "start_date": h.start_date.strftime("%Y-%m-%d"),
            "end_date": h.end_date.strftime("%Y-%m-%d")
        }
        for h in pagination.items
    ]
    return jsonify({
        "data": holidays,
        "page": page,
        "per_page": per_page,
        "total": pagination.total
    }), 200

@holiday_bp.route("/api/holiday/all", methods=["GET"])
@jwt_required()
def get_all_holidays():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Access denied"}), 403

    # Lấy tất cả ngày nghỉ không phân biệt trường học
    holidays = Holiday.query.all()
    result = [
        {
            "id": h.id,
            "name": h.name,
            "start_date": h.start_date.strftime("%Y-%m-%d"),
            "end_date": h.end_date.strftime("%Y-%m-%d"),
            "school_id": h.school_id,
            "school_name": h.school.name if h.school else "Toàn hệ thống"
        }
        for h in holidays
    ]

    return jsonify({
        "data": result,
        "total": len(result)
    }), 200

@holiday_bp.route("/api/holiday/<int:holiday_id>", methods=["PUT"])
@jwt_required()
def update_holiday(holiday_id):
    holiday = Holiday.query.get(holiday_id)
    if not holiday:
        return jsonify({"error": "Holiday not found"}), 404

    data = request.get_json()
    # Yêu cầu gửi đúng field "name", "start_date" và "end_date"
    if "name" in data:
        holiday.name = data["name"]
    if "start_date" in data:
        try:
            holiday.start_date = date.fromisoformat(data["start_date"])
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if "end_date" in data:
        try:
            holiday.end_date = date.fromisoformat(data["end_date"])
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    try:
        db.session.commit()
        return jsonify({"message": f"Holiday {holiday_id} updated successfully"}), 200
    except Exception as e:
        logging.error(f"Error updating holiday {holiday_id}: {e}")
        return jsonify({"message": "An unexpected error occurred"}), 500

@holiday_bp.route("/api/holiday/<int:holiday_id>", methods=["DELETE"])
@jwt_required()
def delete_holiday(holiday_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Access denied"}), 403

    holiday = Holiday.query.get(holiday_id)
    if not holiday:
        return jsonify({"error": "Holiday not found"}), 404

    try:
        # Logic to delete the holiday
        db.session.delete(holiday)
        db.session.commit()
        return jsonify({"message": f"Holiday {holiday_id} deleted successfully"}), 200
    except Exception as e:
        logging.error(f"Error deleting holiday {holiday_id}: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Web routes - giữ nguyên đường dẫn 
@holiday_bp.route('/holidays', methods=['GET'])
@login_required
@admin_required
def holidays_page():
    holidays = Holiday.query.all()
    return render_template('holidays.html', holidays=holidays)

# POST /holidays/add
@holiday_bp.route('/holidays/add', methods=['POST'])
@login_required
@admin_required
def add_holiday():
    school_id = request.form.get('school_id') or None
    name = request.form.get('name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format! Please use YYYY-MM-DD.', 'danger')
        return redirect(url_for('holiday.holidays_page'))
    # Kiểm tra trùng ngày nghỉ
    if Holiday.query.filter_by(name=name, school_id=school_id, start_date=start_date, end_date=end_date).first():
        flash('Ngày nghỉ này đã tồn tại!', 'danger')
        return redirect(url_for('holiday.holidays_page'))
    holiday = Holiday(
        school_id=school_id,
        name=name,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(holiday)
    db.session.commit()
    flash('Thêm ngày nghỉ thành công!', 'success')
    return redirect(url_for('holiday.holidays_page'))

@holiday_bp.route('/holidays/edit/<int:holiday_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def web_edit_holiday(holiday_id):
    holiday = Holiday.query.get_or_404(holiday_id)
    schools = School.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        school_id = request.form.get('school_id') or None
        
        # Kiểm tra ngày nghỉ đã tồn tại chưa (nếu thay đổi thông tin)
        existing_holiday = Holiday.query.filter(
            Holiday.id != holiday_id,
            Holiday.name == name, 
            Holiday.school_id == school_id,
            Holiday.start_date == start_date, 
            Holiday.end_date == end_date
        ).first()
        
        if existing_holiday:
            flash('Ngày nghỉ này đã tồn tại!', 'danger')
            return redirect(url_for('holiday.web_edit_holiday', holiday_id=holiday_id))
        
        # Kiểm tra start_date <= end_date
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start_date > end_date:
                flash('Ngày bắt đầu phải sớm hơn hoặc bằng ngày kết thúc!', 'danger')
                return redirect(url_for('holiday.web_edit_holiday', holiday_id=holiday_id))
        except ValueError:
            flash('Invalid date format! Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('holiday.web_edit_holiday', holiday_id=holiday_id))
        
        # Cập nhật thông tin
        holiday.name = name
        holiday.start_date = start_date
        holiday.end_date = end_date
        holiday.school_id = school_id
        
        db.session.commit()
        flash('Cập nhật ngày nghỉ thành công!', 'success')
        return redirect(url_for('holiday.holidays_page'))
    
    # GET request - hiển thị form chỉnh sửa
    return render_template('edit_holiday.html', holiday=holiday, schools=schools)

@holiday_bp.route('/holidays/delete/<int:holiday_id>', methods=['POST'])
@login_required
@admin_required
def web_delete_holiday(holiday_id):
    holiday = Holiday.query.get_or_404(holiday_id)
    db.session.delete(holiday)
    db.session.commit()
    flash('Xóa ngày nghỉ thành công!', 'success')
    return redirect(url_for('holiday.holidays_page'))
