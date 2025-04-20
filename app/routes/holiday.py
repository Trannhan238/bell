from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError, validates_schema
from datetime import datetime

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
})

# POST /api/holiday/
@holiday_bp.route("/", methods=["POST"])
@jwt_required()
def create_holiday():
    try:
        data = holiday_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # Logic to create a holiday (e.g., save to DB)
    # Example response:
    return jsonify({"message": "Holiday created successfully", "data": data}), 201

# GET /api/holiday/
@holiday_bp.route("/", methods=["GET"])
@jwt_required()
def get_holidays():
    args = pagination_schema.load(request.args)
    page = args["page"]
    per_page = args["per_page"]
    search = args["search"]

    # Logic to fetch holidays with pagination and search
    # Example: Filter holidays by name if `search` is provided
    holidays = [
        # Mock data for demonstration
        {"id": 1, "name": "New Year", "start_date": "2025-01-01", "end_date": "2025-01-02"},
        {"id": 2, "name": "Summer Break", "start_date": "2025-06-01", "end_date": "2025-06-30"}
    ]
    if search:
        holidays = [h for h in holidays if search.lower() in h["name"].lower()]

    # Paginate results
    start = (page - 1) * per_page
    end = start + per_page
    paginated_holidays = holidays[start:end]

    return jsonify({
        "data": paginated_holidays,
        "total": len(holidays),
        "page": page,
        "per_page": per_page
    }), 200

# PUT /api/holiday/<int:holiday_id>
@holiday_bp.route("/<int:holiday_id>", methods=["PUT"])
@jwt_required()
def update_holiday(holiday_id):
    try:
        data = holiday_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # Logic to update a holiday (e.g., update in DB)
    # Example response:
    return jsonify({"message": f"Holiday {holiday_id} updated successfully", "data": data}), 200

# DELETE /api/holiday/<int:holiday_id>
@holiday_bp.route("/<int:holiday_id>", methods=["DELETE"])
@jwt_required()
def delete_holiday(holiday_id):
    # Logic to delete a holiday (e.g., remove from DB)
    # Example response:
    return jsonify({"message": f"Holiday {holiday_id} deleted successfully"}), 200
