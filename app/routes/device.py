from flask import Blueprint, request, jsonify
from app import db
from app.models.device import Device
from flask_jwt_extended import jwt_required

device_bp = Blueprint("device", __name__)

@device_bp.route("/create", methods=["POST"])
@jwt_required()
def create_device():
    data = request.get_json()
    name = data.get("name")
    ip_address = data.get("ip_address")
    mac_address = data.get("mac_address")
    user_id = data.get("user_id")
    school_id = data.get("school_id")
    
    new_device = Device(
        name=name,
        ip_address=ip_address,
        mac_address=mac_address,
        user_id=user_id,
        school_id=school_id
    )
    db.session.add(new_device)
    db.session.commit()
    
    return jsonify(message="Device created successfully"), 201

@device_bp.route("/list", methods=["GET"])
@jwt_required()
def list_devices():
    devices = Device.query.all()
    device_list = [{"id": device.id, "name": device.name, "ip_address": device.ip_address} for device in devices]
    return jsonify(device_list), 200
