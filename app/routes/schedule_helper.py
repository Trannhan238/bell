from flask import Blueprint, jsonify, request
from app.models.holiday import Holiday
from app.models.device import Device
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
