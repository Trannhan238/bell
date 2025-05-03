from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def login_required(view_func):
    """
    Decorator dùng cho các route giao diện web
    KHÔNG liên quan đến JWT hay API
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user' not in session:
            flash('Bạn cần đăng nhập để truy cập!', 'warning')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped_view

def admin_required(view_func):
    """
    Decorator dùng cho các route giao diện web yêu cầu admin
    Dựa vào session, KHÔNG liên quan đến JWT
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user' not in session:
            flash('Bạn cần đăng nhập để truy cập!', 'warning')
            return redirect(url_for('auth.login'))
        if session['user'].get('role') != 'admin':
            flash('Bạn không có quyền truy cập!', 'danger')
            return redirect(url_for('index'))
        return view_func(*args, **kwargs)
    return wrapped_view

def school_user_required(view_func):
    """
    Decorator dùng cho các route giao diện web yêu cầu school_user
    Dựa vào session, KHÔNG liên quan đến JWT
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user' not in session:
            flash('Bạn cần đăng nhập để truy cập!', 'warning')
            return redirect(url_for('auth.login'))
        if session['user'].get('role') not in ['school_user', 'admin', 'school_admin']:
            flash('Bạn không có quyền truy cập!', 'danger')
            return redirect(url_for('index'))
        return view_func(*args, **kwargs)
    return wrapped_view

def school_admin_required(view_func):
    """
    Decorator dùng cho các route giao diện web yêu cầu school_admin
    Dựa vào session, KHÔNG liên quan đến JWT
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user' not in session:
            flash('Bạn cần đăng nhập để truy cập!', 'warning')
            return redirect(url_for('auth.login'))
        if session['user'].get('role') not in ['school_admin', 'admin']:
            flash('Bạn không có quyền truy cập!', 'danger')
            return redirect(url_for('index'))
        return view_func(*args, **kwargs)
    return wrapped_view

def school_specific_access(view_func):
    """
    Decorator dùng cho các route giao diện web yêu cầu phân quyền theo trường
    - Admin hệ thống: xem tất cả trường
    - Admin trường: chỉ xem được trường của mình quản lý
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user' not in session:
            flash('Bạn cần đăng nhập để truy cập!', 'warning')
            return redirect(url_for('auth.login'))
        
        user = session['user']
        logging.debug(f"User session data in decorator: {user}")
        # Admin hệ thống có quyền xem tất cả
        if user.get('role') == 'admin':
            return view_func(*args, **kwargs)
        
        # School users can only access their own school's data
        elif user.get('role') in ['school_admin', 'school_user']:
            school_id = kwargs.get('school_id') or request.args.get('school_id')
            logging.debug(f"School user/admin accessing with school_id: {school_id}")

            # Use school_id from session for school_user if not provided
            if user.get('role') == 'school_user' and not school_id:
                school_id = user.get('school_id')
                logging.debug(f"Defaulting school_id to session value: {school_id}")

            if not school_id:
                return view_func(*args, **kwargs)

            if int(school_id) == int(user.get('school_id', 0)):
                return view_func(*args, **kwargs)

            flash('Bạn không có quyền truy cập dữ liệu của trường này!', 'danger')
            return redirect(url_for('index'))
        
        # Các role khác không có quyền
        logging.warning(f"Unauthorized access attempt by user: {user}")
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))
    
    return wrapped_view
