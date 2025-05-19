from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from app.models.device import Device
from app.models.school import School
from app.utils.decorators import login_required, admin_required
from app.utils.helpers import get_devices_and_schools
from app import db
from flask_jwt_extended import jwt_required

frontend_bp = Blueprint("device_frontend", __name__)
device_bp = Blueprint("device_api", __name__)

@frontend_bp.route('/devices', methods=['GET', 'POST'])
@login_required
def devices_page():
    user = session.get('user')

    if not user:
        flash('Không tìm thấy thông tin người dùng!', 'danger')
        return redirect(url_for('auth.login'))

    # Use shared helper function to fetch devices and schools
    devices, schools = get_devices_and_schools()

    return render_template('pages/devices.html', devices=devices, schools=schools)

@frontend_bp.route('/devices/edit/<int:device_id>', methods=['POST'])
@login_required
@admin_required
def edit_device(device_id):
    """Edit a device by ID."""
    device = Device.query.get_or_404(device_id)
    name = request.form.get('name')
    ip_address = request.form.get('ip_address')
    mac_address = request.form.get('mac_address')
    school_id = request.form.get('school_id') or None
    user_id = request.form.get('user_id') or None
    active = True if request.form.get('active') else False

    # Check for duplicate MAC address (excluding the current device)
    if Device.query.filter(Device.mac_address == mac_address, Device.id != device_id).first():
        flash('A device with this MAC address already exists!', 'danger')
        return redirect(url_for('device_frontend.devices_page'))

    device.name = name
    device.ip_address = ip_address
    device.mac_address = mac_address
    device.school_id = school_id
    device.user_id = user_id
    device.active = active
    db.session.commit()

    flash('Device updated successfully!', 'success')
    return redirect(url_for('device_frontend.devices_page'))

@frontend_bp.route('/devices/delete/<int:device_id>', methods=['POST'])
@login_required
@admin_required
def delete_device(device_id):
    """Delete a device by ID."""
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()

    flash('Device deleted successfully!', 'success')
    return redirect(url_for('device_frontend.devices_page'))

@frontend_bp.route('/devices/add', methods=['POST'])
@login_required
@admin_required
def add_device():
    """Add a new device."""
    name = request.form.get('name')
    ip_address = request.form.get('ip_address')
    mac_address = request.form.get('mac_address')
    school_id = request.form.get('school_id') or None
    user_id = request.form.get('user_id') or None

    # Check if a device with the same MAC address already exists
    if Device.query.filter_by(mac_address=mac_address).first():
        flash('A device with this MAC address already exists!', 'danger')
        return redirect(url_for('device_frontend.devices_page'))

    device = Device(
        name=name,
        ip_address=ip_address,
        mac_address=mac_address,
        school_id=school_id,
        user_id=user_id,
        active=True,
        status='assigned'
    )
    db.session.add(device)
    db.session.commit()

    flash('Device added successfully!', 'success')
    return redirect(url_for('device_frontend.devices_page'))

@device_bp.route('/devices/add', methods=['POST'])
@login_required
@admin_required
def add_device():
    name = request.form.get('name')
    ip_address = request.form.get('ip_address')
    mac_address = request.form.get('mac_address')
    school_id = request.form.get('school_id') or None
    user_id = request.form.get('user_id') or None
    # Kiểm tra MAC đã tồn tại chưa
    if Device.query.filter_by(mac_address=mac_address).first():
        flash('Thiết bị với địa chỉ MAC này đã tồn tại!', 'danger')
        return redirect(url_for('device.devices_page'))
    device = Device(
        name=name,
        ip_address=ip_address,
        mac_address=mac_address,
        school_id=school_id,
        user_id=user_id,
        active=True,
        status='assigned'
    )
    db.session.add(device)
    db.session.commit()
    flash('Thêm thiết bị thành công!', 'success')
    return redirect(url_for('device.devices_page'))

@device_bp.route('/devices/edit/<int:device_id>', methods=['POST'])
@login_required
@admin_required
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    name = request.form.get('name')
    ip_address = request.form.get('ip_address')
    mac_address = request.form.get('mac_address')
    school_id = request.form.get('school_id') or None
    user_id = request.form.get('user_id') or None
    active = True if request.form.get('active') else False
    # Kiểm tra trùng MAC (trừ chính nó)
    if Device.query.filter(Device.mac_address == mac_address, Device.id != device_id).first():
        flash('Thiết bị với địa chỉ MAC này đã tồn tại!', 'danger')
        return redirect(url_for('device.devices_page'))
    device.name = name
    device.ip_address = ip_address
    device.mac_address = mac_address
    device.school_id = school_id
    device.user_id = user_id
    device.active = active
    db.session.commit()
    flash('Cập nhật thiết bị thành công!', 'success')
    return redirect(url_for('device.devices_page'))

@device_bp.route('/devices/delete/<int:device_id>', methods=['POST'])
@login_required
@admin_required
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash('Xóa thiết bị thành công!', 'success')
    return redirect(url_for('device.devices_page'))

@device_bp.route("/create", methods=["POST"])
@jwt_required()
def create_device():
    data = request.get_json()
    name = data.get("name")
    ip_address = data.get("ip_address")
    mac_address = data.get("mac_address")
    user_id = data.get("user_id")
    school_id = data.get("school_id")
    
    # Kiểm tra thiết bị đã tồn tại chưa
    existing_device = Device.query.filter_by(mac_address=mac_address).first()
    if existing_device:
        return jsonify(message="Thiết bị với địa chỉ MAC này đã tồn tại"), 400
    
    new_device = Device(
        name=name,
        ip_address=ip_address,
        mac_address=mac_address,
        user_id=user_id,
        school_id=school_id,
        active=True,
        status="assigned"
    )
    db.session.add(new_device)
    db.session.commit()
    
    return jsonify(message="Device created successfully"), 201

@device_bp.route("/list", methods=["GET"])
@jwt_required()
def list_devices():
    devices = Device.query.all()
    device_list = [{"id": device.id, "name": device.name, "ip_address": device.ip_address, 
                    "mac_address": device.mac_address, "status": device.status, 
                    "active": device.active} for device in devices]
    return jsonify(device_list), 200

@device_bp.route("/unassigned", methods=["GET"])
@jwt_required()
def list_unassigned_devices():
    """Liệt kê tất cả thiết bị chưa được gán cho admin"""
    unassigned_devices = Device.query.filter_by(status="unassigned").all()
    device_list = [{"id": d.id, "name": d.name, "mac_address": d.mac_address, 
                    "last_seen": d.last_seen.isoformat() if d.last_seen else None} 
                   for d in unassigned_devices]
    return jsonify(device_list), 200

@device_bp.route("/assign", methods=["POST"])
@jwt_required()
def assign_device():
    """Endpoint để admin gán thiết bị cho trường học và người dùng"""
    data = request.get_json()
    device_id = data.get("device_id")
    name = data.get("name")
    school_id = data.get("school_id")
    user_id = data.get("user_id")
    active = data.get("active", True)
    
    if not all([device_id, school_id, user_id]):
        return jsonify(message="Missing required fields"), 400
    
    device = Device.query.get(device_id)
    if not device:
        return jsonify(message="Device not found"), 404
    
    # Cập nhật thông tin thiết bị
    device.name = name if name else device.name
    device.school_id = school_id
    device.user_id = user_id
    device.active = active
    device.status = "assigned"
    
    db.session.commit()
    
    return jsonify(message="Device assigned successfully"), 200

@device_bp.route("/update", methods=["POST"])
@jwt_required()
def update_device():
    """Endpoint để cập nhật thông tin thiết bị"""
    data = request.get_json()
    device_id = data.get("device_id")
    
    if not device_id:
        return jsonify(message="Missing device ID"), 400
    
    device = Device.query.get(device_id)
    if not device:
        return jsonify(message="Device not found"), 404
    
    # Cập nhật các trường được cung cấp
    for field in ["name", "active", "school_id", "user_id"]:
        if field in data:
            setattr(device, field, data[field])
    
    db.session.commit()
    
    return jsonify(message="Device updated successfully"), 200

@device_bp.route("/api/devices/all", methods=["GET"])
@jwt_required()
def get_device_details():
    """Lấy danh sách thông tin chi tiết tất cả các thiết bị cho admin"""
    devices = Device.query.all()
    
    result = []
    for device in devices:
        device_data = {
            "id": device.id,
            "name": device.name,
            "ip_address": device.ip_address,
            "mac_address": device.mac_address,
            "status": device.status,
            "active": device.active,
            "school_id": device.school_id,
            "user_id": device.user_id,
            "last_seen": device.last_seen.isoformat() if device.last_seen else None
        }
        result.append(device_data)
    
    return jsonify(result), 200
