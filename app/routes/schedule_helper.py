from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.holiday import Holiday
from app.models.device import Device
from app.models.user import User
from app.models.schedule import Schedule
from app.models.season_config import SeasonConfig  # Updated import to point to the correct file
from app import db
from datetime import date

schedule_helper_bp = Blueprint("schedule_helper", __name__, url_prefix="/api/schedule-helper")

# API: Kiểm tra hôm nay có phải là ngày nghỉ không
@schedule_helper_bp.route("/is_holiday", methods=["GET"])
def check_today_is_holiday():
    device_id = request.args.get("device_id")
    today = date.today()

    if device_id:
        device = Device.query.get(device_id)
        if not device:
            return jsonify(message="Device not found"), 404

        holidays = Holiday.query.filter(
            ((Holiday.school_id == None) | (Holiday.school_id == device.school_id)) &
            (Holiday.start_date <= today) & (Holiday.end_date >= today)
        ).all()
    else:
        holidays = Holiday.query.filter(
            (Holiday.school_id == None) &
            (Holiday.start_date <= today) & (Holiday.end_date >= today)
        ).all()

    is_holiday = len(holidays) > 0
    return jsonify(is_holiday=is_holiday)

# API: Lấy lịch chuông hôm nay
@schedule_helper_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_schedule():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role not in ['school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403

    if not user.school_id:
        return jsonify(message="User is not assigned to any school"), 403

    today = date.today()
    weekday = today.weekday()  # Monday is 0, Sunday is 6

    # Kiểm tra nếu hôm nay là ngày nghỉ
    holiday = Holiday.query.filter(
        Holiday.school_id == user.school_id,
        Holiday.start_date <= today,
        Holiday.end_date >= today
    ).first()

    if holiday:
        return jsonify(message="Today is a holiday", schedules=[])

    # Tự động xác định mùa
    season = SeasonConfig.query.filter_by(school_id=user.school_id).first()
    if not season:
        return jsonify(message="Missing season config", schedules=[]), 400

    is_summer = season.summer_start <= today <= season.summer_end

    # Lấy lịch chuông
    schedules = Schedule.query.filter_by(
        school_id=user.school_id,
        day_of_week=weekday,
        is_summer=is_summer
    ).all()

    schedules_data = []
    for schedule in schedules:
        schedules_data.append({
            "id": schedule.id,
            "time_point": schedule.time_point.strftime('%H:%M') if hasattr(schedule, 'time_point') and schedule.time_point else None,
            "bell_type": schedule.bell_type,
            "is_summer": schedule.is_summer
        })

    return jsonify(
        message="Today's schedules",
        date=today.strftime('%Y-%m-%d'),
        is_summer=is_summer,
        schedules=schedules_data
    )

# Alias route for compatibility
@schedule_helper_bp.route("/schedule/today", methods=["GET"])
def alias_get_today_schedule():
    return get_today_schedule()
