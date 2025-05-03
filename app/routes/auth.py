from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user'] = {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'school_id': user.school_id  # Thêm school_id vào session
            }
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Đã đăng xuất!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/check-session')
def check_session():
    """Route để kiểm tra thông tin session hiện tại"""
    if 'user' not in session:
        return jsonify({'error': 'Không có thông tin người dùng trong session'})
    
    return jsonify({
        'user': session['user'],
        'message': 'Kiểm tra console/terminal để xem thêm thông tin debug'
    })
