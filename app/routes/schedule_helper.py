from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.holiday import Holiday
from app.models.device import Device
from app.models.user import User
from app.models.schedule import Schedule
from app.models.season_config import SeasonConfig  # Updated import to point to the correct file
from app.models.winter_shift_config import WinterShiftConfig  # Sử dụng đường dẫn đầy đủ
from app import db
from datetime import date, datetime

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

    # Fetch winter shift configuration for the school
    winter_shift = WinterShiftConfig.query.filter_by(school_id=user.school_id).first()

    # Adjust schedules for winter shift if applicable
    schedules_data = [
        {
            "id": schedule.id,
            "time_point": apply_winter_shift(
                schedule.time_point,
                today,
                winter_shift.morning_shift_minutes if schedule.bell_type == 'morning' else winter_shift.afternoon_shift_minutes
            ).strftime('%H:%M') if schedule.time_point else None,
            "bell_type": schedule.bell_type,
            "is_summer": schedule.is_summer
        }
        for schedule in schedules
    ]

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

def process_schedule_with_winter_shift(school_id, base_schedule):
    """
    Adjusts the schedule based on winter time shift configuration.

    :param school_id: ID of the school to fetch winter shift config.
    :param base_schedule: List of base bell times (summer times).
    :return: Adjusted schedule with winter shifts applied if applicable.
    """
    today = datetime.now()
    current_month = today.month

    # Fetch winter shift configuration for the school
    winter_shift = WinterShiftConfig.query.filter_by(school_id=school_id).first()

    if not winter_shift:
        return base_schedule  # No winter shift config, return base schedule

    # Check if the current date is within the winter shift range
    is_winter = (
        winter_shift.start_month <= current_month or current_month <= winter_shift.end_month
    )

    if not is_winter:
        return base_schedule  # Not in winter range, return base schedule

    # Adjust the schedule based on winter shift minutes
    adjusted_schedule = []
    for bell_time in base_schedule:
        if bell_time['type'] == 'morning':
            adjusted_time = bell_time['time'] + winter_shift.morning_shift_minutes
        elif bell_time['type'] == 'afternoon':
            adjusted_time = bell_time['time'] + winter_shift.afternoon_shift_minutes
        else:
            adjusted_time = bell_time['time']

        adjusted_schedule.append({
            'type': bell_time['type'],
            'time': adjusted_time
        })

    return adjusted_schedule

def apply_winter_shift(time_point, today, shift_minutes):
    """
    Applies winter shift to a given time point.

    :param time_point: Original time point.
    :param today: Current date.
    :param shift_minutes: Minutes to shift.
    :return: Adjusted time point.
    """
    if not time_point:
        return None

    return time_point + timedelta(minutes=shift_minutes)
