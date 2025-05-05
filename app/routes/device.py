from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from app import db
from app.models.device import Device
from app.models.school import School
from app.models.user import User
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
from app.utils.decorators import login_required, admin_required, school_admin_required
from app.utils.helpers import validate_mac_address
from app.models.winter_shift_config import WinterShiftConfig  # Sử dụng đường dẫn đầy đủ
import logging

device_bp = Blueprint("device", __name__)

@device_bp.route("/register", methods=["POST"])
def register_device():
    """Endpoint for ESP32 to register itself with the server"""
    data = request.get_json()
    mac_address = data.get("mac_address")
    ip_address = request.remote_addr  # Lấy IP address từ request
    
    if not validate_mac_address(mac_address):
        return jsonify(message="Invalid or missing MAC address"), 400
    
    # Kiểm tra thiết bị đã tồn tại chưa
    device = Device.query.filter_by(mac_address=mac_address).first()
    
    if device:
        # Cập nhật IP và thời gian hoạt động
        device.ip_address = ip_address
        device.last_seen = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Device already registered",
            "device_id": device.id,
            "active": device.active,
            "status": device.status
        }), 200
    else:
        # Tạo thiết bị mới với trạng thái chưa được gán
        new_device = Device(
            name=f"ESP32-{mac_address[-6:]}",  # Tên tạm thời
            ip_address=ip_address,
            mac_address=mac_address,
            active=False,
            status="unassigned",
            last_seen=datetime.utcnow()
        )
        db.session.add(new_device)
        db.session.commit()
        
        return jsonify({
            "message": "Device registered successfully, awaiting assignment",
            "device_id": new_device.id
        }), 201

import json

@device_bp.route("/authenticate", methods=["POST"])
def authenticate_device():
    """Endpoint for ESP32 to authenticate and get JWT token"""
    data = request.get_json()
    mac_address = data.get("mac_address")
    
    if not mac_address:
        return jsonify(message="Missing MAC address"), 400
    
    device = Device.query.filter_by(mac_address=mac_address).first()
    
    if not device:
        return jsonify(message="Device not registered"), 404
    
    if not device.active:
        return jsonify(message="Device not activated yet"), 403
    
    # Cập nhật IP và thời gian
    device.ip_address = request.remote_addr
    device.last_seen = datetime.utcnow()
    db.session.commit()
    
    # Tạo JWT token với identity là chuỗi
    identity = f"{device.id}:{mac_address}"
    
    token = create_access_token(
        identity=identity,
        expires_delta=timedelta(days=30)
    )
    
    return jsonify({
        "message": "Authentication successful",
        "token": token,
        "device_id": device.id,
        "school_id": device.school_id
    }), 200


@device_bp.route("/schedule/today", methods=["GET"])
@jwt_required()
def get_device_schedule():
    """Endpoint cho ESP32 lấy lịch chuông của ngày hôm nay"""
    logging.info("Received request for today's schedule")

    # Lấy thông tin từ JWT token
    identity = get_jwt_identity()
    logging.info(f"JWT identity: {identity}")

    # Phân tích identity từ chuỗi
    try:
        device_id = int(identity.split(":")[0])
        logging.info(f"Device ID: {device_id}")
    except (ValueError, AttributeError, IndexError):
        logging.error("Invalid device identity")
        return jsonify(message="Invalid device identity"), 403

    # Lấy thông tin thiết bị
    device = Device.query.get(device_id)
    if not device or not device.active:
        logging.error("Device not found or inactive")
        return jsonify(message="Device not found or inactive"), 404

    if not device.school_id:
        logging.error("Device not assigned to any school")
        return jsonify(message="Device not assigned to any school"), 403

    from app.models.holiday import Holiday
    from app.models.schedule import Schedule
    from datetime import date

    today = date.today()
    weekday = today.weekday()  # Monday is 0, Sunday is 6
    logging.info(f"Today: {today}, Weekday: {weekday}")

    # Kiểm tra nếu hôm nay là ngày nghỉ
    holiday = Holiday.query.filter(
        ((Holiday.school_id == None) | (Holiday.school_id == device.school_id)),
        (Holiday.start_date <= today),
        (Holiday.end_date >= today)
    ).first()

    if holiday:
        logging.info("Today is a holiday")
        return jsonify(message="Today is a holiday", schedules=[])

    # Xác định mùa dựa trên WinterShiftConfig
    winter_config = WinterShiftConfig.query.filter_by(school_id=device.school_id).first()
    logging.info(f"Winter config: {winter_config}")

    # Mặc định là không phải mùa hè (tức là mùa học bình thường)
    is_summer = False

    # Nếu có cấu hình mùa đông, kiểm tra xem hôm nay có phải là mùa đông không
    is_winter = False
    if winter_config:
        current_month = today.month
        # Xử lý trường hợp tháng bắt đầu > tháng kết thúc (ví dụ: 10 -> 3, tức là từ tháng 10 đến tháng 3 năm sau)
        if winter_config.start_month > winter_config.end_month:
            is_winter = (current_month >= winter_config.start_month) or (current_month <= winter_config.end_month)
        else:
            is_winter = winter_config.start_month <= current_month <= winter_config.end_month
        logging.info(f"Is winter: {is_winter}")

    logging.info(f"Device school_id: {device.school_id}")
    logging.info(f"Querying schedules with: school_id={device.school_id}, day_of_week={weekday}, is_summer={is_summer}")

    schedules = Schedule.query.filter_by(
        school_id=device.school_id,
        day_of_week=weekday,
        is_summer=is_summer
    ).order_by(Schedule.time_point).all()

    logging.info(f"Schedules found: {len(schedules)}")

    # Điều chỉnh thời gian nếu là mùa đông
    schedules_data = []
    if is_winter and winter_config:
        for schedule in schedules:
            time_point = schedule.time_point
            shift_minutes = winter_config.morning_shift_minutes if time_point.hour < 12 else winter_config.afternoon_shift_minutes
            from datetime import datetime, timedelta
            adjusted_dt = datetime.combine(today, time_point) + timedelta(minutes=shift_minutes)
            schedules_data.append({
                "id": schedule.id,
                "time": adjusted_dt.strftime('%H:%M'),
                "bell_type": schedule.bell_type
            })
    else:
        for schedule in schedules:
            schedules_data.append({
                "id": schedule.id,
                "time": schedule.time_point.strftime('%H:%M'),
                "bell_type": schedule.bell_type
            })

    logging.info(f"Schedules data: {schedules_data}")
    return jsonify({
        "message": "Lịch hôm nay",
        "date": today.strftime('%Y-%m-%d'),
        "is_winter": is_winter,
        "schedules": schedules_data
    })

