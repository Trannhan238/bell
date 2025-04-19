from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.season import SeasonConfig
from app.models.user import User
from app import db
from datetime import date

season_bp = Blueprint("season", __name__, url_prefix="/api/season")

@season_bp.route('/config', methods=['GET'], endpoint='get_season_config')
def get_season_config():
    return {"message": "Season config endpoint"}, 200

# API: Lấy cấu hình mùa cho trường
@season_bp.route("/", methods=["GET"], endpoint='get_season_config_root')
@jwt_required()
def get_season_config():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role not in ['school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403

    if not user.school_id:
        return jsonify(message="User is not assigned to any school"), 403

    season = SeasonConfig.query.filter_by(school_id=user.school_id).first()

    if not season:
        return jsonify(message="Season config not found"), 404

    return jsonify({
        "school_id": season.school_id,
        "summer_start": season.summer_start.strftime('%Y-%m-%d'),
        "summer_end": season.summer_end.strftime('%Y-%m-%d')
    })

# API: Thêm hoặc cập nhật cấu hình mùa
@season_bp.route("/", methods=["POST", "PUT"], endpoint='create_or_update_season_config')
@jwt_required()
def create_or_update_season_config():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role not in ['school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403

    if not user.school_id:
        return jsonify(message="User is not assigned to any school"), 403

    data = request.get_json()

    summer_start = data.get('summer_start')
    summer_end = data.get('summer_end')

    if not summer_start or not summer_end:
        return jsonify(message="Missing required fields: summer_start or summer_end"), 400

    # Kiểm tra và định dạng lại ngày tháng
    try:
        summer_start = date.fromisoformat(summer_start)
        summer_end = date.fromisoformat(summer_end)
    except ValueError:
        return jsonify(message="Invalid date format. Use YYYY-MM-DD."), 400

    # Kiểm tra xem có tồn tại config mùa cho trường không
    season = SeasonConfig.query.filter_by(school_id=user.school_id).first()

    if season:
        # Cập nhật
        season.summer_start = summer_start
        season.summer_end = summer_end
        db.session.commit()
        return jsonify(message="Season config updated successfully"), 200
    else:
        # Thêm mới
        new_season = SeasonConfig(
            school_id=user.school_id,
            summer_start=summer_start,
            summer_end=summer_end
        )
        db.session.add(new_season)
        db.session.commit()
        return jsonify(message="Season config created successfully"), 201

# API: Lấy cấu hình mùa theo ID
@season_bp.route("/<int:season_id>", methods=["GET"], endpoint='get_season_by_id')
@jwt_required()
def get_season_by_id(season_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role not in ['school_user', 'school_admin']:
        return jsonify(message="Access denied"), 403

    season = SeasonConfig.query.filter_by(id=season_id, school_id=user.school_id).first()

    if not season:
        return jsonify(message="Season config not found"), 404

    return jsonify({
        "id": season.id,
        "school_id": season.school_id,
        "summer_start": season.summer_start.strftime('%Y-%m-%d'),
        "summer_end": season.summer_end.strftime('%Y-%m-%d')
    }), 200
