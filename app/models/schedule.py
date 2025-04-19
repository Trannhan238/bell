from app import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    bell_time = db.Column(db.Time, nullable=False)  # Thời gian chuông
    bell_type = db.Column(db.String(50), nullable=False, default="custom")  # kiểu chuông (start_class, break_time, etc.)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = CN, 6 = T7
    profile_id = db.Column(db.Integer, db.ForeignKey("bell_profiles.id"), nullable=True)  # giờ mùa hè / đông

    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False)
