from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.school import School

school_bp = Blueprint('school', __name__, url_prefix='/school')  # Đổi tên từ 'bp' thành 'school_bp'

@school_bp.route('/', methods=['GET'])
@jwt_required()
def get_schools():
    # Truy vấn danh sách các trường học từ cơ sở dữ liệu
    schools = School.query.all()
    school_list = [{"id": school.id, "name": school.name, "address": school.address, "phone": school.phone} for school in schools]
    return jsonify(school_list), 200