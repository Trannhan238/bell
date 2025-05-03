from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.season_config import SeasonConfig
from app.models.user import User
from app.models.school import School
from app.utils.decorators import login_required, admin_required
from app import db
from datetime import date
from sqlalchemy.orm import joinedload
# Protect this API so only 'admin' or 'school_admin' users can access it. Return 403 with JSON if not authorized.

# Bỏ url_prefix để các route web hoạt động đúng
season_bp = Blueprint("season", __name__)

@season_bp.route("/api/season/config", methods=["GET"])
@jwt_required()
def get_season_config():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # Chỉ cho phép admin hệ thống
    if not user or user.role != 'admin':
        return jsonify(message="Access denied"), 403

    school_id = request.args.get("school_id")
    if not school_id:
        return jsonify(message="Missing required parameter: school_id"), 400

    season = SeasonConfig.query.filter_by(school_id=school_id).first()
    if not season:
        return jsonify(message="Season config not found"), 404

    return jsonify({
        "school_id": season.school_id,
        "summer_start": season.summer_start.strftime('%Y-%m-%d'),
        "summer_end": season.summer_end.strftime('%Y-%m-%d')
    }), 200

@season_bp.route("/api/season/config", methods=["PUT"])
@jwt_required()
def update_season_config():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # Chỉ cho phép admin hệ thống
    if not user or user.role != 'admin':
        return jsonify(message="Access denied"), 403

    data = request.get_json()
    summer_start = data.get("summer_start")
    summer_end = data.get("summer_end")
    if not summer_start or not summer_end:
        return jsonify(message="Missing required fields: summer_start, summer_end"), 400

    try:
        summer_start = date.fromisoformat(summer_start)
        summer_end = date.fromisoformat(summer_end)
    except ValueError:
        return jsonify(message="Invalid date format. Use YYYY-MM-DD."), 400

    if summer_start >= summer_end:
        return jsonify(message="summer_start must be before summer_end"), 400

    school_id = data.get("school_id")
    if not school_id:
        return jsonify(message="Missing required field: school_id"), 400

    season = SeasonConfig.query.filter_by(school_id=school_id).first()
    if season:
        season.summer_start = summer_start
        season.summer_end = summer_end
        message = "Season config updated successfully"
    else:
        season = SeasonConfig(
            school_id=school_id,
            summer_start=summer_start,
            summer_end=summer_end
        )
        db.session.add(season)
        message = "Season config created successfully"

    try:
        db.session.commit()
        return jsonify(message=message), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message="An unexpected error occurred", error=str(e)), 500

@season_bp.route("/api/season/<int:season_id>", methods=["DELETE"])
@jwt_required()
def delete_season_config(season_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # Chỉ cho phép admin hệ thống
    if not user or user.role != 'admin':
        return jsonify(message="Access denied"), 403

    season = SeasonConfig.query.filter_by(id=season_id).first()
    if not season:
        return jsonify(message="Season config not found"), 404

    try:
        db.session.delete(season)
        db.session.commit()
        return jsonify(message="Season config deleted successfully"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message="An unexpected error occurred", error=str(e)), 500

@season_bp.route("/seasons", methods=["GET"])
@login_required
@admin_required
def list_seasons():
    """Hiển thị trang quản lý cấu hình mùa"""
    seasons = SeasonConfig.query.options(joinedload(SeasonConfig.school)).all()
    schools = School.query.options(joinedload(School.seasons)).all()
    print("Schools:", schools)
    print("Seasons:", seasons)
    return render_template('seasons.html', seasons=seasons, schools=schools)

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

        # Check if a season config already exists for this school
        existing_season = SeasonConfig.query.filter_by(school_id=school_id).first()
        if existing_season:
            flash('A season configuration already exists for this school!', 'danger')
            return redirect(url_for('season.list_seasons'))

        # Create new season config
        new_season = SeasonConfig(
            school_id=school_id,
            summer_start=summer_start_date,
            summer_end=summer_end_date
        )
        db.session.add(new_season)
        db.session.commit()

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
    season = SeasonConfig.query.get_or_404(season_id)
    schools = School.query.all()

    if request.method == "POST":
        school_id = request.form.get('school_id')
        summer_start = request.form.get('summer_start')
        summer_end = request.form.get('summer_end')

        if not all([school_id, summer_start, summer_end]):
            flash('Missing required fields!', 'danger')
            return redirect(url_for('season.edit_season', season_id=season_id))

        try:
            # Convert strings to date objects
            summer_start_date = date.fromisoformat(summer_start)
            summer_end_date = date.fromisoformat(summer_end)

            # Validate dates
            if summer_start_date >= summer_end_date:
                flash('Summer start date must be before summer end date.', 'danger')
                return redirect(url_for('season.edit_season', season_id=season_id))

            # Update season config
            season.school_id = school_id
            season.summer_start = summer_start_date
            season.summer_end = summer_end_date

            db.session.commit()
            flash('Season configuration updated successfully!', 'success')
            return redirect(url_for('season.list_seasons'))
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating season configuration: {str(e)}', 'danger')

    return render_template('edit_season.html', season=season, schools=schools)
