from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from app import db
from app.models.device import Device
from app.models.school import School
from app.models.user import User
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
from app.utils.decorators import login_required, admin_required, school_admin_required
from app.utils.helpers import validate_mac_address

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
    # Lấy thông tin từ JWT token
    identity = get_jwt_identity()
    
    # Phân tích identity từ chuỗi
    try:
        device_id = int(identity.split(":")[0])
    except (ValueError, AttributeError, IndexError):
        return jsonify(message="Invalid device identity"), 403
    
    # Lấy thông tin thiết bị
    device = Device.query.get(device_id)
    if not device or not device.active:
        return jsonify(message="Device not found or inactive"), 404
    
    if not device.school_id:
        return jsonify(message="Device not assigned to any school"), 403
    
    from app.models.holiday import Holiday
    from app.models.schedule import Schedule
    from app.models.season_config import SeasonConfig  # Updated import to use season_config
    from datetime import date
    
    today = date.today()
    weekday = today.weekday()  # Monday is 0, Sunday is 6
    
    # Kiểm tra nếu hôm nay là ngày nghỉ
    holiday = Holiday.query.filter(
        ((Holiday.school_id == None) | (Holiday.school_id == device.school_id)),
        (Holiday.start_date <= today),
        (Holiday.end_date >= today)
    ).first()
    
    if holiday:
        return jsonify(message="Today is a holiday", schedules=[])
    
    # Tự động xác định mùa
    season = SeasonConfig.query.filter_by(school_id=device.school_id).first()
    if not season:
        return jsonify(message="Missing season config", schedules=[]), 400
    
    is_summer = False
    if season.summer_start and season.summer_end:
        is_summer = season.summer_start <= today <= season.summer_end
    
    # Lấy lịch chuông
    schedules = Schedule.query.filter_by(
        school_id=device.school_id,
        day_of_week=weekday,
        is_summer=is_summer
    ).order_by(Schedule.time_point).all()
    
    schedules_data = []
    for schedule in schedules:
        schedules_data.append({
            "id": schedule.id,
            "time": schedule.time_point.strftime('%H:%M'),
            "bell_type": schedule.bell_type
        })
    
    return jsonify({
        "message": "Lịch hôm nay",
        "date": today.strftime('%Y-%m-%d'),
        "is_summer": is_summer,
        "schedules": schedules_data
    })

