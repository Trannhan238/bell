from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.school import School
from app import db
from werkzeug.security import generate_password_hash
from app.utils.decorators import login_required, admin_required

# Bỏ url_prefix để các route web hoạt động đúng
user_bp = Blueprint("user", __name__)

# API route với đường dẫn /api/user/me
@user_bp.route("/api/user/me", methods=["GET"])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    return jsonify({
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "school": {
            "id": user.school.id if user.school else None,
            "name": user.school.name if user.school else None,
            "address": user.school.address if user.school else None
        }
    })

# Route web giữ nguyên đường dẫn /users
@user_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def users_page():
    users = User.query.all()
    schools = School.query.all()
    return render_template('pages/users.html', users=users, schools=schools)

@user_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    role = request.form.get('role')
    school_id = request.form.get('school_id') or None
    # Kiểm tra username đã tồn tại chưa
    if User.query.filter_by(username=username).first():
        flash('Tên đăng nhập đã tồn tại!', 'danger')
        return redirect(url_for('user.users_page'))
    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        email=email,
        role=role,
        school_id=school_id
    )
    db.session.add(user)
    db.session.commit()
    flash('Thêm người dùng thành công!', 'success')
    return redirect(url_for('user.users_page'))

@user_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def web_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    schools = School.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        full_name = request.form.get('full_name') 
        email = request.form.get('email')
        role = request.form.get('role')
        school_id = request.form.get('school_id') or None
        password = request.form.get('password')
        
        # Kiểm tra username đã tồn tại chưa (nếu thay đổi username)
        if username != user.username and User.query.filter_by(username=username).first():
            flash('Username đã tồn tại!', 'danger')
            return redirect(url_for('user.web_edit_user', user_id=user_id))
        
        # Kiểm tra email đã tồn tại chưa (nếu thay đổi email)
        if email != user.email and User.query.filter_by(email=email).first():
            flash('Email đã tồn tại!', 'danger')
            return redirect(url_for('user.web_edit_user', user_id=user_id))
        
        # Cập nhật thông tin
        user.username = username
        user.full_name = full_name
        user.email = email
        user.role = role
        user.school_id = school_id
        
        # Nếu có mật khẩu mới
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash('Cập nhật người dùng thành công!', 'success')
        return redirect(url_for('user.users_page'))
    
    # GET request - hiển thị form chỉnh sửa
    return render_template('pages/edit_user.html', user=user, schools=schools)

@user_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def web_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Xóa người dùng thành công!', 'success')
    return redirect(url_for('user.users_page'))
