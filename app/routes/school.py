from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.school import School
from app.models.user import User
from app import db
from app.utils.decorators import login_required, admin_required, school_admin_required

school_bp = Blueprint('school', __name__)

@school_bp.route('/api/schools', methods=['GET'])
@jwt_required()
def get_schools():
    """API endpoint to get schools information"""
    user_id = get_jwt_identity()
    
    # If the identity is a device, extract device_id
    is_device = False
    if isinstance(user_id, str) and ":" in user_id:
        is_device = True
        try:
            device_id = int(user_id.split(":")[0])
            from app.models.device import Device
            device = Device.query.get(device_id)
            if device:
                # Return only the device's school
                school = device.school
                if school:
                    return jsonify([{
                        "id": school.id,
                        "name": school.name,
                        "address": school.address,
                        "phone": school.phone
                    }])
                return jsonify([])
        except (ValueError, AttributeError, IndexError):
            return jsonify(message="Invalid identity"), 403
    
    # For admin users, return all schools
    if not is_device:
        user = User.query.get(user_id)
        if user and user.role == "admin":
            schools = School.query.all()
            result = []
            for school in schools:
                result.append({
                    "id": school.id,
                    "name": school.name,
                    "address": school.address,
                    "phone": school.phone
                })
            return jsonify(result)
    
    return jsonify(message="Unauthorized"), 403

@school_bp.route('/schools', methods=['GET'])
@login_required
@admin_required
def list_schools():
    schools = School.query.all()
    return render_template('schools.html', schools=schools)

@school_bp.route('/schools/add', methods=['POST'])
@login_required
@admin_required
def add_school():
    name = request.form.get('name')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    # Kiểm tra tên trường đã tồn tại chưa
    if School.query.filter_by(name=name).first():
        flash('Tên trường đã tồn tại!', 'danger')
        return redirect(url_for('school.list_schools'))
    
    school = School(name=name, address=address, phone=phone)
    db.session.add(school)
    db.session.commit()
    
    flash('Thêm trường học thành công!', 'success')
    return redirect(url_for('school.list_schools'))

@school_bp.route('/schools/edit/<int:school_id>', methods=['GET'])
@login_required
@admin_required
def edit_school_form(school_id):
    school = School.query.get_or_404(school_id)
    return render_template('edit_school.html', school=school)

@school_bp.route('/schools/edit/<int:school_id>', methods=['POST'])
@login_required
@admin_required
def edit_school(school_id):
    school = School.query.get_or_404(school_id)
    
    name = request.form.get('name')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    # Kiểm tra tên trường đã tồn tại chưa (nếu thay đổi tên)
    if name != school.name and School.query.filter_by(name=name).first():
        flash('Tên trường đã tồn tại!', 'danger')
        return redirect(url_for('school.edit_school_form', school_id=school_id))
    
    school.name = name
    school.address = address
    school.phone = phone
    
    db.session.commit()
    
    flash('Cập nhật trường học thành công!', 'success')
    return redirect(url_for('school.list_schools'))

@school_bp.route('/schools/delete/<int:school_id>', methods=['POST'])
@login_required
@admin_required
def delete_school(school_id):
    school = School.query.get_or_404(school_id)
    db.session.delete(school)
    db.session.commit()
    
    flash('Xóa trường học thành công!', 'success')
    return redirect(url_for('school.list_schools'))