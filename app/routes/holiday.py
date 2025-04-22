from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError, validates_schema
from datetime import datetime, date
from app.models.holiday import Holiday  # Ensure Holiday is imported
from app.models.user import User  # Ensure User is imported
from app import db  # Import db for database operations
import logging  # Add logging for debugging

holiday_bp = Blueprint("holiday", __name__, url_prefix="/api/holiday")

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

# POST /api/holiday/
@holiday_bp.route("/", methods=["POST"])
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

# GET /api/holiday/
@holiday_bp.route("/", methods=["GET"])
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

# PUT /api/holiday/<int:holiday_id>
@holiday_bp.route("/<int:holiday_id>", methods=["PUT"])
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

# DELETE /api/holiday/<int:holiday_id>
@holiday_bp.route("/<int:holiday_id>", methods=["DELETE"])
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
