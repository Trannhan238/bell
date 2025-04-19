from flask import Blueprint, jsonify

bp = Blueprint('school', __name__, url_prefix='/school')

@bp.route('/', methods=['GET'])
def get_schools():
    return jsonify({'msg': 'school endpoint'})