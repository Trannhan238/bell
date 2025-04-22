from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.season_config import SeasonConfig
from app.models.user import User
from app import db
from datetime import date

season_bp = Blueprint("season", __name__, url_prefix="/api/season")

@season_bp.route("/config", methods=["GET"])
@jwt_required()
def get_season_config():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role not in ['school_user', 'school_admin', 'admin']:
        return jsonify(message="Access denied"), 403

    # Với admin trường dùng school_id của user,
    # với admin hệ thống yêu cầu truyền school_id qua query params
    if user.role == "school_admin":
        school_id = user.school_id
        if not school_id:
            return jsonify(message="User is not assigned to any school"), 403
    else:
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

@season_bp.route("/config", methods=["PUT"])
@jwt_required()
def update_season_config():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # Cho phép admin hệ thống và admin trường
    if not user or user.role not in ["admin", "school_admin"]:
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

    if user.role == "school_admin":
        school_id = user.school_id
        if not school_id:
            return jsonify(message="User is not assigned to any school"), 403
    else:
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

    db.session.commit()
    return jsonify(message=message), 200

@season_bp.route("/<int:season_id>", methods=["DELETE"], endpoint='delete_season_config')
@jwt_required()
def delete_season_config(season_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # Cho phép admin hệ thống và admin trường
    if not user or user.role not in ["admin", "school_admin"]:
        return jsonify(message="Access denied"), 403
    season = SeasonConfig.query.filter_by(id=season_id).first()
    if not season:
        return jsonify(message="Season config not found"), 404
    # Nếu user là school_admin thì chỉ được thao tác trên school của mình
    if user.role == "school_admin" and season.school_id != user.school_id:
        return jsonify(message="Access denied"), 403
    try:
        db.session.delete(season)
        db.session.commit()
        return jsonify(message="Season config deleted successfully"), 200
    except Exception as e:
        return jsonify(message="An unexpected error occurred"), 500
