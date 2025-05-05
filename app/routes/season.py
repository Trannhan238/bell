from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.school import School
from app.models.winter_shift_config import WinterShiftConfig  # Sử dụng đường dẫn đầy đủ
from app.utils.decorators import login_required, admin_required
from app import db
from datetime import date
from sqlalchemy.orm import joinedload

# Bỏ url_prefix để các route web hoạt động đúng
season_bp = Blueprint("season", __name__)

@season_bp.route("/seasons", methods=["GET"])
@login_required
@admin_required
def list_seasons():
    """Hiển thị trang quản lý cấu hình mùa"""
    schools = School.query.all()  # Removed joinedload(School.seasons) as season_config no longer exists
    print("Schools:", schools)
    return render_template('seasons.html', schools=schools)

@season_bp.route("/seasons/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_season():
    if request.method == "GET":
        school_id = request.args.get('school_id')
        schools = School.query.all()
        return render_template('add_season.html', school_id=school_id, schools=schools)

    # Xử lý POST để thêm mùa vụ mới
    school_id = request.form.get('school_id')
    summer_start = request.form.get('summer_start')
    summer_end = request.form.get('summer_end')

    if not all([school_id, summer_start, summer_end]):
        flash('Missing required fields!', 'danger')
        return redirect(url_for('season.list_seasons'))

    try:
        # Convert strings to date objects
        summer_start_date = date.fromisoformat(summer_start)
        summer_end_date = date.fromisoformat(summer_end)

        # Validate dates
        if summer_start_date >= summer_end_date:
            flash('Summer start date must be before summer end date.', 'danger')
            return redirect(url_for('season.list_seasons'))

        flash('Season configuration added successfully!', 'success')
    except ValueError:
        flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding season configuration: {str(e)}', 'danger')

    return redirect(url_for('season.list_seasons'))
@season_bp.route("/seasons/edit/<int:season_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_season(season_id):
    """Edit an existing season configuration."""
    schools = School.query.all()

    if request.method == "POST":
        school_id = request.form.get('school_id')
        
        # Kiểm tra school_id có giá trị và chuyển sang integer
        if not school_id:
            flash('School ID is required!', 'danger')
            return redirect(url_for('season.edit_season', season_id=season_id))

        try:
            school_id = int(school_id)  # Ensure school_id is an integer

            start_month = int(request.form.get('start_month'))
            end_month = int(request.form.get('end_month'))
            shift_minutes = int(request.form.get('shift_minutes'))

            if not (1 <= start_month <= 12 and 1 <= end_month <= 12):
                raise ValueError("Tháng phải nằm trong khoảng từ 1 đến 12.")

            # Example: Save to winter_shift_config table
            winter_shift = WinterShiftConfig.query.filter_by(school_id=school_id).first()
            if not winter_shift:
                winter_shift = WinterShiftConfig(
                    school_id=school_id,
                    start_month=start_month,
                    end_month=end_month,
                    morning_shift_minutes=shift_minutes,
                    afternoon_shift_minutes=shift_minutes
                )
                db.session.add(winter_shift)
            else:
                winter_shift.start_month = start_month
                winter_shift.end_month = end_month
                winter_shift.morning_shift_minutes = shift_minutes
                winter_shift.afternoon_shift_minutes = shift_minutes

            db.session.commit()

            flash('Configuration updated successfully!', 'success')
            return redirect(url_for('season.list_seasons'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating configuration: {str(e)}', 'danger')

    season = None  # Set season to None as season_config table no longer exists
    return render_template('edit_season.html', season=season, schools=schools)


@season_bp.route("/seasons/delete/<int:season_id>", methods=["GET"])
@login_required
@admin_required
def delete_season(season_id):
    """Delete a season configuration."""
    try:
        flash('Season configuration deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting season configuration: {str(e)}', 'danger')

    return redirect(url_for('season.list_seasons'))
