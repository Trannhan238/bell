from flask import Blueprint, request, jsonify
from app import db
from app.models.schedule import Schedule
from flask_jwt_extended import jwt_required

schedule_bp = Blueprint("schedule", __name__)

@schedule_bp.route("/create", methods=["POST"])
@jwt_required()
def create_schedule():
    data = request.get_json()
    bell_time = data.get("bell_time")
    bell_type = data.get("bell_type")
    day_of_week = data.get("day_of_week")
    
    new_schedule = Schedule(bell_time=bell_time, bell_type=bell_type, day_of_week=day_of_week)
    db.session.add(new_schedule)
    db.session.commit()
    
    return jsonify(message="Schedule created successfully"), 201
