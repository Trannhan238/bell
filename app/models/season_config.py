from app import db
from datetime import date

class SeasonConfig(db.Model):
    __tablename__ = 'season_config'
    __table_args__ = {'extend_existing': True}  # Cho phép mở rộng bảng đã có
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, nullable=False, unique=True)
    summer_start = db.Column(db.Date, nullable=False)
    summer_end = db.Column(db.Date, nullable=False)